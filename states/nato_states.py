from aiogram.dispatcher.fsm.state import StatesGroup, State


class Nato_states(StatesGroup):
    nato_pre_end = State()
    nato_map = State()
    nato_ucraine_in = State()
    nato_no_args = State()
    nato_countries = State()
    nato_other_questions = State()
    poll_answer = State()
    first_poll = State()
    nato_start = State()

