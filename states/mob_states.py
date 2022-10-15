from aiogram.dispatcher.fsm.state import StatesGroup, State


class MobState(StatesGroup):
    save_yourself = State()
    jail = State()
    front = State()
    skipping = State()
    voenkomat_poll = State()
    nazi_poll = State()
    city_poll = State()
    first_part = State()
    main = State()
