from .protocols import StatsStorage, UserStats


class StatsRepository(StatsStorage):
    def __init__(self, path: str) -> None:
        self._path = path

    def ensure_player(self, user_id: int) -> None:
        raise NotImplementedError

    def record_game_result(self, user_id: int, won: bool) -> None:
        raise NotImplementedError

    def get_stats(self, user_id: int) -> UserStats:
        raise NotImplementedError

    def get_leaderboard(self, limit: int = 10) -> list[UserStats]:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError
