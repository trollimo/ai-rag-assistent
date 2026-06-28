 ── Stage 1: Next.js builder ──────────────────────────────────────
FROM node:20-slim AS web-builder
WORKDIR /app
COPY web/package.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# ── Stage 2: Final image ──────────────────────────────────────────
FROM python:3.11-slim

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_MODELS=/root/.ollama/models
ENV NODE_ENV=production

# curl + zstd for downloading and extracting ollama binary
RUN apt-get update && apt-get install -y curl ca-certificates zstd && rm -rf /var/lib/apt/lists/*

# Ollama from tar.zst archive (no ollama/ollama image)
RUN curl -fsSL https://github.com/ollama/ollama/releases/download/v0.30.10/ollama-linux-amd64.tar.zst \
    | zstd -dc | tar -xf - -C /usr/local/lib/ollama && \
    ln -sf /usr/local/lib/ollama/ollama /usr/local/bin/ollama

# Pull LLM model
RUN ollama serve & sleep 3 && ollama pull qwen2.5:1.5b

# Python dependencies
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Pre-cache fastembed model (all-MiniLM-L6-v2, ~90 MB ONNX)
RUN python -c "from chromadb.utils.embedding_functions import FastEmbedEmbeddingFunction; FastEmbedEmbeddingFunction('all-MiniLM-L6-v2')"

# Backend source
COPY backend /app/backend

# Node binary for Next.js runtime (copied from builder, no npm needed)
COPY --from=web-builder /usr/local/bin/node /usr/local/bin/node

# Next.js standalone output
WORKDIR /app/web
COPY --from=web-builder /app/.next/standalone ./
COPY --from=web-builder /app/public ./public
COPY --from=web-builder /app/.next/static ./.next/static

WORKDIR /app
EXPOSE 11434 8000 3000

CMD sh -c "ollama serve & uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 & node /app/web/server.js"
