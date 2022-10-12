from aiogram.dispatcher.fsm.state import StatesGroup, State


class StopWarState(StatesGroup):
    result = State()
    final = State()
    main = State()
    questions = State()
    must_watch = State()
    next_1 = State()
    war_1 = State()
    arg_1 = State()
    arg_2 = State()
    arg_3 = State()
