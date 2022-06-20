from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from data_base.DBuse import poll_write, sql_safe_select, redis_pop, poll_get, redis_delete_from_list
from filters.All_filters import option_filter, second_donbass_filter
from handlers.true_resons_hand import TruereasonsState
from keyboards.main_keys import filler_kb
from middleware import CounterMiddleware
from resources.all_polls import donbass_first_poll, donbass_second_poll
from states.donbass_states import donbass_state

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


@router.message(F.text == 'Что главное?')
async def donbass_chart_1(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_chart_1'})
    ph_id = await sql_safe_select('t_id', 'assets', {'name': 'donbass_chart_1'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Что значит "гражданские"?'))
    nmarkup.add(types.KeyboardButton(text='Да, знал'))
    nmarkup.add(types.KeyboardButton(text='Нет, не знал'))
    nmarkup.adjust(1, 2)
    try:
        await message.answer_photo(ph_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    except:
        await message.answer_video(ph_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(text_contains=('значит'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def eight_years_add(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_years_add'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='Да, знал'))
    nmarkup.add(types.KeyboardButton(text='Нет, не знал'))
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
    nmarkup.add(types.KeyboardButton(text='Продолжай'))
    await message.reply_poll("Отметьте один или более вариантов, с которыми вы согласны или частично согласны",
                             donbass_first_poll, is_anonymous=False, allows_multiple_answers=True,
                             reply_markup=nmarkup.as_markup())


@router.message(donbass_state.eight_years_selection, (F.text == 'Продолжай'))
async def poll_filler(message: types.Message, bot: Bot):
    await message.answer('Чтобы продолжить -- отметьте ответы выше и нажмите "Проголосовать" или "Vote"', reply_markup=ReplyKeyboardRemove())


# Тут удвоение первого поста каждой ветки, потому что нам надо отвечать СРАЗУ после опроса
@router.poll_answer(state=donbass_state.eight_years_selection)
async def poll_answer_handler(poll_answer: types.PollAnswer, bot: Bot, state=FSMContext):
    indexes = poll_answer.option_ids
    true_options = list()
    print(indexes)
    for index in indexes:
        if index == 0:
            # TODO:перекидывать дальше
            continue
        true_options.append(donbass_first_poll[index])
        await poll_write(f'Usrs: {poll_answer.user.id}: Donbass_polls: First:', donbass_first_poll[index])
    if 'Если бы мы не нанесли упреждающий удар, то Украина напала бы первая, и жертв было бы больше' in true_options:
        text = 'У меня есть уточняющий вопрос.\nПродолжите: "Если бы мы не нанесли упреждающий удар, то Украина напала бы первая..." Куда?'
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="...на ДНР/ЛНР и Крым"))
        nmarkup.row(types.KeyboardButton(text="...вместе с НАТО на Россию"))
        nmarkup.row(types.KeyboardButton(text="Оба варианта"))
        nmarkup.adjust(2, 1)
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
    elif 'ООН врет, не может быть таких жертв среди гражданского населения' in true_options:
        text = await sql_safe_select('text', 'texts', {'name': 'civil_casualties'})
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: First:')
        await bot.send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
    elif 'Эти "мирные люди" — жители Украины, а значит неонацисты, которых не жалко' in true_options:
        await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
        text = 'Считать, что люди заслуживают смерти только потому, что у них есть украинский паспорт — и есть нацизм.\n' \
               'В любом случае этот хэндлер будет готов принять любой сценарий, но пока что перейдите к следующей части.'
        if 'Денацификация / Уничтожить нацистов' not in (
                await poll_get(f'Usrs: {poll_answer.user.id}: Start_answers: Invasion:')):
            await poll_write(f'Usrs: {poll_answer.user.id}: Start_answers: Invasion:',
                             'Денацификация / Уничтожить нацистов')
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: First:')
        await bot.send_message(poll_answer.user.id, text, reply_markup=filler_kb(), parse_mode="HTML")
    elif 'Украинцам надо было просто сдаться, тогда бы стольких жертв не было' in true_options:
        text = await sql_safe_select('text', 'texts', {'name': 'only_war_objects'})
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(
            types.KeyboardButton(text="А кто сказал, что это сделали российские войска? Может, это провокация!"))
        nmarkup.row(types.KeyboardButton(text="Просто укронацисты размещаются в жилых домах или рядом."))
        nmarkup.row(types.KeyboardButton(text="Просто ужас. Давай к следующей теме."))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               parse_mode="HTML")
    elif 'Так они используют население как живой щит! Поэтому погибают мирные жители' in true_options:
        text = 'Еще одна заглушка. Блок про живой щит начинается здесь'
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Зачем они вообще сопротивлялись? Мы же им желаем добра!"))
        await bot.send_message(poll_answer.user.id, text, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               parse_mode="HTML")
    elif 'Украинцам надо было просто сдаться, тогда бы стольких жертв не было' in true_options:
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
    elif 'Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны' in true_options:
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
"""@router.message(option_filter(option = 'Если бы мы не нанесли упреждающий удар, то Украина напала бы первая, и жертв было бы больше'))
async def preventive_strike(message: Message, state=FSMContext):
    text = 'У меня есть уточняющий вопрос.\nПродолжите: "Если бы мы не нанесли упреждающий удар, то Украина напала бы первая..." Куда?'
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

@router.message(option_filter(option='ООН врет, не может быть таких жертв среди гражданского населения'),
                (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_OOH(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_OOH'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer(text, reply_markup=filler_kb())


@router.message(option_filter(option='Эти "мирные люди" — жители Украины, а значит неонацисты, которых не жалко'),
                (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_nazi(message: Message, state=FSMContext):
    await state.update_data(nazi='В Украине процветает неонацизм и геноцид русскоязычного населения')
    if 'Денацификация / Уничтожить нацистов' not in (
    await poll_get(f'Usrs: {message.from_user.id}: Start_answers: Invasion:')):
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                         'Денацификация / Уничтожить нацистов')
        print('TEST NAZI')
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_nazi'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer(text, reply_markup=filler_kb())


@router.message(
    option_filter(option='Это укронацисты стреляют по своим же жителям! Мы же бьем только по военным объектам'),
    (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_only_war_objects(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'only_war_objects'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="А кто сказал, что это сделали российские войска? Может, это провокация!"))
    nmarkup.row(types.KeyboardButton(text="Просто укронацисты размещаются в жилых домах или рядом."))
    nmarkup.row(types.KeyboardButton(text="Просто ужас. Давай к следующей теме."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(text_contains=('российские', 'провокация'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def provocation(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'protection'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Просто укронацисты размещаются в жилых домах или рядом."))
    nmarkup.row(types.KeyboardButton(text="Жертвы среди мирного населения - плохо, но все ради важных целей."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


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
async def exit_point_zero(message: Message, state=FSMContext):
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    answers = await poll_get(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    thing = 'Так они используют население как живой щит! Поэтому погибают мирные жители'
    if thing not in answers:
        await poll_write(f'Usrs: {message.from_user.id}: Donbass_polls: First:', thing)
    await message.answer('Полностью разделяю ваши чувства.', reply_markup=filler_kb(), parse_mode="HTML")


@router.message(option_filter(option='Так они используют население как живой щит! Поэтому погибают мирные жители'),
                (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_live_shield_start(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_live_shield_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Зачем они вообще сопротивлялись? Мы же им желаем добра!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(text_contains=('сопротивлялись', 'добра'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def provocation(message: Message, state=FSMContext):
    await state.update_data(surrender='Украинцам нужно было просто сдаться, тогда не было бы стольких жертв')
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer('Об этом чуть позже, но не волнуйтесь: до всего дойдет свой черед.', reply_markup=filler_kb(),
                         parse_mode="HTML")


@router.message(option_filter(option='Украинцам надо было просто сдаться, тогда бы стольких жертв не было'),
                (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_why_not_surrender(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_why_not_surrender'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Тут другое дело! Мы шли освобождать их от неонацистов, захвативших власть."))
    nmarkup.row(types.KeyboardButton(text="Согласен, я понимаю, почему украинцы начали защищаться."))
    nmarkup.row(types.KeyboardButton(
        text="Не согласен, в случае нападения на Россию пусть лучше солдаты сложат оружие, зато не будет жертв."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message(text_contains=('другое', 'освобождать'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def donbas_putin_unleashed(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_putin_unleashed'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await state.update_data(neonazi='В Украине процветает неонационализм и геноцид русского населения.')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")


@router.message(text_contains=('на', 'россию', 'сложат'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def donbas_strange_world(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_strange_world'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен, я понимаю, почему украинцы начали защищаться."))
    nmarkup.row(types.KeyboardButton(text="Лучше бы никто ни на кого не нападал."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message(text_contains=('Лучше', 'никто', 'кого'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def donbas_sentient_bot(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_sentient_bot'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")


@router.message(text_contains=('Согласен', 'понимаю', 'начали'), content_types=types.ContentType.TEXT,
                text_ignore_case=True)
async def donbas_understanding(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_understanding'})
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: First:')
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML")


@router.message(
    option_filter(option='Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны'),
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
    nmarkup.row(types.KeyboardButton(text="В подробностях"))
    nmarkup.row(types.KeyboardButton(text="Покороче"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == 'В подробностях'))
async def donbas_long_maidan(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_long_maidan'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что случилось дальше?"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message((F.text == "Что случилось дальше?"))
async def donbas_can_you_be_normal(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_can_you_be_normal'})
    await message.answer(text, parse_mode="HTML")
    await message.reply_poll('Вернемся к текущим событиями, или у вас есть что сказать по этой теме?',
                             donbass_second_poll, is_anonymous=False, allows_multiple_answers=True)


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
                               "Вообще-то наши войска были в ДНР и ЛНР, вот доказательства:\n\n<i>Доказательства (существуют)</i>",
                               reply_markup=filler_kb())
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: Second:')
    elif 'Путин просто помогал русскоязычному населению, которые не хотели жить в Украине после Майдана' in true_options:
        await bot.send_message(poll_answer.user.id,
                               "Русскоязычное население Украины с удовольствием бы помогло Путину перестать быть\n\n<i>Доказательства: (существуют)</i>",
                               reply_markup=filler_kb())
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: Second:')
    elif 'Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО' in true_options:
        await bot.send_message(poll_answer.user.id,
                               "Теперь НАТО впору просить вступить в Украину. Где доказательства?..\n\n\n\n\nЗдесь: (доказателство) (доказательство)",
                               reply_markup=filler_kb())
        await redis_pop(f'Usrs: {poll_answer.user.id}: Donbass_polls: Second:')
    elif indexes == [0]:
        await bot.send_message(poll_answer.user.id, 'Ну что же, похоже мне не надо вас переубеждать. Пойдем дальше?',
                               reply_markup=filler_kb())
    await state.set_state(donbass_state.after_second_poll)


@router.message(second_donbass_filter(
    option='Путин просто помогал русскоязычному населению, которые не хотели жить в Украине после Майдана'),
    (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_no_army_here(message: Message, state=FSMContext):
    await message.answer(
        "Русскоязычное население Украины с удовольствием бы помогло Путину перестать быть\n\n<i>Доказательства: (существуют)</i>",
        reply_markup=filler_kb())
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: Second:')


@router.message(
    second_donbass_filter(option='Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО'),
    (F.text.in_({'Договорились', "Хорошо", "Понятно"})))
async def donbas_no_army_here(message: Message, state=FSMContext):
    await message.answer(
        "Теперь НАТО впору просить вступить в Украину. Где доказательства?..\nЗдесь:\n\n\n\n (доказателство)\n           *кродется*\n\n(доказательство2)\n *спит*",
        reply_markup=filler_kb())
    await redis_pop(f'Usrs: {message.from_user.id}: Donbass_polls: Second:')


@router.message(state=donbass_state.after_second_poll)
async def donbas_no_army_here(message: Message, state=FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Почему бы и нет"))
    # Удаление из списка донбасса
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Start_answers: Invasion:',
                                 "Защитить русских в Донбассе")
    await state.set_state(TruereasonsState.main)
    await message.answer(
        "Рад, что мы разобрали все, что связано с Донбассом. Вернемся же к причинам войны.\nВ дальнейшем это сообщение может не понадобиться, но сейчас оно есть.",
        reply_markup=nmarkup.as_markup(resize_keyboard=True))
