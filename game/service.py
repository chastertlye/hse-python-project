from similarity.protocols import SimilarityModel

from .protocols import Game, GuessResult, WordPicker


class GameService(Game):
    def __init__(self, model: SimilarityModel, picker: WordPicker) -> None:
        self._model = model
        self._picker = picker

    def start_game(self, user_id: int) -> None:
        raise NotImplementedError

    def has_active_game(self, user_id: int) -> bool:
        raise NotImplementedError

    def make_guess(self, user_id: int, text: str) -> GuessResult:
        raise NotImplementedError

    def stop_game(self, user_id: int) -> None:
        raise NotImplementedError


class RandomWordPicker(WordPicker):
    def pick(self) -> str:
        raise NotImplementedError("Выбор слова пока не реализован")
