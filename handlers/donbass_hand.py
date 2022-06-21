from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import poll_write, sql_safe_select, redis_pop, poll_get, redis_delete_from_list
from filters.All_filters import DonbassOptionsFilter, second_donbass_filter
from handlers.true_resons_hand import TruereasonsState
from keyboards.main_keys import filler_kb
from middleware import CounterMiddleware
from resources.all_polls import donbass_first_poll, donbass_second_poll
from states.donbass_states import donbass_state
from utilts import simple_media

router = Router()
router.message.middleware(CounterMiddleware())

router.message.filter(state=donbass_state)

"""@router.message(((F.text == 'Начнем')))
async def reasons_war(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_big_tragedy'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что главное?'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
"""


@router.message(F.text == 'Что главное? 🤔')
async def donbass_chart_1(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что значит «гражданские»? 👨‍👩‍👧‍👦'))
    nmarkup.add(types.KeyboardButton(text='Да, знал(а) 👌🏼'))
    nmarkup.add(types.KeyboardButton(text='Нет, не знал(а) 🤔'))
    nmarkup.adjust(1, 2)
    await simple_media(message, 'donbass_chart_1', nmarkup.as_markup(resize_keyboard=True))


@router.message(text_contains='значит', content_types=types.ContentType.TEXT, text_ignore_case=True)
async def eight_years_add(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_years_add'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='Да, знал(а) 👌🏼'))
    nmarkup.add(types.KeyboardButton(text='Нет, не знал(а)'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('знал')))
async def donbass_chart_2(message: Message, state=FSMContext):
    await state.set_state(donbass_state.eight_years_selection)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_chart_2'})
    ph_id = await sql_safe_select('t_id', 'assets', {'name': 'donbass_chart_2'})
    try:
        await message.answer_photo(ph_id, caption=text)
    except:
        await message.answer_video(ph_id, caption=text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='Покажи варианты ✍️'))
    await message.reply_poll("Отметьте один или более вариантов, с которыми вы согласны или частично согласны",
                             donbass_first_poll, is_anonymous=False, allows_multiple_answers=True,
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(donbass_state.eight_years_selection, (F.text == 'Покажи варианты ✍️'))
async def poll_filler(message: types.Message):
    await message.answer('Чтобы продолжить -- отметьте ответы выше и нажмите "Проголосовать" или "Vote"',
                         reply_markup=ReplyKeyboardRemove())


# Тут удвоение первого поста каждой ветки, потому что нам надо отвечать СРАЗУ после опроса
@router.poll_answer(state=donbass_state.eight_years_selection)
async def poll_answer_handler(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    indexes = poll_answer.option_ids
    true_options = list()
    print(indexes)
    for index in indexes:
        if index == 0:
            # TODO:перекидывать дальше
            continue
        true_options.append(donbass_first_poll[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Donbass_polls: First:', donbass_first_poll[index])
    if "🛡 Если бы мы не нанесли упреждающий удар, то Украина напала бы первая, и жертв было бы больше" in true_options:
        text = 'У меня есть уточняющий вопрос.\n' \
               'Продолжите: "Если бы мы не нанесли упреждающий удар, то Украина напала бы первая..." Куда?'
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="...на ДНР/ЛНР и Крым"))
        nmarkup.row(types.KeyboardButton(text="...вместе с НАТО на Россию"))
        nmarkup.row(types.KeyboardButton(text="Оба варианта"))
        nmarkup.adjust(2, 1)
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    elif "📊 ООН врет, не может быть таких жертв среди гражданского населения" in true_options:
        text = await sql_safe_select('text', 'texts', {'name': 'civil_casualties'})
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: First:')
        await bot.send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
    elif "😕 Эти \"мирные люди\" — жители Украины, а значит неонацисты, которых не жалко" in true_options:
        await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
        text = 'Считать, что люди заслуживают смерти только потому,' \
               ' что у них есть украинский паспорт — и есть нацизм.\n' \
               'В любом случае этот хэндлер будет готов принять любой сценарий,' \
               ' но пока что перейдите к следующей части.'
        if 'Денацификация / Уничтожить нацистов' not in (
                await poll_get(f'Usrs: {poll_answer.user.id}: Start_answers: Invasion:')):
            await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: Invasion:',
                             '🤬 Денацификация / Уничтожить нацистов')
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: First:')
        await bot.send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
    elif "🏢 Это укронацисты стреляют по своим же жителям! Мы же бьем только по военным объектам" in true_options:
        text = await sql_safe_select('text', 'texts', {'name': 'only_war_objects'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(
            types.KeyboardButton(text="Просто ужас. 😨 Давай к следующей теме."))
        nmarkup.row(types.KeyboardButton(text="Но это может быть и провокация, чтобы обвинить Россию 👆"))

        nmarkup.row(
            types.KeyboardButton(text="Просто укронацисты размещаются в домах и делают их легитимной военной целью 😡"))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               parse_mode="HTML", disable_web_page_preview=True)
    elif "👨👩👧👦 Так они используют население как живой щит! Поэтому погибают мирные жители" in true_options:
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: First:')
        text = 'Еще одна заглушка. Блок про живой щит начинается здесь'
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Зачем они вообще сопротивлялись? Мы же им желаем добра!"))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               parse_mode="HTML")
    elif "🏳️ Украинцам надо было просто сдаться, тогда бы стольких жертв не было" in true_options:
        await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
        text = await sql_safe_select('text', 'texts', {'name': 'war_beginning'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(
            types.KeyboardButton(text="Тут другое дело! Мы шли освобождать их от неонацистов, захвативших власть."))
        nmarkup.row(types.KeyboardButton(text="Согласен, я понимаю, почему украинцы начали защищаться."))
        nmarkup.row(types.KeyboardButton(
            text="Не согласен, в случае нападения на Россию пусть лучше солдаты сложат оружие, зато не будет жертв."))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               parse_mode="HTML")
    elif "🎯 Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны" in true_options:
        text = await sql_safe_select('text', 'texts', {'name': 'reasons_here'})
        data = await state.get_data()
        reason_list = data.values()
        reason_text = ''
        for reason in reason_list:
            reason_text = reason_text + '- ' + reason + '\n'
        text = text + '\n\n' + reason_text + '\n\nОбязательно их все обсудим, а пока что вернемся к теме Донбасса'
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: First:')
        await bot.send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
    elif indexes == [0]:
        await bot.send_message(poll_answer.user.id, 'Ну что же, похоже мне не надо вас переубеждать. Пойдем дальше?',
                               reply_markup=filler_kb())
    await state.set_state(donbass_state.after_poll)


# Этот скорее всего никогда не будет использоваться
"""@router.message(option_filter(option = 'Если бы мы не нанесли упреждающий удар,
 то Украина напала бы первая, и жертв было бы больше'))
async def preventive_strike(message: Message, state=FSMContext):
    text = 'У меня есть уточняющий вопрос.\nПродолжите: "Если бы мы не нанесли упреждающий удар,
     то Украина напала бы первая..." Куда?'
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="...на ДНР/ЛНР и Крым"))
    nmarkup.row(types.KeyboardButton(text="...вместе с НАТО на Россию"))
    nmarkup.row(types.KeyboardButton(text="Оба варианта"))
    nmarkup.adjust(2,1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))"""


@router.message((F.text.contains('ДНР/ЛНР') | (F.text.contains('НАТО')) | (F.text.contains('Оба'))))
async def donbas_reason_to_war(message: Message, state=FSMContext):
    reason = str
    if message.text == "...на ДНР/ЛНР и Крым":
        reason = 'Если бы мы не напали первыми, то Украина бы напала на ДНР/ЛНР и Крым'
    if message.text == "...вместе с НАТО на Россию":
        reason = 'Если бы мы не напали первыми, то Украина бы напала вместе с НАТО на Россию'
    if message.text == "Оба варианта":
        reason = 'Если бы мы не напали первыми, то Украина бы напала на ДНР/ЛНР и вместе с НАТО на Россию'
    await state.update_data(war_reasons=reason)
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    text = await sql_safe_select('text', 'texts', {'name': 'reason_to_war'})
    video_id = await sql_safe_select('t_id', 'assets', {'name': 'putin_may'})
    try:
        await message.answer_video(video_id, caption=text, reply_markup=filler_kb())
    except:
        await message.answer_photo(video_id, caption=text, reply_markup=filler_kb())


@router.message(DonbassOptionsFilter(option='📊 ООН врёт, не может быть таких жертв среди мирного населения'),
                (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_OOH(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_OOH'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer(text, reply_markup=filler_kb())


# @router.message(
#     DonbassOptionsFilter(option='Эти "мирные люди" — жители Украины, а значит неонацисты, которых не жалко'),
#     (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
# async def donbas_nazi(message: Message, state=FSMContext):
#     await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
#     if 'Денацификация / Уничтожить нацистов' not in (
#             await poll_get(f'Usrs: {message.from_user.id}: Start_answers: Invasion:')):
#         await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
#                          '🤬 Денацификация / Уничтожить нацистов')
#         print('TEST NAZI')
#     text = await sql_safe_select('text', 'texts', {'name': 'donbas_nazi'})
#     await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
#     await message.answer(text, reply_markup=filler_kb())


@router.message(
    DonbassOptionsFilter(option='🏢 Это украинцы сами стреляют по своим же жителям! Мы же бьем только по военным объектам'),
    (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_only_war_objects(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'only_war_objects'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А кто сказал, что это сделали российские войска? Может, это провокация!"))
    nmarkup.row(types.KeyboardButton(text="Просто укронацисты размещаются в жилых домах или рядом."))
    nmarkup.row(types.KeyboardButton(text="Просто ужас. Давай к следующей теме."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(text_contains=('российские', 'провокация'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def provocation(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'protection'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="[3] Просто укронацисты размещаются в домах и делают их легитимной военной целью 😡"))
    nmarkup.row(types.KeyboardButton(text="Жертвы среди мирного населения - плохо, но все ради важных целей."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML", disable_web_page_preview=True)


@router.message(text_contains=('укронацисты', 'жилых'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def exit_point_one(message: Message, state=FSMContext):
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    answers = await poll_get(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    thing = 'Так они используют население как живой щит! Поэтому погибают мирные жители'
    if thing not in answers:
        await poll_write(f'Usrs: {message.from_user.id}: Donbass_polls: First:', thing)
    await state.update_data(live_shield='Украинская армия использует население, как живой щит!')
    await message.answer('Что же, я услышал ваш ответ.\nДавайте поговорим об этом позже.', reply_markup=filler_kb(),
                         parse_mode="HTML")


@router.message(text_contains=('жертвы', 'плохо', 'важных'), content_types=types.ContentType.TEXT,
                text_ignore_case=True)
async def exit_point_two(message: Message, state=FSMContext):
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    answers = await poll_get(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    thing = "Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны"
    if thing not in answers:
        await poll_write(f'Usrs: {message.from_user.id}: Donbass_polls: First:', thing)
    await state.update_data(big_game='Помимо защиты жителей Донбасса есть более весомые причины для начала войны.')
    await message.answer('Возможно вы правы. Обязательно обсудим все причины\nА пока вернемся к теме Донбасса',
                         reply_markup=filler_kb(), parse_mode="HTML")


@router.message(text_contains=('ужас', 'следующей', 'теме'), content_types=types.ContentType.TEXT,
                text_ignore_case=True)
async def exit_point_zero(message: Message):
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    answers = await poll_get(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    thing = 'Так они используют население как живой щит! Поэтому погибают мирные жители'
    if thing not in answers:
        await poll_write(f'Usrs: {message.from_user.id}: Donbass_polls: First:', thing)
    await message.answer('Полностью разделяю ваши чувства.', reply_markup=filler_kb(), parse_mode="HTML")


@router.message(
    DonbassOptionsFilter(option='👨👩👧👦 Так они используют население, как живой щит! Поэтому погибают мирные жители'),
    (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_live_shield_start(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_live_shield_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Зачем они вообщесопротивлялись? 🤷‍♀️Мы же им желаем мира."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(text_contains=('сопротивлялись', 'добра'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def provocation(message: Message, state=FSMContext):
    await state.update_data(surrender='Украинцам нужно было просто сдаться, тогда не было бы стольких жертв')
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer('Об этом чуть позже, но не волнуйтесь: до всего дойдет свой черед.', reply_markup=filler_kb(),
                         parse_mode="HTML")


@router.message(DonbassOptionsFilter(option='🏳️ Украинцам надо было просто сдаться, тогда бы столько жертв не было'),
                (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_why_not_surrender(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_why_not_surrender'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а), я понимаю, почему украинцы начали защищаться 👌🏼"))
    nmarkup.row(types.KeyboardButton(text="Тут другое дело, мы их освобождаем от неонацистов, захвативших власть на Украине 🙋‍♂️"))
    nmarkup.row(types.KeyboardButton(
        text="Не согласен(а), в случае нападения на Россию лучше сдаться, зато не будет жертв 🕊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message(text_contains=('другое', 'освобождать', 'освобождаем страну'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def donbas_putin_unleashed(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_putin_unleashed'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await state.update_data(neonazi='В Украине процветает неонационализм и геноцид русского населения.')
    await poll_write(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                     "💀 На Украине происходит геноцид русскоязычного населения")
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")


@router.message(text_contains=('на', 'россию', 'сложат'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def donbas_strange_world(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_strange_world'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а), я понимаю, почему украинцы начали защищаться 👌🏼"))
    nmarkup.row(types.KeyboardButton(text="Лучше бы просто никто ни на кого не нападал 🕊"))
    nmarkup.row(types.KeyboardButton(text="Но Россия - не агрессор. Мы не нападаем, а освобождаем страну от неонацизма 🙋‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")

# @router.message(text_contains=('освобождаем страну от неонацизма'), content_types=types.ContentType.TEXT, text_ignore_case=True)
# async def donbas_strange_world(message: Message):
#     await poll_write(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
#                      "💀 На Украине происходит геноцид русскоязычного населения")

@router.message(text_contains=('Лучше', 'никто', 'кого'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def donbas_sentient_bot(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_sentient_bot'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")


@router.message(text_contains=('Согласен', 'понимаю', 'начали'), content_types=types.ContentType.TEXT,
                text_ignore_case=True)
async def donbas_understanding(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_understanding'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")


@router.message(DonbassOptionsFilter(
    option='🎯 Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны'),
    (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_more_reasons(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_more_reasons'})
    data = await state.get_data()
    reason_list = data.values()
    reason_text = ''
    for reason in reason_list:
        reason_text = reason_text + '- ' + reason + '\n'
    text = text + '\n\n' + reason_text + '\n\nОбязательно их все обсудим, а пока что вернемся к теме Донбасса'
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")


@router.message(state=donbass_state.after_poll)
async def donbas_who_do_that(message: Message, state=FSMContext):
    await state.set_state(donbass_state.second_poll)
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_who_do_that'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В подробностях 📜"))
    nmarkup.row(types.KeyboardButton(text=" Покороче ⏱"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == 'В подробностях 📜'))
async def donbas_long_maidan(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_long_maidan'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что случилось дальше? ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == "Что случилось дальше? ⏳"))
async def donbas_can_you_be_normal(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернемся к другим причинам войны 👌🏼"))
    nmarkup.row(types.KeyboardButton(text="Путин просто помогал, которые не хотели жить в Украине после Майдана 🤷"))
    nmarkup.row(
        types.KeyboardButton(text="Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО 🛡"))
    nmarkup.row(types.KeyboardButton(text="Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅"))
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_can_you_be_normal'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.poll_answer(state=donbass_state.second_poll)
async def poll_answer_handler(poll_answer: types.PollAnswer, bot: Bot, state=FSMContext):
    indexes = poll_answer.option_ids
    true_options = list()
    print(indexes)
    for index in indexes:
        if index == 0:
            continue
        true_options.append(donbass_second_poll[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Donbass_polls: Second:', donbass_second_poll[index])
    if 'Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет' in true_options:
        await bot.send_message(poll_answer.user.id,
                               "Вообще-то наши войска были в ДНР и ЛНР, вот доказательства:\n\n"
                               "<i>Доказательства (существуют)</i>", reply_markup=filler_kb())
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: Second:')
    elif 'Путин просто помогал русскоязычному населению,' \
         ' которые не хотели жить в Украине после Майдана' in true_options:
        await bot.send_message(poll_answer.user.id,
                               "Русскоязычное население Украины с удовольствием бы помогло Путину перестать быть\n\n"
                               "<i>Доказательства: (существуют)</i>", reply_markup=filler_kb())
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: Second:')
    elif 'Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО' in true_options:
        await bot.send_message(poll_answer.user.id,
                               "Теперь НАТО впору просить вступить в Украину."
                               " Где доказательства?..\n\n\n\n\nЗдесь: (доказателство) (доказательство)"
                               , reply_markup=filler_kb())
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: Second:')
    elif indexes == [0]:
        await bot.send_message(poll_answer.user.id, 'Ну что же, похоже мне не'
                                                    ' надо вас переубеждать. Пойдем дальше?', reply_markup=filler_kb())
    await state.set_state(donbass_state.after_second_poll)


@router.message(second_donbass_filter(
    option='Путин просто помогал русскоязычному населению, которые не хотели жить в Украине после Майдана'),
    (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_no_army_here(message: Message):
    await message.answer(
        "Русскоязычное население Украины с удовольствием бы помогло Путину перестать быть\n\n"
        "<i>Доказательства: (существуют)</i>",
        reply_markup=filler_kb())
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: Second:')


@router.message(
    second_donbass_filter(option='Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО'),
    (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_no_army_here(message: Message):
    await message.answer(
        "Теперь НАТО впору просить вступить в Украину. Где доказательства?..\n"
        "Здесь:\n\n\n\n (доказателство)\n           *кродется*\n\n(доказательство2)\n *спит*",
        reply_markup=filler_kb())
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: Second:')


@router.message(state=donbass_state.after_second_poll)
async def donbas_no_army_here(message: Message, state=FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Почему бы и нет"))
    # Удаление из списка донбасса
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "👪 Защитить русских в Донбассе")
    await state.set_state(TruereasonsState.main)
    await message.answer(
        "Рад, что мы разобрали все, что связано с Донбассом."
        " Вернемся же к причинам войны.\n"
        "В дальнейшем это сообщение может не понадобиться, но сейчас оно есть.",
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == " Покороче ⏱"))
async def donbas_no_army_here(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'short_separ_text'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернемся к другим причинам войны 👌🏼"))
    nmarkup.row(types.KeyboardButton(text="Путин просто помогал, которые не хотели жить в Украине после Майдана 🤷"))
    nmarkup.row(
        types.KeyboardButton(text="Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО 🛡"))
    nmarkup.row(types.KeyboardButton(text="Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅"))
    # Удаление из списка донбасса

    await message.answer(
        text,
        reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == "Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО 🛡"))
@router.message((F.text == "Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅"))
async def donbas_no_army_here(message: Message, state=FSMContext):
    text1 = "Это возможно. Но о какой защите жителей Донбасса тогда может идти речь. Это просто напросто использование в своих интересах и не стоит в таком случае прикрываться такой благородной целью, как защита русскоязычного населения."
    text2 = "Это неправда. Свидетельств присутствия российских войск очень очень очень много. Я не буду здесь заваливать вас фактами, а просто оставлю ссылку на Википедию. Там хороший раздел, со ссылками и доказательствами."

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай🖱"))

    # Удаление из списка донбасса
    if message.text == "Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅":
        await message.answer(
            text2,
            reply_markup=nmarkup.as_markup(resize_keyboard=True))
    elif message.text == "Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО 🛡":
        await message.answer(
            text1,
            reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == "Продолжай🖱"))
@router.message((F.text == "Вернемся к другим причинам войны 👌🏼"))
@router.message((F.text == "Путин просто помогал, которые не хотели жить в Украине после Майдана 🤷"))
async def donbas_no_army_here(message: Message, state=FSMContext):
    text = "Напоследок, посмотрите на это фото. Оно сделано в Луганске. Замечаете что-то необычное?"
    photo = await sql_safe_select('t_id', 'assets', {'name': 'donbass_no_male'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, замечаю‍♀"))
    nmarkup.row(types.KeyboardButton(text="Нет, не замечаю🤷‍♀"))
    nmarkup.row(types.KeyboardButton(text="Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅"))

    await message.answer_photo(photo=photo,
                               caption=text,
                               reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == "Да, замечаю‍♀"))
@router.message((F.text == "Нет, не замечаю🤷‍♀"))
async def donbas_no_army_here(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'lnr_mobilization'})
    video = await sql_safe_select('t_id', 'assets', {'name': 'lnr_mobilization'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай продолжим👉"))
    nmarkup.row(types.KeyboardButton(text="Какой ужас 😨"))
    nmarkup.row(
        types.KeyboardButton(text="Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО 🛡"))
    nmarkup.row(types.KeyboardButton(text="Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅"))
    # Удаление из списка донбасса

    await message.answer_video(video=video,
                               caption=text,
                               reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")
