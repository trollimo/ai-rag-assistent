from chromadb import EmbeddingFunction
from fastembed import TextEmbedding


class MultilingualEmbeddingFunction(EmbeddingFunction):
    DEFAULT_MODEL = "intfloat/multilingual-e5-large"

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self._model_name = model_name
        self.model = TextEmbedding(model_name=model_name)

    def __call__(self, input):
        return list(self.model.embed(input))
