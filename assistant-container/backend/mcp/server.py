import contextlib
import logging
from pathlib import Path

import httpx
import yaml
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from backend.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("backend.mcp")

RAG_API_URL = "http://localhost:8000"

def _load_tool_config():
    config_path = Path(__file__).resolve().parent.parent / "config" / "mcp-tools.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

tool_config = _load_tool_config()

mcp = FastMCP("knowledge-rag")


@mcp.tool(description=tool_config["tools"]["search_docs"]["description"].strip())
def search_docs(query: str, top_k: int | None = None):
    if top_k is None:
        top_k = tool_config.get("search", {}).get("default_top_k", 3)
    logger.info("MCP tool search_docs query=%s top_k=%d", query, top_k)
    try:
        resp = httpx.post(
            f"{RAG_API_URL}/search",
            json={"query": query, "top_k": top_k},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        count = len(data.get("matches", []))
        logger.debug("MCP tool search_docs result count=%d", count)
        return data
    except Exception as e:
        logger.error("MCP tool search_docs error: %s", e)
        return {"error": str(e)}


@mcp.tool(description=tool_config["tools"]["list_topics"]["description"].strip())
def list_topics(filter: str = "", top_k: int | None = None):
    logger.info("MCP tool list_topics filter=%s top_k=%s", filter, top_k)
    try:
        body = {"filter": filter}
        if top_k is not None:
            body["top_k"] = top_k
        resp = httpx.post(
            f"{RAG_API_URL}/topics",
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        count = len(data.get("topics", []))
        logger.debug("MCP tool list_topics result count=%d", count)
        return data
    except Exception as e:
        logger.error("MCP tool list_topics error: %s", e)
        return {"error": str(e)}


mcp.settings.message_path = '/sse/messages/'

streamable_app = mcp.streamable_http_app()
sse_app = mcp.sse_app()


@contextlib.asynccontextmanager
async def combined_lifespan(app):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp._session_manager.run())
        yield


app = Starlette(routes=[*streamable_app.routes, *sse_app.routes], lifespan=combined_lifespan)

if __name__ == "__main__":
    import uvicorn
    logger.info("MCP server: /mcp (streamable-http) + /sse (SSE) on port 9081")
    uvicorn.run(app, host="0.0.0.0", port=9081)
