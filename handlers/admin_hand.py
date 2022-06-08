import asyncio
import pathlib

from psycopg2 import sql
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import State, StatesGroup
from aiogram.types import Message
from bata import all_data

from DBuse import safe_data_getter

class admin_home(StatesGroup):
    admin = State()

router = Router()
router.message.filter(state = admin_home)



@router.message(content_types=types.ContentType.TEXT, text_ignore_case=True, text_contains='Довольно', state=admin_home)
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Удачи!", reply_markup=types.ReplyKeyboardRemove())

@router.message(content_types=types.ContentType.TEXT, state=admin_home)
async def get_text(message: Message, state: FSMContext):
    new_text = message.text
    data = {'text':new_text}
    #Временное решение для того, чтобы отправить только текст без других параметров в базе данных
    sql_query = sql.SQL("INSERT INTO public.texts ({}) VALUES ({}) RETURNING id;").format(
        sql.SQL(', ').join(map(sql.Identifier, data)),
        sql.SQL(", ").join(map(sql.Placeholder, data))
    )
    safe_data_getter(sql_query, data)
    await message.answer('Текст добавлен')


@router.message(content_types='photo', state=admin_home)
async def get_photo(message: Message, state: FSMContext):
    conn = all_data().get_postg()
    ph_id = message.photo[0].file_id
    capt = message.caption.replace(" ","_")
    data = {'t_id':ph_id, 'name': capt}
    sql_query = sql.SQL("INSERT INTO public.assets ({}) VALUES ({});").format(
        sql.SQL(', ').join(map(sql.Identifier, data)),
        sql.SQL(", ").join(map(sql.Placeholder, data))
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql_query, data)
    conn.close()
    await message.answer('Фотография добавлена')

@router.message(content_types='video', state=admin_home)
async def get_photo(message: Message, state: FSMContext):
    conn = all_data().get_postg()
    ph_id = message.video.file_id
    capt = message.caption.replace(" ","_")
    data = {'t_id':ph_id, 'name': capt}
    sql_query = sql.SQL("INSERT INTO public.assets ({}) VALUES ({});").format(
        sql.SQL(', ').join(map(sql.Identifier, data)),
        sql.SQL(", ").join(map(sql.Placeholder, data))
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql_query, data)
    conn.close()
    await message.answer('Видео добавлено')
