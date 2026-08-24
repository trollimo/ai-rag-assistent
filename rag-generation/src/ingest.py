import hashlib
import logging
import os
import time
from pathlib import Path
import json
import yaml
from chroma_client import build_client
from embedding_fn import MultilingualEmbeddingFunction
from chunking import split_markdown, generate_manifest
from skills import find_skill_roots, parse_skill_metadata, build_skill_archive

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


def chunk_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def build_fingerprint(cfg, model_name):
    """Settings that make previously stored vectors incomparable when changed."""
    return {
        "model": model_name,
        "chunk_size": cfg["chunking"]["chunk_size"],
        "overlap": cfg["chunking"]["overlap"],
        "e5_prefixes": bool(os.environ.get("RAG_EMBED_E5_PREFIXES", "")),
    }


def load_manifest(path):
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Cannot read manifest (%s), rebuilding from scratch", e)
        return {}


def plan_changes(previous, current_hashes, fingerprint):
    """Return (ids_to_embed, ids_to_delete, reason).

    A changed fingerprint forces a full rebuild: vectors made with different
    settings cannot be compared against new ones.
    """
    if previous.get("fingerprint") != fingerprint:
        if previous:
            log.info("Build settings changed -> full reindex")
            log.info("  was: %s", previous.get("fingerprint"))
            log.info("  now: %s", fingerprint)
        return list(current_hashes), [], "full"

    old_hashes = previous.get("hashes")
    if not old_hashes:
        return list(current_hashes), [], "full"

    changed = [cid for cid, h in current_hashes.items() if old_hashes.get(cid) != h]
    removed = [cid for cid in old_hashes if cid not in current_hashes]
    return changed, removed, "incremental"


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
    client = build_client(
        cfg.get("storage", {}),
        (BASE_DIR / cfg["storage"]["path"]).resolve(),
    )
    model_name = cfg.get("embeddings", {}).get("model", MultilingualEmbeddingFunction.DEFAULT_MODEL)
    embedding_func = MultilingualEmbeddingFunction(model_name=model_name)
    collection = client.get_or_create_collection(
        name=cfg["storage"]["collection"],
        embedding_function=embedding_func,
    )

    docs, ids, metas = [], [], []
    source_names = []
    skills_index = []  # populated only by type: skills sources

    for source in cfg["sources"]:
        source_dir = (BASE_DIR / source["path"]).resolve()
        if not source_dir.exists():
            log.warning("Source dir not found: %s", source_dir)
            continue

        if source.get("type") == "skills":
            skill_roots = find_skill_roots(source_dir)
            if not skill_roots:
                log.warning("No skill folders (with SKILL.md) in %s", source["path"])
                continue
            archive_cfg = source.get("archive", {})
            skills_out_dir = BASE_DIR / "output" / "skills"
            for skill_root in skill_roots:
                meta = parse_skill_metadata(skill_root)
                log.info("Skill '%s' (%s): %s", meta["name"], meta["version"], meta["description"][:80])

                # RAG side: only the .md files, same chunker as everything else.
                md_files = list(iter_md_files(skill_root, source.get("include")))
                for file_path in md_files:
                    text = file_path.read_text(encoding="utf-8-sig")
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
                            # Lets the assistant recognize "this chunk belongs
                            # to an installable skill" without re-parsing text.
                            "is_skill": True,
                            "skill_name": meta["name"],
                            "skill_root": skill_root.relative_to(BASE_DIR).as_posix(),
                        })
                source_names.append(source["name"])

                # Install side: the whole folder, zipped. Always rebuilt --
                # these are small (single-digit MB), not worth the extra
                # staleness-tracking complexity that bit prepare-offline-bundle.ps1.
                dest_zip = skills_out_dir / f"{meta['name']}.zip"
                archive_info = build_skill_archive(
                    skill_root,
                    exclude_patterns=archive_cfg.get("exclude", []),
                    max_size_mb=archive_cfg.get("max_size_mb", 25),
                    dest_zip=dest_zip,
                )
                skills_index.append({**meta, **archive_info, "archive": dest_zip.name})
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

    manifest_path = BASE_DIR / "output" / "manifest.json"
    fingerprint = build_fingerprint(cfg, model_name)
    hashes = {cid: chunk_hash(doc) for cid, doc in zip(ids, docs)}
    previous = load_manifest(manifest_path)
    to_embed, to_delete, mode = plan_changes(previous, hashes, fingerprint)

    if mode == "full" and previous:
        # Stale vectors would otherwise linger alongside the new ones
        existing = collection.get(include=[])["ids"]
        if existing:
            log.info("Dropping %d existing chunks before full rebuild", len(existing))
            collection.delete(ids=existing)

    if to_delete:
        log.info("Removing %d chunks that no longer exist in sources", len(to_delete))
        collection.delete(ids=to_delete)

    if to_embed:
        by_id = dict(zip(ids, zip(docs, metas)))
        sub_ids = to_embed
        sub_docs = [by_id[i][0] for i in sub_ids]
        sub_metas = [by_id[i][1] for i in sub_ids]
        log.info("Writing %d of %d chunks to ChromaDB (%s) ...", len(sub_ids), len(ids), mode)
        t0 = time.perf_counter()
        collection.upsert(ids=sub_ids, documents=sub_docs, metadatas=sub_metas)
        upsert_elapsed = time.perf_counter() - t0
        embed_elapsed = embedding_func.total_embed_seconds
        log.info(
            "Timing: upsert_total=%.2fs embedding=%.2fs chroma_write=%.2fs (%d chunks)",
            upsert_elapsed, embed_elapsed, upsert_elapsed - embed_elapsed, len(sub_ids),
        )
    else:
        log.info("Nothing changed — %d chunks already up to date", len(ids))

    manifest = generate_manifest(
        docs, source_names,
        chunk_size=cfg["chunking"]["chunk_size"],
        overlap=cfg["chunking"]["overlap"],
        hashes=hashes,
        fingerprint=fingerprint,
    )
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    log.info("Done! %d chunks indexed (%d embedded, %d removed)",
             len(ids), len(to_embed), len(to_delete))
    log.info("Manifest: %s", manifest_path)

    if skills_index:
        skills_index_path = BASE_DIR / "output" / "skills" / "index.json"
        skills_index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(skills_index_path, "w", encoding="utf-8") as f:
            json.dump({"skills": skills_index}, f, indent=2, ensure_ascii=False)
        log.info("Skills: %d archives built -> %s", len(skills_index), skills_index_path)


if __name__ == "__main__":
    main()
