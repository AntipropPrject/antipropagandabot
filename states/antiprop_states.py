from aiogram.dispatcher.fsm.state import State, StatesGroup


class propaganda_victim(StatesGroup):

    start = State()
    options = State()
    tv_first = State()
    tv_russia24 = State()
    tv_russia1 = State()
    tv_HTB = State()
    tv_star = State()
    tv_ren = State()
    dialogue_start_over = State()
    ppl_propaganda = State()

    final = State()
