from aiogram import Router, types, F, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from data_base.DBuse import data_getter, sql_safe_insert
from filters.isAdmin import IsAdmin
from handlers.admin_handlers.admin_statistics import pretty_add_progress_stats
from states.admin_states import admin
from utilts import ref_master

router = Router()
router.message.filter(state=admin)

@router.message(IsAdmin(level=['Маркетинг']), (F.text == 'Маркетинг 📈'), state=admin.menu)
async def marketing_menu(message: Message, state: FSMContext):
    await state.set_state(admin.marketing)
    nmarkup = ReplyKeyboardBuilder()
    text = 'Это меню маркетинга. На данный момент в нем вы можете:\n- Получить новую ссылку-счетчик' \
           '\n- Проверить статистику по имеющимся счетчикам\n\nУдачи!'
    nmarkup.row(types.KeyboardButton(text="Получить новую ссылку"))
    nmarkup.row(types.KeyboardButton(text="Проверить все ссылки"))
    nmarkup.row(types.KeyboardButton(text="Статистика по конкретной кампании"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню администрирования"))
    await message.answer(text, reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == 'Получить новую ссылку'), state=admin.marketing)
async def marketing_new_link_name(message: Message, state: FSMContext):
    await state.set_state(admin.market_new_link)
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Отмена"))
    await message.answer('Пожалуйста, дайте своей ссылке понятное имя. К примеру,'
                         ' название рекламной кампании, которую вы планируете провести.',
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message(state=admin.market_new_link)
async def marketing_new_link(message: Message, bot: Bot, state: FSMContext):
    all_adv = await data_getter("SELECT * FROM dumbstats.advertising WHERE id like 'adv_%'")
    leng = len(all_adv) if isinstance(all_adv, list) else 0
    label = message.text.replace(" ", "_")
    link = f'adv_{leng + 1}'
    await ref_master(bot, link)
    await sql_safe_insert('dumbstats', 'advertising', {'id': link, 'label': label, 'count': 0})
    nmarkup = ReplyKeyboardBuilder()
    nmarkup.row(types.KeyboardButton(text="Получить новую ссылку"))
    nmarkup.row(types.KeyboardButton(text="Проверить все ссылки"))
    nmarkup.row(types.KeyboardButton(text="Вернуться в меню администрирования"))
    await state.set_state(admin.marketing)
    bot_link = f'https://t.me/{(await bot.get_me()).username.replace(" ", "_")}?start={link}'
    await message.answer(f'Создание ссылки под названием {label} успешно завершено:\n{bot_link}',
                         reply_markup=nmarkup.as_markup(resize_keyboard=True))


@router.message((F.text == "Проверить все ссылки"), state=admin.marketing)
async def marketing_all_links(message: Message, bot: Bot, state: FSMContext):
    query = "SELECT * FROM dumbstats.advertising WHERE id like 'adv_%' ORDER BY id"
    companies = await data_getter(query)
    if isinstance(companies, list):
        count, text = 0, ''
        for company in companies:
            count += 1
            bot_link = f'https://t.me/{(await bot.get_me()).username.replace(" ", "_")}?start={company[0]}'
            text = text + '-------------------------------------\n' + \
                   f'<code>Название кампании: {company[1]}\n' \
                   f'Ссылка кампании:\n{bot_link}\n' \
                   f'Количество нажавших "Старт": {company[2]}</code>' + \
                   '\n-------------------------------------\n'
            if count == 3 or company == companies[-1]:
                await message.answer(text)
                count, text = 0, ''
    # ДОБАВИТЬ СОЗДАНИЕ ТАБЛИЦЫ ЛИБО СЮДА, ЛИБО ЕЩЕ КУДА-ТО ПРИ СТАРТЕ


@router.message((F.text == "Статистика по конкретной кампании"), state=admin.marketing)
async def marketing_choose_capmagin(message: Message, state: FSMContext):
    ads = await data_getter("SELECT * FROM dumbstats.advertising WHERE id like 'adv_%' ORDER BY id")
    inmarkup = InlineKeyboardBuilder()
    for ad in ads:
        print(ad[0])
        inmarkup.row(InlineKeyboardButton(text=ad[1], callback_data=ad[0]))
    inmarkup.adjust(2)
    await message.answer("<b>Нажмите на кнопку с интересующей вас ссылкой:</b>", reply_markup=inmarkup.as_markup())


@router.callback_query(F.data.contains("adv_"))
async def marketing_choose_capmagin(query: CallbackQuery, state: FSMContext):
    await query.answer()
    adv_tag = query.data
    ad_name = (await data_getter(f"SELECT label FROM dumbstats.advertising WHERE id = '{adv_tag}'"))[0][0]
    text = await pretty_add_progress_stats(adv_tag, ad_name)
    await query.message.answer(text)
