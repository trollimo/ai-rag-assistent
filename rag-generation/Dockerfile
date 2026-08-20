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

# ── e5 query:/passage: prefixes ──────────────────────────────────
# The e5 models are trained with "passage: " on documents and "query: " on
# searches; fastembed never adds them. Enabling this can improve retrieval,
# but measured slightly WORSE on the small starting corpus
# (hit@1 18->17, MRR .929->.902 over 20 Russian queries), so it stays off.
#
# Re-test once the knowledge base grows to hundreds of documents. If enabled,
# set the SAME value on the assistant container - documents and queries must
# be embedded identically or search quality collapses. Changing it triggers a
# full reindex automatically (the manifest fingerprint no longer matches).
# ENV RAG_EMBED_E5_PREFIXES=1

# Source code
COPY src/ ./src/
COPY config/ ./config/

# Output dir (can be overridden by mount or env)
ENV RAG_OUTPUT=/rag/output
VOLUME ["/rag/output"]

CMD ["python", "src/ingest.py"]
