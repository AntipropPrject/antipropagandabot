from aiogram.dispatcher.fsm.state import StatesGroup, State


class admin(StatesGroup):
    game_deleting = State()
    tv_lie_st = State()
    tv_lie_reb = State()
    tv_lie = State()
    ucraine_or_not_media = State()
    ucraine_or_not = State()
    normal_game = State()
    putin_game_old_lies = State()
    putin_game = State()
    truthgame_media_statement = State()
    truthgame_media_rebuttal = State()
    truthgame_media_truth = State()
    truthgame_deletion = State()
    truthgame_update = State()
    truthgame_update_stt = State()
    truthgame_update_rbb = State()
    truthgame_update_truth = State()
    truthgame_update_approve = State()
    truthgame = State()
    home = State()
    menu = State()
    add = State()
    pop = State()
    editors_menu = State()
    spam_menu = State()
    edit_context = State()
    add_text = State()
    edit_text = State()
    edit_text_test = State()
    add_media = State()
    edit_media_test = State()
    edit_media = State()
    confirm_add_text = State()
    confirm_edit_text = State()
    confirm_add_media = State()
    confirm_edit_media = State()
    repeat_add_text = State()
    repeat_edit_text = State()
    repeat_add_media = State()
    repeat_edit_media = State()
    delete_text_test = State()
    delete_text = State()
    delete_media_test = State()
    delete_media = State()
    import_menu = State()
    import_csv = State()
    import_csv_from_local = State()
    secretreborn = State()
    addingMistakeOrLie = State()
    addingMistakeOrLie_media = State()
    add_news = State()
    update_news = State()
    mass_media_menu = State()
    mass_media_add = State()
    mass_media_add_exposure = State()
    mass_media_del = State()
    mass_media_Done = State()
    mass_media_pop_Done = State()
    mass_media_edit = State()
    mass_media_edit_add = State()
    mass_media_edit_add_exposure = State()
    mass_media_edit_Done = State()
