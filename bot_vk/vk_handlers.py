import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import logging
import re
from vk_api.utils import get_random_id

from redis_client import r, get_random_question_id, get_question_by_id
from bot_vk.keyboards import get_main_menu_keyboard


logger = logging.getLogger(__name__)


class VkStates:
    CHOOSING = "CHOOSING"
    ANSWERING = "ANSWERING"


def normalize_answer(answer: str) -> str:
    answer = re.sub(r"\([^)]*\)", "", answer)
    if "." in answer:
        answer = answer.split(".")[0]
    answer = re.sub(r"[\'\"«»]", "", answer)
    return answer.strip().lower()


def get_state(user_id: int) -> str:
    """Получить состояние пользователя из Redis"""
    return r.get(f"vk_user:{user_id}:state") or VkStates.CHOOSING


def set_state(user_id: int, state: str):
    r.set(f"vk_user:{user_id}:state", state)


def handle_start(event, vk_api):
    user_id = event.user_id
    set_state(user_id, VkStates.CHOOSING)
    vk_api.messages.send(
        peer_id=event.peer_id,
        random_id=get_random_id(),
        message="Здравствуйте! Я бот для викторин!",
        keyboard=get_main_menu_keyboard(),
    )


def handle_new_question(event, vk_api):
    user_id = event.user_id
    q_id = get_random_question_id()
    if not q_id:
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message="Вопросы не загружены. Попробуйте позже.",
        )
        return

    question_text, answer_text = get_question_by_id(q_id)
    if not question_text or not answer_text:
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message="Ошибка загрузки вопроса.",
        )
        return

    r.setex(f"vk_user:{user_id}:current_question_id", 3600, q_id)

    set_state(user_id, VkStates.ANSWERING)
    vk_api.messages.send(
        peer_id=event.peer_id,
        random_id=get_random_id(),
        message=question_text,
        keyboard=get_main_menu_keyboard(),
    )


def handle_give_up(event, vk_api):
    user_id = event.user_id
    q_id = r.get(f"vk_user:{user_id}:current_question_id")
    if q_id:
        _, correct_answer = get_question_by_id(q_id)
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message=f"Правильный ответ: {correct_answer}",
        )
        r.delete(f"vk_user:{user_id}:current_question_id")
        handle_new_question(event, vk_api)
    else:
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message="У вас нет активного вопроса.",
        )
        set_state(user_id, VkStates.CHOOSING)
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message="Выберите действие:",
            keyboard=get_main_menu_keyboard(),
        )


def handle_my_account(event, vk_api):
    user_id = event.user_id
    score = r.get(f"vk_user:{user_id}:score") or 0
    vk_api.messages.send(
        peer_id=event.peer_id,
        random_id=get_random_id(),
        message=f"Ваш счёт: {score} очков",
        keyboard=get_main_menu_keyboard(),
    )


def handle_answer(event, vk_api):
    user_id = event.user_id
    q_id = r.get(f"vk_user:{user_id}:current_question_id")
    if not q_id:
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message="Сначала нажмите «Новый вопрос».",
        )
        set_state(user_id, VkStates.CHOOSING)
        return

    question_text, correct_answer_full = get_question_by_id(q_id)
    if not correct_answer_full:
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message="Ошибка: ответ не найден в базе.",
        )
        r.delete(f"vk_user:{user_id}:current_question_id")
        set_state(user_id, VkStates.CHOOSING)
        return

    user_text = event.text.strip().lower()
    correct_normalized = normalize_answer(correct_answer_full)

    if user_text == correct_normalized:
        r.incr(f"vk_user:{user_id}:score")
        score = r.get(f"vk_user:{user_id}:score")
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message=(
                f"Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос».\n"
                f"Ваш счёт: {score} очков"
            ),
            keyboard=get_main_menu_keyboard(),
        )
        r.delete(f"vk_user:{user_id}:current_question_id")
        set_state(user_id, VkStates.CHOOSING)
    else:
        vk_api.messages.send(
            peer_id=event.peer_id,
            random_id=get_random_id(),
            message="Неправильно… Попробуешь ещё раз?",
            keyboard=get_main_menu_keyboard(),
        )


def handle_fallback(event, vk_api):
    vk_api.messages.send(
        peer_id=event.peer_id,
        random_id=get_random_id(),
        message="Извините, я понимаю только команды из меню.",
    )
