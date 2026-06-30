#!/bin/sh
set -e

CONFIG_FILE=/app/backend/config/mcp-tools.yaml

CTX_SIZE=$(awk '/ctx_size:/{print $2}' "$CONFIG_FILE")
CTX_SIZE=${CTX_SIZE:-2048}

llama-server --host 0.0.0.0 --port 9080 -m /models/qwen2.5.gguf \
  --alias qwen2.5 --ctx-size "$CTX_SIZE" &

sleep 2

uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 &

python -m backend.mcp.server sse &

node /app/web/server.js

wait
