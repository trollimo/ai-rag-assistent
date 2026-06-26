from pathlib import Path
import json
import yaml
import chromadb
from sentence_transformers import SentenceTransformer
from chunking import split_markdown, generate_manifest

BASE_DIR = Path(__file__).resolve().parent.parent


def load_config():
    with open(BASE_DIR / "config" / "rag-sources.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def iter_md_files(root):
    yield from Path(root).rglob("*.md")


def main():
    cfg = load_config()
    model = SentenceTransformer(cfg["embeddings"]["model"])
    client = chromadb.PersistentClient(
        path=str(BASE_DIR / cfg["storage"]["path"].lstrip("./"))
    )
    collection = client.get_or_create_collection(name=cfg["storage"]["collection"])

    docs, ids, metas, embs = [], [], [], []
    source_names = []

    for source in cfg["sources"]:
        source_dir = BASE_DIR / source["path"].lstrip("./")
        if not source_dir.exists():
            print(f"  [!] source dir not found: {source_dir}")
            continue
        for file_path in iter_md_files(source_dir):
            print(f"  [>] {file_path.relative_to(BASE_DIR)}")
            text = file_path.read_text(encoding="utf-8")
            chunks = split_markdown(
                text,
                max_chars=cfg["chunking"]["chunk_size"],
                overlap=cfg["chunking"]["overlap"],
            )
            for idx, chunk in enumerate(chunks):
                doc_id = f"{file_path.as_posix()}::{idx}"
                docs.append(chunk)
                ids.append(doc_id)
                metas.append({
                    "source": file_path.as_posix(),
                    "source_name": source["name"],
                    "chunk": idx,
                })
                embs.append(model.encode(chunk).tolist())
            source_names.append(source["name"])

    if docs:
        print(f"\n  [*] Writing {len(docs)} chunks to ChromaDB ...")
        collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embs)

    manifest = generate_manifest(docs, source_names)
    manifest_path = BASE_DIR / "output" / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n  [v] Done! Indexed {len(docs)} chunks")
    print(f"  [~] Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
