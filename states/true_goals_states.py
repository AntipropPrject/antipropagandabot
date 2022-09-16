from aiogram.dispatcher.fsm.state import State, StatesGroup


class TrueGoalsState(StatesGroup):
    before_shop = State()
    before_shop_operation = State()
    main = State()
    opp_root = State()
    game = State()
    final = State()
