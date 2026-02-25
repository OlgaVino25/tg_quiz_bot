from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_main_menu_keyboard():
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("Новый вопрос", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Сдаться", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()

    keyboard.add_button("Мой счёт", color=VkKeyboardColor.PRIMARY)

    return keyboard.get_keyboard()
