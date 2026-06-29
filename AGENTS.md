# AGENTS.md — контекст для AI-агентов

## 🧠 О проекте

Локальная offline-система RAG знаний с двумя точками входа:
- **Человек** → Next.js Web UI → FastAPI → RAG → локальная LLM → ответ
- **Агент opencode** → MCP (stdio) → FastAPI RAG service → ответ

## 📁 Структура

```
├── rag-generation/           # 🏗️ Построение RAG-базы (offline)
│   ├── config/rag-sources.yaml
│   ├── docs/rules/            # примеры .md для обучения
│   ├── docs/poetry/
│   ├── output/chroma_db/      # сгенерированная БД
│   ├── src/
│   │   ├── ingest.py          # chromadb + fastembed (без torch!)
│   │   ├── chunking.py
│   ├── rag-generate.ps1
│   ├── rag-generate.sh
│   └── requirements.txt
│
└── assistant-container/       # 🐳 Runtime: Web + MCP (один контейнер)
    ├── backend/
    │   ├── api/main.py        # FastAPI (port 8000)
    │   ├── core/settings.py   # конфиги
    │   ├── mcp/server.py      # MCP tool (stdio, отдельный процесс)
    │   ├── rag/retriever.py   # chromadb + fastembed (без torch!)
    │   └── rag/prompts.py     # промпты для LLM
    ├── web/                   # Next.js (port 3000)
    │   ├── app/
    │   ├── components/
    │   └── styles/
    ├── Dockerfile             # TODO: переписать под llama-server
    ├── Dockerfile.offline     # multi-stage: llama-server + python:3.11-slim + node
    ├── prepare-offline-bundle.ps1  # скачивает всё для офлайн-сборки
    ├── docker-compose.yml
    ├── requirements.txt
    ├── package.json
    ├── MIGRATE_TO_LLAMASERVER.md  # план миграции Ollama → llama.cpp
    ├── offline-bundle/        # предзагруженные артефакты для offline-сборки
    └── next.config.js
```

## 🧰 Стек

| Компонент | Технология |
|-----------|-----------|
| Vector DB | ChromaDB (PersistentClient) |
| Embeddings | fastembed / all-MiniLM-L6-v2 (ONNX, без torch) |
| Backend API | FastAPI (port 8000) |
| Frontend | Next.js + TailwindCSS (port 3000) |
| LLM Runtime | llama-server (port 8080) + qwen2.5-1.5b-instruct Q4_K_M (llama.cpp) |
| MCP | FastMCP (stdio transport, отдельный процесс) |
| Контейнеры | Docker + docker-compose (один контейнер) |

## 🔗 Ссылки

- https://opencode.ai/docs/mcp-servers
- https://docs.trychroma.com/guides/build/chunking
- https://github.com/vercel-labs/nextjs-fastapi-chat-app-starter

## 📌 Состояние

- [x] RAG-generation: ингрест + чанкинг + chromadb
- [x] Embeddings: fastembed (ONNX, без torch)
- [x] FastAPI backend + retriever
- [x] Dockerfile (offline) — multi-stage: llama-server + python:3.11-slim + node (собран, 1.19 GB)
- [x] Dockerfile (online) — multi-stage: llama-server + python:3.11-slim + node, модель качается с HuggingFace
- [x] prepare-offline-bundle.ps1 — скачивает бандл для офлайна
- [x] MCP server (stdio + HTTP SSE)
- [x] Web UI (Next.js чат)
- [x] backend/core/settings.py — заменить OLLAMA_HOST на LLAMA_HOST
- [x] backend/api/main.py — заменить Ollama API на OpenAI-формат llama-server
- [x] docker-compose.yml — порт 11434 → 8080
