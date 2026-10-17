import json
import random
from http.client import HTTPException
from typing import Any
from urllib.request import Request, urlopen

from similarity.protocols import SimilarityModel

from .protocols import (
    AlreadyActiveGameError,
    Game,
    Guess,
    GuessResult,
    NoActiveGameError,
    WordPicker,
)

# backbone на случай если упадет api
WORDS: list[str] = ["кошка", "машина", "дом", "питон"]


class GameService(Game):
    def __init__(self, model: SimilarityModel, picker: WordPicker) -> None:
        self.model = model
        self.picker = picker
        self.games: dict[int, dict[str, Any]] = {}

    def start_game(self, user_id: int) -> str:
        if self.has_active_game(user_id):
            raise AlreadyActiveGameError("В этом чате уже есть активная игра")

        word = self.picker.pick()
        self.games[user_id] = {"word": word, "attempts": 0, "guesses": {}}
        return word

    def has_active_game(self, user_id: int) -> bool:
        return user_id in self.games

    def make_guess(self, user_id: int, text: str) -> GuessResult:
        if not self.has_active_game(user_id):
            raise NoActiveGameError("В этом чате нет активной игры")
        cleaned_text = text.strip().lower()
        if len(cleaned_text) == 0:
            raise ValueError("Введите непустой текст")
        game = self.games[user_id]
        is_correct = cleaned_text == str(game["word"]).strip().lower()
        score = (
            1.0
            if is_correct
            else float(self.model.similarity(cleaned_text, game["word"]))
        )
        game["attempts"] += 1
        game["guesses"][cleaned_text] = Guess(
            word=cleaned_text, similarity=score, is_correct=is_correct
        )
        if is_correct:
            del self.games[user_id]
        return GuessResult(
            similarity=score,
            is_correct=is_correct,
            attempts=game["attempts"],
            guesses=tuple(
                sorted(
                    game["guesses"].values(),
                    key=lambda guess: guess.similarity,
                    reverse=True,
                )
            ),
        )

    def stop_game(self, user_id: int) -> None:
        if not self.has_active_game(user_id):
            raise NoActiveGameError("В этом чате нет активной игры")
        del self.games[user_id]


class RandomWordPicker(WordPicker):
    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout = timeout

    def pick(self) -> str:
        request = Request(
            "https://associ.ru/api/v1/play",
            data=b"{}",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self._timeout) as response:
                word = json.load(response)["new"]["word"]
                return word.strip().lower()
        except (OSError, ValueError, HTTPException, KeyError, TypeError):
            pass
        return random.choice(WORDS)
