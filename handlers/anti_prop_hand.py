import asyncio
from typing import List
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bata import all_data
from data_base.DBuse import poll_get, redis_just_one_read
from data_base.DBuse import sql_safe_select, data_getter, sql_safe_update
from filters.All_filters import WebPropagandaFilter, TVPropagandaFilter, PplPropagandaFilter, PoliticsFilter
from handlers.true_resons_hand import TruereasonsState
from keyboards.map_keys import antip_why_kb, antip_killme_kb
from middleware import CounterMiddleware
from resources.all_polls import web_prop
from resources.other_lists import channels
from states.antiprop_states import propaganda_victim
from stats.stat import mongo_update_stat
from utilts import simple_media

router = Router()
router.message.middleware(CounterMiddleware())

router.message.filter(state=propaganda_victim)


# Подразумевается, что человеку был присвоен статус "жертва пропаганды", после чего он нажал на кнопку "Поехали!".


@router.message(TVPropagandaFilter(option="Скорее да"), (F.text == 'Поехали!'))
async def antiprop_rather_yes_start(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_rather_yes_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Да, полностью доверяю"), (F.text == 'Поехали!'))
async def antiprop_all_yes_start(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай 📺"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Да, полностью доверяю"), (F.text == 'Продолжай 📺'))
async def antiprop_all_yes_second(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Скорее нет"), (F.text == 'Поехали!'))
async def rather_no_TV(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_rather_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option="Нет, не верю ни слову"), (F.text == 'Поехали!'))
async def antip_all_no_TV(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Пропустим этот шаг"))
    nmarkup.row(types.KeyboardButton(text="Покажи ложь на ТВ -- мне интересно посмотреть! 📺"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(
        (F.text.in_({'Открой мне глаза 👀', "Ну удиви меня 🤔", "Покажи ложь на ТВ -- мне интересно посмотреть! 📺"})))
async def antiprop_tv_selecter(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_pile_of_lies'})
    utv_list = ['1️⃣ Первый', '🇷🇺1️⃣ Россия 1 / 24', '❇️▶️НТВ', '⭐️🅾️ Звезда']
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Что такое пропаганда?"))
    for channel in utv_list:
        nmarkup.row(types.KeyboardButton(text=channel))
    nmarkup.row(types.KeyboardButton(text="Какая-то теория заговора, не верю... 👽"))
    nmarkup.adjust(1, 2, 2, 1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('1️⃣')) & ~(F.text.contains('🇷🇺')))
async def antiprop_tv_first(message: Message, state: FSMContext):
    await state.set_state(propaganda_victim.tv_first)
    try:
        count = (await state.get_data())['first_tv_count']
    except:
        count = 0
    if count == 5:
        count = 0
    count += 1
    await state.update_data(first_tv_count=count)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так? 🤔"))
    await simple_media(message, f'tv_first_lie_{count}', nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('🇷🇺1️⃣')))
async def antiprop_tv_24(message: Message, state: FSMContext):
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
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так? 🤔"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет с России24')


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
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так? 🤔"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет с НТВ')


@router.message((F.text.contains('⭐️🅾️')))
async def antiprop_tv_star(message: Message, state: FSMContext):
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
    nmarkup.row(types.KeyboardButton(text="Видео посмотрел, что с ним не так? 🤔"))
    await message.answer_video(vid_id, reply_markup=nmarkup.as_markup(resize_keyboard=True),
                               caption=f'{count} сюжет со Звезды')


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_first)
async def russia_tv_first_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['first_tv_count']
    text = f'{count} Разоблачение первого канала'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_first_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет с 1️⃣ Первого канала 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔛"))
    nmarkup.row(types.KeyboardButton(text="Хватит, мне все понятно ✋"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_russia24)
async def tv_russia24_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['rus24_tv_count']
    text = f'{count} Разоблачение россии24'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_24_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет 🇷🇺1️⃣ c России1/24 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔛"))
    nmarkup.row(types.KeyboardButton(text="Хватит, мне все понятно ✋"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_HTB)
async def tv_HTB_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['HTB_tv_count']
    text = f'{count} Разоблачение НТВ'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_HTB_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет ❇️▶️ НТВ 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔛"))
    nmarkup.row(types.KeyboardButton(text="Хватит, мне все понятно ✋"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('что')) & F.text.contains('не так'), state=propaganda_victim.tv_star)
async def tv_star_reb(message: Message, state=FSMContext):
    count = (await state.get_data())['Star_tv_count']
    text = f'{count} Разоблачение совканала'
    vid_id = await sql_safe_select('t_id', 'assets', {'name': f'tv_star_reb_{count}'})
    nmarkup = ReplyKeyboardBuilder()
    if count < 5:
        nmarkup.row(types.KeyboardButton(text="Покажи еще один сюжет ⭐️🅾️ Звезды 📺"))
    nmarkup.row(types.KeyboardButton(text="Хочу выбрать другой телеканал 🔛"))
    nmarkup.row(types.KeyboardButton(text="Хватит, мне все понятно ✋"))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Хватит') & (F.text.contains('понятно'))))
async def antip_crossed_boy_1(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_crossed_boy_1'})
    vid_id = await sql_safe_select('t_id', 'assets', {'name': 'TV_rebuttal_filler'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text='Посмотрел(а) 📺'))
    await message.answer_video(vid_id, caption=text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Посмотрел(а) 📺'))
async def antip_crossed_boy_2(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_crossed_boy_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай... ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Продолжай... ⏳'))
async def antip_crossed_boy_3(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_crossed_boy_3'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Какой ужас😱"))
    nmarkup.row(types.KeyboardButton(text="Давай продолжим😕"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Какой ужас😱") | (F.text == "Давай продолжим😕"))
async def antip_crossed_boy_3(message: Message):
    text2 = await sql_safe_select('text', 'texts', {'name': 'antip_be_honest'})
    await message.answer(text2, reply_markup=antip_killme_kb())


@router.message((F.text.contains('другой телеканал')) | (F.text.contains('посмотреть еще')))
async def antip_another_tv(message: Message, state: FSMContext):
    bigdata = await state.get_data()
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хватит, мне все понятно"))
    tvtags = {'first_tv_count': '1️⃣', 'rus1_tv_count': '🇷🇺1️⃣', 'HTB_tv_count': '❇️▶️', 'Star_tv_count': '⭐️🅾️'}
    for tag in tvtags:
        try:
            if bigdata[tag] < 5:
                raise Exception
        except:
            nmarkup.row(types.KeyboardButton(text=tvtags[tag]))
    nmarkup.adjust(1, 2, 2)
    await message.answer('Я собрал для вас большую базу лжи на федеральных каналах.'
                         ' Выбирайте любой -- и убедитесь сами!', reply_markup=nmarkup.as_markup())


@router.message((F.text.contains('пропаганда')))
async def russia_in_nutshell(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_what_is_prop'})
    utv_list = ['1️⃣ Первый', '🇷🇺1️⃣ Россия 1 / 24', '❇️▶️НТВ', '⭐️🅾️ Звезда']
    nmarkup = ReplyKeyboardBuilder()
    for channel in utv_list:
        nmarkup.row(types.KeyboardButton(text=channel))
    nmarkup.row(types.KeyboardButton(text="Какая-то теория заговора, не верю... 👽"))
    nmarkup.adjust(2, 2, 1)
    await message.answer(text, disable_web_page_preview=True)


@router.message((F.text.contains('заговора')))
async def antip_conspirasy(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_conspiracy'})
    await message.answer(text)


@router.message(WebPropagandaFilter(), (
        (F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) |
        (F.text.contains('знал'))))
@router.message(WebPropagandaFilter(), commands=["test"])
async def antip_not_only_TV(message: Message, web_lies_list: List[str], state=FSMContext):
    answer_id_str = await poll_get(f'Usrs: {message.from_user.id}: Start_answers: ethernet_id:')
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Показывай"))
    lies_list = web_lies_list
    answer_id_int = []
    all_answers = web_prop
    for i in answer_id_str:
        answer_id_int.append(int(i))  # числа ответов пользователя
    try:
        answer_id_int.remove(2)
        lies_list.remove('Meduza / BBC / Радио Свобода / Медиазона / Настоящее время / Популярная Политика')
        all_answers.remove('Meduza / BBC / Радио Свобода / Медиазона / Настоящее время / Популярная Политика')
    except:
        pass
    try:
        answer_id_int.remove(8)
        lies_list.remove('Википедия')
        all_answers.remove("Википедия")
    except:
        pass
    try:
        answer_id_int.remove(9)
        lies_list.remove('Никому из них...')
        all_answers.remove("Никому из них...")
    except:
        pass

    await state.update_data(all_answers=all_answers)  # Все ответы опроса
    await state.update_data(answers_int=answer_id_int)  # Все ответы пользователя индексы
    await state.update_data(answers_str=lies_list)  # Все ответы пользователя строки
    channel = lies_list[0]
    text = 'Но пропаганда в России не заканчивается ' \
           'на ТВ. Молодое поколение получает ' \
           'новости из интернета: новостных ' \
           'порталов, соцсетей и телеграм-каналов.  ' \
           'Больше 10 лет пропаганда постепенно ' \
           'захватывала интернет-ресурсы, которые ' \
           'до этого были независимыми: РИА ' \
           'Новости, Известия, Коммерсант, РБК и ' \
           'даже Яндекс.Новости. Этот список ' \
           'включает в себя сотни интернет-порталов,  ' \
           'а также блогеров и телеграм-каналы.\n\n' \
           'Я заметил, что среди источников, которым ' \
           f'вы доверяете - есть {channel}.' \
           f' К сожалению, {channel} ставит целью не ' \
           'донести правдивые новости, а составить у ' \
           'людей нужную [властям] картину мира. ' \
           'Давайте я покажу несколько сюжетов,  ' \
           'которые это докажут'
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


async def keyboard_for_next_chanel(text):
    markup = ReplyKeyboardBuilder()
    if text:
        markup.row(types.KeyboardButton(text=text))
    markup.row(types.KeyboardButton(text="Достаточно, мне все понятно 🤚"))
    return markup


async def keyboard_for_all_chanel(lst_kb):
    markup = ReplyKeyboardBuilder()
    for button in lst_kb:
        markup.row(types.KeyboardButton(text=button+' 👀'))
    markup.row(types.KeyboardButton(text='Хватит, пропустим остальные источники 🙅‍♂️'))
    return markup


@router.message(((F.text.contains('Показывай')) | (F.text.contains('РИА Новости 👀')) | (
        F.text.contains('Russia Today 👀')) | (
                         F.text.contains('Телеграм-каналы: Военный осведомитель / WarGonzo / Kotsnews 👀')) | (
                         F.text.contains('Телеграм-канал: Война с фейками 👀')) | (F.text.contains('РБК 👀')) | (
                         F.text.contains('ТАСС / Комсомольская правда / АиФ / Ведомости / Лента / Интерфакс 👀')) | (
                         F.text.contains('Яндекс.Новости 👀')) | (
                         F.text.contains('Хорошо, давай вернемся и посмотрим 👀'))) & ~(
F.text.contains('еще')))  # вход в цикл
async def show_the_news(message: types.Message, state=FSMContext):
    data = await state.get_data()
    if message.text == 'Показывай':
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Новость посмотрел(а). Что с ней не так? 🤔"))
        # получить самый первый источник из списка выбранных каналов
        user_answer_str = data['answers_str']
        one_channel = channels[channels.index(user_answer_str[0]) + 1]  # получаю первый канал из ответа пользователя
        one_media = await sql_safe_select('t_id', 'assets',
                                          {'name': list(one_channel[0].keys())[0][0]})  # Получаю id видео
        one_caption = await sql_safe_select('text', 'texts',
                                            {'name': list(one_channel[0].keys())[0][1]})  # Получаю описание
        await state.update_data(viewed_channel=user_answer_str[0])  # передаю канал для разоблачения
        await state.update_data(count_news=0)  # Ставлю счетчик на 0 для первой новости
        await state.update_data(all_viwed=[user_answer_str[0]])  # записываю просмотренный источник
        await message.answer_video(one_media, caption=one_caption, reply_markup=markup.as_markup(resize_keyboard=True))
    elif message.text != 'Хорошо, давай вернемся и посмотрим 👀':
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Новость посмотрел(а). Что с ней не так? 🤔"))
        await state.update_data(count_news=0)
        await state.update_data(viewed_channel=message.text[:-2])
        new_data = 0
        other_channel = message.text
        if other_channel != 'Хватит, пропустим остальные источники 🙅‍♂️':
            viewed = data["all_viwed"]
            viewed.append(other_channel)
            await state.update_data(all_viwed=list(set(viewed)))  # Список просмотренных источников

        channel_exposure = channels[channels.index(other_channel[:-2]) + 1]
        media = await sql_safe_select('t_id', 'assets',
                                      {'name': list(channel_exposure[new_data].keys())[0][0]})  # Получаю id видео
        caption = await sql_safe_select('text', 'texts',
                                        {'name': list(channel_exposure[new_data].keys())[0][1]})  # Получаю описание
        await message.answer_video(media, caption=caption, reply_markup=markup.as_markup(resize_keyboard=True))

    elif message.text == 'Хорошо, давай вернемся и посмотрим 👀':
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Новость посмотрел(а). Что с ней не так? 🤔"))
        await state.update_data(count_news=0)
        new_data = 0
        other_channel = data['not_viewed_chanel']
        await state.update_data(viewed_channel=other_channel)
        if other_channel != 'Хватит, пропустим остальные источники 🙅‍♂️':
            viewed = data["all_viwed"]
            viewed.append(other_channel)
            await state.update_data(all_viwed=list(set(viewed)))  # Список просмотренных источников
        channel_exposure = channels[channels.index(other_channel) + 1]
        media = await sql_safe_select('t_id', 'assets',
                                      {'name': list(channel_exposure[new_data].keys())[0][0]})  # Получаю id видео
        caption = await sql_safe_select('text', 'texts',
                                        {'name': list(channel_exposure[new_data].keys())[0][1]})  # Получаю описание
        await message.answer_video(media, caption=caption, reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        await message.answer('Неправильная команда')
        await poll_get(f'Usrs: {message.from_user.id}: Start_answers: ethernet:')


@router.message((F.text.contains('Новость посмотрел(а). Что с ней не так? 🤔')))
async def revealing_the_news(message: types.Message, state=FSMContext):
    data = await state.get_data()
    viewed_channel = data['viewed_channel']  # Просматриваемый канал  менять эту дату для следующих каналов
    count_news = data['count_news']  # Получаю номер новости
    if count_news <= 3:  # Проверка если новости закончились
        markup = await keyboard_for_next_chanel(f"Покажи еще новость с {viewed_channel} 👀")
        channel_exposure = channels[channels.index(viewed_channel) + 1]

        media_exposure = await sql_safe_select('t_id', 'assets', {
            'name': list(channel_exposure[count_news].values())[0][0]})  # Получаю id видео
        caption_exposure = await sql_safe_select('text', 'texts', {
            'name': list(channel_exposure[count_news].values())[0][1]})  # Получаю описание

        await message.answer_video(media_exposure, caption=caption_exposure,
                                   reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Достаточно, мне все понятно 🤚"))
        channel_exposure = channels[channels.index(viewed_channel) + 1]

        media_exposure = await sql_safe_select('t_id', 'assets', {
            'name': list(channel_exposure[count_news].values())[0][0]})  # Получаю id видео
        caption_exposure = await sql_safe_select('text', 'texts', {
            'name': list(channel_exposure[count_news].values())[0][1]})  # Получаю описание
        await message.answer_video(media_exposure, caption=caption_exposure,
                                   reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(text_contains=('Покажи', 'еще', 'новость'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def show_more(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_data = data['count_news'] + 1
    await state.update_data(count_news=new_data)  # обновление счетчика
    viewed_channel = data['viewed_channel']  # Просматриваемый канал
    channel_exposure = channels[channels.index(viewed_channel) + 1]
    media = await sql_safe_select('t_id', 'assets',
                                  {'name': list(channel_exposure[new_data].keys())[0][0]})  # Получаю id видео
    caption = await sql_safe_select('text', 'texts',
                                    {'name': list(channel_exposure[new_data].keys())[0][1]})  # Получаю описание
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Новость посмотрел(а). Что с ней не так? 🤔"))
    await message.answer_video(media, caption=caption, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Достаточно, мне все понятно 🤚')))
async def revealing_the_news(message: Message, state: FSMContext):
    data = await state.get_data()
    if len(data['answers_str']) - len(data['all_viwed']) != 0:
        # Посмотрел ли юзер все источники
        data = await state.get_data()
        markup = await keyboard_for_all_chanel(data['answers_str'])
        text = await sql_safe_select('text', 'texts', {'name': 'antip_another_web_lie'})
        await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        redis = all_data().get_data_red()
        for key in redis.scan_iter(f"Usrs: {message.from_user.id}: Start_answers: ethernet:*"):
            redis.delete(key)
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text='Конечно!'))
        await message.answer("Среди того, что может казаться альтернативными источниками, может быть полно лжи. "
                             "Надеюсь, что теперь вы со мной в этом согласитесь. В любом случае, у меня кончились примеры."
                             "\nГотовы продолжить?")


@router.message((F.text.contains('Хватит, пропустим остальные источники 🙅‍♂️')))
async def skip_web(message: Message, state: FSMContext):
    data = await state.get_data()
    answer_channel = data['answers_str']  # Все выбранные источники
    all_viwed = data['all_viwed']  # Все просмотренные источники
    not_viewed = list(set(answer_channel) - set(all_viwed))
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Хорошо, давай вернемся и посмотрим 👀'))
    markup.row(types.KeyboardButton(text='Не надо, я и так знаю, что они врут'))
    markup.row(types.KeyboardButton(text='Не надо, я все равно буду доверять им'))
    lst_web_answers = str(', '.join(not_viewed))
    next_channel = str(not_viewed[0])
    await state.update_data(not_viewed_chanel=not_viewed[0])
    await message.answer("Я хотел показать вам еще, как врут "
                         f"{lst_web_answers}, ведь вы "
                         "отметили, что доверяете им. Для нашей "
                         "дальнейшей беседы важно, чтобы мы "
                         "разобрались, кому можно верить, а кому нет.\n\n"
                         "Можно я все-таки покажу хотя бы один "
                         f"сюжет от {next_channel}?", reply_markup=markup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Не надо')))
async def antip_web_exit_1(message: Message, state=FSMContext):
    text = 'Хорошо, это ваше право. Тогда предлагаю продолжить -- мне столько нужно вам показать!'
    redis = all_data().get_data_red()
    for key in redis.scan_iter(f"Usrs: {message.from_user.id}: Start_answers: ethernet:"):
        redis.delete(key)
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Ну давай'))
    await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))


@router.message(PplPropagandaFilter(),
                (F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (
                        F.text.contains('знал')) | (F.text == 'Конечно!') | (F.text == 'Ну давай'))
async def antip_bad_people_lies(message: Message, ppl_lies_list, state: FSMContext):
    redis = all_data().get_data_red()
    await state.set_state(propaganda_victim.ppl_propaganda)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_bad_people_lies'})
    for key in redis.scan_iter(f'Usrs: {message.from_user.id}: Start_answers: who_to_trust:*'):
        redis.delete(key)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давайте начнём!"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (
        F.text.contains('знал')) | (F.text == 'Конечно!') | (F.text == 'Ну давай'))
async def antip_truth_game_start(message: Message, state: FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_truth_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнем! 🚀"))
    nmarkup.row(types.KeyboardButton(text="Пропустим игру 🙅‍♀️"))
    nmarkup.adjust(2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Начнем! 🚀") | (F.text == "Продолжаем, давай еще! 👉"))
async def antip_truth_game_start_question(message: Message, state: FSMContext):
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
        nmarkup.row(types.KeyboardButton(text="Это правда ✅"))
        nmarkup.row(types.KeyboardButton(text="Это ложь ❌"))
        if truth_data[1] is not None:
            capt = ""
            if truth_data[2] is not None:
                capt = truth_data[2]
            try:
                await message.answer_video(truth_data[1], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
            except:
                await message.answer_photo(truth_data[1], caption=capt,
                                           reply_markup=nmarkup.as_markup(resize_keyboard=True))
        else:
            await message.answer(truth_data[2], reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        await message.answer(
                "Ой, у меня закончились примеры для игры :(\n\nДавайте я лучше вместо этого расскажу вам анекдот!",
                reply_markup=nmarkup.as_markup())


@router.message((F.text == "Это правда ✅") | (F.text == "Это ложь ❌"))
async def antip_truth_game_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    base_update_dict = dict()
    if message.text == "Это правда ✅":
        if data['truth'] == True:
            reality = "чистая правда, вы правы!"
            reb = ""
        elif data['truth'] == False:
            reality = "на самом деле чистая ложь, боюсь, что вы ошиблись."
            reb = f"И вот почему:\n{data['rebuttal']}\n"
        base_update_dict = {'belivers': data['belive'] + 1}
        print('Этому верит', base_update_dict)
    elif message.text == "Это ложь ❌":
        if data['truth'] == True:
            reality = "чистая правда, вы совершили ошибку."
            reb = f"И вот почему:\n{data['rebuttal']}\n"
        elif data['truth'] == False:
            reality = "ложь, совершенно верно!"
            reb = ""
        base_update_dict = {'nonbelivers': data['not_belive'] + 1}
        print('Этому верит', base_update_dict)
    await sql_safe_update("truthgame", base_update_dict, {'id': data['gamecount']})
    t_percentage = data['belive'] / (data['belive'] + data['not_belive'])
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжаем, давай еще! 👉"))
    nmarkup.row(types.KeyboardButton(text="Достаточно, двигаемся дальше  🙅‍♀️"))
    await message.answer(
            f'Конечно же это {reality}\n{reb}\nРезультаты других участников:\nПравда: {round(t_percentage * 100, 1)}%\nЛожь: {round((100 - t_percentage * 100), 1)}',
            reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Пропустим игру 🙅‍♀️") | (F.text.contains("двигаемся дальше")))
async def antip_ok(message: Message):
    await message.answer("Хорошо", reply_markup=ReplyKeyboardRemove())
    if await redis_just_one_read(f'Usrs: {message.from_user.id}: INFOState:') == 'Жертва пропаганды':
        await asyncio.sleep(2)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай"))
        await message.answer("У меня есть анекдот")
        await asyncio.sleep(1)
        await message.answer("Хотите послушать?", reply_markup=nmarkup.as_markup(resize_keyboard=True))
    else:
        await asyncio.sleep(1)
        nmarkup = ReplyKeyboardBuilder()
        nmarkup.row(types.KeyboardButton(text="Давай поговорим про военные действия в Украине"))
        await message.answer("Похоже, что пропаганда до вас не добралась. Тогда давай поговорим о главном...",
                             reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Давай'))
async def antip_anecdote(message: Message, state: FSMContext):
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
async def antip_emoji(message: Message):
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Конечно! 🙂"))
    nmarkup.row(types.KeyboardButton(text="Ну давай 🤮"))
    await message.answer("Можно вопрос?", reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.in_({"Конечно! 🙂", "Ну давай 🤮"})))
async def antip_do_you_agree(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_do_you_agree'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Да, полностью согласен 👌🏼"))
    nmarkup.row(types.KeyboardButton(text="Возможно / частично 🤷‍♀️"))
    nmarkup.row(types.KeyboardButton(text="Нет, не согласен(сна) 🙅‍♂️"))
    nmarkup.row(types.KeyboardButton(text="Да, но почему тогда люди ей верят? 🤔"))
    nmarkup.row(types.KeyboardButton(text="Да, как и во многих других странах 🇺🇸"))

    nmarkup.adjust(2, 1, 2)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('почему')))
async def antip_why_they_belive(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_why_they_belive'})
    await message.answer(text, reply_markup=antip_why_kb())


@router.message((F.text.contains('Возможно') | (F.text.contains('полностью')) | (F.text.contains('Скорее'))))
async def antip_to_the_main(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_to_the_main'})
    await message.answer(text, reply_markup=antip_why_kb())


@router.message((F.text.contains('во многих')))
async def antip_to_the_main(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_prop_difference'})
    await message.answer(text, reply_markup=antip_why_kb())


@router.message((F.text.contains('Нет, не согласен(сна)')))
async def antip_love_propaganda(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_love_propaganda'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Скорее согласен(сна)"))
    nmarkup.row(types.KeyboardButton(text="Да, как и во многих других странах 🇺🇸"))
    nmarkup.row(types.KeyboardButton(text="Нет, нам хотят донести правду 😌"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(F.text == 'Нет, нам хотят донести правду 😌')
async def antip_big_love_propaganda(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_big_love_propaganda'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(
            text="Продолжить 🇷🇺🇺🇦"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('правда. Откуда ты знаешь')))
async def antip_reputation_matters(message: Message):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_reputation_matters'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Я готов продолжить. Поговорим про военные действия в Украине."))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


# По хорошему, это уже начало войны
# Я НЕ ЗНАЮ КАК ЭТО НОРМАЛЬНО ПОВЕСИТЬ
@router.message(PoliticsFilter(title='Сторонник войны'),
                ((F.text.contains('действия')) & (F.text.contains('Украине'))) | (
                        F.text.contains('Продолжить 🇷🇺🇺🇦')))
async def war_point_now(message: Message, state: FSMContext):
    await mongo_update_stat(message.from_user.id, 'antiprop')
    await state.set_state(TruereasonsState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_war_point_now'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай ⏳"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)


@router.message(PoliticsFilter(title='Аполитичный'),
                ((F.text.contains('действия')) & (F.text.contains('Украине'))) | (
                        F.text.contains("Продолжить 🇷🇺🇺🇦")))
async def reasons_lets_figure(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_lets_figure'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай попробуем 👌🏼"))
    nmarkup.row(types.KeyboardButton(text="Я не интересуюсь политикой 😐"))
    nmarkup.row(types.KeyboardButton(text="Незачем, ведь эти цели - бессмысленны 🤬"))
    nmarkup.adjust(2,1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True), disable_web_page_preview=True)



@router.message(((F.text.contains('действия')) & (F.text.contains('Украине'))) | (
        F.text.contains('Продолжить 🇷🇺🇺🇦')))
async def reasons_king_of_info(message: Message, state: FSMContext):
    await state.set_state(TruereasonsState.main)
    text = await sql_safe_select('text', 'texts', {'name': 'reasons_king_of_info'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Хорошо 👌🏼"))
    nmarkup.row(types.KeyboardButton(text="Подожди. Я так не говорил(а). С чего ты взял, что это ненастоящие цели? 🤷‍♂️"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))
