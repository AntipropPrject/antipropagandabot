from aiogram.dispatcher.fsm.state import StatesGroup, State


class MobState(StatesGroup):
    nazi_poll = State()
    city_poll = State()
    first_part = State()
    main = State()
