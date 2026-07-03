FROM python:3.11-slim

WORKDIR /rag

# System deps (none needed for this stack)
# Python deps: chromadb pulls fastembed (ONNX, no torch)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Pre-cache fastembed model from offline bundle (multilingual-e5-large, ~535 MB ONNX int8)
COPY --from=fastembed-cache . /root/.cache/fastembed
ENV FASTEMBED_CACHE_PATH=/root/.cache/fastembed
ENV HF_HUB_OFFLINE=1

# Source code
COPY src/ ./src/
COPY config/ ./config/

# Output dir (can be overridden by mount or env)
ENV RAG_OUTPUT=/rag/output
VOLUME ["/rag/output"]

CMD ["python", "src/ingest.py"]
