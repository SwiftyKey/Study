import asyncio
import os

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
    def __init__(self, token: str, pipeline: RAGPipeline):
        self.bot = Bot(token=token)
        self.pipeline = pipeline

    async def run(self):
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)

        router = Router()

        self.dp.include_router(router)
        router.message.register(self.cmd_start, Command('start'))
        router.message.register(self.main, StateFilter("BotState:main_state"))

        await self.dp.start_polling(self.bot)

    async def cmd_start(self, message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer(text="Привет. Я ассистент по дисциплине Базы Данных. Задавай вопросы.")
        await state.set_state(BotState.main_state)

    async def main(self, message: types.Message, state: FSMContext):
        answer = self.pipeline.run(message.text)
        await message.answer(text=markdownify(answer), parse_mode='MarkdownV2')


token = os.getenv('BOT_TOKEN')
gigchat_api_key = os.getenv('GIGACHAT_API_KEY')

service = GigaChatService(api_key=gigchat_api_key)
bot = DatabasesSubjectAssistantBot(token=token, pipeline=RAGPipeline(service, k=5))

async def main():
    await bot.run()

if __name__ == '__main__':
    print('Бот запущен')
    asyncio.run(main())

