import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from backend.rag.retriever import Retriever
from backend.rag.prompts import RAG_PROMPT_TEMPLATE
from backend.core import settings

app = FastAPI(title="RAG Assistant API")
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


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    matches = retriever.search(req.question, top_k=5)
    context = "\n\n".join([m["text"] for m in matches])

    prompt = RAG_PROMPT_TEMPLATE.format(context=context, question=req.question)
    answer = await _ask_ollama(prompt)

    return ChatResponse(
        question=req.question,
        answer=answer,
        sources=[{"source": m["source"], "chunk": m["chunk"]} for m in matches],
    )


async def _ask_ollama(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{settings.OLLAMA_HOST}/api/generate",
                json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
    except Exception as e:
        return f"[Ollama error: {e}]"
