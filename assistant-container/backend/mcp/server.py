from mcp.server.fastmcp import FastMCP
from backend.rag.retriever import Retriever

mcp = FastMCP("knowledge-rag")
retriever = Retriever()


@mcp.tool()
def search_docs(query: str, top_k: int = 5):
    return {"matches": retriever.search(query, top_k=top_k)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
