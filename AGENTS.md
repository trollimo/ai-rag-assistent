# AGENTS.md — контекст для AI-агентов

## 🧠 О проекте

Локальная offline-система RAG знаний с двумя точками входа:
- **Человек** → Next.js Web UI → FastAPI → RAG → локальная LLM → ответ
- **Агент opencode** → MCP (stdio) → FastAPI RAG service → ответ

## 📁 Структура

```
├── rag-generation/       # 🏗️ Построение RAG-базы (offline)
│   ├── config/rag-sources.yaml
│   ├── docs/rules/        # примеры .md для обучения
│   ├── docs/poetry/
│   ├── output/chroma_db/  # сгенерированная БД
│   ├── src/
│   │   ├── ingest.py
│   │   ├── chunking.py
│   │   ├── embeddings.py
│   │   └── storage.py
│   ├── rag-generate.ps1
│   ├── rag-generate.sh
│   └── requirements.txt
│
└── assistant-container/   # 🐳 Runtime: Web + MCP (один контейнер)
    ├── backend/
    │   ├── api/main.py        # FastAPI (port 8000)
    │   ├── core/settings.py   # конфиги
    │   ├── mcp/server.py      # MCP tool (stdio, отдельный процесс)
    │   ├── rag/retriever.py   # поиск по ChromaDB
    │   └── rag/prompts.py     # промпты для LLM
    ├── web/                   # Next.js (port 3000)
    │   ├── app/
    │   ├── components/
    │   └── styles/
    ├── Dockerfile            # multi-stage: ollama + python + node
    ├── docker-compose.yml
    ├── requirements.txt
    ├── package.json
    └── next.config.js
```

## 🧰 Стек

| Компонент | Технология |
|-----------|-----------|
| Vector DB | ChromaDB (PersistentClient) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Backend API | FastAPI (port 8000) |
| Frontend | Next.js + TailwindCSS (port 3000) |
| LLM Runtime | Ollama (port 11434) + phi4-mini |
| MCP | FastMCP (stdio transport, отдельный процесс) |
| Контейнеры | Docker + docker-compose (один контейнер) |

## 🔗 Ссылки

- https://opencode.ai/docs/mcp-servers
- https://docs.trychroma.com/guides/build/chunking
- https://github.com/vercel-labs/nextjs-fastapi-chat-app-starter

## 📌 Состояние

Начальная стадия. Скелет кода есть в main-project-goal.md.
Требуется реализовать все модули и собрать Docker.
