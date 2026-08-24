import asyncio
import logging
import re
from collections import Counter
from pathlib import Path

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.rag.retriever import Retriever
from backend.rag.skills_registry import SkillsRegistry
from backend.rag.prompts import SYSTEM_PROMPT_STRICT, SYSTEM_PROMPT_COMBINED, RAG_PROMPT_TEMPLATE
from backend.core import settings
from backend.core.logging_config import setup_logging
from backend.core.interaction_cache import InteractionCache
from backend.core.redaction import redact_if
from backend.db import engine as db_engine
from backend.db import repo
from backend.feedback import clustering

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
skills_registry = SkillsRegistry(settings.RAG_SKILLS_PATH / "index.json")

# Holds answers that have not been written to the database yet. Only load
# bearing when log_questions is off: there, an interaction reaches disk only
# if a human reacts to it, and the server keeps its own copy meanwhile
# rather than trusting the client to send everything back.
interaction_cache = InteractionCache()


@app.on_event("startup")
async def _startup():
    # In the background so a slow (or absent) database never delays serving
    # answers -- the assistant has no depends_on for it by design.
    asyncio.create_task(_connect_feedback())


async def _connect_feedback():
    await db_engine.init_with_retry()
    if db_engine.is_available() and settings.FEEDBACK_SHOWCASE:
        asyncio.create_task(clustering.loop(_ask_llama))
        logger.info("Showcase clustering scheduled every %d min",
                    settings.FEEDBACK_CLUSTER_INTERVAL_MINUTES)


@app.on_event("shutdown")
async def _shutdown():
    await db_engine.dispose()

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
    # Anonymous per-browser id from localStorage. Groups one person's
    # activity without identifying them -- used to require several distinct
    # people before a showcase topic goes public, and to de-duplicate votes.
    client_id: str | None = None


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list
    related_topics: list = []
    answer_source: str = "no_info"  # "rag" | "llm_knowledge" | "no_info" -- for the UI badge
    normalized_query: str | None = None  # what was actually embedded for search, if different
    skills: list = []  # [{name, title, download_url}] -- skills touched by the matched chunks
    interaction_id: str | None = None  # handle for POST /feedback; None when module is off


@app.get("/")
def root():
    return {"status": "ok"}


class UiConfigResponse(BaseModel):
    """What the frontend needs to know before rendering optional features."""
    feedback_enabled: bool
    showcase_enabled: bool
    contribute_hint: str


@app.get("/ui/config", response_model=UiConfigResponse)
def ui_config():
    # The reaction buttons and the "Запросы" tab are hidden outright when the
    # feedback module is off -- a deployment without a database should look
    # like the feature was never built, not like it is broken.
    return UiConfigResponse(
        feedback_enabled=settings.FEEDBACK_ENABLED,
        showcase_enabled=settings.FEEDBACK_ENABLED and settings.FEEDBACK_SHOWCASE,
        contribute_hint=settings.REACTIONS_CONTRIBUTE_HINT,
    )


class ReactionsConfigResponse(BaseModel):
    contribute_hint: str


@app.get("/reactions/config", response_model=ReactionsConfigResponse)
def reactions_config():
    # Kept for backward compatibility; /ui/config supersedes it.
    return ReactionsConfigResponse(contribute_hint=settings.REACTIONS_CONTRIBUTE_HINT)


class FeedbackRequest(BaseModel):
    interaction_id: str | None = None
    kind: str  # up | down | contribute
    comment: str | None = None
    author: str | None = None
    client_id: str | None = None


class FeedbackResponse(BaseModel):
    stored: bool
    detail: str | None = None


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(req: FeedbackRequest):
    if not settings.FEEDBACK_ENABLED:
        raise HTTPException(status_code=404, detail="Feedback module is disabled")
    if req.kind not in ("up", "down", "contribute"):
        raise HTTPException(status_code=400, detail="Unknown feedback kind")
    if not db_engine.is_available():
        return FeedbackResponse(stored=False, detail="Хранилище обратной связи недоступно")

    interaction_id = req.interaction_id
    # In log_questions=false mode the interaction is still sitting in memory
    # and has never been written; a reaction is what makes it worth keeping.
    if interaction_id:
        pending = interaction_cache.pop(interaction_id)
        if pending is not None:
            pending["client_id"] = pending.get("client_id") or req.client_id
            await repo.save_interaction(pending)

    comment = redact_if(req.comment or "", settings.FEEDBACK_REDACT) or None
    author = redact_if(req.author or "", settings.FEEDBACK_REDACT) or None

    ok = await repo.save_feedback(interaction_id, req.kind, comment, author, req.client_id)
    if not ok and interaction_id:
        # The interaction is gone (cache expired and it was never logged), so
        # the foreign key cannot hold. Keeping what the person typed still
        # beats discarding it -- admin sees it flagged as context-less.
        ok = await repo.save_feedback(None, req.kind, comment, author, req.client_id)
    return FeedbackResponse(stored=ok, detail=None if ok else "Не удалось сохранить")


# ── Public showcase: topics people asked about that the base cannot answer ──

class ShowcaseTopic(BaseModel):
    id: int
    title: str
    status: str
    question_count: int
    vote_count: int
    resolution: str | None = None
    voted: bool = False


class ShowcaseResponse(BaseModel):
    topics: list[ShowcaseTopic]


@app.get("/requests", response_model=ShowcaseResponse)
async def showcase(client_id: str = ""):
    if not (settings.FEEDBACK_ENABLED and settings.FEEDBACK_SHOWCASE):
        raise HTTPException(status_code=404, detail="Showcase is disabled")
    rows = await repo.published_topics()
    mine = set(await repo.voted_topic_ids(client_id)) if client_id else set()
    return ShowcaseResponse(topics=[
        ShowcaseTopic(**{**r, "voted": r["id"] in mine}) for r in rows
    ])


class VoteRequest(BaseModel):
    client_id: str


class VoteResponse(BaseModel):
    vote_count: int | None


@app.post("/requests/{topic_id}/vote", response_model=VoteResponse)
async def vote(topic_id: int, req: VoteRequest):
    if not (settings.FEEDBACK_ENABLED and settings.FEEDBACK_SHOWCASE):
        raise HTTPException(status_code=404, detail="Showcase is disabled")
    if not req.client_id:
        raise HTTPException(status_code=400, detail="client_id required")
    return VoteResponse(vote_count=await repo.vote_topic(topic_id, req.client_id))


# ── Admin ─────────────────────────────────────────────────────────

def _require_admin(token: str | None):
    """Shared-token gate. Not user auth -- it just closes 'anyone who finds
    the URL'. A blank ADMIN_TOKEN disables the admin API entirely rather
    than leaving it wide open."""
    if not settings.FEEDBACK_ENABLED:
        raise HTTPException(status_code=404, detail="Feedback module is disabled")
    if not settings.ADMIN_TOKEN:
        raise HTTPException(status_code=404, detail="Admin API is disabled (ADMIN_TOKEN unset)")
    if token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Bad admin token")


@app.get("/admin/feedback")
async def admin_feedback(status: str = "", kind: str = "",
                         x_admin_token: str | None = Header(default=None)):
    _require_admin(x_admin_token)
    return {"items": await repo.admin_feedback(status or None, kind or None)}


@app.get("/admin/topics")
async def admin_topics(x_admin_token: str | None = Header(default=None)):
    _require_admin(x_admin_token)
    return {"items": await repo.admin_topics()}


@app.get("/admin/stats")
async def admin_stats(x_admin_token: str | None = Header(default=None)):
    _require_admin(x_admin_token)
    return await repo.stats()


class AdminFeedbackPatch(BaseModel):
    status: str
    resolution: str | None = None


@app.patch("/admin/feedback/{fid}")
async def admin_patch_feedback(fid: int, body: AdminFeedbackPatch,
                               x_admin_token: str | None = Header(default=None)):
    _require_admin(x_admin_token)
    return {"ok": await repo.update_feedback_status(fid, body.status, body.resolution)}


class AdminTopicPatch(BaseModel):
    status: str | None = None
    title: str | None = None
    resolution: str | None = None


@app.patch("/admin/topics/{tid}")
async def admin_patch_topic(tid: int, body: AdminTopicPatch,
                            x_admin_token: str | None = Header(default=None)):
    _require_admin(x_admin_token)
    return {"ok": await repo.update_topic(tid, body.status, body.title, body.resolution)}


@app.post("/admin/cluster")
async def admin_cluster(x_admin_token: str | None = Header(default=None)):
    """Run a clustering pass now instead of waiting for the timer."""
    _require_admin(x_admin_token)
    return await clustering.run_once(_ask_llama)


class SkillSummary(BaseModel):
    name: str
    title: str
    description: str
    version: str
    files_count: int
    size_bytes: int
    download_url: str


class SkillDetail(SkillSummary):
    files: list
    sha256: str
    install_hint: str


class SkillsListResponse(BaseModel):
    skills: list[SkillSummary]


def _skill_summary(entry: dict) -> SkillSummary:
    name = entry["name"]
    return SkillSummary(
        name=name,
        title=entry.get("title", name),
        description=entry.get("description", ""),
        version=entry.get("version", ""),
        files_count=len(entry.get("files", [])),
        size_bytes=entry.get("size_bytes", 0),
        download_url=f"{settings.PUBLIC_BASE_URL}/skills/{name}/archive",
    )


@app.get("/skills", response_model=SkillsListResponse)
def list_skills():
    return SkillsListResponse(skills=[_skill_summary(e) for e in skills_registry.list()])


@app.get("/skills/{name}", response_model=SkillDetail)
def get_skill(name: str):
    entry = skills_registry.get(name)
    if not entry:
        raise HTTPException(status_code=404, detail="Skill not found")
    summary = _skill_summary(entry)
    install_hint = settings.SKILLS_INSTALL_HINT.format(
        name=summary.name, download_url=summary.download_url
    )
    return SkillDetail(
        **summary.model_dump(),
        files=entry.get("files", []),
        sha256=entry.get("sha256", ""),
        install_hint=install_hint,
    )


@app.get("/skills/{name}/archive")
def download_skill_archive(name: str):
    path = skills_registry.archive_path(name)
    if not path:
        raise HTTPException(status_code=404, detail="Skill archive not found")
    return FileResponse(path, media_type="application/zip", filename=path.name)


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

    # Embed once and reuse. The dominant-source path runs retrieval twice and
    # used to re-embed the same text each time -- pure waste on a CPU where
    # one embedding costs ~1-2s. Off the event loop for the same reason
    # (CLAUDE.md item #8: this call serialises concurrent users).
    query_vector = await asyncio.to_thread(retriever.embed_query, search_query)

    if req.source_name:
        matches = retriever.search(search_query, top_k=settings.DEFAULT_TOP_K,
                                   source_filter=req.source_name, query_vector=query_vector)
    else:
        first_pass = retriever.search(search_query, top_k=settings.DEFAULT_TOP_K,
                                      query_vector=query_vector)
        detected = _detect_source(first_pass)
        if detected:
            matches = retriever.search(search_query, top_k=settings.DEFAULT_TOP_K,
                                       path_filter=detected, query_vector=query_vector)
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

    # Which skills (if any) this answer touches -- structural, from the
    # matched chunks' metadata, no extra LLM call needed. Lets the UI show
    # "📦 this answer touches an installable skill" under the answer.
    skill_names = sorted({m["skill_name"] for m in matches if m.get("skill_name")})
    skills_hit = []
    for skill_name in skill_names:
        entry = skills_registry.get(skill_name)
        if entry:
            skills_hit.append({
                "name": skill_name,
                "title": entry.get("title", skill_name),
                "download_url": f"{settings.PUBLIC_BASE_URL}/skills/{skill_name}/archive",
            })

    interaction_id = await _record_interaction(
        req, search_query, answer, answer_source, matches, skills_hit, query_vector
    )

    return ChatResponse(
        question=req.question,
        answer=answer,
        sources=list(sources_by_file.values()),
        related_topics=related_topics,
        answer_source=answer_source,
        normalized_query=search_query if search_query != req.question else None,
        skills=skills_hit,
        interaction_id=interaction_id,
    )


async def _record_interaction(req: ChatRequest, search_query: str, answer: str,
                              answer_source: str, matches: list, skills_hit: list,
                              query_vector) -> str | None:
    """Persist (or park in memory) what just happened. Never raises.

    The server is the source of truth here on purpose: the alternative --
    having the browser post the question, answer and sources back when
    someone clicks a reaction -- is forgeable, bulky, and can drift from
    what actually happened.
    """
    if not settings.FEEDBACK_ENABLED:
        return None
    try:
        redact = settings.FEEDBACK_REDACT
        interaction_id = repo.new_id()
        # Only unanswered questions get their vector stored: they are the
        # only ones the showcase ever clusters, and 4 KB of float32 on every
        # single interaction would dwarf the rest of the row for nothing.
        keep_vector = answer_source in ("no_info", "llm_knowledge")
        payload = {
            "id": interaction_id,
            "question": redact_if(req.question, redact),
            "normalized_query": redact_if(search_query, redact) if search_query != req.question else None,
            "answer": answer,
            "mode": req.mode,
            "answer_source": answer_source,
            "sources": sorted({m["source"] for m in matches}),
            "chunks": [
                {"id": f"{m['source']}::{m['chunk']}", "distance": m.get("distance")}
                for m in matches
            ],
            "skills": [s["name"] for s in skills_hit],
            "client_id": req.client_id,
            "channel": "web",
            "query_vector": clustering.pack_vector(query_vector) if keep_vector else None,
        }
        if settings.FEEDBACK_LOG_QUESTIONS:
            await repo.save_interaction(payload)
        else:
            # Nothing reaches disk unless a human reacts -- see FeedbackRequest.
            interaction_cache.put(interaction_id, payload)
        return interaction_id
    except Exception as e:
        logger.warning("Recording interaction failed: %s", e)
        return None


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
