from pathlib import Path

RAG_DB_PATH = Path("/data/chroma_db")
COLLECTION_NAME = "knowledge_base"
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "phi4-mini"
