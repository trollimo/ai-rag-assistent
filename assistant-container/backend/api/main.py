import logging

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag.retriever import Retriever
from backend.rag.prompts import RAG_PROMPT_TEMPLATE
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


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list


@app.get("/")
def root():
    return {"status": "ok"}


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResponse(BaseModel):
    matches: list


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    logger.debug("REST /search query=%s top_k=%d", req.query, req.top_k)
    matches = retriever.search(req.query, top_k=req.top_k)
    logger.debug("REST /search result count=%d", len(matches))
    return SearchResponse(matches=matches)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    logger.info("REST /chat question=%s", req.question[:120])

    matches = retriever.search(req.question, top_k=5)
    context = "\n\n".join([m["text"] for m in matches])
    logger.debug("RAG context chunks=%d chars=%d", len(matches), len(context))

    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=req.question)
    answer = await _ask_llama(prompt)

    logger.info("REST /chat answer=%s", answer[:200])
    return ChatResponse(
        question=req.question,
        answer=answer,
        sources=[{"source": m["source"], "chunk": m["chunk"]} for m in matches],
    )


async def _ask_llama(prompt: str) -> str:
    logger.debug("LLM ask prompt_preview=%s ...", prompt[:150])
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{settings.LLAMA_HOST}/v1/chat/completions",
                json={
                    "model": settings.LLAMA_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                },
            )
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"]
            logger.debug("LLM reply chars=%d", len(result))
            return result
    except Exception as e:
        logger.error("LLM error: %s", e)
        return f"[LLM error: {e}]"
