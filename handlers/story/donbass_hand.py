from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot_statistics.stat import mongo_update_stat, mongo_update_stat_new
from data_base.DBuse import poll_write, sql_safe_select, poll_get, redis_delete_from_list, mongo_count_docs
from filters.MapFilters import DonbassOptionsFilter
from handlers.story.true_resons_hand import TruereasonsState
from keyboards.main_keys import filler_kb
from resources.all_polls import donbass_first_poll, welc_message_one
from states.donbass_states import donbass_state
from states.true_goals_states import WarGoalsState
from utilts import simple_media, CoolPercReplacer

flags = {"throttling_key": "True"}
router = Router()
router.message.filter(state=donbass_state)
router.poll_answer.filter(state=donbass_state)


async def donbass_big_tragedy(message: Message, state: FSMContext):
    await state.set_state(donbass_state.start)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_big_tragedy'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='Помню ✔️'))
    nmarkup.add(types.KeyboardButton(text='Не помню 🤔️'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(F.text.in_({'Помню ✔️', 'Не помню 🤔️'}), state=donbass_state.start, flags=flags)
async def donbass_chart_1(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='Продолжай ⏳'))
    nmarkup.row(types.KeyboardButton(text='Что значит «гражданские»? 👨‍👩‍👧‍👦'))
    nmarkup.adjust(2, 1)
    await simple_media(message, 'donbass_chart_1', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Что значит')), state=donbass_state.start, flags=flags)
async def eight_years_add(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_years_add'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='Продолжай ⏳'))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == 'Продолжай ⏳'), state=donbass_state.start, flags=flags)
async def donbass_chart_2(message: Message, state: FSMContext):
    await state.set_state(donbass_state.poll)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='Покажи варианты ✍️'))
    await simple_media(message, 'donbass_chart_2', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Покажи варианты ✍️')), state=donbass_state.poll, flags=flags)
async def donbas_args_poll(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_args_poll'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.add(types.KeyboardButton(text='Продолжить'))
    await message.answer_poll(text, donbass_first_poll, is_anonymous=False, allows_multiple_answers=True,
                              reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(donbass_state.poll, (F.text == 'Продолжить'), flags=flags)
async def poll_filler(message: types.Message):
    await message.answer('Чтобы продолжить — отметьте варианты выше и нажмите «ГОЛОСОВАТЬ» или «VOTE»',
                         reply_markup=ReplyKeyboardRemove())


@router.poll_answer(state=donbass_state.poll)
async def donbass_arguments_result(poll_answer: types.PollAnswer, bot: Bot, state: FSMContext):
    await state.set_state(donbass_state.after_poll)
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_arguments_result'})

    answers_indexes = poll_answer.option_ids
    user_answers = list()
    for index in answers_indexes:
        answer = donbass_first_poll[index]
        user_answers.append(answer)
        await poll_write(f'Usrs: {poll_answer.user.id}: Donbas_poll:', answer)
    await mongo_update_stat_new(tg_id=poll_answer.user.id, column='donbass_ex', value=user_answers)

    if answers_indexes == [0]:
        await mongo_update_stat_new(tg_id=poll_answer.user.id, column='donbas_poll_summary',
                                    value='🤝 Согласились без возражений')
    else:
        if 0 in answers_indexes:
            await mongo_update_stat_new(tg_id=poll_answer.user.id, column='donbas_poll_summary',
                                        value='☝️ Согласились, но возразили')
        else:
            await mongo_update_stat_new(tg_id=poll_answer.user.id, column='donbas_poll_summary',
                                        value='🙅‍♂️ Не согласились и возразили')

    sorted_dict = await CoolPercReplacer.make_sorted_statistics_dict('donbass_ex', donbass_first_poll[1:])
    sorted_text = str()
    for item in sorted_dict:
        line = str(sorted_dict[item]) + '%: ' + item + '\n\n'
        sorted_text += line
    text = text.replace('[[LIST]]', sorted_text)

    all_sumary = await mongo_count_docs('database', 'statistics_new', {'donbas_poll_summary': {'$exists': True}})
    agree_sumary = await mongo_count_docs('database', 'statistics_new',
                                          {'donbas_poll_summary': '🤝 Согласились без возражений'})
    agree_but_sumary = await mongo_count_docs('database', 'statistics_new',
                                              {'donbas_poll_summary': '☝️ Согласились, но возразили'})
    not_agree_sumary = await mongo_count_docs('database', 'statistics_new',
                                              {'donbas_poll_summary': '🙅‍♂️ Не согласились и возразили'})
    txt = CoolPercReplacer(text, all_sumary)
    txt.replace('XX', agree_sumary)
    txt.replace('YY', agree_but_sumary)
    txt.replace('ZZ', not_agree_sumary)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Продолжим 👉'))
    await bot.send_message(poll_answer.user.id, txt(),
                           reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(DonbassOptionsFilter(option='ООН врёт, не может быть таких жертв среди мирного населения'),
                (F.text.in_({'Договорились 👌', "Хорошо  👌", "Понятно 👌", "Согласен(а) 👌"})), flags=flags)
async def donbas_OOH(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Donbass_polls: First:', donbass_first_poll[2])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Понятно 👌"))
    await simple_media(message, 'civil_casualties', nmarkup.as_markup(resize_keyboard=True))


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
    DonbassOptionsFilter(
        option="🏢 Это украинцы сами стреляют по своим же жителям! Мы же бьем только по военным объектам"),
    (F.text.in_({'Договорились 👌', "Хорошо  👌", "Понятно 👌", "Согласен(а) 👌"})), flags=flags)
async def donbas_only_war_objects(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Donbass_polls: First:', donbass_first_poll[4])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Просто ужас. 😨 Давай к следующей теме."))
    nmarkup.row(types.KeyboardButton(text="Но это может быть и провокация, чтобы обвинить Россию 👆"))
    nmarkup.row(
        types.KeyboardButton(text="Просто укронацисты размещаются в домах и делают их легитимной военной целью 😡"))
    await simple_media(message, 'only_war_objects', nmarkup.as_markup(resize_keyboard=True))


@router.message(text_contains=('обвинить', 'провокация'), content_types=types.ContentType.TEXT, text_ignore_case=True,
                flags=flags)
async def protection(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'protection'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(
        types.KeyboardButton(text="Просто укронацисты размещаются в домах и делают их легитимной военной целью 😡"))
    nmarkup.row(
        types.KeyboardButton(text="Жертвы среди мирного населения - это плохо, но это все ради важных целей. 🇷🇺"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


@router.message(text_contains=('среди', 'населения', 'важных'), content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)
async def donbas_return_to_donbass(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_return_to_donbass'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо  👌"))
    await poll_write(f'Usrs: {message.from_user.id}: Donbass_polls: First:', donbass_first_poll[7])
    await state.update_data(big_game='Помимо защиты жителей Донбасса есть более весомые причины для начала войны.')
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML")


@router.message(text_contains=('ужас', 'следующей', 'теме'), content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)
async def exit_point_zero(message: Message, state: FSMContext):
    await DonbassManualFilter(message, state)


@router.message(text_contains=('укронацисты', 'легитимной'), content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)
@router.message(
    DonbassOptionsFilter(
        option="👨‍👩‍👧‍👦 Так они используют население, как живой щит! Поэтому погибают мирные жители"),
    (F.text.in_({'Договорились 👌', "Хорошо  👌", "Понятно 👌", "Согласен(а) 👌"})), flags=flags)
async def donbas_live_shield_start(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Donbass_polls: First:', donbass_first_poll[5])
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_live_shield_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а) 👌"))
    nmarkup.row(types.KeyboardButton(text="Зачем они вообще сопротивлялись? 🤷‍♀️Мы же им желаем мира."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(text_contains=('сопротивлялись', 'мира'), content_types=types.ContentType.TEXT, text_ignore_case=True,
                flags=flags)
async def provocation(message: Message, state: FSMContext):
    await state.update_data(surrender="🏳️ Украинцам надо было просто сдаться, тогда бы столько жертв не было")
    await donbas_why_not_surrender(message)


@router.message(DonbassOptionsFilter(option=donbass_first_poll[6]),
                (F.text.in_({'Договорились 👌', "Хорошо  👌", "Понятно 👌", "Согласен(а) 👌"})), flags=flags)
async def donbas_why_not_surrender(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Donbass_polls: First:', donbass_first_poll[6])
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_why_not_surrender'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а), я понимаю, почему украинцы начали защищаться 👌"))
    nmarkup.row(types.KeyboardButton(
        text="Тут другое дело, мы их освобождаем от неонацистов, захвативших власть на Украине 🙋‍♂️"))
    nmarkup.row(types.KeyboardButton(
        text="Не согласен(а), в случае нападения на Россию лучше сдаться, зато не будет жертв 🕊"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


@router.message(text_contains=('освобождаем', 'неонац'), content_types=types.ContentType.TEXT, text_ignore_case=True,
                flags=flags)
async def donbas_putin_unleashed(message: Message, state: FSMContext):
    await state.update_data(neonazi='В Украине процветает неонационализм и геноцид русского населения.')
    await poll_write(f'Usrs: {message.from_user.id}: Nazi_answers: first_poll:',
                     "💀 На Украине происходит геноцид русскоязычного населения")
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо  👌"))
    await simple_media(message, 'donbas_putin_unleashed', nmarkup.as_markup(resize_keyboard=True))


@router.message(text_contains=('случае', 'жертв', 'сдаться'), content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)
async def donbas_strange_world(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_strange_world'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Согласен(а), я понимаю, почему украинцы начали защищаться 👌"))
    nmarkup.row(types.KeyboardButton(text="Лучше бы просто никто ни на кого не нападал 🕊"))
    nmarkup.row(
        types.KeyboardButton(text="Но Россия - не агрессор. Мы не нападаем, а освобождаем страну от неонацизма 🙋‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


@router.message(text_contains=('Лучше', 'никто', 'кого'), content_types=types.ContentType.TEXT, text_ignore_case=True,
                flags=flags)
async def donbas_sentient_bot(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_sentient_bot'})
    await message.answer(text, reply_markup=filler_kb(), parse_mode="HTML", disable_web_page_preview=True)


@router.message(text_contains=('Согласен', 'понимаю', 'начали'), content_types=types.ContentType.TEXT,
                text_ignore_case=True, flags=flags)
async def donbas_understanding(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо  👌"))
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_understanding'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


@router.message(DonbassOptionsFilter(
    option='🎯 Это ужасно, но помимо защиты жителей Донбасса есть более весомые причины для начала войны'),
    (F.text.in_({'Договорились 👌', "Хорошо  👌", "Понятно 👌", "Согласен(а) 👌"})), flags=flags)
async def donbas_more_reasons(message: Message):
    await redis_delete_from_list(f'Usrs: {message.from_user.id}: Donbass_polls: First:', donbass_first_poll[7])
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_more_reasons'})
    reason_list_2 = set(await poll_get(f'Usrs: {message.from_user.id}: Start_answers: Invasion:'))
    reason_text = '\n\n'
    for reason in reason_list_2:
        if reason == welc_message_one[-1]:
            continue
        reason_text = reason_text + reason + '\n'
    text = text.replace('[перечислить списком все выбранные причины]', reason_text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо  👌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


@router.message(state=donbass_state.after_poll, flags=flags)
async def donbas_who_do_that(message: Message, state: FSMContext):
    await state.set_state(donbass_state.second_poll)
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_who_do_that'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="В подробностях 📜"))
    nmarkup.row(types.KeyboardButton(text="Покороче ⏱"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


@router.message((F.text == "Покороче ⏱"), flags=flags)
async def short_separ_text(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'short_separ_text'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернемся к другим причинам войны 👌"))
    nmarkup.row(types.KeyboardButton(text="Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅"))
    nmarkup.row(types.KeyboardButton(
        text="Путин просто помогал жителям Донбасса, которым не понравились результаты Майдана 🤷"))
    nmarkup.row(
        types.KeyboardButton(text="Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО 🛡"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


@router.message((F.text == 'В подробностях 📜'), flags=flags)
async def donbas_long_maidan(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_long_maidan'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что случилось дальше? ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


@router.message((F.text == "Что случилось дальше? ⏳"), flags=flags)
async def donbas_can_you_be_normal(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Вернемся к другим причинам войны 👌"))
    nmarkup.row(types.KeyboardButton(text="Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅"))
    nmarkup.row(types.KeyboardButton(
        text="Путин просто помогал жителям Донбасса, которым не понравились результаты Майдана 🤷"))
    nmarkup.row(
        types.KeyboardButton(text="Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО 🛡"))
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_can_you_be_normal'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), parse_mode="HTML",
                         disable_web_page_preview=True)


"""@router.poll_answer(state=donbass_state.second_poll)
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
"""

"""@router.message(second_donbass_filter(
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
        reply_markup=nmarkup.as_markup(resize_keyboard=True))"""


@router.message((F.text == "Путин помог разжечь этот конфликт, чтобы помешать Украине вступить в НАТО 🛡"), flags=flags)
async def donbas_hypocrisy(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='donbass_end', value='Путин мешал вступить в НАТО')
    text = await sql_safe_select('text', 'texts', {'name': 'donbas_hypocrisy'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text == "Вообще-то, наших войск не было в ДНР/ ЛНР все эти 8 лет 🙅"), flags=flags)
async def donbas_untrue(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='donbass_end', value='Наших не было в ЛДНР')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо 👌"))
    await simple_media(message, 'donbas_untrue', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⏳") | (F.text == 'Хорошо 👌'), flags=flags)
@router.message((F.text == "Вернемся к другим причинам войны 👌"))
@router.message((F.text == "Путин просто помогал жителям Донбасса, которым не понравились результаты Майдана 🤷"))
async def donbas_no_army_here(message: Message):
    if 'Путин' in message.text or 'причинам' in message.text:
        await mongo_update_stat_new(tg_id=message.from_user.id, column='donbass_end', value=message.text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, замечаю  😯"))
    nmarkup.row(types.KeyboardButton(text="Нет, не замечаю🤷‍♀"))
    await simple_media(message, 'donbass_no_male', nmarkup.as_markup(resize_keyboard=True))


async def donbass_mobilization(message: Message):
    await mongo_update_stat(message.from_user.id, 'donbass')
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой ужас 😨"))
    nmarkup.row(types.KeyboardButton(text="Давай продолжим 👉"))
    await simple_media(message, 'donbass_mobilization', reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Скорее да, это лишь предлог 👌") | (F.text == "Скорее нет, это настоящая причина 🙅‍♂️") |
                (F.text == "Затрудняюсь ответить 🤷‍♀️"), flags=flags)
async def donbass_honest_result(message: Message, state: FSMContext):
    await state.set_state(WarGoalsState.main)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    text = await sql_safe_select('text', 'texts', {'name': 'donbass_honest_result'})
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
