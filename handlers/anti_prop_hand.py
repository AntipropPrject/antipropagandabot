import asyncio

from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from DBuse import sql_safe_select
from bata import all_data
from filters.All_filters import WebPropagandaFilter, TVPropagandaFilter, PplPropagandaFilter
from keyboards.map_keys import antip_why_kb
from states.antiprop_states import propaganda_victim

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
async def antiprop_rather_yes_start(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'rather_no_TV'})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Открой мне глаза 👀"))
    nmarkup.row(types.KeyboardButton(text="Ну удиви меня 🤔"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))

@router.message(TVPropagandaFilter(option ="Нет, не верю ни слову"), (F.text == 'Поехали!'))
async def antiprop_rather_yes_start(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'all_no_TV'})
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


@router.message((F.text.contains('пропаганда')))
async def russia_in_nutshell(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_what_is_prop'})
    await message.answer(text)



@router.message((F.text.contains('заговора')))
async def antip_conspirasy(message: Message, state=FSMContext):
    text = await sql_safe_select('text', 'texts', {'name': 'antip_conspiracy'})
    await message.answer(text)



@router.message(WebPropagandaFilter(), ((F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (F.text.contains('знал'))))
async def antip_not_only_TV(message: Message, web_lies_list, state=FSMContext):
    lies_list = web_lies_list['web_lies_list']
    print(lies_list)
    text = await sql_safe_select('text', 'texts', {'name': 'antip_not_only_TV'})
    await message.answer(text)
    await message.answer('Начало блока с выбором новостей в интернете.')


@router.message(PplPropagandaFilter(), (F.text.contains('шаг')) | (F.text.contains('удивлен')) | (F.text.contains('шоке')) | (F.text.contains('знал')))
async def antip_bad_people_lies(message: Message, ppl_lies_list,state=FSMContext):
    lies_list = ppl_lies_list["ppl_lies_list"]
    text = await sql_safe_select('text', 'texts', {'name': 'antip_bad_people_lies'})
    await message.answer(text)
    await message.answer('Начало блока с пропагандистами.')


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
