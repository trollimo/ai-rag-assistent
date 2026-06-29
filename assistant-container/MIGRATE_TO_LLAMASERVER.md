# Migration: Ollama → llama.cpp (OpenAI-compatible API)

## Статус (28.06.2026)

### ✅ Выполнено

- `Dockerfile.offline` — переписан на multi-stage:
  - `samueltallet/alpine-llama-cpp-server` → llama-server binary (glibc b9804)
  - `node:20-slim` → node binary
  - `python:3.11-slim` → финальный слой (Python + Node.js + llama-server)
- Образ собран: `rag-assistant-offline:test` — **1.19 GB**
- `backend/core/settings.py` — OLLAMA_HOST/LLAMA_MODEL → LLAMA_HOST/LLAMA_MODEL
- `backend/api/main.py` — `_ask_ollama` на `_ask_llama`, API с `/api/generate` на `/v1/chat/completions`
- `docker-compose.yml` — порт 11434 → 9080, OLLAMA_HOST → LLAMA_HOST
- CORS middleware добавлен в main.py
- Полный smoke-тест (4/4) пройден

### ❌ Осталось сделать

- `Dockerfile` (online) — переписать под llama-server (аналогично Dockerfile.offline)

---

## ~~1. `backend/core/settings.py`~~ ✅ Готово

Заменить `OLLAMA_HOST` / `OLLAMA_MODEL` на `LLAMA_HOST` / `LLAMA_MODEL`:

```python
from pathlib import Path

RAG_DB_PATH = Path("/data/chroma_db")
COLLECTION_NAME = "knowledge_base"
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"
LLAMA_HOST = "http://localhost:9080"
LLAMA_MODEL = "qwen2.5"
```

## 2. `backend/api/main.py`

Переименовать `_ask_ollama` → `_ask_llama`, заменить вызов с `/api/generate` (Ollama) на `/v1/chat/completions` (OpenAI-формат):

```python
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
```

Также заменить вызов в `/chat`:
```python
answer = await _ask_ollama(prompt)  # → answer = await _ask_llama(prompt)
```

## 3. `docker-compose.yml`

Заменить порт `11434` → `9080`, `OLLAMA_HOST` → `LLAMA_HOST`:

```yaml
ports:
  - "3000:3000"
  - "8000:8000"
  - "9080:9080"
environment:
  - LLAMA_HOST=http://localhost:9080
```

## 4. `Dockerfile` (online)

Переписать аналогично `Dockerfile.offline`:

```dockerfile
# ── Stage 1: llama-server binary ────────────────────────────────
FROM samueltallet/alpine-llama-cpp-server:latest AS llama-source

# ── Stage 2: Node binary ────────────────────────────────────────
FROM node:20-slim AS node-source

# ── Stage 3: Final image ────────────────────────────────────────
FROM python:3.11-slim

# llama-server (statically linked, works on glibc)
COPY --from=llama-source /opt/llama.cpp/llama-server /usr/local/bin/llama-server

# Node binary for Next.js runtime
COPY --from=node-source /usr/local/bin/node /usr/local/bin/node

# Python dependencies
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Pre-cache fastembed model
RUN python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()"

# Backend source
COPY backend /app/backend

# Next.js standalone
WORKDIR /app/web
COPY web/package.json ./
RUN npm install
COPY web/ ./
RUN npm run build

WORKDIR /app

ENV LLAMA_HOST=http://localhost:8080
ENV LLAMA_MODEL=qwen2.5
ENV NODE_ENV=production

EXPOSE 9080 8000 9081 3000

CMD ["sh", "-c", "\
  llama-server --host 0.0.0.0 --port 9080 -m /models/qwen2.5.gguf --alias qwen2.5 & \
  sleep 2 && \
  uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 & \
  node /app/web/server.js"]
```

Для онлайн-сборки модель можно скачать через curl:
```dockerfile
RUN curl -Lo /models/qwen2.5.gguf \
  https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf
```
