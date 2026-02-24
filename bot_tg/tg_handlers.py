import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import logging

from aiogram import types


logger = logging.getLogger(__name__)


async def start(message: types.Message):
    await message.answer("Здравствуйте!")


async def echo(message: types.Message):
    await message.answer(message.text)
