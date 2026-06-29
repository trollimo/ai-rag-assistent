# Changelog

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
