from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
from backend.core import settings


class Retriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(settings.RAG_DB_PATH))
        embedding_func = ONNXMiniLM_L6_V2()
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            embedding_function=embedding_func,
        )

    def search(self, query: str, top_k: int = 5):
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
        return matches
