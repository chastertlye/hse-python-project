import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import Message

from game.service import AlreadyActiveGameError, NoActiveGameError

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token, game, database):
        self._game = game
        self._database = database
        self._bot = Bot(token=token)
        self._dp = Dispatcher(
            events_isolation=SimpleEventIsolation(),
            fsm_strategy=FSMStrategy.GLOBAL_USER,
        )

    @staticmethod
    def _percent(similarity: float, is_correct: bool) -> float:
        if is_correct:
            return 100.0
        return min(round(similarity * 100, 1), 99.9)

    async def _reply(self, message: Message, text: str):
        while text:
            end = len(text)
            if end > 4000:
                end = text.rfind("\n", 0, 4000)
                if end <= 0:
                    end = 4000
            await message.answer(text[:end])
            text = text[end:].lstrip("\n")

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
        await self._reply(
            message,
            "Привет! Я загадываю слово, а ты угадываешь.\n\n"
            "Команды:\n"
            "/play — начать игру\n"
            "/stop — сдаться\n"
            "/stats — моя статистика\n"
            "/leaderboard — кто самый лучший",
        )

    async def on_play(self, message: Message):
        user_id = message.from_user.id
        try:
            word = await asyncio.to_thread(self._game.start_game, user_id)
        except AlreadyActiveGameError:
            await self._reply(message, "Игра уже идёт! Пиши слово или /stop.")
            return
        logger.info("%s start: %s", user_id, word)
        await self._reply(message, "Игра началась! Напиши первое слово.")

    async def on_stop(self, message: Message):
        user_id = message.from_user.id
        try:
            self._game.stop_game(user_id)
        except NoActiveGameError:
            await self._reply(message, "Игры нет! Начни через /play")
            return
        self._database.record_game_result(user_id, won=False)
        logger.info("%s end: loss", user_id)
        await self._reply(message, "Ты сдался. Игра закончена.")

    async def on_stats(self, message: Message):
        user_id = message.from_user.id
        stats = self._database.get_stats(user_id)
        await self._reply(message, f"Побед: {stats.wins}\nИгр сыграно: {stats.games}")

    async def on_leaderboard(self, message: Message):
        leaders = self._database.get_leaderboard(limit=10)
        if not leaders:
            await self._reply(message, "Пока никто не выиграл.")
            return
        text = "🏆 Лучшие игроки:\n"
        for i, player in enumerate(leaders, start=1):
            text += f"{i}. {player.user_id} — {player.wins} побед\n"
        await self._reply(message, text)

    async def on_text(self, message: Message):
        user_id = message.from_user.id
        text = (message.text or "").strip()

        if not text:
            await self._reply(message, "Напиши что-нибудь не пустое!")
            return

        try:
            result = self._game.make_guess(user_id, text)
        except NoActiveGameError:
            await self._reply(message, "Игры нет! Начни через /play")
            return

        logger.info("%s attempt: %s", user_id, text)
        if result.is_correct:
            self._database.record_game_result(user_id, won=True)
            logger.info("%s end: win", user_id)
            await self._reply(message, "🎉")
            reply = f"Ура! Угадал за {result.attempts} попыток!"
        else:
            percent = self._percent(result.similarity, result.is_correct)
            reply = f"Похоже на {percent:.1f}%.\nПопыток: {result.attempts}"

        words = "\n".join(
            f"{index}. {guess.word} — "
            f"{self._percent(guess.similarity, guess.is_correct):.1f}%"
            for index, guess in enumerate(result.guesses, start=1)
        )
        if words:
            reply += f"\n\nПопытки:\n{words}"
        await self._reply(message, reply)
