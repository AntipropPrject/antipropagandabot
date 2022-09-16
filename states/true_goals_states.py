from aiogram.dispatcher.fsm.state import State, StatesGroup


class TrueGoalsState(StatesGroup):
    before_shop = State()
    before_shop_operation = State()
    main = State()
    opp_root = State()
    game = State()
    final = State()


class Shop(StatesGroup):
    main = State()
    after_first_poll = State()
    shop_transfer = State()
    shop_bucket = State()
    shop_why_so_many = State()
    shop_callback = State()
