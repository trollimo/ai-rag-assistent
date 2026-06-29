import os
from pathlib import Path

RAG_DB_PATH = Path(os.getenv("RAG_DB_PATH", "/data/chroma_db"))
COLLECTION_NAME = "knowledge_base"
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
LLAMA_HOST = os.getenv("LLAMA_HOST", "http://localhost:9080")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "qwen2.5")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
