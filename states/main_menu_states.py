from aiogram.dispatcher.fsm.state import State, StatesGroup


class MainMenuStates(StatesGroup):
    main = State()
    state_for_button_1 = State()
    state_for_button_2 = State()
    state_for_button_3 = State()
    again = State()
    baseoflie = State()
    crossed_boy = State()
    about_bucha = State()
    tv = State()
    web = State()
    ppl = State()
    ptn = State()
    games = State()
    truthgame = State()
    normalgame = State()
    nazigame = State()
    strikememes = State()
