import logging
import re
from collections import Counter
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag.retriever import Retriever
from backend.rag.prompts import SYSTEM_PROMPT, RAG_PROMPT_TEMPLATE
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


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list
    related_topics: list = []


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


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    logger.info("REST /chat question=%s source_name=%s", req.question, req.source_name)

    if req.source_name:
        matches = retriever.search(req.question, top_k=settings.DEFAULT_TOP_K, source_filter=req.source_name)
    else:
        first_pass = retriever.search(req.question, top_k=settings.DEFAULT_TOP_K)
        detected = _detect_source(first_pass)
        if detected:
            matches = retriever.search(req.question, top_k=settings.DEFAULT_TOP_K, path_filter=detected)
        else:
            matches = first_pass

    context = "\n\n".join([m['text'] for m in matches])
    logger.debug("RAG context=%s", context)

    user_prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=req.question)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    answer = await _ask_llama(messages)

    if settings.CHAT_SHOW_SOURCES and matches:
        source_names = sorted(set(Path(m["source"]).stem for m in matches))
        answer += settings.CHAT_SOURCES_SEPARATOR + ", ".join(source_names)

    logger.info("REST /chat answer=%s", answer)

    used_names = {Path(m["source"]).stem for m in matches}
    related_topics = [
        t for t in retriever.list_topics(top_k=settings.TOPICS_DEFAULT_TOP_K)
        if Path(t["source"]).stem not in used_names
    ][:4]

    return ChatResponse(
        question=req.question,
        answer=answer,
        sources=[{"source": m["source"], "chunk": m["chunk"]} for m in matches],
        related_topics=related_topics,
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
