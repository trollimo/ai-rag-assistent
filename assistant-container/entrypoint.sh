#!/usr/bin/env bash
# bash, not sh: /bin/sh is dash here and lacks `wait -n`
set -e

# Retrieval + API + MCP + Web UI. The LLM runs elsewhere — either the sibling
# `llm` container or a corporate endpoint — and is reached over LLM_BASE_URL.

MCP_SERVER_URL=${MCP_SERVER_URL:-http://localhost:9081/mcp}
LLM_BASE_URL=${LLM_BASE_URL:-http://llm:9080}

echo "[entrypoint] LLM endpoint: $LLM_BASE_URL (model: ${LLM_MODEL_NAME:-qwen2.5})"
echo "[entrypoint] MCP endpoint: $MCP_SERVER_URL"

uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

python -m backend.mcp.server &
MCP_PID=$!

node /app/web/server.js &
WEB_PID=$!

# Exit as soon as any process dies, instead of lingering half-broken —
# restart: unless-stopped then brings the whole container back.
wait -n $API_PID $MCP_PID $WEB_PID
EXIT_CODE=$?
echo "[entrypoint] a service exited (code $EXIT_CODE), shutting down"
kill $API_PID $MCP_PID $WEB_PID 2>/dev/null
exit $EXIT_CODE
