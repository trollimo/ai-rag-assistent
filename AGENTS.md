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
└── assistant-container/   # 🐳 Runtime: Web + MCP
    ├── app/
    │   ├── api/main.py        # FastAPI
    │   ├── core/settings.py   # конфиги
    │   ├── mcp/server.py      # MCP tool
    │   ├── rag/retriever.py   # поиск по ChromaDB
    │   ├── rag/prompts.py     # промпты для LLM
    │   ├── llm/loader.py      # загрузка phi4-mini
    │   └── web/next_frontend/ # Next.js чат (встроен в контейнер)
    ├── Dockerfile            # один контейнер: Next.js + FastAPI
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
| Frontend | Next.js + TailwindCSS |
| MCP | FastMCP (stdio transport) |
| Локальная LLM | phi4-mini (Microsoft) |
| Контейнеры | Docker + docker-compose |

## 🔗 Ссылки

- https://opencode.ai/docs/mcp-servers
- https://docs.trychroma.com/guides/build/chunking
- https://github.com/vercel-labs/nextjs-fastapi-chat-app-starter

## 📌 Состояние

Начальная стадия. Скелет кода есть в main-project-goal.md.
Требуется реализовать все модули и собрать Docker.
