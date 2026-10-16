import sqlite3
from .protocols import StatsStorage, UserStats


class StatsRepository(StatsStorage):
    def __init__(self, path: str) -> None:
        """Открыть SQLite-базу по переданному пути и создать необходимые таблицы."""
        self._path = path
        self._conn = sqlite3.connect(self._path)
        self._init_db()

    def _init_db(self) -> None:
        """Создание таблицы для хранения статистики, если она ещё не существует."""
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    wins INTEGER NOT NULL DEFAULT 0,
                    games INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def ensure_player(self, user_id: int) -> None:
        """Создать пользователя с wins=0, games=0, если его нет. \
        Для существующего пользователя ничего не сбрасывать."""
        with self._conn:
            self._conn.execute(
                """
                INSERT OR IGNORE INTO user_stats (user_id, wins, games)
                VALUES (?, 0, 0)
                """,
                (user_id,),
            )

    def record_game_result(self, user_id: int, won: bool) -> None:
        """Увеличить games на один. При won=True также увеличить wins на один. \
        Если пользователь отсутствует — создать его."""
        win_inc = 1 if won else 0
        with self._conn:
            # Создаём запись, если пользователя ещё нет
            self._conn.execute(
                """
                INSERT OR IGNORE INTO user_stats (user_id, wins, games)
                VALUES (?, 0, 0)
                """,
                (user_id,),
            )
            # Обновляем счётчики
            self._conn.execute(
                """
                UPDATE user_stats
                SET games = games + 1,
                    wins = wins + ?
                WHERE user_id = ?
                """,
                (win_inc, user_id),
            )

    def get_stats(self, user_id: int) -> UserStats:
        """Вернуть UserStats. Для неизвестного пользователя вернуть wins=0, games=0."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT wins, games
            FROM user_stats
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = cursor.fetchone()
        if row is not None:
            return UserStats(user_id=user_id, wins=row[0], games=row[1])
        return UserStats(user_id=user_id, wins=0, games=0)

    def get_leaderboard(self, limit: int = 10) -> list[UserStats]:
        """Вернуть максимум limit объектов UserStats, отсортированных по убыванию побед. \
        При равенстве побед — по возрастанию user_id."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT user_id, wins, games
            FROM user_stats
            ORDER BY wins DESC, user_id ASC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [UserStats(user_id=row[0], wins=row[1], games=row[2]) for row in rows]

    def close(self) -> None:
        """Закрыть соединение с SQLite."""
        if self._conn:
            self._conn.close()
