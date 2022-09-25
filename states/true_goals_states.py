from aiogram.dispatcher.fsm.state import State, StatesGroup


class TrueGoalsState(StatesGroup):
    putin = State()
    power_change = State()
    absurd = State()
    normal_game = State()
    more_goals_poll = State()
    before_shop = State()
    really_goals = State()
    more_goals_sort = State()
    more_goals_no_truth = State()
    more_goals = State()
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
