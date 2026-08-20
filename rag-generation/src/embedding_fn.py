import logging
import os
import time

from chromadb import EmbeddingFunction
from fastembed import TextEmbedding

log = logging.getLogger("rag-generator")


def _env_int(name):
    value = os.environ.get(name)
    return int(value) if value else None


class MultilingualEmbeddingFunction(EmbeddingFunction):
    DEFAULT_MODEL = "intfloat/multilingual-e5-large"

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self._model_name = model_name
        threads = _env_int("RAG_EMBED_THREADS")
        self.model = TextEmbedding(model_name=model_name, threads=threads)
        self._parallel = _env_int("RAG_EMBED_PARALLEL")
        self._batch_size = _env_int("RAG_EMBED_BATCH_SIZE") or 256
        self.total_embed_seconds = 0.0
        self.total_docs = 0
        log.info(
            "Embedding model=%s threads=%s parallel=%s batch_size=%s cpu_count=%s",
            model_name, threads, self._parallel, self._batch_size, os.cpu_count(),
        )

    def __call__(self, input):
        t0 = time.perf_counter()
        result = list(self.model.embed(input, batch_size=self._batch_size, parallel=self._parallel))
        elapsed = time.perf_counter() - t0
        self.total_embed_seconds += elapsed
        self.total_docs += len(input)
        log.info(
            "Embedded %d chunks in %.2fs (%.1f chunks/s)",
            len(input), elapsed, len(input) / elapsed if elapsed else 0,
        )
        return result
