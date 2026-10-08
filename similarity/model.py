from .protocols import SimilarityModel


class DummyModel(SimilarityModel):
    def similarity(self, first: str, second: str) -> float:
        """Получить семантическую близость двух текстов в диапазоне [0.0, 1.0]"""

        return 0.5
