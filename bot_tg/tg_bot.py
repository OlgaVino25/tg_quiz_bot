import os
import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import functools
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from settings import (
    TG_TOKEN,
    ADMIN_CHAT_ID,
)
import tg_handlers as tg_h
from logger import setup_logging


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
    dp = Dispatcher()

    dp.message.register(tg_h.start, Command(commands=["start"]))
    dp.message.register(tg_h.echo)
    dp.message.register(functools.partial(handle_user_message_with_error_handling))
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Непредвиденная ошибка в Telegram боте")
        raise


if __name__ == "__main__":
    asyncio.run(main())
