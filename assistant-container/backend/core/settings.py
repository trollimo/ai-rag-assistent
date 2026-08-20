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
# LLM endpoint — any OpenAI-compatible /v1/chat/completions server:
# the bundled llama-server, or a corporate model reached over the network.
# LLAMA_* names are the pre-split spelling, kept so old deploys keep working.
LLM_BASE_URL = os.getenv("LLM_BASE_URL") or os.getenv("LLAMA_HOST", "http://localhost:9080")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME") or os.getenv("LLAMA_MODEL", "qwen2.5")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

# Deprecated aliases
LLAMA_HOST = LLM_BASE_URL
LLAMA_MODEL = LLM_MODEL_NAME
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DEFAULT_TOP_K = _cfg.get("search", {}).get("default_top_k", 3)
MAX_DISTANCE = _cfg.get("search", {}).get("max_distance")
TOPICS_DEFAULT_TOP_K = _cfg.get("topics", {}).get("default_top_k", 100)
TOPICS_MAX = _cfg.get("topics", {}).get("max_topics", 500)

LLM_MAX_TOKENS = _cfg.get("llm", {}).get("max_tokens", 2048)
CHAT_SHOW_SOURCES = _cfg.get("chat", {}).get("show_sources", False)
CHAT_SOURCES_SEPARATOR = _cfg.get("chat", {}).get("sources_separator", "\n\n---\n**Источники:** ")
