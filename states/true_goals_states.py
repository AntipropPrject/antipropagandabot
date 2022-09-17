from aiogram.dispatcher.fsm.state import State, StatesGroup


class TrueGoalsState(StatesGroup):
    more_goals_poll = State()
    before_shop = State()
    more_goals = State()
    more_goals_2 = State()
    before_shop_operation = State()
    main = State()
    more_goals = State()
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
