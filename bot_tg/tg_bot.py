import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage


from settings import TG_TOKEN, ADMIN_CHAT_ID
from bot_tg import handlers as tg_h
from bot_tg.states import QuizStates
from logger import setup_logging

import logging


logger = logging.getLogger(__name__)


async def handle_user_message_with_error_handling(message, project_id):
    """Для обработки исключений при обработке сообщений пользователя"""
    try:
        await tg_h.handle_user_message(message, project_id)
    except Exception as err:
        logger.exception("Ошибка в Telegram обработчике")


async def main():
    setup_logging(
        telegram_token=TG_TOKEN, admin_chat_id=ADMIN_CHAT_ID, logger_instance=None
    )

    bot = Bot(token=TG_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.register(tg_h.start, Command(commands=["start"]))
    dp.message.register(tg_h.start, lambda msg: msg.text == "start")

    dp.message.register(
        tg_h.new_question,
        lambda msg: msg.text == "Новый вопрос",
        StateFilter(QuizStates.CHOOSING),
    )
    dp.message.register(tg_h.give_up, lambda msg: msg.text == "Сдаться")
    dp.message.register(tg_h.my_account, lambda msg: msg.text == "Мой счёт")

    dp.message.register(tg_h.handle_answer, StateFilter(QuizStates.ANSWERING))

    dp.message.register(tg_h.echo)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Непредвиденная ошибка в Telegram боте")
        raise


if __name__ == "__main__":
    asyncio.run(main())
