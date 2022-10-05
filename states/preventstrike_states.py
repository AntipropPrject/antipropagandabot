from aiogram.dispatcher.fsm.state import StatesGroup, State


class PreventStrikeState(StatesGroup):
    after_game = State()
    memes = State()
    before_game = State()
    main = State()
    results = State()
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
