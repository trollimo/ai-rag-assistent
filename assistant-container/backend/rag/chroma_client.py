"""One place that decides how we talk to Chroma.

Two modes, same `Collection` API afterwards -- `PersistentClient` and
`HttpClient` are interchangeable for everything this project does, so the
rest of the code never learns which one it got.

* **file** (default): the embedded client opens the SQLite index directly.
  Simple, no extra service, and the only option when running the generator
  as a plain script without Docker. Its limit is the reason server mode
  exists: two processes cannot hold the same index while one of them
  writes, so reindexing means stopping the assistant.
* **server**: a separate `chroma` container owns the index; generator and
  assistant are both clients. Reindexing no longer requires downtime, which
  is what makes webhook-driven reindexing possible at all.

Deliberately NOT the default: server mode adds a container, a volume, an
image to ship into the closed network, and a client/server version pairing
to keep in step. That is worth it once reindexing is automated, and not
before.
"""
import logging

import chromadb

logger = logging.getLogger("backend.rag")


def build_client(mode: str, db_path, host: str, port: int, ssl: bool = False):
    """Return a Chroma client for `mode` ("file" or "server")."""
    if mode == "server":
        logger.info("Chroma: server mode at %s:%s (ssl=%s)", host, port, ssl)
        return chromadb.HttpClient(host=host, port=port, ssl=ssl)
    if mode != "file":
        logger.warning("Unknown Chroma mode %r, falling back to 'file'", mode)
    logger.info("Chroma: embedded (file) mode at %s", db_path)
    return chromadb.PersistentClient(path=str(db_path))
