import logging
from pathlib import Path
import json
import yaml
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from chunking import split_markdown, generate_manifest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("rag-generator")

BASE_DIR = Path(__file__).resolve().parent.parent


def load_config():
    config_path = BASE_DIR / "config" / "rag-sources.yaml"
    log.info("Loading config: %s", config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def iter_md_files(root, patterns):
    if not patterns:
        patterns = ["**/*.md"]
    seen = set()
    for pat in patterns:
        for f in Path(root).glob(pat):
            resolved = f.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield resolved


def main():
    cfg = load_config()
    client = chromadb.PersistentClient(
        path=str((BASE_DIR / cfg["storage"]["path"]).resolve())
    )
    embedding_func = ONNXMiniLM_L6_V2()
    collection = client.get_or_create_collection(
        name=cfg["storage"]["collection"],
        embedding_function=embedding_func,
    )

    docs, ids, metas = [], [], []
    source_names = []

    for source in cfg["sources"]:
        source_dir = (BASE_DIR / source["path"]).resolve()
        if not source_dir.exists():
            log.warning("Source dir not found: %s", source_dir)
            continue
        files = list(iter_md_files(source_dir, source.get("include")))
        if not files:
            log.warning("No .md files in %s", source["path"])
            continue
        for file_path in files:
            try:
                display = file_path.relative_to(BASE_DIR)
            except ValueError:
                display = file_path
            log.info("Parsing %s", display)
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
            source_names.append(source["name"])

    if docs:
        log.info("Writing %d chunks to ChromaDB ...", len(docs))
        collection.add(ids=ids, documents=docs, metadatas=metas)

    manifest = generate_manifest(
        docs, source_names,
        chunk_size=cfg["chunking"]["chunk_size"],
        overlap=cfg["chunking"]["overlap"],
    )
    manifest_path = BASE_DIR / "output" / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    log.info("Done! Indexed %d chunks", len(docs))
    log.info("Manifest: %s", manifest_path)


if __name__ == "__main__":
    main()
