import logging

import httpx
from mcp.server.fastmcp import FastMCP
from backend.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("backend.mcp")

RAG_API_URL = "http://localhost:8000"

mcp = FastMCP("knowledge-rag")


@mcp.tool()
def search_docs(query: str, top_k: int = 5):
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


if __name__ == "__main__":
    import sys, uvicorn
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    logger.info("MCP server starting transport=%s", transport)
    if transport == "sse":
        uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8001)
    else:
        mcp.run(transport="stdio")
