from aiogram.dispatcher.fsm.state import State, StatesGroup


class propaganda_victim(StatesGroup):
    start = State()
    next_0 = State()
    next_1 = State()
    choose_TV = State()
    ukrainian_TV = State()
    options = State()
    tv_first = State()
    tv_russia24 = State()
    tv_russia1 = State()
    tv_HTB = State()
    tv_star = State()
    tv_ren = State()
    yandex = State()
    wiki = State()
    dialogue_start_over = State()
    ppl_propaganda = State()
    web = State()
    final = State()
