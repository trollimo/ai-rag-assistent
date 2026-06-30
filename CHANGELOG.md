# Changelog

## 1.8.0 (2026-06-30) — rag-generation

### Added
- `AGENTS.md.template` — контекст для AI-агентов (структура проекта, стек, ссылки)

### Changed
- `embedding_fn.py`: модель `all-MiniLM-L6-v2` → `intfloat/multilingual-e5-large` (русский + английский)

## 1.5.0 (2026-06-30) — assistant-container

### Added
- MCP-сервер (stdio + HTTP SSE) с инструментами `search_docs` и `list_topics`
- FastAPI endpoint `/topics` — группировка чанков по источникам
- Web UI: `TopicsPanel.tsx` — просмотр доступных источников знаний
- `entrypoint.sh` — запуск всех сервисов (llama-server, uvicorn, MCP)
- `embedding_fn.py` — обёртка fastembed для ChromaDB (multilingual-e5-large)
- `mcp-tools.yaml` — конфиг для описания MCP инструментов

### Changed
- `retriever.py`: `all-MiniLM-L6-v2` → `MultilingualEmbeddingFunction` (мультиязычные эмбеддинги)
- `main.py`: рефакторинг `/chat` — автодетект источника, контекст с метками `[source: ...]`
- `settings.py`: загрузка параметров из `mcp-tools.yaml`
- `docker-compose.yml`: переезд на multi-stage offline-сборку
- Dockerfiles: переписаны под offline/online multi-stage сборку
- `docker-run.ps1`: поддержка `-Attach` для отладки
- `offline-bundle`: подготовка через `prepare-offline-bundle.ps1`

## 1.7.0 (2026-06-30) — rag-generation

### Changed
- `chunking.py`: merge threshold 300 → 800 — мелкие секции склеиваются в более крупные чанки

## 1.4.0 (2026-06-30) — assistant-container

### Changed
- `mcp-tools.yaml`: search default_top_k 3 → 5 — увеличен объём контекста для LLM
- `main.py`: каждый чанк обёрнут в `[source: имя-файла]\n{текст}` перед отправкой LLM
- `prompts.py`: добавлена инструкция не смешивать источники (без хардкода языков)
- `docker-compose.yml`: добавлен закомментированный volume для `prompts.py` (отладка без пересборки)

## 1.6.0 (2026-06-29)

### Added
- Language-specific coding rules: `java-rules.md`, `python-rules.md`, `kotlin-rules.md`
- Guide in `README.md` on splitting technologies into separate files for better RAG accuracy

### Changed
- `coding-rules.md` — stripped to generic rules only (no language-specific content)

## 1.3.0 (2026-06-29)

### Added
- MCP tool description now loaded from `backend/config/mcp-tools.yaml` — editable without rebuild
- `search_docs` now exposes a docstring to guide the AI agent on when to use it

## 1.2.0 (2026-06-29)

### Fixed
- ONNX model pre-cache in assistant-container Dockerfiles: `FastEmbedEmbeddingFunction` → `ONNXMiniLM_L6_V2()(['test'])` so the model is actually downloaded during build instead of at runtime
- Offline bundle: chromadb cache path corrected from `fastembed-cache` → `chroma-cache` (`/root/.cache/chroma`)
- `prepare-offline-bundle.ps1`: downloads model using `ONNXMiniLM_L6_V2` matching the retriever class

## 1.5.0 (2026-06-29)

### Changed
- `collection.add()` → `collection.upsert()` in ingest.py: re-running generator now updates changed .md files instead of crashing on duplicate IDs

## 1.4.0 (2026-06-29)

### Changed
- Fixed ONNX model pre-cache in Dockerfile — now triggers actual download with `(['test'])` instead of no-op `__init__`
- Removed `COPY docs/` from image — docs mount via volume `./docs:/rag/docs:ro`
- Added `.dockerignore` (excludes `__pycache__`, `.git`, `output/`, etc.)

## 1.2.0 (2026-06-29)

### Fixed
- Source paths with `../` (e.g. `../../skills`) now resolve correctly instead of being broken by `lstrip("./")`
- File display for paths outside `BASE_DIR` no longer crashes

### Added
- Respect `include` glob patterns from `rag-sources.yaml`
- Warn when a source dir exists but no files match the pattern

## 1.1.0 (2026-06-29)

### Changed
- Ports: llama-server 8080→9080, MCP SSE 8001→9081
- Bump rag-generation and assistant-container to 1.1.0

## 1.0.0 (2026-06-29)

### Added
- RAG-generation pipeline: ingest, chunking, ChromaDB (fastembed, no torch)
- FastAPI backend with `/chat` and `/search` endpoints
- MCP server (stdio + HTTP SSE transport)
- Next.js Web UI with TailwindCSS
- llama-server runtime with Qwen2.5-1.5B Q4_K_M
- Offline bundle support (`offline-bundle/`) for air-gapped builds
- Docker multi-stage builds (online + offline variants)
- `docker-run.ps1` — convenience script for build/start/stop/logs
- Semantic versioning (`VERSION` files per package)

### Changed
- Migrated from Ollama to llama.cpp llama-server
- Migrated from SentenceTransformer+torch to fastembed (ONNX)
- Switched from `/api/generate` (Ollama) to `/v1/chat/completions` (OpenAI format)
- Replaced `OLLAMA_HOST`/`OLLAMA_MODEL` with `LLAMA_HOST`/`LLAMA_MODEL`

### Fixed
- MCP server now calls FastAPI `/search` via HTTP instead of direct ChromaDB access
- Structured logging across all backend modules
