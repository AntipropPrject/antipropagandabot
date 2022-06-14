import asyncio

from typing import List
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from DBuse import poll_get, redis_pop
from DBuse import sql_safe_select
from bata import all_data
from filters.All_filters import WebPropagandaFilter, TVPropagandaFilter, PplPropagandaFilter
from keyboards.map_keys import antip_why_kb
from states.antiprop_states import propaganda_victim
from resources.all_polls import web_prop

router = Router()
router.message.filter(state = propaganda_victim)

#Подразумевается, что человеку был присвоен статус "жертва пропаганды", после чего он нажал на кнопку "Поехали!".



@router.message(TVPropagandaFilter(option ="Скорее да"), (F.text == 'Поехали!'))
async def antiprop_rather_yes_start(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_rather_yes_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option ="Да, полностью доверяю"), (F.text == 'Поехали!'))
async def antiprop_all_yes_start(message: Message, state=FSMContext):
    print('IN LIE HE TRUST')
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Продолжай"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(TVPropagandaFilter(option ="Да, полностью доверяю"), (F.text == 'Продолжай'))
async def antiprop_all_yes_second(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_yes_TV_2'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup())


@router.message(TVPropagandaFilter(option ="Скорее нет"), (F.text == 'Поехали!'))
async def rather_no_TV(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'rather_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message(TVPropagandaFilter(option ="Нет, не верю ни слову"), (F.text == 'Поехали!'))
async def antip_all_no_TV(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_all_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Покажи ложь на ТВ -- мне интересно посмотреть!"))
    nmarkup.row(types.KeyboardButton(text="Пропустим этот шаг"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message((F.text.in_({'Открой мне глаза 👀', "Ну удиви меня 🤔", "Покажи ложь на ТВ -- мне интересно посмотреть!"})))
async def antiprop_tv_selecter(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_pile_of_lies'})
    utv_list = ['1️⃣','2️⃣4️⃣','🇷🇺1️⃣','❇️▶️', '⭐️🅾️', '🟠🍺']
    nmarkup = ReplyKeyboardBuilder()
    for channel in utv_list:
        nmarkup.row(types.KeyboardButton(text=channel))
    nmarkup.row(types.KeyboardButton(text="Что такое пропаганда?"))
    nmarkup.row(types.KeyboardButton(text="Какая-то теория заговора, не верю"))
    nmarkup.adjust(3,3,1,1)
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


#Тут ифами, но можно и по роутерам
@router.message((F.text.in_({'1️⃣','2️⃣4️⃣','🇷🇺1️⃣','❇️▶️', '⭐️🅾️', '🟠🍺'})))
async def antiprop_tv_selecter(message: Message, state=FSMContext):
    if message.text == '1️⃣':
        await message.answer("Тут будет сюжет с первого канала")
    elif message.text == '2️⃣4️⃣':
        await message.answer("Тут будет сюжет с России24")
    elif message.text == '🇷🇺1️⃣':
        await message.answer("Тут будет сюжет с России1")
    elif message.text == '❇️▶️':
        await message.answer("Тут будет сюжет с НТВ")
    elif message.text == '⭐️🅾️':
        await message.answer("Тут будет сюжет с звезды")
    elif message.text == '🟠🍺':
        await message.answer("Тут будет сюжет с РенТВ")
    vid_id = await sql_safe_select('t_id', 'assets', {'name': '123'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Разоблачение"))
    await message.answer_video(vid_id, caption='Это временная заглушка для всех каналов',
                               reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text.contains('Разоблачение')))
async def russia_in_nutshell(message: Message, state=FSMContext):
    text = 'Разоблачение'
    await message.answer(text)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))



@router.message((F.text.contains('пропаганда')))
async def russia_in_nutshell(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_what_is_prop'})
    await message.answer(text)



@router.message((F.text.contains('заговора')))
async def antip_conspirasy(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_conspiracy'})
    await message.answer(text)



@router.message(WebPropagandaFilter(), ((F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (F.text.contains('знал'))))
@router.message(WebPropagandaFilter(), commands=["test"])
async def antip_not_only_TV(message: Message, web_lies_list: List[str], state=FSMContext):
    print("HERE LIES LIES LIST", web_lies_list)
    answer_id_str = await poll_get(f'Start_answers: ethernet_id: {message.from_user.id}')
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text="Показывай"))
    lies_list = web_lies_list
    answer_id_int = []
    all_answers = web_prop
    for i in answer_id_str:
        answer_id_int.append(int(i)) # числа ответов пользователя
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
    await state.update_data(answers_int=answer_id_int) # Все ответы пользователя индексы
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


channels = [
    "РИА Новости", [{("RIANEWS_media_1", "RIANEWS_caption_1"): ("RIANEWS_exposure_1", "RIANEWS_cap_exposure_1")},
                    {("RIANEWS_media_2", "RIANEWS_caption_2"): ("RIANEWS_exposure_2", "RIANEWS_cap_exposure_2")},
                    {("RIANEWS_media_3", "RIANEWS_caption_3"): ("RIANEWS_exposure_3", "RIANEWS_cap_exposure_3")},
                    {("RIANEWS_media_4", "RIANEWS_caption_4"): ("RIANEWS_exposure_4", "RIANEWS_cap_exposure_4")},
                    {("RIANEWS_media_5", "RIANEWS_caption_5"): ("RIANEWS_exposure_5", "RIANEWS_cap_exposure_5")}],

    "Russia Today", [{("RUSSIATODAY_media_1", "RUSSIATODAY_caption_1"): ("RUSSIATODAY_exposure_1", "RUSSIATODAY_cap_exposure_1")},
                     {("RUSSIATODAY_media_2", "RUSSIATODAY_caption_2"): ("RUSSIATODAY_exposure_2", "RUSSIATODAY_cap_exposure_2")},
                     {("RUSSIATODAY_media_3", "RUSSIATODAY_caption_3"): ("RUSSIATODAY_exposure_3", "RUSSIATODAY_cap_exposure_3")},
                     {("RUSSIATODAY_media_4", "RUSSIATODAY_caption_4"): ("RUSSIATODAY_exposure_4", "RUSSIATODAY_cap_exposure_4")},
                     {("RUSSIATODAY_media_5", "RUSSIATODAY_caption_5"): ("RUSSIATODAY_exposure_5", "RUSSIATODAY_cap_exposure_5")}],

    "Телеграм-каналы: Военный осведомитель / WarGonzo / Kotsnews", [{("TCHANEL_media_1", "TCHANEL_caption_1"): ("TCHANEL_exposure_1", "TCHANEL_cap_exposure_1")},
                        {("TCHANEL_media_2", "TCHANEL_caption_2"): ("TCHANEL_exposure_2", "TCHANEL_cap_exposure_2")},
                        {("TCHANEL_media_3", "TCHANEL_caption_3"): ("TCHANEL_exposure_3", "TCHANEL_cap_exposure_3")},
                        {("TCHANEL_media_4", "TCHANEL_caption_4"): ("TCHANEL_exposure_4", "TCHANEL_cap_exposure_4")},
                        {("TCHANEL_media_5", "TCHANEL_caption_5"): ("TCHANEL_exposure_5", "TCHANEL_cap_exposure_5")}],

    "Телеграм-канал: Война с фейками", [{("TCHANEL_WAR_media_1", "TCHANEL_WAR_caption_1"):("TCHANEL_WAR_exposure_1", "TC_WAR_cap_exposure_1")},
                        {("TCHANEL_WAR_media_2", "TCHANEL_WAR_caption_2"): ("TCHANEL_WAR_exposure_2", "TC_WAR_cap_exposure_2")},
                        {("TCHANEL_WAR_media_3", "TCHANEL_WAR_caption_3"): ("TCHANEL_WAR_exposure_3", "TC_WAR_cap_exposure_3")},
                        {("TCHANEL_WAR_media_4", "TCHANEL_WAR_caption_4"): ("TCHANEL_WAR_exposure_4", "TC_WAR_cap_exposure_4")},
                        {("TCHANEL_WAR_media_5", "TCHANEL_WAR_caption_5"): ("TCHANEL_WAR_exposure_5", "TC_WAR_cap_exposure_5")}],

    "РБК", [{("RBK_media_1", "RBK_caption_1"): ("RBK_exposure_1", "RBK_cap_exposure_1")},
                        {("RBK_media_2", "RBK_caption_2"):("RBK_exposure_2", "RBK_cap_exposure_2")},
                        {("RBK_media_3", "RBK_caption_3"):("RBK_exposure_3", "RBK_cap_exposure_3")},
                        {("RBK_media_4", "RBK_caption_4"):("RBK_exposure_4", "RBK_cap_exposure_4")},
                        {("RBK_media_5", "RBK_caption_5"):("RBK_exposure_5", "RBK_cap_exposure_5")}],

    "ТАСС / Комсомольская правда / АиФ / Ведомости / Лента / Интерфакс", [{("TACC_media_1", "TACC_caption_1"):("TACC_exposure_1", "TACC_cap_exposure_1")},
                        {("TACC_media_2", "TACC_caption_2"):("TACC_exposure_2", "TACC_cap_exposure_2")},
                        {("TACC_media_3", "TACC_caption_3"):("TACC_exposure_3", "TACC_cap_exposure_3")},
                        {("TACC_media_4", "TACC_caption_4"):("TACC_exposure_4", "TACC_cap_exposure_4")},
                        {("TACC_media_5", "TACC_caption_5"):("TACC_exposure_5", "TACC_cap_exposure_5")}],

    "Яндекс.Новости", [{("YANDEXNEWS_media_1", "YANDEXNEWS_caption_1"):("YANDEXNEWS_exposure_1", "YNEWS_cap_exposure_1")},
                        {("YANDEXNEWS_media_2", "YANDEXNEWS_caption_2"):("YANDEXNEWS_exposure_2", "YNEWS_cap_exposure_2")},
                        {("YANDEXNEWS_media_3", "YANDEXNEWS_caption_3"):("YANDEXNEWS_exposure_3", "YNEWS_cap_exposure_3")},
                        {("YANDEXNEWS_media_4", "YANDEXNEWS_caption_4"):("YANDEXNEWS_exposure_4", "YNEWS_cap_exposure_4")},
                        {("YANDEXNEWS_media_5", "YANDEXNEWS_caption_5"):("YANDEXNEWS_exposure_5", "YNEWS_cap_exposure_5")}]
    ]



async def keyboard_for_next_chanel(text):
    markup = ReplyKeyboardBuilder()
    if text:
        markup.row(types.KeyboardButton(text=text))
    markup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
    return markup

async def keyboard_for_all_chanel(lst_kb):
    markup = ReplyKeyboardBuilder()
    for button in lst_kb:
        markup.row(types.KeyboardButton(text=button))
    markup.row(types.KeyboardButton(text='Хватит, пропустим остальные источники'))
    return markup


@router.message(((F.text.contains('Показывай')) | (F.text.contains('РИА Новости')) |
                (F.text.contains('Russia Today')) | (F.text.contains('Телеграм-каналы: Военный осведомитель / WarGonzo / Kotsnews')) |
                (F.text.contains('Телеграм-канал: Война с фейками')) | (F.text.contains('РБК')) |
                (F.text.contains('ТАСС / Комсомольская правда / АиФ / Ведомости / Лента / Интерфакс')) | (F.text.contains('Яндекс.Новости')) |
                 (F.text.contains('Хорошо, давай вернемся и посмотрим'))) &~(F.text.contains('еще')))  # вход в цикл
async def show_the_news(message: types.Message, state=FSMContext):
    data = await state.get_data()
    if message.text == 'Показывай':
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Новость посмотрел(а). Что с ней не так?"))
        # получить самый первый источник из списка выбранных каналов
        user_answer_str = data['answers_str']
        one_channel = channels[channels.index(user_answer_str[0])+1]  # получаю первый канал из ответа пользователя
        one_media = await sql_safe_select('t_id', 'assets', {'name': list(one_channel[0].keys())[0][0]})  # Получаю id видео
        one_caption = await sql_safe_select('text', 'texts', {'name': list(one_channel[0].keys())[0][1]})  # Получаю описание
        await state.update_data(viewed_channel=user_answer_str[0])  # передаю канал для разоблачения
        await state.update_data(count_news=0)  # Ставлю счетчик на 0 для первой новости
        await state.update_data(all_viwed=[user_answer_str[0]])  # записываю просмотренный источник
        await message.answer_video(one_media, caption=one_caption, reply_markup=markup.as_markup(resize_keyboard=True))

    elif message.text != 'Хорошо, давай вернемся и посмотрим':
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Новость посмотрел(а). Что с ней не так?"))
        await state.update_data(count_news=0)
        await state.update_data(viewed_channel=message.text)
        new_data = 0
        other_channel = message.text
        if other_channel != 'Хватит, пропустим остальные источники':
            viewed = data["all_viwed"]
            viewed.append(other_channel)
            await state.update_data(all_viwed=list(set(viewed)))  # Список просмотренных источников
        channel_exposure = channels[channels.index(other_channel) + 1]
        media = await sql_safe_select('t_id', 'assets', {'name': list(channel_exposure[new_data].keys())[0][0]})  # Получаю id видео
        caption = await sql_safe_select('text', 'texts', {'name': list(channel_exposure[new_data].keys())[0][1]})  # Получаю описание
        await message.answer_video(media, caption=caption, reply_markup=markup.as_markup(resize_keyboard=True))

    elif message.text == 'Хорошо, давай вернемся и посмотрим':
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Новость посмотрел(а). Что с ней не так?"))
        await state.update_data(count_news=0)
        new_data = 0
        other_channel = data['not_viewed_chanel']
        await state.update_data(viewed_channel=other_channel)
        if other_channel != 'Хватит, пропустим остальные источники':
            viewed = data["all_viwed"]
            viewed.append(other_channel)
            await state.update_data(all_viwed=list(set(viewed)))  # Список просмотренных источников
        channel_exposure = channels[channels.index(other_channel) + 1]
        media = await sql_safe_select('t_id', 'assets', {'name': list(channel_exposure[new_data].keys())[0][0]})  # Получаю id видео
        caption = await sql_safe_select('text', 'texts', {'name': list(channel_exposure[new_data].keys())[0][1]})  # Получаю описание
        await message.answer_video(media, caption=caption, reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        await message.answer('Неправильная команда')
        await poll_get(f'Start_answers: ethernet: {message.from_user.id}')






@router.message((F.text.contains('Новость посмотрел(а). Что с ней не так?')))
async def revealing_the_news(message: types.Message, state=FSMContext):
    data = await state.get_data()
    viewed_channel = data['viewed_channel']  # Просматриваемый канал  менять эту дату для следующих каналов
    count_news = data['count_news']  # Получаю номер новости
    print(viewed_channel)
    if count_news <=3: # Проверка если новости закончились
        markup = await keyboard_for_next_chanel(f"Покажи еще новость с {viewed_channel}")
        channel_exposure = channels[channels.index(viewed_channel)+1]

        media_exposure = await sql_safe_select('t_id', 'assets', {'name': list(channel_exposure[count_news].values())[0][0]})  # Получаю id видео
        caption_exposure = await sql_safe_select('text', 'texts', {'name': list(channel_exposure[count_news].values())[0][1]})  # Получаю описание

        await message.answer_video(media_exposure, caption=caption_exposure, reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Достаточно, мне все понятно"))
        channel_exposure = channels[channels.index(viewed_channel) + 1]

        media_exposure = await sql_safe_select('t_id', 'assets', {'name': list(channel_exposure[count_news].values())[0][0]})  # Получаю id видео
        caption_exposure = await sql_safe_select('text', 'texts', {'name': list(channel_exposure[count_news].values())[0][1]})  # Получаю описание
        await message.answer_video(media_exposure, caption=caption_exposure, reply_markup=markup.as_markup(resize_keyboard=True))



@router.message(text_contains=('Покажи', 'еще', 'новость'), content_types=types.ContentType.TEXT, text_ignore_case=True)
async def show_more(message: types.Message, state=FSMContext):
        data = await state.get_data()
        new_data = data['count_news'] + 1
        await state.update_data(count_news=new_data)  # обновление счетчика
        viewed_channel = data['viewed_channel']  # Просматриваемый канал
        channel_exposure = channels[channels.index(viewed_channel) + 1]
        media = await sql_safe_select('t_id', 'assets', {'name': list(channel_exposure[new_data].keys())[0][0]})  # Получаю id видео
        caption = await sql_safe_select('text', 'texts', {'name': list(channel_exposure[new_data].keys())[0][1]})  # Получаю описание
        markup = ReplyKeyboardBuilder()
        markup.row(types.KeyboardButton(text="Новость посмотрел(а). Что с ней не так?"))
        await message.answer_video(media, caption=caption, reply_markup=markup.as_markup(resize_keyboard=True))



@router.message((F.text.contains('Достаточно, мне все понятно')))
async def revealing_the_news(message: Message, state=FSMContext):
    data = await state.get_data()
    if len(data['answers_str']) - len(data['all_viwed']) != 0:
        #Посмотрел ли юзер все источники
        data = await state.get_data()
        markup = await keyboard_for_all_chanel(data['answers_str'])
        text = await sql_safe_select('text', 'texts', {'name': 'antip_another_web_lie'})
        await message.answer(text, reply_markup=markup.as_markup(resize_keyboard=True))
    else:
        await redis_pop(f'Start_answers: ethernet: {message.from_user.id}')


@router.message((F.text.contains('Хватит, пропустим остальные источники')))
async def skip_web(message: Message, state=FSMContext):
    data = await state.get_data()
    answer_channel = data['answers_str']  # Все выбранные источники
    all_viwed = data['all_viwed']  # Все просмотренные источники
    not_viewed = list(set(answer_channel)-set(all_viwed))
    markup = ReplyKeyboardBuilder()
    markup.row(types.KeyboardButton(text='Хорошо, давай вернемся и посмотрим'))
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



@router.message(PplPropagandaFilter(), (F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (F.text.contains('знал')))
async def antip_bad_people_lies(message: Message, ppl_lies_list,state=FSMContext):
    print("HERE LIES LIES LIST", lies_list)
    lies_list = ppl_lies_list
    text = await sql_safe_select('text', 'texts', {'name': 'antip_bad_people_lies'})
    await message.answer(text)
    await message.answer('Начало блока с пропагандистами. В данный момент тупик.')


@router.message((F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (F.text.contains('знал')))
async def antip_truth_game_start(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_truth_game_start'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Начнем!"))
    nmarkup.row(types.KeyboardButton(text="Не сейчас"))
    await message.answer(text, reply_markup=nmarkup.as_markup())


@router.message((F.text == 'Не сейчас'))
async def antip_ok(message: Message, state=FSMContext):
    msg = await message.answer("Хорошо")
    await asyncio.sleep(2)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Давай"))
    all_data().get_bot().edit_message_text("У меня есть анекдот", reply_markup=nmarkup.as_markup(resize_keyboard=True))



@router.message((F.text == 'Не сейчас'))
async def antip_anecdote(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_anecdote'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="😁"))
    nmarkup.row(types.KeyboardButton(text="🙂"))
    nmarkup.row(types.KeyboardButton(text="😕"))
    nmarkup.adjust(1,1,1)
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


#@router.message((F.text @ ({"Да, но почему тогда люди ей верят?", "Да, полностью согласен", "Возможно/Частично", "Да, как и во всех странах", "Нет, не согласен"})))
