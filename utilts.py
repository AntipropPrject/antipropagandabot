import asyncio
import time
from typing import Union

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, ReplyKeyboardMarkup, ForceReply, \
    FSInputFile

from data_base.DBuse import sql_safe_select, sql_safe_insert, sql_safe_update, data_getter
from log import logg


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
            return await message.answer_photo(media, caption=text, reply_markup=reply_markup)
        except TelegramBadRequest:
            try:
                return await message.answer_video(media, caption=text, reply_markup=reply_markup)
            except TelegramBadRequest:
                await logg.get_error(f'NO {tag}')
                return None
    else:
        try:
            return await message.answer_photo(media, reply_markup=reply_markup)
        except TelegramBadRequest:
            try:
                return await message.answer_video(media, reply_markup=reply_markup)
            except TelegramBadRequest:
                await logg.get_error(f'NO {tag}')
                return None


class Phoenix:
    def __init__(self):
        pass

    @staticmethod
    async def feather(message: Message, tag: str):
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
                        try:
                            msg = await message.answer_photo(FSInputFile(f'resources/media/{tag}.png'))
                        except TelegramNetworkError:
                            msg = await message.answer_photo(FSInputFile(f'resources/media/{tag}.jpg'))
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

    @staticmethod
    async def rebirth(message: Message):
        all_media_names = await data_getter('SELECT name FROM assets;')
        for name in all_media_names:
            msg = await simple_media(message, name)
            if msg is None:
                await Phoenix.feather(message, name[0])
            await asyncio.sleep(0.5)
        await message.answer('Это все медиа в базе данных. Для всех медиа, '
                             'для которых не было выдана ошибка, теги теперь привязаны к этому боту.')


    @staticmethod
    async def fire(message: Message, bot: Bot):
        all_media_names = await data_getter('SELECT name FROM assets;')
        for name in all_media_names:
            media = str()
            msg = await simple_media(message, name[0])
            if msg is not None:
                try:
                    media = msg.photo[-1].file_id
                    telegram_path = (await bot.get_file(media)).file_path
                    await bot.download_file(telegram_path, f"resources/media/{name[0]}.jpg")
                except (TelegramBadRequest, AttributeError, TypeError):
                    try:
                        media = msg.video.file_id
                        telegram_path = (await bot.get_file(media)).file_path
                        await bot.download_file(telegram_path, f"resources/media/{name[0]}.mp4")
                    except (TelegramBadRequest, AttributeError):
                        pass
                    else:
                        print(f'video {name[0]} was downloaded')
                else:
                    print(f'photo {name[0]} was downloaded')
            await asyncio.sleep(5)
        await message.answer('Все имеющиеся в базе медиа, для которых удалось найти валидный тег, были сохрнены в папку /resources/media директории бота')