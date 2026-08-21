import logging
import re
from collections import Counter
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag.retriever import Retriever
from backend.rag.prompts import SYSTEM_PROMPT_STRICT, SYSTEM_PROMPT_COMBINED, RAG_PROMPT_TEMPLATE
from backend.core import settings
from backend.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("backend.api")

app = FastAPI(title="RAG Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
retriever = Retriever()

# TODO: переделать на расширяемый справочник (YAML/DB)
_STOP_WORDS = {
    "какой", "какая", "какие", "какое", "каких", "каким",
    "что", "как", "где", "когда", "почему",
    "который", "которая", "которое", "которые",
    "быть", "есть", "иметь", "должен", "должна",
    "is", "are", "the", "a", "an", "of", "in", "to", "for",
    "and", "or", "with", "at", "by", "from", "as", "on",
}


class ChatRequest(BaseModel):
    question: str
    source_name: str | None = None
    mode: str = "strict"  # "strict" (RAG only) or "combined" (falls back to LLM's own knowledge)
    # Per-request override for the query-normalization LLM call (UI settings
    # toggle, mainly for testing). None = use the mcp-tools.yaml master
    # switch. The yaml switch wins if it's off -- this can only turn
    # normalization OFF when the master switch is on, never re-enable it
    # when the master switch is off.
    normalize_query: bool | None = None


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list
    related_topics: list = []
    answer_source: str = "no_info"  # "rag" | "llm_knowledge" | "no_info" -- for the UI badge
    normalized_query: str | None = None  # what was actually embedded for search, if different


@app.get("/")
def root():
    return {"status": "ok"}


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResponse(BaseModel):
    matches: list


class TopicsRequest(BaseModel):
    filter: str = ""
    top_k: int | None = None


class TopicItem(BaseModel):
    source: str
    source_name: str
    chunks: int
    snippet: str


class TopicsResponse(BaseModel):
    topics: list[TopicItem]
    total: int


@app.post("/topics", response_model=TopicsResponse)
def list_topics(req: TopicsRequest):
    top_k = req.top_k if req.top_k is not None else settings.TOPICS_DEFAULT_TOP_K
    logger.debug("REST /topics filter=%s top_k=%d", req.filter, top_k)
    topics = retriever.list_topics(filter=req.filter, top_k=top_k)
    logger.debug("REST /topics result count=%d", len(topics))
    return TopicsResponse(topics=topics, total=len(topics))


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    logger.debug("REST /search query=%s top_k=%d", req.query, req.top_k)
    matches = retriever.search(req.query, top_k=req.top_k)
    logger.debug("REST /search result count=%d", len(matches))
    return SearchResponse(matches=matches)


def _detect_source(first_matches: list) -> str | None:
    stems = [Path(m["source"]).stem for m in first_matches]
    if not stems:
        return None
    dominant = Counter(stems).most_common(1)[0]
    threshold = len(stems) // 2 + 1
    if dominant[1] >= threshold:
        src = first_matches[[s for s in stems].index(dominant[0])]["source"]
        logger.debug("RAG detected source=%s (%d/%d chunks)", dominant[0], dominant[1], len(stems))
        return src
    logger.debug("RAG no dominant source: %s", Counter(stems))
    return None


_NORMALIZE_SYSTEM_PROMPT = (
    "Перефразируй вопрос пользователя в чёткий поисковый запрос для технической "
    "базы знаний. Разверни сленг и сокращения в полные термины (кубер -> "
    "Kubernetes, докер -> Docker, апи -> API и т.п.). Не отвечай на вопрос, "
    "верни только сам переформулированный запрос, без пояснений и кавычек."
)


async def _normalize_query(question: str, enabled: bool | None) -> str:
    """Rewrite a possibly slang/terse question into a clearer search query.

    Mirrors what MCP tool-calling agents do naturally when they pick their
    own search terms (e.g. OpenCode turning "что такое кубер" into "что
    такое Kubernetes" before calling search_docs) -- embedding the raw,
    informal question directly retrieves noticeably worse than embedding a
    canonical phrasing of the same question.

    Only used by /chat (the web UI). /search (what MCP's search_docs calls)
    never normalizes -- an MCP tool-calling agent already picks its own
    search terms, so this would be redundant there.
    """
    if not settings.NORMALIZE_QUERY:
        return question  # master switch off -- no per-request override can re-enable
    if enabled is False:
        return question  # per-request override off
    try:
        normalized = await _ask_llama([
            {"role": "system", "content": _NORMALIZE_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ])
        normalized = normalized.strip().strip('"')
        return normalized or question
    except Exception as e:
        logger.warning("Query normalization failed, using raw question: %s", e)
        return question  # fail open


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    logger.info("REST /chat question=%s source_name=%s mode=%s", req.question, req.source_name, req.mode)

    search_query = await _normalize_query(req.question, req.normalize_query)
    if search_query != req.question:
        logger.debug("Normalized query: %r -> %r", req.question, search_query)

    if req.source_name:
        matches = retriever.search(search_query, top_k=settings.DEFAULT_TOP_K, source_filter=req.source_name)
    else:
        first_pass = retriever.search(search_query, top_k=settings.DEFAULT_TOP_K)
        detected = _detect_source(first_pass)
        if detected:
            matches = retriever.search(search_query, top_k=settings.DEFAULT_TOP_K, path_filter=detected)
        else:
            matches = first_pass

    context = "\n\n".join([m['text'] for m in matches])
    logger.debug("RAG context=%s", context)

    # Combined mode always gets the combined prompt, not just when matches is
    # empty -- retrieval can return real chunks that simply don't answer the
    # question (e.g. "что такое кубер" pulls Deployment/Service/HPA docs,
    # none of which define Kubernetes), and the strict prompt's "only use
    # context" instruction would make the model say "no information" anyway,
    # silently ignoring the user's combined-mode toggle.
    system_prompt = SYSTEM_PROMPT_COMBINED if req.mode == "combined" else SYSTEM_PROMPT_STRICT

    user_prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=req.question)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    answer = await _ask_llama(messages)

    # SYSTEM_PROMPT_COMBINED requires this exact marker when the model used
    # (fully or partly) its own knowledge instead of the context -- structural
    # signal instead of guessing from matches count, which is what silently
    # mislabeled the "кубер" case above. Stripped from the visible answer
    # since the UI badge already conveys it. Despite the prompt demanding the
    # marker be the very first characters, the model sometimes prepends a
    # meta-commentary sentence about following the instruction first -- search
    # the whole answer (not just the prefix) and drop everything up to and
    # including the marker, since that preamble is never meant for the user.
    off_base_marker = "(частично или полностью не из базы знаний)"
    marker_pos = answer.find(off_base_marker)
    if marker_pos != -1:
        answer = answer[marker_pos + len(off_base_marker):].lstrip(" :-\n")
        answer_source = "llm_knowledge"
    else:
        answer_source = "rag" if matches else "no_info"

    logger.info("REST /chat answer=%s answer_source=%s", answer, answer_source)

    used_names = {Path(m["source"]).stem for m in matches}
    related_topics = [
        t for t in retriever.list_topics(top_k=settings.TOPICS_DEFAULT_TOP_K)
        if Path(t["source"]).stem not in used_names
    ][:4]

    # One row per source file, not per chunk -- multiple chunks from the same
    # doc used to render as repeated entries. Keeps every matched chunk's
    # text/distance so the UI can expand any of them, not just the first.
    sources_by_file: dict[str, dict] = {}
    for m in matches:
        entry = sources_by_file.setdefault(m["source"], {"source": m["source"], "chunks": []})
        entry["chunks"].append({"chunk": m["chunk"], "text": m["text"], "distance": m.get("distance")})

    return ChatResponse(
        question=req.question,
        answer=answer,
        sources=list(sources_by_file.values()),
        related_topics=related_topics,
        answer_source=answer_source,
        normalized_query=search_query if search_query != req.question else None,
    )


async def _ask_llama(messages: list) -> str:
    logger.debug("LLM messages=%s", messages)
    body = {
        "model": settings.LLM_MODEL_NAME,
        "messages": messages,
        "max_tokens": settings.LLM_MAX_TOKENS,
        "stream": False,
    }
    headers = {}
    if settings.LLM_API_KEY:
        headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{settings.LLM_BASE_URL.rstrip('/')}/v1/chat/completions",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"]
            logger.debug("LLM reply=%s", result)
            return result
    except Exception as e:
        logger.error("LLM error: %s", e)
        return f"[LLM error: {e}]"
