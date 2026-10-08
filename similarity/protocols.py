from typing import Protocol


class SimilarityModel(Protocol):
    def similarity(self, first: str, second: str) -> float:
        """Получить семантическую близость двух текстов в диапазоне [0.0, 1.0],
        и 1.0 - слова совпадают полностью."""
        ...
