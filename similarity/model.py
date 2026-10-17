from collections import OrderedDict

from sentence_transformers import SentenceTransformer


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
        p = embeddings[0] @ embeddings[1]
        return 1.012 / (1 + 3 ** (-54 * p + 50))

    def _encode(self, text):
        if text in self._cache:
            self._cache.move_to_end(text)
            return self._cache[text]

        embedding = self._model.encode(text, normalize_embeddings=True)
        while len(self._cache) >= self._maxsize:
            self._cache.popitem(last=False)
        self._cache[text] = embedding

        return embedding
