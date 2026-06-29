# ── Stage 1: Next.js builder ──────────────────────────────────────
FROM node:20-slim AS web-builder
WORKDIR /app
COPY web/package.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# ── Stage 2: llama-server dist ───────────────────────────────────
FROM python:3.11-slim AS llama-source
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/* && \
    curl -fsSL "https://github.com/ggml-org/llama.cpp/releases/download/b9804/llama-b9804-bin-ubuntu-x64.tar.gz" -o /tmp/llama.tar.gz && \
    tar -xzf /tmp/llama.tar.gz -C /opt/ && \
    rm /tmp/llama.tar.gz

# ── Stage 3: Final image ──────────────────────────────────────────
FROM python:3.11-slim

ENV LLAMA_HOST=http://localhost:9080
ENV LLAMA_MODEL=qwen2.5
ENV NODE_ENV=production

# Base system deps + curl for downloading model
RUN apt-get update && apt-get install -y curl libgomp1 && rm -rf /var/lib/apt/lists/*

# Node binary (from builder)
COPY --from=web-builder /usr/local/bin/node /usr/local/bin/node

# llama-server
COPY --from=llama-source /opt/llama-b9804 /opt/llama
RUN ln -sf /opt/llama/llama-server /usr/local/bin/llama-server
ENV LD_LIBRARY_PATH=/opt/llama

# Download GGUF model from HuggingFace
RUN mkdir -p /models && \
    curl -fsSL "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf" \
    -o /models/qwen2.5.gguf

# Python dependencies
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Pre-cache fastembed model (all-MiniLM-L6-v2, ~90 MB ONNX)
RUN python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()(['test'])"

# Backend source
COPY backend /app/backend

# Next.js standalone output
WORKDIR /app/web
COPY --from=web-builder /app/.next/standalone ./
COPY --from=web-builder /app/public ./public
COPY --from=web-builder /app/.next/static ./.next/static

WORKDIR /app
EXPOSE 9080 8000 9081 3000

CMD ["sh", "-c", "\
  llama-server --host 0.0.0.0 --port 9080 -m /models/qwen2.5.gguf --alias qwen2.5 & \
  sleep 2 && \
  uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 & \
  python -m backend.mcp.server sse & \
  node /app/web/server.js"]
