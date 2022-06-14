import asyncio
from typing import List

from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from DBuse import sql_safe_select, data_getter, sql_safe_update
from filters.All_filters import WebPropagandaFilter, TVPropagandaFilter, PplPropagandaFilter
from keyboards.map_keys import antip_why_kb, antip_killme_kb
from states.antiprop_states import propaganda_victim

router = Router()
router.message.filter(state=propaganda_victim)


# Подразумевается, что человеку был присвоен статус "жертва пропаганды", после чего он нажал на кнопку "Поехали!".


@router.message(TVPropagandaFilter(option="Скорее да"), (F.text == 'Поехали!'))
async def antiprop_rather_yes_start(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_rather_yes_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Да, полностью доверяю"), (F.text == 'Поехали!'))
async def antiprop_all_yes_start(message: Message, state=FSMContext):
    print('IN LIE HE TRUST')
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Да, полностью доверяю"), (F.text == 'Продолжай'))
async def antiprop_all_yes_second(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Скорее нет"), (F.text == 'Поехали!'))
async def rather_no_TV(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'rather_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Нет, не верю ни слову"), (F.text == 'Поехали!'))
async def antip_all_no_TV(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи ложь на ТВ -- мне интересно посмотреть!"))
    nmarkup.row(types.KeyboardButton(text="Пропустим этот шаг"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(
    (F.text.in_({'Открой мне глаза 👀', "Ну удиви меня 🤔", "Покажи ложь на ТВ -- мне интересно посмотреть!"})))
async def antiprop_tv_selecter(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_pile_of_lies'})
    utv_list = ['1️⃣', '2️⃣4️⃣', '🇷🇺1️⃣', '❇️▶️', '⭐️🅾️', '🟠🍺']
    nmarkup = ReplyKeyboardBuilder()
    for channel in utv_list:
        nmarkup.row(types.KeyboardButton(text=channel))
    nmarkup.row(types.KeyboardButton(text="Что такое пропаганда?"))
    nmarkup.row(types.KeyboardButton(text="Какая-то теория заговора, не верю"))
    nmarkup.adjust(3, 3, 1, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('1️⃣')) & ~(F.text.contains('🇷🇺')))
async def antiprop_tv_first(message: Message, state=FSMContext):
    await state.set_state(propaganda_victim.tv_first)
    try:
        count = (await state.get_data())['first_tv_count']
    except:
        count = 0
    if count == 5:
        count = 0
    count += 1
    await state.update_data(first_tv_count=count)
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_first_lie_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так?"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет с Первого')


@router.message((F.text.contains('2️⃣4️⃣')))
async def antiprop_tv_24(message: Message, state=FSMContext):
    await state.set_state(propaganda_victim.tv_russia24)
    try:
        count = (await state.get_data())['rus24_tv_count']
    except:
        count = 0
    if count == 5:
        count = 0
    count += 1
    await state.update_data(rus24_tv_count=count)
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_24_lie_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так?"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет с России24')


@router.message((F.text.contains('🇷🇺1️⃣')))
async def antiprop_tv_russia1(message: Message, state=FSMContext):
    await state.set_state(propaganda_victim.tv_russia1)
    try:
        count = (await state.get_data())['rus1_tv_count']
    except:
        count = 0
    if count == 5:
        count = 0
    count += 1
    await state.update_data(rus1_tv_count=count)
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_r1_lie_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так?"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет с России1')


@router.message((F.text.contains('❇️▶️')))
async def antiprop_tv_HTB(message: Message, state=FSMContext):
    await state.set_state(propaganda_victim.tv_HTB)
    try:
        count = (await state.get_data())['HTB_tv_count']
    except:
        count = 0
    if count == 5:
        count = 0
    count += 1
    await state.update_data(HTB_tv_count=count)
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_HTB_lie_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так?"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет с НТВ')


@router.message((F.text.contains('⭐️🅾️')))
async def antiprop_tv_star(message: Message, state=FSMContext):
    await state.set_state(propaganda_victim.tv_star)
    try:
        count = (await state.get_data())['Star_tv_count']
    except:
        count = 0
    if count == 5:
        count = 0
    count += 1
    await state.update_data(Star_tv_count=count)
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_star_lie_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так?"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет со Звезды')


@router.message((F.text.contains('🟠🍺')))
async def antiprop_tv_ren(message: Message, state=FSMContext):
    await state.set_state(propaganda_victim.tv_ren)
    try:
        count = (await state.get_data())['ren_tv_count']
    except:
        count = 0
    if count == 5:
        count = 0
    count += 1
    await state.update_data(ren_tv_count=count)
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_ren_lie_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так?"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет с Рентв')


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_first)
async def russia_tv_first_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['first_tv_count']
    text = f'{count} Разоблачение первого канала'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_first_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал"))
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет с 1️⃣ Первого канала"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_russia24)
async def tv_russia24_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['rus24_tv_count']
    text = f'{count} Разоблачение россии24'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_24_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал"))
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет 2️⃣4️⃣ России24"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_russia1)
async def tv_russia1_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['rus1_tv_count']
    text = f'{count} Разоблачение россии1'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_r1_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал"))
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет 🇷🇺1️⃣ России1"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_HTB)
async def tv_HTB_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['HTB_tv_count']
    text = f'{count} Разоблачение НТВ'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_HTB_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал"))
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет ❇️▶️ НТВ"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_star)
async def tv_star_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['Star_tv_count']
    text = f'{count} Разоблачение совканала'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_star_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал"))
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет ⭐️🅾️ Звезды"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_ren)
async def russia_in_nutshell(message: Message, state=FSMContext):
    count = (await state.get_data())['ren_tv_count']
    text = f'{count} Разоблачение рентв'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_ren_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал"))
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет 🟠🍺 Рентв"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Достаточно') & (F.text.contains('понятно'))))
async def antip_crossed_boy_1(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_crossed_boy_1'})
    vid_id = await sql_safe_select('t_id', 'assets', {'name': 'TV_rebuttal_filler'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Посмотрел"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Посмотрел'))
async def antip_crossed_boy_2(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_crossed_boy_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай..."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжай...'))
async def antip_crossed_boy_3(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_crossed_boy_3'})
    text2 = await sql_safe_select('text', 'texts', {'name': 'antip_be_honest'})
    await message.answer(text)
    await asyncio.sleep(3)
    # await state.clear()
    # await state.set_state(propaganda_victim.start)
    await message.answer(text2, reply_markup=antip_killme_kb())


@router.message((F.text.contains('другой телеканал')) | (F.text.contains('посмотреть еще')))
async def antip_another_tv(message: Message, state=FSMContext):
    bigdata = await state.get_data()
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
    try:
        if bigdata['first_tv_count'] < 5:
            raise Exception
    except:
        nmarkup.row(types.KeyboardButton(text='1️⃣'))
    try:
        if bigdata['rus24_tv_count'] < 5:
            raise Exception
    except:
        nmarkup.row(types.KeyboardButton(text='2️⃣4️⃣'))
    try:
        if bigdata['rus1_tv_count'] < 5:
            raise Exception
    except:
        nmarkup.row(types.KeyboardButton(text='🇷🇺1️⃣'))
    try:
        if bigdata['HTB_tv_count'] < 5:
            raise Exception
    except:
        nmarkup.row(types.KeyboardButton(text='❇️▶️'))
    try:
        if bigdata['Star_tv_count'] < 5:
            raise Exception
    except:
        nmarkup.row(types.KeyboardButton(text='⭐️🅾️'))
    try:
        if bigdata['ren_tv_count'] < 5:
            raise Exception
    except:
        nmarkup.row(types.KeyboardButton(text='🟠🍺'))
    nmarkup.adjust(1, 3, 3)
    await message.answer(
        'Я собрал для вас большую базу лжи на фееральных каналах. Выбирайте любой -- и убедитесь сами!',
        reply_markup=nmarkup.as_markup())


@router.message((F.text.contains('пропаганда')))
async def russia_in_nutshell(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_what_is_prop'})
    await message.answer(text)


@router.message((F.text.contains('заговора')))
async def antip_conspirasy(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_conspiracy'})
    await message.answer(text)


@router.message(WebPropagandaFilter(), (
        (F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (
F.text.contains('знал'))))
async def antip_not_only_TV(message: Message, web_lies_list: List[str], state=FSMContext):
    print("HERE LIES LIES LIST", web_lies_list)
    lies_list = web_lies_list
    text = await sql_safe_select('text', 'texts', {'name': 'antip_not_only_TV'})
    await message.answer(text)
    await message.answer('Начало блока с выбором новостей в интернете. В данный момент тупик')


@router.message(PplPropagandaFilter(),
                (F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (
                F.text.contains('знал')))
async def antip_bad_people_lies(message: Message, ppl_lies_list, state=FSMContext):
    print("HERE LIES LIES LIST", ppl_lies_list)
    lies_list = ppl_lies_list
    text = await sql_safe_select('text', 'texts', {'name': 'antip_bad_people_lies'})
    await message.answer(text)
    await message.answer('Начало блока с пропагандистами. В данный момент тупик.')


@router.message(
    (F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (F.text.contains('знал')))
async def antip_truth_game_start(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_truth_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай начнем"))
    nmarkup.row(types.KeyboardButton(text="Не сейчас"))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Давай начнем") | (F.text == "Продолжаем, давай еще!"))
async def antip_truth_game_start(message: Message, state=FSMContext):
    try:
        count = (await state.get_data())['gamecount']
    except:
        count = 0

    how_many_rounds = data_getter("SELECT COUNT (*) FROM public.truthgame")[0][0]
    print(f"В таблице {how_many_rounds} записей, а вот счетчик сейчас {count}")
    if count < how_many_rounds:
        count += 1
        truth_data = data_getter("SELECT truth, t_id, text, belivers, nonbelivers, rebuttal FROM public.truthgame "
                                 "left outer join assets on asset_name = assets.name "
                                 "left outer join texts ON text_name = texts.name "
                                 f"where id = {count}")[0]
        print('aaaaaa', truth_data)
        await state.update_data(gamecount=count, truth=truth_data[0], rebuttal=truth_data[5], belive=truth_data[3],
                                not_belive=truth_data[4])
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Это правда!"))
        nmarkup.row(types.KeyboardButton(text="Это ложь."))
        if truth_data[1] != None:
            try:
                await message.answer_video(truth_data[1], reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[1], reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(truth_data[2], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        await message.answer(
            "Ой, у меня закончились примеры для игры :(\n\nДавайте я лучше вместо этого расскажу вам анекдот!",
            reply_markup=nmarkup.as_markup())


@router.message((F.text == "Это правда!") | (F.text == "Это ложь."))
async def antip_truth_game_answer(message: Message, state=FSMContext):
    data = await state.get_data()
    base_update_dict = dict()
    if message.text == "Это правда!":
        if data['truth'] == True:
            reality = "чистая правда, вы правы!"
            reb = ""
        elif data['truth'] == False:
            reality = "на самом деле настоящая ложь, боюсь, что вы ошиблись."
            reb = f"И вот почему:\n{data['rebuttal']}\n"
        base_update_dict = {'belivers': data['belive'] + 1}
        print('Этому верит', base_update_dict)
    elif message.text == "Это ложь.":
        if data['truth'] == True:
            reality = "чистая правда, вы совершили ошибку."
            reb = f"И вот почему:\n{data['rebuttal']}\n"
        elif data['truth'] == False:
            reality = "лживая ложь из лживых лжей, совершенно верно!"
            reb = ""
        base_update_dict = {'nonbelivers': data['not_belive'] + 1}
        print('Этому верит', base_update_dict)
    await sql_safe_update("truthgame", base_update_dict, {'id': str(data['gamecount'])})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем, давай еще!"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, двигаемся дальше."))
    await message.answer(
        f'Конечно же это {reality}\n{reb}\nРезультаты других участников:\nПравда: {round(t_percentage * 100, 1)}%\nЛожь: {round((100 - t_percentage * 100), 1)}',
        reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Не сейчас') | (F.text.contains("двигаемся дальше")))
async def antip_ok(message: Message):
    await message.answer("Хорошо", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(2)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    await message.answer("У меня есть анекдот")
    await asyncio.sleep(1)
    await message.answer("Хотите послушать?", reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Давай'))
async def antip_anecdote(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_anecdote'})
    await state.clear()
    await state.set_state(propaganda_victim.start)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="😁"))
    nmarkup.row(types.KeyboardButton(text="🙂"))
    nmarkup.row(types.KeyboardButton(text="😕"))
    nmarkup.adjust(1, 1, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({'😁', "🙂", "😕"})))
async def antip_emoji(message: Message, state=FSMContext):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Конечно! 🙂"))
    nmarkup.row(types.KeyboardButton(text="Ну давай 🤮"))
    await message.answer("Можно вопрос?", reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Конечно! 🙂", "Ну давай 🤮"})))
async def antip_do_you_agree(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_do_you_agree'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, но почему тогда люди ей верят?"))
    nmarkup.row(types.KeyboardButton(text="Да, полностью согласен"))
    nmarkup.row(types.KeyboardButton(text="Возможно/Частично"))
    nmarkup.row(types.KeyboardButton(text="Да, как и во всех странах"))
    nmarkup.row(types.KeyboardButton(text="Нет, не согласен"))
    nmarkup.adjust(1, 2, 2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('почему')))
async def antip_why_they_belive(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_why_they_belive'})
    await message.answer(text, reply_markup=antip_why_kb())


@router.message((F.text.contains('Возможно') | (F.text.contains('полностью'))))
async def antip_to_the_main(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_to_the_main'})
    await message.answer(text, reply_markup=antip_why_kb())


@router.message((F.text.contains('во всех')))
async def antip_to_the_main(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_prop_difference'})
    await message.answer(text, reply_markup=antip_why_kb())
