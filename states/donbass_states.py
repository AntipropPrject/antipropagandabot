from aiogram.dispatcher.fsm.state import State, StatesGroup


class donbass_state(StatesGroup):
    poll = State()
    start = State()
    main = State()
    eight_years_add = State()
    eight_years_selection = State()
    after_poll = State()
    second_poll = State()
    after_second_poll = State()
