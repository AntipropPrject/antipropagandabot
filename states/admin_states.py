from aiogram.dispatcher.fsm.state import StatesGroup, State


class admin(StatesGroup):
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
    add_news = State()
    update_news = State()