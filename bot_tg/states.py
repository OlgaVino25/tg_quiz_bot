from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    CHOOSING = State()
    ANSWERING = State()
