from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class UserStats:
    user_id: int
    wins: int
    games: int


class StatsStorage(Protocol):
    def ensure_player(self, user_id: int) -> None:
        """Создать пользователя с нулём побед, если его нет."""

    def record_game_result(self, user_id: int, won: bool) -> None:
        """Добавить завершённую игру; при won=True также добавить победу."""
        ...

    def get_stats(self, user_id: int) -> UserStats:
        """Для нового пользователя вернуть wins=0."""
        ...

    def get_leaderboard(self, limit: int = 10) -> list[UserStats]:
        """Вернуть пользователей по убыванию числа побед."""
        ...

    def close(self) -> None:
        """Закрыть соединение с базой."""
        ...
