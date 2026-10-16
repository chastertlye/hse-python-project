from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from game.protocols import Game
from database.protocols import StatsStorage
from game.service import AlreadyActiveGameError, NoActiveGameError


class TelegramBot:
    def __init__(self, token, game, database):
        self._game = game
        self._database = database
        self._bot = Bot(token=token)
        self._dp = Dispatcher()

    async def run(self):
        self._dp.message.register(self.on_start, Command("start"))
        self._dp.message.register(self.on_play, Command("play"))
        self._dp.message.register(self.on_stop, Command("stop"))
        self._dp.message.register(self.on_stats, Command("stats"))
        self._dp.message.register(self.on_leaderboard, Command("leaderboard"))
        self._dp.message.register(self.on_text)

        await self._dp.start_polling(self._bot)

    async def on_start(self, message: Message):
        user_id = message.from_user.id
        self._database.ensure_player(user_id)
        await message.answer(
            "Привет! Я загадываю слово, а ты угадываешь.\n\n"
            "Команды:\n"
            "/play — начать игру\n"
            "/stop — сдаться\n"
            "/stats — моя статистика\n"
            "/leaderboard — кто самый лучший"
        )

    async def on_play(self, message: Message):
        user_id = message.from_user.id
        try:
            self._game.start_game(user_id)
        except AlreadyActiveGameError:
            await message.answer("Игра уже идёт! Пиши слово или /stop.")
            return
        await message.answer("Игра началась! Напиши первое слово.")

    async def on_stop(self, message: Message):
        user_id = message.from_user.id
        try:
            self._game.stop_game(user_id)
        except NoActiveGameError:
            await message.answer("Игры нет начни через /play")
            return
        self._database.record_game_result(user_id, won=False)
        await message.answer("Ты сдался. Игра закончена.")

    async def on_stats(self, message: Message):
        user_id = message.from_user.id
        stats = self._database.get_stats(user_id)
        await message.answer(
            f"Побед: {stats['wins']}\n"
            f"Игр сыграно: {stats['games']}"
        )

    async def on_leaderboard(self, message: Message):
        leaders = self._database.get_leaderboard(limit=10)
        if not leaders:
            await message.answer("Пока никто не выиграл.")
            return
        text = "🏆 Лучшие игроки:\n"
        for i, player in enumerate(leaders, start=1):
            text += f"{i}. {player['user_id']} — {player['wins']} побед\n"
        await message.answer(text)

    async def on_text(self, message: Message):
        user_id = message.from_user.id
        text = message.text.strip()

        if not text:
            await message.answer("Напиши что-нибудь, не пустое!")
            return

        try:
            result = self._game.make_guess(user_id, text)
        except NoActiveGameError:
            await message.answer("Игры нет начни через /play")
            return
        except ValueError:
            await message.answer("Напиши что-нибудь, не пустое!")
            return

        if result["correct"]:
            self._database.record_game_result(user_id, won=True)
            await message.answer(
                f"🎉 Ура! Угадал за {result['attempts']} попыток!"
            )
        else:
            percent = round(result["similarity"] * 100)
            await message.answer(
                f"Не то. Похоже на {percent}%.\n"
                f"Попыток: {result['attempts']}"
            )
 