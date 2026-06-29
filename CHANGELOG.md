# Changelog

## 1.2.0 (2026-06-29)

### Fixed
- ONNX model pre-cache in assistant-container Dockerfiles: `FastEmbedEmbeddingFunction` → `ONNXMiniLM_L6_V2()(['test'])` so the model is actually downloaded during build instead of at runtime
- Offline bundle: chromadb cache path corrected from `fastembed-cache` → `chroma-cache` (`/root/.cache/chroma`)
- `prepare-offline-bundle.ps1`: downloads model using `ONNXMiniLM_L6_V2` matching the retriever class

## 1.4.0 (2026-06-29)

### Changed
- Fixed ONNX model pre-cache in Dockerfile — now triggers actual download with `(['test'])` instead of no-op `__init__`
- Removed `COPY docs/` from image — docs mount via volume `./docs:/rag/docs:ro`
- Added `.dockerignore` (excludes `__pycache__`, `.git`, `output/`, etc.)

## 1.3.0 (2026-06-29)

### Added
- `rag-build.ps1 -Config` for custom `rag-sources.yaml` without image rebuild
- Volume mount for config in `docker-compose.yml`
- `rag-generation/README.md` with usage docs

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
