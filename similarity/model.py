from collections import OrderedDict

from sentence_transformers import SentenceTransformer

from .protocols import SimilarityModel  # noqa


class TransformerModel:
    def __init__(self, model_name, maxsize=128):
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self._cache = OrderedDict()
        self._maxsize = maxsize

    def similarity(self, first: str, second: str) -> float:
        if not first or not second:
            return 0.0

        embeddings = self._encode(first), self._encode(second)
        return embeddings[0] @ embeddings[1]

    def _encode(self, text):
        if text in self._cache:
            self._cache.move_to_end(text)
            return self._cache[text]

        embedding = self._model.encode(text, normalize_embeddings=True)
        while len(self._cache) >= self._maxsize:
            self._cache.popitem(last=False)
        self._cache[text] = embedding

        return embedding
