from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from backend.core import settings


class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDINGS_MODEL)
        self.client = chromadb.PersistentClient(path=str(settings.RAG_DB_PATH))
        self.collection = self.client.get_or_create_collection(name=settings.COLLECTION_NAME)

    def search(self, query: str, top_k: int = 5):
        q_emb = self.model.encode(query).tolist()
        result = self.collection.query(query_embeddings=[q_emb], n_results=top_k)
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
