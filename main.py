import asyncio
import os

from dotenv import load_dotenv

from bot.app import TelegramBot
from database.repository import StatsRepository
from game.service import GameService, RandomWordPicker
from similarity.model import TransformerModel


async def main() -> None:
    load_dotenv()
    token = os.environ["TELEGRAM_TOKEN"]

    model = TransformerModel("sergeyzh/rubert-tiny-sts-v2")
    picker = RandomWordPicker()
    database = StatsRepository("stats.sqlite3")

    try:
        game = GameService(model=model, picker=picker)
        bot = TelegramBot(token=token, game=game, database=database)
        await bot.run()
    finally:
        database.close()


if __name__ == "__main__":
    asyncio.run(main())
