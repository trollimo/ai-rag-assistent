import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag.retriever import Retriever
from backend.rag.prompts import RAG_PROMPT_TEMPLATE
from backend.core import settings

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
    matches = retriever.search(req.query, top_k=req.top_k)
    return SearchResponse(matches=matches)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    matches = retriever.search(req.question, top_k=5)
    context = "\n\n".join([m["text"] for m in matches])

    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=req.question)
    answer = await _ask_llama(prompt)

    return ChatResponse(
        question=req.question,
        answer=answer,
        sources=[{"source": m["source"], "chunk": m["chunk"]} for m in matches],
    )


async def _ask_llama(prompt: str) -> str:
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
            return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM error: {e}]"
