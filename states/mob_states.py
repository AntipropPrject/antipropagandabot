from aiogram.dispatcher.fsm.state import StatesGroup, State


class MobState(StatesGroup):
    voenkomat_poll = State()
    mob_still_ignore_it = State()
    mob_why_he_did_it = State()
    mob_rules_of_nature = State()
    mob_bad_ingrish = State()
    mob_street_fighter = State()
    mob_they_coming_for_you = State()
    mob_ignore_it_go_away = State()
    mob_laws_lol = State()
    mob_only_to_lit = State()
    mob_is_he_insane = State()
    mob_nazi_is_here = State()
    mob_wot_mvps = State()
    nazi_poll = State()
    city_poll = State()
    first_part = State()
    main = State()
