from aiogram import Router, F, Bot
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bata import all_data
from bot_statistics.stat import mongo_update_stat_new
from data_base.DBuse import poll_write, sql_safe_select, redis_just_one_write, \
    poll_get, redis_just_one_read, mongo_count_docs
from log.logg import get_logger
from states.welcome_states import start_dialog
from utilts import simple_media, ref_spy_sender, CoolPercReplacer

flags = {"throttling_key": "True"}
router = Router()

router.message.filter(state=start_dialog)
logger = get_logger('welcome_stories')


@router.message((F.text.contains('верить') | F.text.contains('50 000')), flags=flags)  # А с чего мне тебе верить?
async def start_why_belive(message: types.Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='first_button', value='А с чего мне тебе верить?')
    markup = ReplyKeyboardBuilder()
    markup.add(types.KeyboardButton(text="Начнём 🇷🇺🇺🇦"))
    text = await sql_safe_select("text", "texts", {"name": "start_why_belive"})
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message((F.text.contains("Начнём 🇷🇺🇺🇦")), flags=flags)
async def start_why_communicate(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_why_communicate'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Хочу узнать правду о кофликте России и Украины 🇷🇺🇺🇦"))
    nmarkap.row(types.KeyboardButton(text="Хочу получить советы по поводу мобилизации 🪖"))
    nmarkap.row(types.KeyboardButton(text="Да просто знакомые уговорили пообщаться 🤷‍♂️"))
    nmarkap.row(types.KeyboardButton(text="Другое 🤔"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))

@router.message((F.text.contains("Хочу узнать правду")), flags=flags)
async def start_info_first(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_info_first'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Хорошо 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))

@router.message((F.text.contains("Хочу получить советы")), flags=flags)
async def start_info_second(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_info_second'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Хорошо 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))

@router.message((F.text.contains("уговорили пообщаться")), flags=flags)
async def start_info_third(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_info_third'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Хорошо 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))

@router.message((F.text.contains("Другое 🤔")), flags=flags)
async def start_info_fourth(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_info_fourth'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Хорошо 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))

@router.message((F.text.contains("Хорошо 👌")), flags=flags)
async def start_info_fourth(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="На частичную мобилизацию 🧍‍♂️"))
    nmarkap.row(types.KeyboardButton(text="На общую мобилизацию 🧍‍♂️🧍‍♂️🧍‍♂️"))
    nmarkap.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀️"))
    await simple_media(message, 'start_putin_mobilization', reply_markup=nmarkap.as_markup(resize_keyboard=True))

@router.message((F.text.in_({"На частичную мобилизацию 🧍‍♂️", "На общую мобилизацию 🧍‍♂️🧍‍♂️🧍‍♂️",
                             "Затрудняюсь ответить 🤷‍♀️"})), flags=flags)
async def start_mobilisation_result(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='goals_mobilisation', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'start_mobilisation_result'})

    m_all = await mongo_count_docs('database', 'statistics_new', {'goals_mobilisation': {'$exists': True}})
    m_part = await mongo_count_docs('database', 'statistics_new',
                                    {'goals_mobilisation': "На частичную мобилизацию 🧍‍♂️"})
    m_full = await mongo_count_docs('database', 'statistics_new',
                                    {'goals_mobilisation': "На общую мобилизацию 🧍‍♂️🧍‍♂️🧍‍♂️"})
    a_idk = await mongo_count_docs('database', 'statistics_new', {'goals_mobilisation': "Затрудняюсь ответить 🤷‍♀️"})

    txt = CoolPercReplacer(text, m_all)
    txt.replace("AA", m_part)
    txt.replace("BB", m_full)
    txt.replace("CC", a_idk)

    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжим 👌"))
    await state.set_state(start_dialog.button_next_1)
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)

@router.message((F.text.contains("Продолжим 👌")), state=start_dialog.button_next_1,  flags=flags)
async def start_shoigu_loss(message: Message, state: FSMContext):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Да, доверяю 👍"))
    nmarkap.row(types.KeyboardButton(text="Думаю погибло больше ☹️"))
    nmarkap.row(types.KeyboardButton(text="Затрудняюсь ответить 🤷‍♀️"))
    await state.set_state(start_dialog.big_story)
    await simple_media(message, 'start_shoigu_loss', reply_markup=nmarkap.as_markup(resize_keyboard=True))

@router.message((F.text.in_({"Да, доверяю 👍", "Думаю погибло больше ☹️",
                             "Затрудняюсь ответить 🤷‍♀️"})), flags=flags)
async def start_result_loss(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_result_loss', value=message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'start_result_loss'})

    m_all = await mongo_count_docs('database', 'statistics_new', {'start_result_loss': {'$exists': True}})
    m_part = await mongo_count_docs('database', 'statistics_new', {'start_result_loss': "Да, доверяю 👍"})
    m_full = await mongo_count_docs('database', 'statistics_new', {'start_result_loss': "Думаю погибло больше ☹️"})
    a_idk = await mongo_count_docs('database', 'statistics_new', {'start_result_loss': "Затрудняюсь ответить 🤷‍♀️"})

    txt = CoolPercReplacer(text, m_all)
    txt.replace("AA", m_part)
    txt.replace("BB", m_full)
    txt.replace("CC", a_idk)
    await state.set_state(start_dialog.button_next_2)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай 👌"))
    nmarkup.row(types.KeyboardButton(text="Что такое пропаганда? 🤔"))
    await message.answer(txt(), reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(start_dialog.button_next_2, (F.text.contains('такое пропаганда')), flags=flags)
async def start_what_is_prop(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_what_is_prop'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Давай 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message(start_dialog.button_next_2, (F.text.contains('Давай 👌')), flags=flags)
async def start_is_war_bad(message: Message, state: FSMContext):
    await state.set_state(start_dialog.big_story)
    text = await sql_safe_select('text', 'texts', {'name': 'start_is_war_bad'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Какой феномен? 🤔"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Какой феномен? 🤔'), flags=flags)
async def start_disgusting(message: Message):
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжай  ⏳"))
    await simple_media(message, 'start_disgusting', reply_markup=nmarkap.as_markup(resize_keyboard=True))


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
        count_right = await collection.count_documents({'start_trolley_1_result': "Сверну направо ➡️"})
        count_straight = await collection.count_documents({'start_trolley_1_result': 'Продолжу ехать прямо ⬆️'})
        all_people = count_straight + count_right
        text = text.replace('XX', f"{(round(count_straight / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(count_right / all_people * 100, 1) if all_people > 0 else 'N/A')}")
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
    if message.text == "Ничего не буду делать 🙅‍♂️" and \
            await mongo_count_docs('database', 'statistics_new',
                                   {'_id': message.from_user.id, 'start_trolley_1_result': "Сверну направо ➡️"}):
        text_tag = 'start_trolley_2_result'
    else:
        text_tag = 'start_trolley_2_peace_result'
    text = await sql_safe_select('text', 'texts', {'name': text_tag})

    fat_all = await mongo_count_docs('database', 'statistics_new', {'start_trolley_2_result': {'$exists': True}})
    fat_not = await mongo_count_docs('database', 'statistics_new',
                                     {'start_trolley_2_result': "Ничего не буду делать 🙅‍♂️"})
    fat_kill = await mongo_count_docs('database', 'statistics_new',
                                      {'start_trolley_2_result': "Столкну толстяка с моста ⬇️"})
    right_turn = await mongo_count_docs('database', 'statistics_new',
                                        {'start_trolley_1_result': "Сверну направо ➡️"})
    txt = CoolPercReplacer(text, fat_all)
    txt.replace('XX', fat_not)
    txt.replace('YY', fat_kill)
    txt.replace('ZZ', right_turn - fat_kill)
    nmarkap = ReplyKeyboardBuilder()
    if text_tag != 'start_trolley_2_peace_result':
        nmarkap.row(types.KeyboardButton(text="В отличии от рабочего на путях, толстяк не замешан в этой ситуации 🤔"))
        nmarkap.row(types.KeyboardButton(text="Во втором случае мы лишь наблюдаем, а не участвуем — это другое 👀"))
        nmarkap.row(types.KeyboardButton(text="Убивать своими руками — это совсем другое ☝️"))
        nmarkap.row(types.KeyboardButton(text="Я не знаю / Другая причина 🤷‍♀️"))
    await message.answer(txt(), disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))
    if text_tag == 'start_trolley_2_peace_result':
        await start_are_you_ready(message)


@router.message((F.text.contains('другое')) | (F.text.contains('Другая причина')) |
                (F.text.contains('толстяк не замешан')), flags=flags)
async def start_trolley_2_result_answers(message: Message):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_are_you_ready',
                                value=message.text)
    text = None
    if 'толстяк не замешан' in message.text:
        text = await sql_safe_select('text', 'texts', {'name': 'start_worker_is_guilty'})
    elif 'не участвуем' in message.text:
        text = await sql_safe_select('text', 'texts', {'name': 'start_fatty_in_trolley'})
    elif 'это совсем другое' in message.text:
        text = await sql_safe_select('text', 'texts', {'name': 'start_fatty_to_trap'})
    if text:
        await message.answer(text, disable_web_page_preview=True)
    await start_are_you_ready(message)


async def start_are_you_ready(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_are_you_ready'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Продолжим 👌"))
    nmarkap.row(types.KeyboardButton(text="Дай ссылку на лекцию про моральную сторону убийства 🛤"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Дай ссылку на лекцию про моральную сторону убийства 🛤"), flags=flags)
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
    nmarkap.row(types.KeyboardButton(text="Я понимаю, готов(а) продолжить 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == 'Я понимаю, готов(а) продолжить 👌'), flags=flags)
async def start_key_questions(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_key_questions'})
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
async def start_continue_or_peace_results(message: Message, state: FSMContext):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_continue_or_peace_results',
                                value=message.text)
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitList:', message.text)
    text = await sql_safe_select('text', 'texts', {'name': 'start_continue_or_peace_results'})
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        war = await collection.count_documents({'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️'})
        stop_war = await collection.count_documents(
            {'start_continue_or_peace_results': 'Переходить к мирным переговорам 🕊'})
        dont_know = await collection.count_documents({'start_continue_or_peace_results': 'Затрудняюсь ответить 🤷‍♀️'})
        all_people = war + stop_war + dont_know
        text = text.replace('XX', f"{(round(war / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('YY', f"{(round(stop_war / all_people * 100, 1) if all_people > 0 else 'N/A')}")
        text = text.replace('ZZ', f"{(round(dont_know / all_people * 100, 1) if all_people > 0 else 'N/A')}")
    except:
        text = text.replace('XX', 'N/A')
        text = text.replace('YY', 'N/A')
        text = text.replace('ZZ', 'N/A')
    await state.set_state(start_dialog.ask_1)
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Задавай 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message(start_dialog.ask_1, (F.text == "Задавай 👌"), flags=flags)
async def start_now_you_putin(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_now_you_putin'})
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Начну военную операцию ⚔️"))
    nmarkap.row(types.KeyboardButton(text="Не стану этого делать 🕊"))
    nmarkap.row(types.KeyboardButton(text="Затрудняюсь  ответить  🤷‍♀️"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Начну военную операцию ⚔️", "Не стану этого делать 🕊",
                             "Затрудняюсь  ответить  🤷‍♀️"})), flags=flags)
async def start_now_you_putin_results(message: Message, bot: Bot):
    await mongo_update_stat_new(tg_id=message.from_user.id, column='start_now_you_putin_results',
                                value=message.text)
    await poll_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitList:', message.text)
    user_answers = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: NewPolitList:')
    if "Начну военную операцию ⚔️" in user_answers and "Продолжать военную операцию ⚔️" in user_answers:
        status = 'Сторонник спецоперации ⚔️'
        await redis_just_one_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:',
                                   'Сторонник спецоперации ⚔️')
        await mongo_update_stat_new(tg_id=message.from_user.id, column='NewPolitStat_start',
                                    value='Сторонник спецоперации')
    elif "Переходить к мирным переговорам 🕊" in user_answers and "Не стану этого делать 🕊" in user_answers:
        status = 'Противник войны 🕊'
        await redis_just_one_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:', 'Противник войны 🕊')
        await mongo_update_stat_new(tg_id=message.from_user.id, column='NewPolitStat_start', value='Противник войны')
    else:
        status = 'Сомневающийся 🤷'
        await redis_just_one_write(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:', 'Сомневающийся 🤷')
        await mongo_update_stat_new(tg_id=message.from_user.id, column='NewPolitStat_start', value='Сомневающийся')

    if await redis_just_one_read(f'Usrs: {message.from_user.id}: Ref'):
        parent_text = await sql_safe_select('text', 'texts', {'name': 'ref_start_polit'})
        await ref_spy_sender(bot, message.from_user.id, parent_text,
                             {'[first_q]': user_answers[0], '[second_q]': user_answers[1], '[polit_status]': status})

    text = await sql_safe_select('text', 'texts', {'name': 'start_now_you_putin_results'})
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        war = await collection.count_documents({'start_now_you_putin_results': 'Начну военную операцию ⚔️'})
        stop_war = await collection.count_documents({'start_now_you_putin_results': 'Не стану этого делать 🕊'})
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
    await simple_media(message, 'start_donbas_results', nmarkap.as_markup(resize_keyboard=True),
                       custom_caption=text)


@router.message((F.text == "Продолжай ⌛️"), flags=flags)
async def start_donbas_putin(message: Message):
    await simple_media(message, 'start_donbas_putin')
    nmarkap = ReplyKeyboardBuilder()
    if (await redis_just_one_read(f'Usrs: {message.from_user.id}: StartDonbas:')) == "Знал(а) ✅" or (
            await redis_just_one_read(f'Usrs: {message.from_user.id}: Start_answers: NewPolitStat:')) == \
            'Противник войны 🕊':
        await start_remember_money(message)
    else:
        text = await sql_safe_select('text', 'texts', {'name': 'start_how_are_you'})
        nmarkap.row(types.KeyboardButton(text="Интересно, продолжаем 👌"))
        nmarkap.row(types.KeyboardButton(text="Хорошо, но интересно, с какой целью ты это делаешь? 🤔"))
        nmarkap.row(types.KeyboardButton(text="Звучит однобоко — ты не учитываешь другие факторы ☝️"))
        nmarkap.row(types.KeyboardButton(text="Не надо лезть ко мне в голову, давай к следующим темам. 👉"))
        await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))


"""@router.message((F.text == "Покажи 🤔"), flags=flags)
async def start_many_numbers(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_many_numbers'})
    try:
        client = all_data().get_mongo()
        database = client.database
        collection = database['statistics_new']
        knew_war = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Знал(а) ✅'},
            {'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️'}]})
        knew_dont_war = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Знал(а) ✅'},
            {'start_continue_or_peace_results': 'Переходить к мирным переговорам 🕊'}]})
        knew_hx = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Знал(а) ✅'},
            {'start_continue_or_peace_results': 'Затрудняюсь ответить 🤷‍♀️'}]})
        dont_knew_war = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Не знал(а) ❌'},
            {'start_continue_or_peace_results': 'Продолжать военную операцию ⚔️'}]})
        dont_knew_dont_war = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Не знал(а) ❌'},
            {'start_continue_or_peace_results': 'Переходить к мирным переговорам 🕊'}]})
        dont_knew_hr = await collection.count_documents({'$and': [
            {'start_donbas_results': 'Не знал(а) ❌'},
            {'start_continue_or_peace_results': 'Затрудняюсь ответить 🤷‍♀️'}]})
        all_people_knew = knew_war + knew_dont_war + knew_hx
        all_people_dont_knew = dont_knew_war + dont_knew_dont_war + dont_knew_hr
        try:
            AA = float(knew_war / all_people_knew * 100)
            DD = float(dont_knew_war / all_people_dont_knew * 100)
            XX = DD - AA
        except Exception as e:
            XX = 1
            logger.error(e)
        print((round(XX, 1) if XX >= 0 else str('-') + str(round(abs(XX), 1))))
        text = text.replace('AA', f"{(round(knew_war / all_people_knew * 100, 1) if all_people_knew > 0 else 'N/A')}")
        text = text.replace('BB', f"{(round(knew_dont_war / all_people_knew * 100, 1) if all_people_knew > 0 else 'N/A')}")
        text = text.replace('CC', f"{(round(knew_hx / all_people_knew * 100, 1) if all_people_knew > 0 else 'N/A')}")
        text = text.replace('DD', f"{(round(dont_knew_war / all_people_dont_knew * 100, 1) if all_people_dont_knew > 0 else 'N/A')}")
        text = text.replace('EE', f"{(round(dont_knew_dont_war / all_people_dont_knew * 100, 1) if all_people_dont_knew > 0 else 'N/A')}")
        text = text.replace('FF', f"{(round(dont_knew_hr / all_people_dont_knew * 100, 1) if all_people_dont_knew > 0 else 'N/A')}")
        text = text.replace('XX', f"{(round(XX, 1) if XX >= 0 else str('-') + str(round(abs(XX), 1)))}")
    except Exception as e:
        logger.error(e)
        text = text.replace('AA', 'N/A')
        text = text.replace('BB', 'N/A')
        text = text.replace('CC', 'N/A')
        text = text.replace('DD', 'N/A')
        text = text.replace('EE', 'N/A')
        text = text.replace('FF', 'N/A')
        text = text.replace('XX', 'N/A')

    await message.answer(text, disable_web_page_preview=True)"""


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
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Давай  👌"))
    await simple_media(message, 'start_I_will_rates', reply_markup=nmarkap.as_markup(resize_keyboard=True))


@router.message((F.text == "Давай  👌"), flags=flags)
async def start_how_to_manipulate(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'start_how_to_manipulate'})
    await redis_just_one_write(f'Usrs: {message.from_user.id}: StartDonbas:', message.text)
    nmarkap = ReplyKeyboardBuilder()
    nmarkap.row(types.KeyboardButton(text="Готов(а) продолжить 👌"))
    await message.answer(text, disable_web_page_preview=True, reply_markup=nmarkap.as_markup(resize_keyboard=True))
