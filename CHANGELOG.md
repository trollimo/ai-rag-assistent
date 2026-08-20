# Changelog

## 1.8.1 (2026-08-21) — assistant-container

### Fixed
- `retriever.py`: single-topic follow-up search used `where["source"] = {"$contains": path_filter}`
  — `$contains` filters document text (`where_document`), not metadata (`where`); on metadata it
  silently matched nothing. Every question where `_detect_source()` found a dominant topic (e.g.
  "Расскажи про deployment", the related-topics buttons) got zero results regardless of relevance.
  `path_filter` is always an exact source path already, so exact match (`where["source"] = path_filter`)
  is both the fix and the semantically correct behavior — never needed substring matching.

## 1.8.0 (2026-08-21) — assistant-container

### Added
- `retriever.py` / `mcp-tools.yaml`: `search.max_distance` cutoff — chromadb results past this l2
  distance are dropped instead of always returning `top_k` regardless of relevance. Found via a
  real case: a question about code review pulled in an unrelated Kubernetes Service troubleshooting
  chunk because on this small, topically mixed corpus the model doesn't separate "relevant" from
  "irrelevant" by a wide margin (irrelevant chunks landed within ~1 distance unit of relevant ones).
  Threshold (300) is corpus/model-specific — see `rag-generation/docs/embedding-model-research.md`.

## 1.7.3 (2026-08-20) — assistant-container

### Fixed
- `offline-bundle/next-standalone`: the bundle refresh after the 1.7.0 UI rewrite silently kept
  serving the old single-column chat UI. Cause: `rm -rf next-standalone/*` and `cp -r .../standalone/*
  ...` — bash glob `*` does not match dotfiles, so the hidden `.next/` directory (where Next.js
  standalone actually puts the compiled server-side pages) was never cleared or replaced. Same class
  of bug is possible in `prepare-offline-bundle.ps1` if it's ever run with a stale bundle already
  present — PowerShell's `Copy-Item -Path "x\*"` does not have this specific glob gap, but the
  script's own "skip if `$nextSize -gt 1MB`" staleness check means it never rebuilds automatically
  once *any* content exists there, stale or not.

## 1.7.1 (2026-08-20) — assistant-container

### Fixed
- `requirements.txt`: pin `mcp<2.0.0`. `offline-bundle/wheels` doesn't cover every transitive
  dependency, so this build's `pip install` partly reached PyPI and landed on `mcp` 2.0.0, which
  renamed `mcp.server.fastmcp` -> `mcp.server.mcpserver`. `backend/mcp/server.py` targets the 1.x
  API, so the MCP process crashed on import; `entrypoint.sh`'s `wait -n` then took the whole
  container down with it, producing a `restart: unless-stopped` crash-loop.

### Changed
- `prompts.py`: system prompt now explicitly requires answering in Russian regardless of question language.

## 1.7.0 (2026-08-20) — assistant-container

### Added
- `Dockerfile.llm` / `docker-compose.yml`: llama-server + GGUF split out of the assistant image into
  its own `llm` service — swappable for a corporate OpenAI-compatible endpoint without touching the
  rest of the stack. Along the way: found and fixed a real llama.cpp bug where
  `ggml_backend_load_all()` fails with "no backends are loaded" if the process's cwd is `/`,
  regardless of how the binary itself is invoked — fixed with an explicit non-root `WORKDIR`.
- `settings.py`: `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL_NAME` — generalized OpenAI-compatible
  connector, local `llm` service or external endpoint are interchangeable. `LLAMA_HOST`/`LLAMA_MODEL`
  kept as deprecated aliases.
- `web/components/Workspace.tsx` + `ChatSidebar.tsx` + `AnswerPanel.tsx`: two-column UI (chat history
  left, presentation panel right: question -> answer -> sources -> related topics), replacing the
  single-column chat-bubble layout. `/chat` now returns `related_topics`.
- `Dockerfile.offline`: no longer fetches `node:20-slim` or llama.cpp from GitHub at build time —
  both come from an already-built donor image, with `fetch-llama-dist.ps1` as a from-scratch fallback.

### Known gaps
- `offline-bundle/wheels` is incomplete (see 1.7.1) — build isn't fully offline yet.
- `@tailwindcss/typography` is listed in `package.json` but not installed (registry was unreachable
  mid-session) — `answer-markdown` CSS in `globals.css` is the fallback until it's installed.

## 1.10.0 (2026-08-21) — rag-generation

### Added
- `ingest.py` / `chunking.py`: incremental indexing — chunk hashes recorded in `manifest.json`, only
  changed/new chunks are re-embedded, removed ones are deleted from the collection. A build
  fingerprint (model/chunk_size/overlap/prefixes) forces a full reindex when any of them change, so
  stored vectors never get silently compared across incompatible settings. On the ~15-minute,
  630-chunk slow-indexing case from `CLAUDE.md`: a single-file edit now re-embeds in ~2s.
- `embedding_fn.py`: optional `RAG_EMBED_E5_PREFIXES` (`query:`/`passage:`) — off by default, measured
  slightly worse on the corpus size tested (hit@1 18/20 -> 17/20 over 20 Russian queries).
- `docs/kubernetes/*`, `docs/security/*`: real reference docs (Kubernetes Deployment/Service/Ingress/
  Helm/ConfigMap/StatefulSet/HPA; OWASP Top 10, injection/XSS, access control, dependency scanning,
  Docker image hardening, prompt injection) — indexed into the real knowledge base, not a synthetic
  test fixture.
- `docs/embedding-model-research.md`: why `multilingual-e5-large` fp32 stays the embedding model —
  a lighter model (MiniLM) and int8 quantization of the same model were both tested and rejected
  (int8's expected 2.7-3.4x speedup needs AVX512-VNNI the test CPU doesn't have; got +15% with a
  real quality regression instead).

### Fixed
- Root cause of the slow-indexing bug in `CLAUDE.md`: not Ollama (unused), not missing batching
  (already batched), not missing threads (ONNXRuntime already saturates all cores) — 99% of the time
  is the `multilingual-e5-large` inference itself, the heaviest model in fastembed's catalog, on a
  CPU without AVX512-VNNI. Chroma write time is <1% of total.

## 1.6.1 (2026-07-01) — assistant-container

### Added
- `retriever.py`: при старте выводится количество чанков и тем в БД

## 1.6.0 (2026-07-01) — assistant-container

### Added
- MCP: Streamable HTTP (`/mcp`) — основной транспорт, замена stdio
- MCP: SSE (`/sse`) — обратная совместимость
- `mcp>=1.9.1` в requirements (streamable_http_app + auto root_path)
- Volumes для дебага (`./backend`, `./entrypoint.sh`) в docker-compose.yml
- Закомментированный volume для `mcp-tools.yaml`

### Changed
- `server.py`: единое Starlette-приложение с двумя роутами `/mcp` + `/sse` на порту 9081
- `entrypoint.sh`: запуск MCP без аргументов (оба транспорта сразу)
- README, AGENTS.md: документация под новый протокол
- `docker-compose.yml`: подписаны порты

## 1.9.0 (2026-06-30) — rag-generation

### Added
- `md-content-guidelines.md`: раздел про стоп-слова с полным списком и примером хорошего/плохого запроса
- `md-content-guidelines.md`: раздел про разделение технологий по разным `.md` файлам

### Fixed
- `md-content-guidelines.md`: минимальный размер чанка 200→800 (реальный merge threshold)

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
