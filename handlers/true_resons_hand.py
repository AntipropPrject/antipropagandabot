from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from data_base.DBuse import data_getter, sql_safe_select, sql_safe_update, redis_just_one_write, poll_write
from data_base.DBuse import redis_delete_from_list
from filters.All_filters import OperationWar, WarReason
from handlers import anti_prop_hand
from handlers.nazi_hand import NaziState
from handlers.preventive_strike import PreventStrikeState
from handlers.putin_hand import StateofPutin
from middleware import CounterMiddleware
from resources.all_polls import nazizm
from states.donbass_states import donbass_state
from utilts import simple_media


class TruereasonsState(StatesGroup):
    main = State()
    game = State()
    final = State()


router = Router()
router.message.middleware(CounterMiddleware())
router.message.filter(state=TruereasonsState)


@router.message((F.text.contains('не')) & (F.text.contains('интересуюсь')) & (F.text.contains('политикой')))
async def reasons_true_reason_for_all(message: Message):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Аполитичный')
    base_list = ["Защитить русских в Донбассе", "Предотвратить вторжение на территорию России или ЛНР/ДНР",
                 "Денацификация / Уничтожить нацистов"]
    for thing in base_list:
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', thing)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_true_reason_for_all'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай поговорим о целях"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Подожди. Я такого не говорил(а). С чего ты взял, что это ненастоящие цели?"))
async def reasons_king_of_info(message: Message):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Сторонник войны')
    base_list = ["Защитить русских в Донбассе", "Предотвратить вторжение на территорию России или ЛНР/ДНР",
                 "Денацификация / Уничтожить нацистов"]
    for thing in base_list:
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', thing)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_not_so_fast'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай поговорим о целях"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Давай попробуем"))
async def reasons_now_you_fucked(message: Message, state: FSMContext):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Сторонник войны')
    await anti_prop_hand.war_point_now(message, state)


@router.message((F.text == "Хорошо!"))
async def reasons_now_you_blessed(message: Message, state: FSMContext):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Оппозиционер')
    await reasons_normal_game_start(message, state)


@router.message(OperationWar(answer='Специальная военная операция (СВО)'), (F.text == 'Продолжай'),
                state=TruereasonsState.main)
async def reasons_operation(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо -- "война".'))
    nmarkup.row(types.KeyboardButton(text='Нет, это спецоперация.'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('это спецоперация')))
async def reasons_war(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_sorry_im_bot'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо...'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('война') & (F.text.contains('Хорошо...'))))
@router.message(OperationWar(answer='Война / Вторжение в Украину'), (F.text == 'Продолжай'))
async def reasons_war(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнем'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer='Защитить русских в Донбассе'))
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_big_tragedy'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что главное?'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer='Денацификация / Уничтожить нацистов'))
async def reasons_denazi(message: Message, state=FSMContext):
    await state.set_state(NaziState.first_poll)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 'Денацификация / Уничтожить нацистов')
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_start'})
    question = "Отметьте один или более вариантов, с которыми согласны или частично согласны"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    await message.answer_poll(question, nazizm, allows_multiple_answers=True, is_anonymous=False)


@router.message(WarReason(answer="Предотвратить вторжение на территорию России или ЛНР/ДНР"))
async def prevent_strike_start(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "Предотвратить вторжение на территорию России или ЛНР/ДНР")
    await state.clear()
    await state.set_state(PreventStrikeState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'prevent_strike_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Давай разберем'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Демилитаризация / Снижение военной мощи"))
async def reasons_demilitarism(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "Демилитаризация / Снижение военной мощи")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_putin_demilitar'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Им наверху виднее'))
    nmarkup.row(types.KeyboardButton(text='Я не знаю'))
    nmarkup.row(types.KeyboardButton(text='Думаю он хотел, как лучше, а получилось наоборот'))
    nmarkup.row(types.KeyboardButton(text='Предотвратить размещение военных баз НАТО'))
    nmarkup.row(types.KeyboardButton(text='Предотвратить создание ядерного оружия на Украине'))
    nmarkup.adjust(2, 1, 1, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Им наверху виднее') | (F.text == 'Я не знаю') | (F.text.contains('хотел, как лучше')))
async def reasons_lie_no_more_1(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_lie_no_more_1'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Тогда продолжим'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('размещение военных баз')))
async def reasons_lie_no_more_2(message: Message):
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                     "Предотвратить размещение военных баз НАТО в Украине")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_lie_no_more_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Тогда продолжим'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('создание ядерного оружия на')))
async def reasons_lie_no_more_3(message: Message):
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                     "Уничтожить биолаборатории / Предотвратить создание ядерного оружия")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_lie_no_more_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Тогда продолжим'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Предотвратить размещение военных баз НАТО в Украине"))
async def reasons_big_bad_nato(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "Предотвратить размещение военных баз НАТО в Украине")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_big_bad_NATO'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Давай'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Давай'), state=TruereasonsState.main)
async def reasons_lie_no_more_1(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_NATO_is_coming'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='А почему бы и нет'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Уничтожить биолаборатории / Предотвратить создание ядерного оружия"))
async def reasons_biopigeons(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "Уничтожить биолаборатории / Предотвратить создание ядерного оружия")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_bio_nuclear'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Ладно'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


"""@router.message(WarReason(answer="Захватить территории Донбасса и юга Украины"))
async def reasons_take_lands(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', 
                                                                        "Захватить территории Донбасса и юга Украины")
    text = "Кусок про захват территорий, но мы его не выводим"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Сменить власть в Украине"))
async def reasons_new_power(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', "Сменить власть в Украине")
    text = "Кусок про смену власти в Украине. Но мы его не выводим."
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))"""


@router.message(state=TruereasonsState.main)
async def reasons_normal_game_start(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.game)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_normal_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнем!'))
    nmarkup.row(types.KeyboardButton(text='Пропустим в этот раз'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Начнем!") | (F.text == "Продолжаем, давай еще!")), state=TruereasonsState.game)
async def reasons_normal_game_question(message: Message, state: FSMContext):
    try:
        count = (await state.get_data())['ngamecount']
    except:
        count = 0
    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.normal_game")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT t_id, text, belivers, nonbelivers, rebuttal FROM public.normal_game "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        await state.update_data(ngamecount=count, belive=truth_data[2], not_belive=truth_data[3])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это ненормально!"))
        nmarkup.row(types.KeyboardButton(text="Это нормально."))
        if truth_data[0] is not None:
            capt = ""
            if truth_data[1] is not None:
                capt = truth_data[1]
            try:
                await message.answer_video(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(f'{truth_data[1]}', reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Хорошо, давай дальше"))
        await message.answer(
            "Боюсь, что пока что у меня кончились примеры. Я поищу еще, а пока что продолжим",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Это ненормально!") | (F.text == "Это нормально.")), state=TruereasonsState.game)
async def reasons_normal_game_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    base_update_dict = dict()
    if message.text == "Это нормально.":
        base_update_dict.update({'belivers': (data['belive'] + 1)})
    elif message.text == "Это ненормально!":
        base_update_dict.update({'nonbelivers': (data['not_belive'] + 1)})
    await sql_safe_update("normal_game", base_update_dict, {'id': data['ngamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем, давай еще!"))
    nmarkup.row(types.KeyboardButton(text="Достаточно."))
    await message.answer(
        f'Результаты других участников:\n\nЭто ненормально: {round((100 - t_percentage * 100), 1)}% \n Все в порядке: '
        f'{round(t_percentage * 100, 1)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Достаточно.") | (F.text == "Хорошо, давай дальше") | (F.text == "Пропустим в этот раз")),
                state=TruereasonsState.game)
async def reasons_real_reasons(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Подожди, а какие тогда настоящие цели войны?"))
    nmarkup.row(types.KeyboardButton(text="Продолжай"))
    await simple_media(message, 'reasons_real_reasons', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Подожди, а какие тогда настоящие цели войны?"), state=TruereasonsState.final)
async def reasons_are_they_real(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_are_they_real'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай"), state=TruereasonsState.final)
async def reasons_war_of_noone(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_war_of_noone'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет"))
    nmarkup.row(types.KeyboardButton(text="Думаю, люди наверху знают, что делают"))
    nmarkup.adjust(2, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Думаю, люди наверху знают, что делают") | (F.text == "Скорее нет")),
                state=TruereasonsState.final)
async def reasons_cynical_view(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_cynical_view'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ни в чем не улучшилось"))
    nmarkup.row(types.KeyboardButton(text="Импортозамещение"))
    nmarkup.row(types.KeyboardButton(text="Конец гегемонии США"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Конец гегемонии США"), state=TruereasonsState.final)
async def reasons_usa_gegemony(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_USA_gegemony'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, не понимаю"))
    nmarkup.row(types.KeyboardButton(text="Да, понимаю"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Да, понимаю"), state=TruereasonsState.final)
async def reasons_europe_cold(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_Europe_cold'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, цель не в этом"))
    nmarkup.row(types.KeyboardButton(text="Да, именно в этом"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Ни в чем не улучшилось"), state=TruereasonsState.final)
async def reasons_only_misery(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_only_misery'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Импортозамещение"), state=TruereasonsState.final)
async def reasons_nails_lol(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_nails_lol'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Нет, не понимаю"), state=TruereasonsState.final)
async def reasons_21_cent(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_21_cent'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Нет, цель не в этом"), state=TruereasonsState.final)
async def reasons_hail_china(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_hail_China'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Да, именно в этом"), state=TruereasonsState.final)
async def reasons_bot_afraid(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_bot_afraid'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Давай"), state=TruereasonsState.final)
async def reasons_why_only_rus(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_why_only_rus'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какие результаты?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Какие результаты?"), state=TruereasonsState.final)
async def reasons_eritrea(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_eritrea'})
    media = await sql_safe_select('t_id', 'assets', {'name': 'reasons_eritrea'})
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Показательный пример..."))
    nmarkup.row(types.KeyboardButton(text="Просто весь мир против нас"))
    await simple_media(message, 'reasons_eritrea', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Показательный пример..."), state=TruereasonsState.final)
async def reasons_mb_think(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_mb_think'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Просто весь мир против нас"), state=TruereasonsState.final)
async def reasons_propaganda_man(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_propaganda_man'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Хорошо"), state=TruereasonsState.final)
async def reasons_celeb_video(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_celeb_video'})
    media = await sql_safe_select('t_id', 'assets', {'name': 'reasons_celeb_video'})
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="..."))
    await simple_media(message, 'reasons_celeb_video', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "..."), state=TruereasonsState.final)
async def reasons_open_eyes(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Столько парней погибло, теперь у нас нет права проиграть..."))
    nmarkup.row(types.KeyboardButton(text="Я хочу подумать, дайте паузу..."))
    nmarkup.row(types.KeyboardButton(text="Нет, мне не нужна эта война..."))
    nmarkup.row(types.KeyboardButton(text="Я не знаю...😨"))
    nmarkup.row(types.KeyboardButton(text="Да, я готов(а) это поддерживать"))
    nmarkup.row(types.KeyboardButton(text="Давайте закончим этот разговор"))
    await simple_media(message, 'reasons_open_eyes', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Я хочу подумать, дайте паузу..."), state=TruereasonsState.final)
async def reasons_pause(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, мне не нужна эта война..."))
    nmarkup.row(types.KeyboardButton(text="Я не знаю...😨"))
    nmarkup.row(types.KeyboardButton(text="Да, я готов(а) это поддерживать"))
    await simple_media(message, 'reasons_pause', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Столько парней погибло, теперь у нас нет права проиграть..."),
                state=TruereasonsState.final)
async def reasons_why_support_war(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_why_support_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, мне не нужна эта война..."))
    nmarkup.row(types.KeyboardButton(text="Я не знаю...😨"))
    nmarkup.row(types.KeyboardButton(text="Да, я готов(а) это поддерживать"))
    nmarkup.row(types.KeyboardButton(text="Давайте закончим этот разговор"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.contains('не нужна эта война...')) | (F.text == "Я не знаю...😨")),
                state=TruereasonsState.final)
async def reasons_now_he_normal(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_now_he_normal'})
    await state.set_state(StateofPutin.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, давай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Да, я готов(а) это поддерживать") | (F.text == "Давайте закончим этот разговор")),
                state=TruereasonsState.final)
async def reasons_he_needs_war(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_he_needs_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Показать текст песни"))
    nmarkup.row(types.KeyboardButton(text="Я передумал(а), мне не нужна эта война..."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Показать текст песни"), state=TruereasonsState.final)
async def reasons_generation_z(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_generation_Z'})
    await message.answer(text)


@router.message((F.text == "Скорее да"), state=TruereasonsState.final)
async def reasons_who_to_blame(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_who_to_blame'})
    await state.set_state(StateofPutin.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо, давай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
