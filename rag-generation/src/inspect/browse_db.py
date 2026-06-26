import chromadb
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
DB_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "output" / "chroma_db"
COLLECTION_NAME = sys.argv[2] if len(sys.argv) > 2 else "knowledge_base"

client = chromadb.PersistentClient(path=DB_PATH)
col = client.get_collection(COLLECTION_NAME)
cnt = col.count()
print(f"Total chunks: {cnt}\n")

if cnt:
    data = col.get(limit=cnt)
    for doc, meta, idx in zip(data["documents"], data["metadatas"], data["ids"]):
        print(f"[{idx}]")
        print(f"  source:   {meta['source']}")
        print(f"  chunk #:  {meta['chunk']}")
        print(f"  text ({len(doc)} chars): {doc[:200]}...\n")

    #  search demo
    if len(sys.argv) > 3:
        query = sys.argv[3]
        print(f"\n[Search] \"{query}\"")
        results = col.query(query_texts=[query], n_results=3)
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            print(f"\n  [hit] {meta['source']} chunk#{meta['chunk']}")
            print(f"  {doc[:200]}...")
