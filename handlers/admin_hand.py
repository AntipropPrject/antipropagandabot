import asyncio
import pathlib

from psycopg2 import sql
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
from bata import all_data
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from DBuse import safe_data_getter, data_getter
from keyboards.admin_keys import main_admin_keyboard, middle_admin_keyboard, app_admin_keyboard

class admin_home(StatesGroup):
    admin = State()
    add_text = State()
    add_media = State()
    testing_text = State()
    testing_media = State()
    text_edit_tag = State()
    text_edit = State()
    text_edit_test = State()
    media_edit_tag = State()
    media_edit = State()
    media_edit_test = State()

router = Router()
router.message.filter(state = admin_home)

@router.message(content_types=types.ContentType.TEXT, text_ignore_case=True, text_contains='Выйти', state=admin_home)
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы покинули уютный режим администрирования.\nУдачи!", reply_markup=types.ReplyKeyboardRemove())


@router.message(content_types=types.ContentType.TEXT, text_ignore_case=True, text_contains='меню', state=admin_home)
async def menu(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.admin)
    await message.answer("Чего изволите теперь?", reply_markup=main_admin_keyboard())


@router.message((F.text == 'Добавить блок текста'), state = admin_home.admin)
async def text_hello(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.add_text)
    text = data_getter("SELECT text from public.texts WHERE name = 'any_unique_readible_tag';")[0][0]
    await message.answer(f"Пришлите сообщение в подобном формате:{text}", reply_markup=middle_admin_keyboard())


@router.message(content_types=types.ContentType.TEXT, state=admin_home.add_text)
async def get_text(message: Message, state: FSMContext):
    await state.set_state(admin_home.testing_text)
    new_name = message.text.split("|\n")[0]
    new_text = message.text.split("|\n")[1]
    await state.update_data(text = new_text, name = new_name)
    await message.answer(f'<b>Тэг текста:</b>{new_name}\n<b>Текст:\n</b>{new_text}', parse_mode="HTML", reply_markup=app_admin_keyboard())


@router.message((F.text == 'Добавить медиа'), state = admin_home.admin)
async def text_hello(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.add_media)
    photo = data_getter("SELECT t_id from public.assets WHERE name = 'test_photo_tag';")[0][0]
    await message.answer_photo(photo, caption = 'Пришлите фото или видео, подписав его удобным тегом подобного формата: some_unique_tag', reply_markup=middle_admin_keyboard())

@router.message(content_types='photo', state=admin_home.add_media)
async def get_photo(message: Message, state: FSMContext):
    await state.set_state(admin_home.testing_media)
    ph_id = message.photo[0].file_id
    capt = message.caption.replace(" ","_")
    await state.update_data(t_id = ph_id, name = capt)
    await message.answer_photo(ph_id, caption=capt)
    await message.answer('Все верно?', reply_markup=app_admin_keyboard())

@router.message(content_types='video', state=admin_home.add_media)
async def get_video(message: Message, state: FSMContext):
    await state.set_state(admin_home.testing_media)
    vid_id = message.video.file_id
    capt = message.caption.replace(" ","_")
    await state.update_data(t_id = vid_id, name = capt)
    await message.answer_video(vid_id, caption=capt)
    await message.answer('Все верно?', reply_markup=app_admin_keyboard())

@router.message((F.text == 'Отредактировать блок текста'), state = admin_home.admin)
async def text_edit_tag(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.text_edit_tag)
    await message.answer('Пришлите тэг текстового блока, который вы хотите изменить.', reply_markup=middle_admin_keyboard())

@router.message(content_types=types.ContentType.TEXT, state=admin_home.text_edit_tag)
async def text_edit_text_tag(message: Message, state: FSMContext):
    try:
        data = {'name': message.text}
        sql_query = sql.SQL("SELECT text from public.texts WHERE {} = {};").format(
            sql.SQL(', ').join(map(sql.Identifier, data)),
            sql.SQL(", ").join(map(sql.Placeholder, data))
        )
        text = safe_data_getter(sql_query, data)[0][0]
        await message.answer(f'Выбранный вами пост после линии:\n----------------\n{text}', parse_mode="HTML")
        await message.answer('Если это нужный блок, то отправьте мне его новый вариант.', reply_markup=middle_admin_keyboard())
        await state.set_state(admin_home.text_edit)
        await state.update_data(name = message.text)
    except:
        await message.answer(f'Вы ввели некорректный тэг, попробуйте еще раз', parse_mode="HTML")

@router.message(content_types=types.ContentType.TEXT, state=admin_home.text_edit)
async def text_edit_text_test(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f'Проверьте правильность внесенных данных.\n\n\nТэг текста:{data["name"]}\n\nНовый текст:\n{message.text}',
                         parse_mode="HTML", reply_markup=app_admin_keyboard())
    await state.update_data({"text":message.text})
    await state.set_state(admin_home.text_edit_test)

@router.message((F.text == 'Изменить медиа'), state = admin_home.admin)
async def media_edit_tag(message: types.Message, state: FSMContext):
    await state.set_state(admin_home.media_edit_tag)
    await message.answer('Пришлите тэг медиа, которое вы хотите изменить.', reply_markup=middle_admin_keyboard())

@router.message(content_types=types.ContentType.TEXT, state=admin_home.media_edit_tag)
async def edit_media(message: Message, state: FSMContext):
    try:
        data = {'name':message.text}
        sql_query = sql.SQL("SELECT t_id from public.assets WHERE {} = {};").format(
            sql.SQL(', ').join(map(sql.Identifier, data)),
            sql.SQL(", ").join(map(sql.Placeholder, data))
        )
        media_id = safe_data_getter(sql_query, data)[0][0]
        try:
            await message.answer_photo(media_id, caption='Это выбранная вами картинка. Если все верно, отправьте ту, '
                                                         'на которую вы хотите ее заменить', reply_markup=middle_admin_keyboard())
        except:
            pass
        try:
            await message.answer_video(media_id, caption='Это выбранное вами видео. Если все верно, отправьте то, на которое его надо заменить'
                                       , reply_markup=middle_admin_keyboard())
        except:
            pass
        await state.set_state(admin_home.media_edit)
        await state.update_data(name = message.text)
    except:
        await message.answer('К сожалению, медиа под этим тжгом нет в базе.\nПопробуйте еще раз.', reply_markup=middle_admin_keyboard())


@router.message(content_types='video', state=admin_home.media_edit)
async def appr_updated_video(message: Message, state: FSMContext):
    vid_id = message.video.file_id
    await state.update_data(t_id = vid_id)
    await message.answer_video(vid_id, caption="Вы отправили это видео. Оно заменит старое. Все верно?", reply_markup=app_admin_keyboard())
    await state.set_state(admin_home.media_edit_test)

@router.message(content_types='photo', state=admin_home.media_edit)
async def updated_video_test(message: Message, state: FSMContext):
    photo_id = message.photo[0].file_id
    await state.update_data(t_id = photo_id)
    await message.answer_photo(photo_id, caption="Вы отправили это фото. Оно заменит старое. Все верно?", reply_markup=app_admin_keyboard())
    await state.set_state(admin_home.media_edit_test)

@router.message((F.text == 'Подтвердить'), state=admin_home.media_edit_test)
async def approve_media_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    string = "UPDATE public.assets SET t_id={t_id} WHERE name = {name} Returning id;"
    query = sql.SQL(string).format(
        t_id=sql.Placeholder('t_id'),
        name=sql.Placeholder('name'),
    )
    safe_data_getter(query, data)
    await message.answer('Все готово', reply_markup=main_admin_keyboard())
    await state.set_state(admin_home.admin)

@router.message((F.text == 'Подтвердить'), state=admin_home.text_edit_test)
async def approve_edit_text(message: Message, state: FSMContext):
    data = await state.get_data()
    string = "UPDATE public.texts SET text={text} WHERE name = {name} Returning id;"
    query = sql.SQL(string).format(
        text=sql.Placeholder('text'),
        name=sql.Placeholder('name'),
    )
    safe_data_getter(query, data)
    await message.answer('Все готово', reply_markup=main_admin_keyboard())
    await state.set_state(admin_home.admin)

@router.message((F.text == 'Подтвердить'), state = admin_home.testing_media)
async def approve_media(message: Message, state: FSMContext):
    conn = all_data().get_postg()
    data = await state.get_data()
    sql_query = sql.SQL("INSERT INTO public.assets ({}) VALUES ({});").format(
        sql.SQL(', ').join(map(sql.Identifier, data)),
        sql.SQL(", ").join(map(sql.Placeholder, data))
    )
    safe_data_getter(sql_query, data)
    await state.set_state(admin_home.admin)
    await message.answer('Медиа добавлено. Еще разок?', reply_markup=main_admin_keyboard())

@router.message((F.text == 'Подтвердить'), state = admin_home.testing_text)
async def approve_text(message: Message, state: FSMContext):
    data = await state.get_data()
    sql_query = sql.SQL("INSERT INTO public.texts ({}) VALUES ({}) RETURNING id;").format(
        sql.SQL(', ').join(map(sql.Identifier, data)),
        sql.SQL(", ").join(map(sql.Placeholder, data))
    )
    safe_data_getter(sql_query, data)
    await state.set_state(admin_home.admin)
    await message.answer('Текст добавлен. Еще разок?', reply_markup=main_admin_keyboard())


@router.message((F.text == 'Отменить'), state = (admin_home.testing_text, admin_home.testing_media, admin_home.text_edit_test, admin_home.media_edit_test))
async def reset_text(message: Message, state: FSMContext):
    stt = await state.get_state()
    if stt == 'admin_home:testing_text':
        await state.set_state(admin_home.add_text)
        await message.answer('Хорошо, отправьте мне текст с правками', reply_markup=middle_admin_keyboard())
    elif stt == 'admin_home:testing_media':
        await state.set_state(admin_home.add_media)
        await message.answer('Хорошо, отправьте мне другое медиа', reply_markup=middle_admin_keyboard())
    elif stt == 'admin_home:media_edit_test':
        await state.set_state(admin_home.media_edit)
        await message.answer('Хорошо, отправьте мне медиа, на которое вы хотите заменить старое', reply_markup=middle_admin_keyboard())
    elif stt == 'admin_home:text_edit_test':
        await state.set_state(admin_home.text_edit)
        await message.answer('Хорошо, отправьте мне текст, который заменит старый', reply_markup=middle_admin_keyboard())
    else:
        await state.set_state(admin_home.admin)
        await message.answer('Хорошо, вернемся в меню',
                             reply_markup=main_admin_keyboard())

