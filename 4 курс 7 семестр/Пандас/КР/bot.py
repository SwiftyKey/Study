import asyncio
import os
import sqlite3

from dotenv import load_dotenv
from telegramify_markdown import markdownify

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

from rag_pipeline import RAGPipeline, GigaChatService

load_dotenv()

class BotState(StatesGroup):
    main_state = State()


class DatabasesSubjectAssistantBot:
    def __init__(self, token: str, pipeline: RAGPipeline, db_path: str = "messages.db"):
        self.bot = Bot(token=token)
        self.hello_msg = "Привет. Я ассистент по дисциплине Базы Данных. Задавай вопросы."
        self.pipeline = pipeline
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT,
                    full_name TEXT,
                    message_text TEXT NOT NULL,
                    answer_text TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    chat_id INTEGER NOT NULL
                )
            """)
            conn.commit()

    def log_message(self, message: types.Message, bot_answer: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO messages (user_id, username, full_name, message_text, answer_text, chat_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                message.from_user.id,
                message.from_user.username or "",
                (message.from_user.first_name or "") + (" " + (message.from_user.last_name or "")).strip(),
                message.text or "",
                bot_answer,
                message.chat.id
            ))
            conn.commit()

    async def run(self):
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)

        router = Router()

        self.dp.include_router(router)
        router.message.register(self.cmd_start, Command('start'))
        router.message.register(self.main, StateFilter("BotState:main_state"))

        print('Бот запущен')
        await self.dp.start_polling(self.bot)

    async def cmd_start(self, message: types.Message, state: FSMContext):
        self.log_message(message, self.hello_msg)
        await state.clear()
        await message.answer(text=self.hello_msg)
        await state.set_state(BotState.main_state)

    async def main(self, message: types.Message, state: FSMContext):
        answer = self.pipeline.run(message.text)
        self.log_message(message, answer)
        await message.answer(text=markdownify(answer), parse_mode='MarkdownV2')


token = os.getenv('BOT_TOKEN')
gigchat_api_key = os.getenv('GIGACHAT_API_KEY')

service = GigaChatService(api_key=gigchat_api_key)
bot = DatabasesSubjectAssistantBot(token=token, pipeline=RAGPipeline(service, k=5))

async def main():
    await bot.run()

if __name__ == '__main__':
    asyncio.run(main())

