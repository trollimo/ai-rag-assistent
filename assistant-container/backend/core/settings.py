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
# Extra LLM call before search to expand slang/abbreviations into a cleaner
# query for embedding. Adds latency (one more generation round-trip) but
# noticeably improves retrieval on informal phrasing -- see main.py's
# _normalize_query for the concrete "кубер" -> "Kubernetes" case that
# motivated this.
NORMALIZE_QUERY = _cfg.get("search", {}).get("normalize_query", True)

REACTIONS_CONTRIBUTE_HINT = _cfg.get("reactions", {}).get(
    "contribute_hint",
    "Не нашли готовый ответ, но знаете его сами? Свяжитесь с командой базы знаний.",
).strip()

# Where the generator writes skill archives + index.json (mounted read-only;
# the assistant container has no source files of its own, see
# rag-generation/docs/skills-architecture.md).
RAG_SKILLS_PATH = Path(os.getenv("RAG_SKILLS_PATH", "/data/skills"))
# Base URL the assistant is reachable at from a developer's machine -- baked
# into download_url handed to MCP clients (get_skill/list_skills), since
# those run outside the container and "localhost:8000" would resolve to
# their own machine, not this one.
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
SKILLS_INSTALL_HINT = _cfg.get("skills", {}).get(
    "install_hint",
    "mkdir -p ~/.config/opencode/skills/{name} && curl -fsSL {download_url} -o /tmp/{name}.zip && unzip -o /tmp/{name}.zip -d ~/.config/opencode/skills/{name}",
).strip()
