from aiogram.dispatcher.fsm.state import State, StatesGroup


class start_dialog(StatesGroup):
    big_story = State()
    dialogue_1 = State()
    dialogue_2 = State()
    button_next = State()
    button_next_1 = State()
    button_next_2 = State()
    dialogue_3 = State()
    dialogue_4 = State()
    dialogue_5 = State()
    dialogue_6 = State()
    dialogue_7 = State()
    dialogue_8 = State()
    dialogue_9 = State()
    dialogue_10 = State()
    dialogue_extrafix = State()
