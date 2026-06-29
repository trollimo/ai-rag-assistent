FROM python:3.11-slim

WORKDIR /rag

# System deps (none needed for this stack)
# Python deps: chromadb pulls fastembed (ONNX, no torch)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cache fastembed model (~90 MB ONNX)
RUN python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()(['test'])"

# Source code
COPY src/ ./src/
COPY config/ ./config/

# Output dir (can be overridden by mount or env)
ENV RAG_OUTPUT=/rag/output
VOLUME ["/rag/output"]

CMD ["python", "src/ingest.py"]
