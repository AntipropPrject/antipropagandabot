from aiogram.dispatcher.fsm.state import State, StatesGroup


class donbass_state(StatesGroup):
    eight_years = State()
    eight_years_add = State()
    eight_years_selection = State()
    after_poll = State()

