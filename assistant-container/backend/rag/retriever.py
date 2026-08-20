import logging

import chromadb
from backend.rag.embedding_fn import MultilingualEmbeddingFunction
from backend.core import settings

logger = logging.getLogger("backend.rag")


class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(settings.RAG_DB_PATH))
        self.embedding_func = MultilingualEmbeddingFunction(model_name=settings.EMBEDDINGS_MODEL)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            embedding_function=self.embedding_func,
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
            # Exact match: path_filter is always a full source path handed
            # back by _detect_source(), never a partial string. "$contains"
            # here was wrong -- chromadb's $contains applies to document
            # text (where_document), not metadata (where), so it silently
            # matched nothing and every dominant-source follow-up query
            # returned zero results regardless of max_distance.
            where["source"] = path_filter
        if not where:
            where_clause = None
        else:
            where_clause = {"$and": [{k: v} for k, v in where.items()]} if len(where) > 1 else where
        # Embed the query ourselves so the e5 "query:" prefix is applied —
        # query_texts would route through __call__, which prefixes documents.
        query_vec = self.embedding_func.embed_query(query)
        result = self.collection.query(
            query_embeddings=[query_vec], n_results=top_k, where=where_clause
        )
        matches = []
        dropped = []
        candidates = list(zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ))
        for rank, (doc, meta, dist) in enumerate(candidates):
            # Rank 0 (the single closest match) is always kept, cutoff only
            # applies from rank 1 on. A bare keyword like "Deployment" (no
            # surrounding sentence) embeds measurably farther from its own
            # correct doc than the same word inside a real question does --
            # e.g. 324 vs 246 on this corpus, both past a naive fixed
            # threshold. Every case where an irrelevant chunk actually
            # leaked into an answer (the Kubernetes Service chunk on an
            # unrelated code-review question) was rank 2+, never rank 0 --
            # so dropping only the tail keeps that fix while not returning
            # "no information" when the top hit is genuinely correct.
            if rank > 0 and settings.MAX_DISTANCE is not None and dist > settings.MAX_DISTANCE:
                dropped.append((meta["source"], dist))
                continue
            matches.append({
                "text": doc,
                "source": meta["source"],
                "chunk": meta["chunk"],
                "distance": dist,
            })

        if dropped:
            logger.debug("RAG search dropped %d results past max_distance=%s: %s",
                         len(dropped), settings.MAX_DISTANCE, dropped)
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
