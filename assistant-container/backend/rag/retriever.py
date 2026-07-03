import logging

import chromadb
from backend.rag.embedding_fn import MultilingualEmbeddingFunction
from backend.core import settings

logger = logging.getLogger("backend.rag")


class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(settings.RAG_DB_PATH))
        embedding_func = MultilingualEmbeddingFunction(model_name=settings.EMBEDDINGS_MODEL)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            embedding_function=embedding_func,
        )
        count = self.collection.count()
        if count:
            data = self.collection.get(limit=count, include=["metadatas"])
            topics = len(set(m["source"] for m in data["metadatas"]))
            logger.info("Retriever ready db=%s collection=%s — %d chunks, %d topics",
                         settings.RAG_DB_PATH, settings.COLLECTION_NAME, count, topics)
        else:
            logger.info("Retriever ready db=%s collection=%s — empty",
                         settings.RAG_DB_PATH, settings.COLLECTION_NAME)

    def search(self, query: str, top_k: int = 5, source_filter: str | None = None, path_filter: str | None = None):
        logger.debug("RAG search query=%s top_k=%d source_filter=%s path_filter=%s", query, top_k, source_filter, path_filter)
        where = {}
        if source_filter:
            where["source_name"] = source_filter
        if path_filter:
            where["source"] = {"$contains": path_filter}
        if not where:
            where_clause = None
        else:
            where_clause = {"$and": [{k: v} for k, v in where.items()]} if len(where) > 1 else where
        result = self.collection.query(query_texts=[query], n_results=top_k, where=where_clause)
        matches = []
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            matches.append({
                "text": doc,
                "source": meta["source"],
                "chunk": meta["chunk"],
                "distance": dist,
            })

        logger.debug("RAG search result count=%d sources=%s",
                     len(matches), [m["source"] for m in matches])
        return matches

    def list_topics(self, filter: str = "", top_k: int = 100):
        count = self.collection.count()
        logger.debug("RAG list_topics count=%d filter=%s top_k=%d", count, filter, top_k)
        if count == 0:
            return []

        limit = min(count, settings.TOPICS_MAX)
        data = self.collection.get(limit=limit)

        groups = {}
        for doc, meta in zip(data["documents"], data["metadatas"]):
            src = meta.get("source", "unknown")
            if filter and filter.lower() not in src.lower():
                continue
            if src not in groups:
                groups[src] = {
                    "source": src,
                    "source_name": meta.get("source_name", ""),
                    "chunks": 0,
                    "snippet": "",
                }
            groups[src]["chunks"] += 1
            if not groups[src]["snippet"]:
                groups[src]["snippet"] = doc.strip()[:200]

        result = sorted(groups.values(), key=lambda x: -x["chunks"])[:top_k]
        logger.debug("RAG list_topics result count=%d", len(result))
        return result
