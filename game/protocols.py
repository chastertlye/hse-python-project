from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GuessResult:
    similarity: float
    is_correct: bool
    attempts: int


class NoActiveGameError(Exception):
    """В этом чате нет активной игры."""


class AlreadyActiveGameError(Exception):
    """В этом чате уже есть активная игра."""


class WordPicker(Protocol):
    def pick(self) -> str:
        """Выбрать слово или короткую фразу для новой игры."""
        ...


class Game(Protocol):
    def start_game(self, user_id: int) -> None:
        """Начать новую игру, если она сейчас не начата."""
        ...

    def has_active_game(self, user_id: int) -> bool: ...

    def make_guess(self, user_id: int, text: str) -> GuessResult:
        """Обработать попытку.

        Нет игры — NoActiveGameError.
        Пустой текст — ValueError.
        Правильный ответ завершает игру.
        attempts — общее число попыток в текущей игре.
        """
        ...

    def stop_game(self, user_id: int) -> None:
        """Закончить активную игру пользователя, который сдался"""
        ...
