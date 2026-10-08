from game.protocols import Game
from database.protocols import StatsStorage


class TelegramBot:
    def __init__(
        self,
        token: str,
        game: Game,
        database: StatsStorage,
    ) -> None:
        self._token = token
        self._game = game
        self._database = database

    async def run(self) -> None:
        """Подключить handlers и запустить polling."""
        raise NotImplementedError
