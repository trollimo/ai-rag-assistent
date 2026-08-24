import logging
import os
import time

from chromadb import EmbeddingFunction
from fastembed import TextEmbedding

log = logging.getLogger("rag-generator")


def _env_int(name):
    value = os.environ.get(name)
    return int(value) if value else None


def _env_flag(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() not in ("0", "false", "no", "off", "")


class MultilingualEmbeddingFunction(EmbeddingFunction):
    DEFAULT_MODEL = "intfloat/multilingual-e5-large"

    # e5 is trained with these prefixes and fastembed does not add them, but on
    # this corpus they measured slightly worse (hit@1 18->17, MRR .929->.902),
    # so they stay opt-in via RAG_EMBED_E5_PREFIXES=1. Worth re-testing once the
    # knowledge base grows. Toggling this requires a full reindex: it changes
    # document vectors, and queries must be embedded the same way.
    DOC_PREFIX = "passage: "
    QUERY_PREFIX = "query: "

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self._model_name = model_name
        threads = _env_int("RAG_EMBED_THREADS")
        self.model = TextEmbedding(model_name=model_name, threads=threads)
        self._parallel = _env_int("RAG_EMBED_PARALLEL")
        self._batch_size = _env_int("RAG_EMBED_BATCH_SIZE") or 256
        self._use_prefixes = _env_flag("RAG_EMBED_E5_PREFIXES") and self._is_e5(model_name)
        self.total_embed_seconds = 0.0
        self.total_docs = 0
        log.info(
            "Embedding model=%s threads=%s parallel=%s batch_size=%s e5_prefixes=%s cpu_count=%s",
            model_name, threads, self._parallel, self._batch_size, self._use_prefixes, os.cpu_count(),
        )

    @staticmethod
    def _is_e5(model_name):
        return "e5" in model_name.lower()

    def _embed(self, texts):
        t0 = time.perf_counter()
        result = list(self.model.embed(texts, batch_size=self._batch_size, parallel=self._parallel))
        elapsed = time.perf_counter() - t0
        self.total_embed_seconds += elapsed
        self.total_docs += len(texts)
        log.info(
            "Embedded %d chunks in %.2fs (%.1f chunks/s)",
            len(texts), elapsed, len(texts) / elapsed if elapsed else 0,
        )
        return result

    def __call__(self, input):
        """Chroma calls this for documents at index time."""
        texts = [self.DOC_PREFIX + t for t in input] if self._use_prefixes else list(input)
        return self._embed(texts)

    def embed_query(self, text):
        """Embed a search query. Pass the result to Chroma as query_embeddings."""
        prefixed = self.QUERY_PREFIX + text if self._use_prefixes else text
        return list(self.model.embed([prefixed], batch_size=1))[0]
