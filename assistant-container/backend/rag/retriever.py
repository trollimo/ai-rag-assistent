import logging

import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from backend.core import settings

logger = logging.getLogger("backend.rag")


class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(settings.RAG_DB_PATH))
        embedding_func = ONNXMiniLM_L6_V2()
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            embedding_function=embedding_func,
        )
        logger.info("Retriever ready db=%s collection=%s", settings.RAG_DB_PATH, settings.COLLECTION_NAME)

    def search(self, query: str, top_k: int = 5):
        logger.debug("RAG search query=%s top_k=%d", query, top_k)
        result = self.collection.query(query_texts=[query], n_results=top_k)
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
