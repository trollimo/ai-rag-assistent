import os
from pathlib import Path

import yaml


def _load_rag_config() -> dict:
    config_path = Path(__file__).resolve().parent.parent / "config" / "mcp-tools.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_cfg = _load_rag_config()

RAG_DB_PATH = Path(os.getenv("RAG_DB_PATH", "/data/chroma_db"))
COLLECTION_NAME = "knowledge_base"
EMBEDDINGS_MODEL = "intfloat/multilingual-e5-large"
LLAMA_HOST = os.getenv("LLAMA_HOST", "http://localhost:9080")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "qwen2.5")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DEFAULT_TOP_K = _cfg.get("search", {}).get("default_top_k", 3)
TOPICS_DEFAULT_TOP_K = _cfg.get("topics", {}).get("default_top_k", 100)
TOPICS_MAX = _cfg.get("topics", {}).get("max_topics", 500)

LLM_MAX_TOKENS = _cfg.get("llm", {}).get("max_tokens", 2048)
CHAT_SHOW_SOURCES = _cfg.get("chat", {}).get("show_sources", False)
CHAT_SOURCES_SEPARATOR = _cfg.get("chat", {}).get("sources_separator", "\n\n---\n**Источники:** ")
