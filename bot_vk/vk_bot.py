import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType

from settings import VK_GROUP_TOKEN, TG_TOKEN, ADMIN_CHAT_ID
from bot_vk import vk_handlers as vk_h
from logger import setup_logging


logger = logging.getLogger(__name__)


def main():
    setup_logging(telegram_token=TG_TOKEN, admin_chat_id=ADMIN_CHAT_ID)

    vk_session = vk.VkApi(token=VK_GROUP_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("VK бот запущен")

    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                user_id = event.user_id
                text = event.text.strip()

                state = vk_h.get_state(user_id)

                if text == "start" or text == "/start":
                    vk_h.handle_start(event, vk_api)
                elif text == "Новый вопрос":
                    vk_h.handle_new_question(event, vk_api)
                elif text == "Сдаться":
                    vk_h.handle_give_up(event, vk_api)
                elif text == "Мой счёт":
                    vk_h.handle_my_account(event, vk_api)
                else:
                    if state == vk_h.VkStates.ANSWERING:
                        vk_h.handle_answer(event, vk_api)
                    else:
                        vk_h.handle_fallback(event, vk_api)

    except KeyboardInterrupt:
        logger.warning("VK бот остановлен пользователем (Ctrl+C)")
        print("\nVK бот остановлен")
    except Exception as e:
        logger.exception("Непредвиденная ошибка в VK боте")
        raise


if __name__ == "__main__":
    main()
