from aiogram import Router, F
from aiogram import types
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import poll_write, sql_safe_select, redis_just_one_write, \
    poll_get, redis_just_one_read
from states.welcome_states import start_dialog
from utilts import simple_media

flags = {"throttling_key": "True"}
router = Router()

router.message.filter(state=start_dialog.big_story)


@router.message((F.text.contains('верить') | F.text.contains('50 000')), flags=flags)  # А с чего мне тебе верить?
async def start_why_belive(message: types.Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='first_button', value='А с чего мне тебе верить?')
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Начнём 🇷🇺🇺🇦"))
    text = await sql_safe_select("text", "texts", {"name": "start_why_belive"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message((F.text.contains('Начнём 🇷🇺🇺🇦')), flags=flags)
async def start_is_war_bad(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_is_war_bad'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Какой феномен? 🤔"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Какой феномен? 🤔'), flags=flags)
async def start_disgusting(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_disgusting'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжай  ⏳"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжай  ⏳'), flags=flags)
async def start_what_is_moral(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_what_is_moral'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Давай 👌'), flags=flags)
async def start_trolley_1(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжу ехать прямо ⬆️"))
    nmarkap.add(types.KeyboardButton(text="Сверну направо ➡️"))
    await simple_media(message, 'start_trolley_1', nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Продолжу ехать прямо ⬆️", "Сверну направо ➡️"})), flags=flags)
async def start_trolley_1_result(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_trolley_1_result',
                                value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'start_trolley_1_result'})

    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        count_right = await collection.count_documents({'start_trolley_1_result': 'Сверну направо ➡️'})
        count_straight = await collection.count_documents({'start_trolley_1_result': 'Продолжу ехать прямо ⬆️'})
        all_people = count_straight + count_right
        text = text.replace('XX', f"{(round(count_straight/all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(count_right/all_people * 100, 1) if all_people > 0 else 'N/A')}")
    except:
        text = text.replace('XX', 'N/A')
        text = text.replace('YY', 'N/A')

    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжай 🤔"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай 🤔"), flags=flags)
async def start_trolley_2(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Ничего не буду делать 🙅‍♂️"))
    nmarkap.add(types.KeyboardButton(text="Столкну толстяка с моста ⬇️"))
    await simple_media(message, 'start_trolley_2', nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Ничего не буду делать 🙅‍♂️", "Столкну толстяка с моста ⬇️"})), flags=flags)
async def start_trolley_2_result(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_trolley_2_result',
                                value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'start_trolley_2_result'})

    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        passive = await collection.count_documents({'start_trolley_2_result': 'Ничего не буду делать 🙅‍♂️'})
        active = await collection.count_documents({'start_trolley_2_result': 'Столкну толстяка с моста ⬇️'})
        ZZ = await collection.count_documents({'$and': [{'start_trolley_2_result': 'Столкну толстяка с моста ⬇️'},
                                                        {'start_trolley_1_result': 'Сверну направо ➡️'}]})

        all_people = passive + active
        text = text.replace('XX', f"{(round(passive/all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(active/all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(ZZ/all_people * 100, 1) if all_people > 0 else 'N/A')}")
    except:
        text = text.replace('XX', 'N/A')
        text = text.replace('YY', 'N/A')

    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="В отличии от рабочего на путях, толстяк не замешан в этой ситуации 🤔"))
    nmarkap.row(types.KeyboardButton(text="Во втором случае мы лишь наблюдаем, а не участвуем — это другое 👀"))
    nmarkap.row(types.KeyboardButton(text="Убивать своими руками — это совсем другое ☝️"))
    nmarkap.row(types.KeyboardButton(text="Я не знаю / Другая причина 🤷‍♀️"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.contains('другое')) | (F.text.contains('Другая причина')) |
                (F.text.contains('толстяк не замешан')), flags=flags)
async def start_trolley_2_result_answers(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_are_you_ready',
                                value=message.text)
    text = None
    if 'толстяк не замешан' in message.text:
        text = await sql_safe_select('text', 'texts', {'name': 'start_worker_is_guilty'})
    elif 'мы лишь наблюдаем' in message.text:
        text = await sql_safe_select('text', 'texts', {'name': 'start_fatty_in_trolley'})
    elif 'это совсем другое' in message.text:
        text = await sql_safe_select('text', 'texts', {'name': 'start_fatty_to_trap'})
    if text:
        await message.answer(text, disable_web_page_preview=True)
    text = await sql_safe_select('text', 'texts', {'name': 'start_are_you_ready'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Дай ссылку на лекцию про моральную сторону убийства 🔫"))
    nmarkap.row(types.KeyboardButton(text="Продолжим 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Дай ссылку на лекцию про моральную сторону убийства 🔫"), flags=flags)
async def start_good_lecture(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжим 👌"))
    await simple_media(message, 'start_good_lecture', nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжим 👌'), flags=flags)
async def start_they_show_bad_things(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_they_show_bad_things'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжай ⏳'), flags=flags)
async def start_hard_questions(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_hard_questions'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="О чём? 🤔"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'О чём? 🤔'), flags=flags)
async def start_red_pill(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_red_pill'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Давай продолжим 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Давай продолжим 👌'), flags=flags)
async def start_dumb_dam(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_dumb_dam'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Ничего не  буду делать  🙅‍♂️"))
    nmarkap.add(types.KeyboardButton(text="Взорву дамбу 💥"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message(F.text.in_({"Ничего не  буду делать  🙅‍♂️", "Взорву дамбу 💥"}), flags=flags)
async def start_dam_results(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_dam_results',
                                value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'start_dam_results'})

    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        passive = await collection.count_documents({'start_dam_results': 'Ничего не  буду делать  🙅‍♂️'})
        active = await collection.count_documents({'start_dam_results': 'Взорву дамбу 💥'})
        all_people = passive + active
        text = text.replace('XX', f"{(round(passive/all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(active/all_people * 100, 1) if all_people > 0 else 'N/A')}")
    except Exception as e:
        print(e)
        text = text.replace('XX', 'N/A')
        text = text.replace('YY', 'N/A')

    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Задавай вопросы 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Задавай вопросы 👌"), flags=flags)
async def start_continue_or_peace(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_continue_or_peace'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжать военную операцию ⚔️"))
    nmarkap.row(types.KeyboardButton(text="Переходить к мирным переговорам 🕊"))
    nmarkap.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀️"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Продолжать военную операцию ⚔️", "Переходить к мирным переговорам 🕊",
                             "Затрудняюсь ответить 🤷‍♀️"})), flags=flags)
async def start_continue_or_peace_results(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_continue_or_peace_results',
                                value=message.text)
    if "Продолжать военную операцию ⚔️" in message.text:
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitList:', message.text)
    elif "Переходить к мирным переговорам 🕊" in message.text:
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitList:', message.text)
    elif "Затрудняюсь ответить 🤷‍♀️" in message.text:
        await poll_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitList:', message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'start_continue_or_peace_results'})
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        war = await collection.count_documents({'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️'})
        stop_war = await collection.count_documents(
            {'start_continue_or_peace_results': 'Переходить к мирным переговорам 🕊'})
        hz = await collection.count_documents({'start_continue_or_peace_results': 'Затрудняюсь ответить 🤷‍♀️'})
        all_people = war + stop_war + hz
        text = text.replace('XX', f"{(round(war / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(stop_war / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('ZZ', f"{(round(hz / all_people * 100, 1) if all_people > 0 else 'N/A')}")
    except:
        text = text.replace('XX', 'N/A')
        text = text.replace('YY', 'N/A')
        text = text.replace('ZZ', 'N/A')


    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Задавай 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Задавай 👌"), flags=flags)
async def start_now_you_putin(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_now_you_putin'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Начну военную операцию ⚔️"))
    nmarkap.row(types.KeyboardButton(text="Не стану этого делать 🙅‍♂️"))
    nmarkap.row(types.KeyboardButton(text="Затрудняюсь  ответить  🤷‍♀️"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Начну военную операцию ⚔️", "Не стану этого делать 🙅‍♂️",
                             "Затрудняюсь  ответить  🤷‍♀️"})), flags=flags)
async def start_continue_or_peace_results(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_now_you_putin_results',
                                value=message.text)
    user_answers = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: NewPolitList:')
    user_answers.append(message.text)
    if "Начну военную операцию ⚔️" in user_answers and "Продолжать военную операцию ⚔️" in user_answers:
        await redis_just_one_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:',
                                   'Сторонник спецоперации')
    elif "Переходить к мирным переговорам 🕊" in user_answers and "Не стану этого делать 🙅‍♂️" in user_answers:
        await redis_just_one_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:', 'Противник войны')
    else:
        await redis_just_one_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:', 'Сомневающийся')
    text = await sql_safe_select('text', 'texts', {'name': 'start_now_you_putin_results'})

    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        war = await collection.count_documents({'start_now_you_putin_results': 'Начну военную операцию ⚔️'})
        stop_war = await collection.count_documents({'start_now_you_putin_results': 'Не стану этого делать 🙅‍♂️'})
        hz = await collection.count_documents({'start_now_you_putin_results': 'Затрудняюсь  ответить  🤷‍♀️'})
        all_people = war + stop_war + hz
        text = text.replace('XX', f"{(round(war / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(stop_war / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('ZZ', f"{(round(hz / all_people * 100, 1) if all_people > 0 else 'N/A')}")
    except:
        text = text.replace('XX', 'N/A')
        text = text.replace('YY', 'N/A')
        text = text.replace('ZZ', 'N/A')
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Давай посмотрим 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Давай посмотрим 👌"), flags=flags)
async def start_donbas_chart(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Знал(а) ✅"))
    nmarkap.add(types.KeyboardButton(text="Не знал(а) ❌"))
    nmarkap.row(types.KeyboardButton(text="Докажи 🤔"))
    await simple_media(message, 'start_donbas_chart', nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Докажи 🤔"), flags=flags)
async def start_donbas_OOH(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_donbas_OOH'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжим  👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Знал(а) ✅") | (F.text == "Не знал(а) ❌") | (F.text == "Продолжим  👌"), flags=flags)
async def start_donbas_results(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_donbas_results',
                                value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'start_donbas_results'})

    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        knew = await collection.count_documents({'start_donbas_results': 'Знал(а) ✅'})
        dont_knew = await collection.count_documents({'start_donbas_results': 'Не знал(а) ❌'})
        all_people = knew + dont_knew
        text = text.replace('XX', f"{(round(knew / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(dont_knew / all_people * 100, 1) if all_people > 0 else 'N/A')}")
    except Exception as e:
        print(e)
        text = text.replace('XX', 'N/A')
        text = text.replace('YY', 'N/A')
    await redis_just_one_write(f'Usrs: {message.from_user.id}: StartDonbas:', message.text)
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжай ⌛️"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Продолжай ⌛️"), flags=flags)
async def start_donbas_putin(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Покажи 🤔"))
    await simple_media(message, 'start_donbas_putin', nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Покажи 🤔"), flags=flags)
async def start_many_numbers(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_many_numbers'})
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        knew_war = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Знал(а) ✅'},
            {'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️️'}]})
        knew_dont_war = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Знал(а) ✅'},
            {'start_continue_or_peace_results': 'Переходить к мирным переговорам 🕊'}]})
        knew_hx = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Знал(а) ✅'},
            {'start_continue_or_peace_results': 'Затрудняюсь ответить 🤷‍♀️'}]})
        dont_knew_war = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Не знал(а) ❌'},
            {'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️️'}]})
        dont_knew_dont_war = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Не знал(а) ❌'},
            {'start_continue_or_peace_results': 'Переходить к мирным переговорам 🕊'}]})
        dont_knew_hr = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Не знал(а) ❌'},
            {'start_continue_or_peace_results': 'Затрудняюсь ответить 🤷‍♀️'}]})
        all_people = knew_war + knew_dont_war + knew_hx + dont_knew_war + dont_knew_dont_war + dont_knew_hr
        print(all_people)
        AA = float(knew_war / all_people * 100)
        DD = float(dont_knew_war / all_people * 100)
        XX = DD - AA

        text = text.replace('AA', f"{(round(AA) if all_people > 0 else 'N/A')}")
        text = text.replace('BB', f"{(round(knew_dont_war / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('CC', f"{(round(knew_hx / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('DD', f"{(round(DD) if all_people > 0 else 'N/A')}")
        text = text.replace('EE', f"{(round(dont_knew_dont_war / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('FF', f"{(round(dont_knew_hr / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('XX', f"{(round(XX) if all_people > 0 else 'N/A')}")
    except Exception as e:
        print(e)
        text = text.replace('AA', 'N/A')
        text = text.replace('BB', 'N/A')
        text = text.replace('CC', 'N/A')
        text = text.replace('DD', 'N/A')
        text = text.replace('EE', 'N/A')
        text = text.replace('FF', 'N/A')
        text = text.replace('XX', 'N/A')
    await message.answer(text, disable_web_page_preview=True)
    nmarkap = ReplyKeyboardBuilder()
    if (await redis_just_one_read(f'Usrs: {message.from_user.id}: StartDonbas:')) == "Знал(а) ✅" or (
            await redis_just_one_read(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:')) ==\
            'Противник войны':
        await start_remember_money(message)
    else:
        text = await sql_safe_select('text', 'texts', {'name': 'start_how_are_you'})
        nmarkap.row(types.KeyboardButton(text="Интересно, продолжаем 👌"))
        nmarkap.row(types.KeyboardButton(text="Хорошо, но интересно, с какой целью ты это делаешь? 🤔"))
        nmarkap.row(types.KeyboardButton(text="Звучит однобоко — ты не учитываешь другие факторы ☝️"))
        nmarkap.row(types.KeyboardButton(text="Не надо лезть ко мне в голову, давай к следующим темам. 👉"))
        await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Интересно, продолжаем 👌"), flags=flags)
async def start_good(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_good'})
    await message.answer(text, disable_web_page_preview=True)
    await start_remember_money(message)


@router.message((F.text == "Хорошо, но интересно, с какой целью ты это делаешь? 🤔"), flags=flags)
async def start_everybody_lies(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_everybody_lies'})
    await message.answer(text, disable_web_page_preview=True)
    await start_remember_money(message)


@router.message((F.text == "Звучит однобоко — ты не учитываешь другие факторы ☝️"), flags=flags)
async def start_harder_than_dum(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_harder_than_dum'})
    await message.answer(text, disable_web_page_preview=True)
    await start_remember_money(message)


@router.message((F.text == "Не надо лезть ко мне в голову, давай к следующим темам. 👉"), flags=flags)
async def start_why_so_agressive(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_why_so_agressive'})
    await message.answer(text, disable_web_page_preview=True)
    await start_remember_money(message)


async def start_remember_money(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_remember_money'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Помню ✔️"))
    nmarkap.add(types.KeyboardButton(text="Не помню 🤔️"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Помню ✔️", "Не помню 🤔️"})), flags=flags)
async def start_let_them_rates(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_let_them_rates'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Полезный совет 👍"))
    nmarkap.add(types.KeyboardButton(text="Уже так делаю 👌"))
    nmarkap.row(types.KeyboardButton(text="К чему это? 🤷‍♂️"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Полезный совет 👍", "Уже так делаю 👌", "К чему это? 🤷‍♂️"})), flags=flags)
async def start_I_will_rates(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_I_will_rates'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Давай  👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Давай  👌"), flags=flags)
async def start_donbas_results(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_how_to_manipulate'})
    await redis_just_one_write(f'Usrs: {message.from_user.id}: StartDonbas:', message.text)
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Готов(а) продолжить 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))
