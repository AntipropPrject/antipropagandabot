import asyncio
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from data_base.DBuse import data_getter, sql_safe_select, redis_just_one_write, poll_write, mongo_game_answer
from data_base.DBuse import redis_delete_from_list
from filters.MapFilters import OperationWar, WarReason
from handlers import anti_prop_hand
from handlers.nazi_hand import NaziState
from handlers.preventive_strike import PreventStrikeState
from handlers.putin_hand import StateofPutin
from resources.all_polls import welc_message_one
from states.donbass_states import donbass_state
from stats.stat import mongo_update_stat, mongo_update_stat_new
from utilts import simple_media


class TruereasonsState(StatesGroup):
    main = State()
    game = State()
    final = State()


flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=TruereasonsState)


@router.message((F.text.contains('не')) & (F.text.contains('интересуюсь')) & (F.text.contains('политикой')),
                flags=flags)
async def reasons_true_reason_for_all(message: Message):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Аполитичный')
    base_list = ("👪 Защитить русских в Донбассе", "🛡 Предотвратить вторжение на территорию России или ДНР/ЛНР",
                 "🤬 Денацификация / Уничтожить нацистов")
    for thing in base_list:
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', thing)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_true_reason_for_all'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай поговорим о целях 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.contains('цели')) & (F.text.contains('бессмысленны')) & (F.text.contains('Не'))), flags=flags)
async def reasons_king_of_info(message: Message, state: FSMContext):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Сторонник войны')
    await state.set_state(anti_prop_hand.propaganda_victim.final)
    await anti_prop_hand.reasons_king_of_info(message, state)


@router.message((F.text == "Подожди. Я так не говорил(а). С чего ты взял, что это ненастоящие цели? 🤷‍♂️"),
                flags=flags)
async def reasons_king_of_info(message: Message):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Сторонник войны')
    base_list = ("👪 Защитить русских в Донбассе", "🛡 Предотвратить вторжение на территорию России или ДНР/ЛНР",
                 "🤬 Денацификация / Уничтожить нацистов")
    for thing in base_list:
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', thing)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_not_so_fast'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай поговорим о целях 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Давай поговорим о целях 👌"), flags=flags)
async def reasons_now_you_nothing(message: Message, state: FSMContext):
    await anti_prop_hand.war_point_now(message, state)


@router.message((F.text == "Давай попробуем 👌"), flags=flags)
async def reasons_now_you_fucked(message: Message, state: FSMContext):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Аполитичный')
    await anti_prop_hand.war_point_now(message, state)


@router.message((F.text == "Хорошо!"), flags=flags)
async def reasons_now_you_blessed(message: Message, state: FSMContext):
    await redis_just_one_write(f'Usrs: {message.from_user.id}: Politics:', 'Оппозиционер')
    await reasons_normal_game_start(message, state)


@router.message(OperationWar(answer='Специальная военная операция (СВО)'), (F.text == 'Продолжай ⏳'),
                state=TruereasonsState.main, flags=flags)
async def reasons_operation(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_operation'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо - война 🗡'))
    nmarkup.row(types.KeyboardButton(text='Нет - спецоперация 🛡'))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('спецоперация')), flags=flags)
async def reasons_sorry_im_bot(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_sorry_im_bot'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо...'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.contains('война') & (F.text.contains('Хорошо'))) | (F.text == 'Хорошо...')), flags=flags)
@router.message(OperationWar(answer='Война'), (F.text == 'Продолжай ⏳'),
                state=TruereasonsState.main, flags=flags)
async def reasons_war(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Давай попробуем! 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="👪 Защитить русских в Донбассе"), flags=flags)
async def donbass_big_tragedy(message: Message, state=FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_donbass', value='Да')
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "👪 Защитить русских в Донбассе")
    await state.set_state(donbass_state.eight_years)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_big_tragedy'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что главное? 🤔'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(WarReason(answer="🤬 Денацификация / Уничтожить нацистов"), flags=flags)
async def reasons_denazi(message: Message, state=FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_nazi', value='Да')
    await state.set_state(NaziState.first_poll)
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "🤬 Денацификация / Уничтожить нацистов")
    text = await sql_safe_select('text', 'texts', {'name': 'nazi_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Покажи варианты ✍️'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(WarReason(answer="🛡 Предотвратить вторжение на территорию России или ДНР/ЛНР"), flags=flags)
async def prevent_strike_start(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "🛡 Предотвратить вторжение на территорию России или ДНР/ЛНР")
    await state.clear()
    await state.set_state(PreventStrikeState.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Давай разберём 👌'))
    await simple_media(message, 'prevent_strike_start', nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Демилитаризация / Снижение военной мощи"), flags=flags)
async def reasons_demilitarism(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "💣 Демилитаризация / Снижение военной мощи")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_putin_demilitar'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Им наверху виднее 🤔'))
    nmarkup.row(types.KeyboardButton(text='Я не знаю 🤷‍♀️'))
    nmarkup.row(types.KeyboardButton(text='Предотвратить размещение военных баз НАТО 🛡'))
    nmarkup.row(types.KeyboardButton(text='Предотвратить создание ядерного оружия на Украине 💥'))
    nmarkup.row(types.KeyboardButton(text='Думаю он хотел, как лучше, а получилось наоборот 🤷‍♂️'))
    nmarkup.adjust(2, 1, 1, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
    (F.text == 'Им наверху виднее 🤔') | (F.text == 'Я не знаю 🤷‍♀️') | (F.text.contains('хотел, как лучше')),
    flags=flags)
async def reasons_lie_no_more_1(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_lie_no_more_1'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('размещение военных баз')), flags=flags)
async def reasons_lie_no_more_2(message: Message):
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                     "💂 Предотвратить размещение военных баз НАТО на Украине")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_lie_no_more_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('создание ядерного оружия на')), flags=flags)
async def reasons_lie_no_more_3(message: Message):
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                     "🤯 Предотвратить секретные разработки: биологическое оружие / ядерное оружие")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_lie_no_more_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(WarReason(answer="💂 Предотвратить размещение военных баз НАТО на Украине"), flags=flags)
async def reasons_big_bad_nato(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', welc_message_one[8])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Давай 👌'))
    await simple_media(message, 'reasons_big_bad_NATO', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Давай 👌'), state=TruereasonsState.main, flags=flags)
async def reasons_lie_no_more_1(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_NATO_is_coming'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(WarReason(answer="🤯 Предотвратить секретные разработки: биологическое оружие / ядерное оружие"),
                flags=flags)
async def reasons_biopigeons(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "🤯 Предотвратить секретные разработки: биологическое оружие / ядерное оружие")
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_bio_nuclear'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Хорошо, продолжим 👌'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


"""@router.message(WarReason(answer="🗺 Вернуть России исторические земли / Объединить русский народ"))
async def reasons_take_lands(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', 
                                                                        "🗺 Вернуть России исторические земли / Объединить русский народ")
    text = "Кусок про захват территорий, но мы его не выводим"
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(WarReason(answer="Сменить власть в Украине"))
async def reasons_new_power(message: Message, state: FSMContext):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:', "♻️ Сменить власть в Украине")
    text = "Кусок про смену власти в Украине. Но мы его не выводим."
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Кнопка'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))"""


@router.message(state=TruereasonsState.main, flags=flags)
async def reasons_normal_game_start(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.game)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_normal_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Начнем! 🚀'))
    nmarkup.row(types.KeyboardButton(text='Пропустим игру 🙅‍♀️'))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Начнем! 🚀") | (F.text == "Продолжаем, давай еще! 👉")), state=TruereasonsState.game,
                flags=flags)
async def reasons_normal_game_question(message: Message, state: FSMContext):
    if 'Начнем! 🚀' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='normal_game_stats', value='Начали и НЕ закончили')
    try:
        count = (await state.get_data())['ngamecount']
    except:
        count = 0
    how_many_rounds = (await data_getter("SELECT COUNT (*) FROM public.normal_game"))[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = (await data_getter("SELECT * FROM (SELECT t_id, text, belivers, nonbelivers, rebuttal, "
                                        " ROW_NUMBER () OVER (ORDER BY id)"
                                        "FROM normal_game "
                                        "left outer join assets on asset_name = assets.name "
                                        "left outer join texts ON text_name = texts.name)"
                                        f"AS sub WHERE row_number = {count}"))[0]
        await state.update_data(ngamecount=count, belive=truth_data[2], not_belive=truth_data[3])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это абсурд🤦🏼‍♀️"))
        nmarkup.row(types.KeyboardButton(text="Это нормально👌"))
        nmarkup.adjust(2)
        if truth_data[0] is not None:
            capt = ""
            if truth_data[1] is not None:
                capt = truth_data[1]
            try:
                await message.answer_video(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except TelegramBadRequest:
                await message.answer_photo(truth_data[0], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(f'{truth_data[1]}', reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='normal_game_stats', value='Начали и закончили')
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Продолжим 🤝"))
        await message.answer(
            "У меня закончились новости. Спасибо за игру 🤝",
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Это абсурд🤦🏼‍♀️") | (F.text == "Это нормально👌")), state=TruereasonsState.game,
                flags=flags)
async def reasons_normal_game_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    END = bool(data['ngamecount'] == (await data_getter('SELECT COUNT(id) FROM public.normal_game'))[0][0])
    nmarkup = ReplyKeyboardBuilder()
    if END is False:
        nmarkup.row(types.KeyboardButton(text="Продолжаем, давай еще! 👉"))
        nmarkup.row(types.KeyboardButton(text="Достаточно, давай закончим 🙅"))
    else:
        nmarkup.row(types.KeyboardButton(text="Продолжим 🤝"))
    answer_group = str()
    if message.text == "Это абсурд🤦🏼‍♀️":
        answer_group = 'belivers'
    elif message.text == "Это нормально👌":
        answer_group = 'nonbelivers'
    await mongo_game_answer(message.from_user.id, 'normal_game', data['ngamecount'],
                            answer_group, {'id': data['ngamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    await message.answer(
        f'Результаты других участников:\n🤦‍♂️ Это абсурд: {round(t_percentage * 100)}%'
        f'\n👌 Это нормально: {round(100 - t_percentage * 100)}%',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))
    if END is True:
        await message.answer("У меня закончились новости. Спасибо за игру 🤝",
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text.contains("Достаточно,")) | (F.text == "Продолжим 🤝") | (F.text == 'Пропустим игру 🙅‍♀️')),
                state=TruereasonsState.game, flags=flags)
async def reasons_real_reasons(message: Message, state: FSMContext):
    if 'Пропустим игру' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='normal_game_stats', value='Пропустили')

    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    nmarkup.row(types.KeyboardButton(text="Подожди, а какие тогда настоящие цели войны? 🎯"))
    await simple_media(message, 'reasons_real_reasons', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Подожди, а какие тогда настоящие цели войны? 🎯"), state=TruereasonsState.final,
                flags=flags)
async def reasons_are_they_real(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='real_reasons_wanted', value='Да')
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_are_they_real'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Продолжай ⏳"), state=TruereasonsState.final, flags=flags)
async def reasons_war_of_noone(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее да 😔"))
    nmarkup.row(types.KeyboardButton(text="Скорее нет 🙅‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Я думаю, что люди наверху знают, что делают 👮‍♂️"))
    nmarkup.adjust(2, 1)
    await simple_media(message, 'reasons_war_of_noone', nmarkup.as_markup(resize_keyboard=True))


@router.message(((F.text == "Я думаю, что люди наверху знают, что делают 👮‍♂️") | (F.text == "Скорее нет 🙅‍♂️")),
                state=TruereasonsState.final, flags=flags)
async def reasons_cynical_view(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='do_you_need_war_1', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_cynical_view'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Ни в чем не улучшалось 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Импортозамещение 📦"))
    nmarkup.row(types.KeyboardButton(text="Конец гегемонии США / Однополярного мира 🇺🇸"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Конец гегемонии США / Однополярного мира 🇺🇸"), state=TruereasonsState.final, flags=flags)
async def reasons_usa_gegemony(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='how_it_helped', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, не понимаю 🤷‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Да, понимаю ✔️"))
    await simple_media(message, 'reasons_USA_gegemony', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Да, понимаю ✔️"), state=TruereasonsState.final, flags=flags)
async def reasons_europe_cold(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_Europe_cold'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, цель не в этом 🙅‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Да, именно в этом 👍"))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Ни в чем не улучшалось 🤷‍♂️"), state=TruereasonsState.final, flags=flags)
async def reasons_only_misery(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='how_it_helped', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_only_misery'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Импортозамещение 📦"), state=TruereasonsState.final, flags=flags)
async def reasons_nails_lol(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='how_it_helped', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await simple_media(message, 'reasons_nails_lol', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Нет, не понимаю 🤷‍♂️"), state=TruereasonsState.final, flags=flags)
async def reasons_21_cent(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_21_cent'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Нет, цель не в этом 🙅‍♂️"), state=TruereasonsState.final, flags=flags)
async def reasons_hail_china(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_hail_China'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Да, именно в этом 👍"), state=TruereasonsState.final, flags=flags)
async def reasons_bot_afraid(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_bot_afraid'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Давай 👌"), state=TruereasonsState.final, flags=flags)
async def reasons_why_only_rus(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_why_only_rus'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какие результаты? 📊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Какие результаты? 📊"), state=TruereasonsState.final, flags=flags)
async def reasons_eritrea(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_eritrea'})
    media = await sql_safe_select('t_id', 'assets', {'name': 'reasons_eritrea'})
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Это показательный пример... 🙁"))
    nmarkup.row(types.KeyboardButton(text="Просто весь мир против нас 🖕"))
    await simple_media(message, 'reasons_eritrea', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Это показательный пример... 🙁"), state=TruereasonsState.final, flags=flags)
async def reasons_mb_think(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await simple_media(message, 'reasons_mb_think', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Просто весь мир против нас 🖕"), state=TruereasonsState.final, flags=flags)
async def reasons_propaganda_man(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await simple_media(message, 'reasons_propaganda_man', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Давай"), state=TruereasonsState.final, flags=flags)
async def reasons_celeb_video(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_celeb_video'})
    media = await sql_safe_select('t_id', 'assets', {'name': 'reasons_celeb_video'})
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="..."))
    await simple_media(message, 'reasons_celeb_video', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "..."), state=TruereasonsState.final, flags=flags)
async def reasons_open_eyes(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, мне не нужна эта война... 🙅‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Я не знаю...😨"))
    nmarkup.row(types.KeyboardButton(text="Да, я готов(а) поддержать войну / спецоперацию 💥"))
    nmarkup.row(types.KeyboardButton(text="Столько парней погибло, теперь мы не имеем права проиграть... 😔"))
    nmarkup.row(types.KeyboardButton(text="Я хочу подумать, давай сделаем паузу... ⏱"))
    nmarkup.row(types.KeyboardButton(text="Давай закончим этот разговор! 🖕"))
    nmarkup.adjust(2, 1, 1, 2)
    await simple_media(message, 'reasons_open_eyes', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Я хочу подумать, давай сделаем паузу... ⏱"), state=TruereasonsState.final, flags=flags)
async def reasons_pause(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.final)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, мне не нужна эта война... 🙅‍♂️️"))
    nmarkup.row(types.KeyboardButton(text="Я не знаю...😨"))
    nmarkup.row(types.KeyboardButton(text="Да, я готов(а) поддержать войну / спецоперацию 💥"))
    nmarkup.row(types.KeyboardButton(text="Столько парней погибло, теперь мы не имеем права проиграть... 😔"))
    nmarkup.adjust(2, 1, 1)
    await simple_media(message, 'reasons_pause', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Столько парней погибло, теперь мы не имеем права проиграть... 😔"),
                state=TruereasonsState.final, flags=flags)
async def reasons_why_support_war(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='do_you_need_war_2', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_why_support_war'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Нет, мне не нужна эта война... 🙅‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Я не знаю...😨"))
    nmarkup.row(types.KeyboardButton(text="Да, я готов(а) поддержать войну / спецоперацию 💥"))
    nmarkup.row(types.KeyboardButton(text="Я хочу подумать, давай сделаем паузу... ⏱"))
    nmarkup.row(types.KeyboardButton(text="Давай закончим этот разговор! 🖕"))
    nmarkup.adjust(2, 1, 2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(((F.text == "Нет, мне не нужна эта война... 🙅‍♂️") |
                 (F.text == "Я передумал(а), мне не нужна эта война...🙅") |
                 (F.text == "Я не знаю...😨")),
                state=TruereasonsState.final, flags=flags)
async def reasons_now_he_normal(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='do_you_need_war_2', value=message.text)
    if 'не нужна' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='now_he_normal', value='Да')
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_now_he_normal'})
    await mongo_update_stat(message.from_user.id, 'war_aims')
    await state.set_state(StateofPutin.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 🤝"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
    ((F.text == "Да, я готов(а) поддержать войну / спецоперацию 💥") | (F.text == "Давай закончим этот разговор! 🖕")),
    state=TruereasonsState.final, flags=flags)
async def reasons_he_needs_war(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='do_you_need_war_2', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи текст песни 📝"))
    nmarkup.row(types.KeyboardButton(text="Я передумал(а), мне не нужна эта война...🙅"))
    await simple_media(message, 'reasons_he_needs_war', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Покажи текст песни 📝"), state=TruereasonsState.final, flags=flags)
async def reasons_generation_z(message: Message):
    await simple_media(message, 'reasons_generation_Z', ReplyKeyboardRemove())
    await asyncio.sleep(4)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я передумал(а), мне не нужна эта война...🙅"))
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_generation_Z_1'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Скорее да 😔"), state=TruereasonsState.final, flags=flags)
async def reasons_who_to_blame(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='do_you_need_war_1', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_who_to_blame'})
    await state.set_state(StateofPutin.main)
    await mongo_update_stat(message.from_user.id, 'war_aims')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 🤝"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)
