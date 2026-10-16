import random
from typing import Any

from similarity.protocols import SimilarityModel

from .protocols import (
    AlreadyActiveGameError,
    Game,
    GuessResult,
    NoActiveGameError,
    WordPicker,
)

WORDS: list[str] = [
    "дирижабль",
    "папоротник",
    "микроскоп",
    "лабиринт",
    "туманность",
    "архипелаг",
    "молекула",
    "шпиндель",
    "каракатица",
    "флюгер",
    "айсберг",
    "коловорот",
    "батискаф",
    "саксаул",
    "хризантема",
    "обсидиан",
    "бумеранг",
    "сверчок",
    "астероид",
    "акведук",
]


class GameService(Game):
    def __init__(self, model: SimilarityModel, picker: WordPicker) -> None:
        self.model = model
        self.picker = picker
        self.games: dict[int, dict[str, Any]] = {}

    def start_game(self, user_id: int) -> None:
        if self.has_active_game(user_id):
            raise AlreadyActiveGameError("В этом чате уже есть активная игра")

        word = self.picker.pick()
        self.games[user_id] = {"word": word, "attempts": 0}

    def has_active_game(self, user_id: int) -> bool:
        return user_id in self.games

    def make_guess(self, user_id: int, text: str) -> GuessResult:
        if not self.has_active_game(user_id):
            raise NoActiveGameError("В этом чате нет активной игры")
        cleaned_text = text.strip().lower()
        if len(cleaned_text) == 0:
            raise ValueError("Введите непустой текст")
        game = self.games[user_id]
        game["attempts"] += 1
        if cleaned_text == str(game["word"]).strip().lower():
            attempts = int(game["attempts"])
            del self.games[user_id]
            return GuessResult(similarity=1.0, is_correct=True, attempts=attempts)
        score = float(self.model.similarity(cleaned_text, game["word"]))
        return GuessResult(
            similarity=score, is_correct=False, attempts=game["attempts"]
        )

    def stop_game(self, user_id: int) -> None:
        if not self.has_active_game(user_id):
            raise NoActiveGameError("В этом чате нет активной игры")
        del self.games[user_id]


class RandomWordPicker(WordPicker):
    def __init__(self) -> None:
        self._words = WORDS

    def pick(self) -> str:
        return random.choice(self._words)
