"""How the generator connects to Chroma -- mirrors the assistant's factory.

`PersistentClient` and `HttpClient` expose the same `Collection` API, so
`ingest.py` is identical in both modes: only the client differs. That is why
there is one generator, not two.

* **file** (default): writes the SQLite index directly. Required for the
  standalone `rag-generate.ps1` path, which runs in a venv without Docker.
  Cannot be used while the assistant holds the same index.
* **server**: upserts into a running `chroma` service, so indexing no longer
  requires stopping the assistant.

Env vars override the yaml so the same config file works in both a local run
and a container: RAG_CHROMA_MODE / RAG_CHROMA_HOST / RAG_CHROMA_PORT.
"""
import logging
import os

import chromadb

log = logging.getLogger("rag-generator")


def build_client(storage_cfg: dict, db_path):
    """Return a Chroma client from the `storage:` block, env vars winning."""
    mode = os.environ.get("RAG_CHROMA_MODE") or storage_cfg.get("mode", "file")
    mode = str(mode).strip().lower()

    if mode == "server":
        host = os.environ.get("RAG_CHROMA_HOST") or storage_cfg.get("host", "localhost")
        port = int(os.environ.get("RAG_CHROMA_PORT") or storage_cfg.get("port", 8001))
        log.info("Chroma: server mode at %s:%s", host, port)
        return chromadb.HttpClient(host=host, port=port)

    if mode != "file":
        log.warning("Unknown storage.mode %r, falling back to 'file'", mode)
    log.info("Chroma: embedded (file) mode at %s", db_path)
    return chromadb.PersistentClient(path=str(db_path))
