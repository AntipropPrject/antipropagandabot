import asyncio
from typing import Union

from psycopg2._psycopg import connection

from log import logg
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, ReplyKeyboardMarkup, ForceReply, \
    FSInputFile

from data_base.DBuse import sql_safe_select, sql_safe_insert, sql_safe_update, data_getter


async def simple_media(message: Message, tag: str,
                       reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                                           ReplyKeyboardRemove, ForceReply, None] = None):
    """
    You can use one tag. If there text with that tag, it will become caption
    """
    text = await sql_safe_select("text", "texts", {"name": tag})
    media = await sql_safe_select("t_id", "assets", {"name": tag})
    if text is not False:
        try:
            await message.answer_photo(media, caption=text, reply_markup=reply_markup)
        except TelegramBadRequest:
            try:
                await message.answer_video(media, caption=text, reply_markup=reply_markup)
            except TelegramBadRequest:
                logg.get_info(f'No ||{tag}|| in database')
                await phoenix_feather(message, tag)
    else:
        try:
            await message.answer_photo(media, reply_markup=reply_markup)
        except TelegramBadRequest:
            try:
                await message.answer_video(media, reply_markup=reply_markup)
            except TelegramBadRequest:
                logg.get_info(f'No ||{tag}|| in database')
                await phoenix_feather(message, tag)






async def phoenix_feather(message: Message, tag: str):
            """
            This function used when you need to reclaim media for the new bot token FROM DISK.\n
            After single usage, telegram id for this media will be in database.\n
            It uses mp4 format for video and png format for photo.
            """
            media = await sql_safe_select("t_id", "assets", {"name": tag})
            try:
                msg = await message.answer_video(FSInputFile(f'resources/media/{tag}.mp4'))
                if media is False:
                    await sql_safe_insert('assets', {'t_id': msg.video.file_id, 'name': tag})
                else:
                    await sql_safe_update('assets', {'t_id': msg.video.file_id}, {'name': tag})
            except (TelegramNetworkError, TelegramBadRequest):
                try:
                    msg = await message.answer_photo(FSInputFile(f'resources/media/{tag}.png'))
                    if media is False:
                        await sql_safe_insert('assets', {'t_id': msg.photo[-1].file_id, 'name': tag})
                    else:
                        await sql_safe_update('assets', {'t_id': msg.photo[-1].file_id}, {'name': tag})
                except TelegramNetworkError:
                    await logg.get_error(f'Cant find ||{tag}|| file at "resources/media/" !')
                    await message.answer(f'Не удалось получить с диска {tag}')
                else:
                    print(f'Successfully retrieved photo {tag}.png from disk')
            else:
                print(f'Successfully retrieved video {tag}.mp4 from disk')
            finally:
                print(f'There was no {tag} name')


async def phoenix_protocol(message: Message):
    all_media_names = data_getter('SELECT name FROM assets;')
    for name in all_media_names:
        await simple_media(message, name[0])
        await asyncio.sleep(1)
    await message.answer('Это все медиа в базе данных. Для всех медиа, '
                         'для которых не было выдана ошибка, теги теперь существуют.')