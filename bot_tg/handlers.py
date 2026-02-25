import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import logging
import re

from aiogram import types
from aiogram.fsm.context import FSMContext

from bot_tg.keyboards import get_main_menu_keyboard
from redis_client import r, get_random_question_id, get_question_by_id
from bot_tg.states import QuizStates

logger = logging.getLogger(__name__)


def normalize_answer(answer: str) -> str:
    """Приводит ответ к нормальной форме для сравнения."""
    answer = re.sub(r"\([^)]*\)", "", answer)
    if "." in answer:
        answer = answer.split(".")[0]

    answer = re.sub(r"[\'\"«»]", "", answer)
    return answer.strip().lower()


async def start(message: types.Message, state: FSMContext):
    await state.set_state(QuizStates.CHOOSING)
    await message.answer(
        "Здравствуйте! Я бот для викторин!", reply_markup=get_main_menu_keyboard()
    )


async def new_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    q_id = get_random_question_id()
    if not q_id:
        await message.answer("Вопросы не загружены. Попробуйте позже.")
        return

    question_text, answer_text = get_question_by_id(q_id)
    if not question_text or not answer_text:
        await message.answer("Ошибка загрузки вопроса.")
        return

    r.setex(f"user:{user_id}:current_question_id", 3600, q_id)

    await state.set_state(QuizStates.ANSWERING)
    await message.answer(question_text)


async def give_up(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    q_id = r.get(f"user:{user_id}:current_question_id")
    if q_id:
        _, correct_answer = get_question_by_id(q_id)
        await message.answer(f"Правильный ответ: {correct_answer}")
        r.delete(f"user:{user_id}:current_question_id")
        await new_question(message, state)
    else:
        await message.answer("У вас нет активного вопроса.")
        await state.set_state(QuizStates.CHOOSING)
        await message.answer(
            "Выберите действие:", reply_markup=get_main_menu_keyboard()
        )


async def my_account(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    score = r.get(f"user:{user_id}:score") or 0
    await message.answer(f"Ваш счёт: {score} очков")


async def handle_answer(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    q_id = r.get(f"user:{user_id}:current_question_id")
    if not q_id:
        await message.answer("Сначала нажмите «Новый вопрос».")
        await state.set_state(QuizStates.CHOOSING)
        return

    question_text, correct_answer_full = get_question_by_id(q_id)
    if not correct_answer_full:
        await message.answer("Ошибка: ответ не найден в базе.")
        r.delete(f"user:{user_id}:current_question_id")
        await state.set_state(QuizStates.CHOOSING)
        return

    user_text = message.text.strip().lower()
    correct_normalized = normalize_answer(correct_answer_full)

    if user_text == correct_normalized:
        r.incr(f"user:{user_id}:score")
        score = r.get(f"user:{user_id}:score")
        await message.answer(
            f"Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос».\n"
            f"Ваш счёт: {score} очков"
        )
        r.delete(f"user:{user_id}:current_question_id")
        await state.set_state(QuizStates.CHOOSING)
    else:
        await message.answer("Неправильно… Попробуешь ещё раз?")


async def echo(message: types.Message, state: FSMContext):
    await message.answer("Извините, я понимаю только команды из меню.")
