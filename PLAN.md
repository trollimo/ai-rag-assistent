# 🗺️ План действий

## 🎯 Цель

1. **Шаг 1** — запустить `rag-generation` и получить ChromaDB с примерами знаний
2. **Шаг 2** — запустить `assistant-container` с Web UI и MCP-сервером

---

## 📦 Шаг 1: rag-generation 🏗️

### ✅ Что уже есть в goal
| Файл | Статус |
|------|--------|
| `config/rag-sources.yaml` | ❌ не создан |
| `docs/rules/coding-rules.md` | ❌ не создан |
| `docs/poetry/chorovod-rules.md` | ❌ не создан |
| `src/ingest.py` | ❌ не создан |
| `src/chunking.py` | ❌ не создан |
| `rag-generate.ps1` / `.sh` | ❌ не создан |
| `requirements.txt` | ❌ не создан |

**Что нужно сделать:**
1. Создать структуру папок `rag-generation/`
2. Написать `chunking.py` — разбивка markdown по заголовкам с overlap
3. Написать `ingest.py` — читка .md, эмбеддинги, запись в ChromaDB + manifest
4. Создать `requirements.txt` (chromadb, sentence-transformers, pyyaml)
5. Создать `rag-sources.yaml`
6. Создать примеры .md файлов (docs/rules, docs/poetry)
7. Создать `rag-generate.ps1` (Windows) и `rag-generate.sh` (Linux)
8. Запустить генерацию → получить `output/chroma_db/` + `output/manifest.json`

---

## 🐳 Шаг 2: assistant-container

### ✅ Что уже есть в goal
| Файл | Статус |
|------|--------|
| `app/api/main.py` | ❌ не создан |
| `app/rag/retriever.py` | ❌ не создан |
| `app/mcp/server.py` | ❌ не создан |
| `app/core/settings.py` | ❌ не создан |
| `app/rag/prompts.py` | ❌ не создан |
| `app/llm/loader.py` | ❌ не создан |
| `app/web/next_frontend/` | ❌ не создан |
| `Dockerfile` | ❌ не создан |
| `docker-compose.yml` | ❌ не создан |
| `requirements.txt` | ❌ не создан |

### ✅ Принятые решения

| Решение | Значение |
|---------|----------|
| **LLM для чата** | ✅ phi4-mini (Microsoft) |
| **Embeddings** | ✅ sentence-transformers/all-MiniLM-L6-v2 |
| **Контейнер** | ✅ один контейнер: Next.js + FastAPI вместе (multi-stage) |
| **MCP server** | ✅ отдельный процесс (не в контейнере), запускается отдельно |

### 🔴 Что не описано в goal (нужно решить)

| Проблема | Описание |
|----------|----------|
| **❓ Чат Next.js** | В goal есть только идея. Нужно: `app/page.tsx`, `components/Chat.tsx`, fetch к FastAPI, TailwindCSS, `package.json`, `next.config.js` |
| **❓ volume ChromaDB** | `docker-compose.yml` монтирует `../rag-generation/output/chroma_db`. Но база должна быть доступна и FastAPI, и MCP. Удостовериться, что пути совпадают. |
| **❓ pip vs requirements** | Точный список зависимостей не указан. Нужно подобрать версии для chromadb, sentence-transformers, torch (CPU-only чтобы образ был легче). |

### 👣 Что нужно сделать
1. Создать `settings.py` — пути, model name, chroma config
2. Создать `prompts.py` — шаблоны для генерации ответа с phi4-mini
3. Создать `loader.py` — загрузка/кэширование phi4-mini
4. Создать Next.js frontend с чат-интерфейсом
5. Настроить Docker multi-stage: Node.js сборка Next.js → Python с FastAPI
6. Собрать образ и запустить
7. Проверить offline: Web UI чат + MCP `search_docs`

---

## 🧩 Итоговая схема

```
┌──────────────────────────────────────────────────────────────┐
│  Шаг 1: rag-generation (offline)                             │
│  .md → chunking → embeddings → ChromaDB + manifest.json     │
└──────────────────────┬───────────────────────────────────────┘
                       │ volume mount
┌──────────────────────▼───────────────────────────────────────┐
│  Шаг 2: assistant-container (runtime)                        │
│  ┌──────────┐    ┌──────────┐    ┌────────────────────────┐ │
│  │ Next.js  │───▶│ FastAPI  │───▶│ ChromaDB + LLM (local) │ │
│  │ Web UI   │    │ REST API │    │                        │ │
│  └──────────┘    └────┬─────┘    └────────────────────────┘ │
│                       │                                      │
│                 ┌─────▼──────┐                               │
│                 │ MCP server │◀── OpenCode agent             │
│                 │ (stdio)    │                               │
│                 └────────────┘                               │
└──────────────────────────────────────────────────────────────┘
```

---

## ⏳ Оценка

| Шаг | Примерно |
|-----|----------|
| Шаг 1 (rag-generation) | 10-15 файлов, ~1-2ч |
| Шаг 2 (assistant-container) | 20-30 файлов, ~3-5ч |
| Docker + отладка | ~1-2ч |

---

*Жду твоих указаний — с какого шага начинаем* 🚀
