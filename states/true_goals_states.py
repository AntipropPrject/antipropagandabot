from aiogram.dispatcher.fsm.state import State, StatesGroup


class TrueGoalsState(StatesGroup):
    goals_fact_7 = State()
    goals_fact_6 = State()
    goals_fact_5 = State()
    goals_fact_4 = State()
    goals_fact_3 = State()
    goals_fact_2 = State()
    goals_fact_1 = State()
    more_goals_next = State()
    putin_gaming = State()
    putin_next_next = State()
    putin_next = State()
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


class WarGoalsState(StatesGroup):
    bio = State()
    nato = State()
    demilitari = State()
    main = State()
    donbas_enter = State()
    preventive_enter = State()
    nazi_enter = State()


class Shop(StatesGroup):
    shop_callback_child_saved = State()
    main = State()
    after_first_poll = State()
    shop_transfer = State()
    shop_bucket = State()
    shop_why_so_many = State()
    shop_callback = State()
