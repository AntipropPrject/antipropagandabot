import asyncio
import time
from datetime import datetime
from typing import Union
import os
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, ReplyKeyboardMarkup, ForceReply, \
    FSInputFile, InputFile

import aiohttp
import bata
from data_base.DBuse import sql_safe_select, sql_safe_insert, sql_safe_update, data_getter, sql_select_row_like
from log import logg
from utils.spacebot import SpaceBot

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import git


async def simple_media(message: Message, tag: str,
                       reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                                           ReplyKeyboardRemove, ForceReply, None] = None):
    try:
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
    except:
        print("Ошибка")


async def game_answer(message: Message, telegram_media_id: Union[int, InputFile] = None, text: str = None,
                       reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                                           ReplyKeyboardRemove, ForceReply, None] = None):
    if telegram_media_id is not None:
        try:
            return await message.answer_photo(telegram_media_id, caption=text, reply_markup=reply_markup)
        except TelegramBadRequest:
            try:
                return await message.answer_video(telegram_media_id, caption=text, reply_markup=reply_markup)
            except TelegramBadRequest:
                return None
    else:
        await message.answer(text, reply_markup=reply_markup, disable_web_page_preview=True)


async def dynamic_media_answer(message: Message, similarity_tag: str, row_number: int,
                               reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                                                   ForceReply, None] = None):
    media = (await sql_select_row_like('assets', row_number, {'name': similarity_tag}))[0]
    try:
        text = (await sql_select_row_like('texts', row_number, {'name': similarity_tag}))
    except TypeError:
        text = None
    await game_answer(message, media, text, reply_markup)


class Phoenix:
    def __init__(self):
        pass

    @staticmethod
    async def feather(message: Message, tag: str):
                """
                This function used when you need to reclaim media for the new bot token FROM DISK.\n
                After single usage, telegram id for this media will be in database.\n
                It uses mp4 format for video and jpg format for photo.
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
            try:
                await Phoenix.feather(message, name[0])
                await asyncio.sleep(0.5)
            except:
                continue
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
                        print(f'Something wrong with {name[0]}')
                    else:
                        print(f'video {name[0]} was downloaded')
                else:
                    print(f'photo {name[0]} was downloaded')
            await asyncio.sleep(1)
        await message.answer('Все имеющиеся в базе медиа, для которых удалось найти валидный тег, были сохрнены в папку /resources/media директории бота')



async def happy_tester(bot):
    redis = bata.all_data().get_data_red()
    g = git.Git(os.getcwd())
    loginfo = g.log('--pretty=format:%s || %an')
    old_log_set = redis.smembers('LastCommies')
    new_log_set = set([commname for commname in loginfo.split('\n') if commname.find('OTPOR-') != -1])
    redis.sadd('LastCommies', *new_log_set)
    diff = new_log_set - old_log_set
    botname = (await bot.get_me()).username

    s_bot = SpaceBot('https://otporproject.jetbrains.space', '2dd6e561-edfe-414a-9a5b-b01114d46b9c',
                     'c428a143d05f4512ec5275b8ae190627b71441627f5f7bd975f1021d83ad36aa')
    await s_bot.auth()

    if len(diff) != 0:
        string, space_string, count = '', '', 0
        for comm in diff:
            count += 1
            string = string + '\n' + str(count) + '. ' + comm
            space_string = space_string + '\n' + str(count) + '. ' + comm[:comm.find("||")]
        try:
            await bot.send_message(bata.all_data().commichannel, f'[{datetime.now().strftime("%H:%M")}] Bot @{botname} is up, detected new commits:\n {string}')
            await s_bot.send_message('general', f'Bot @{botname} is up, detected new commits:\n {space_string}')
        except TelegramBadRequest:
            print(f'BOT NOT IN CHANNEL AND THIS MESSAGE NEED TO BE IN LOGS')
        print(f'[{datetime.now().strftime("%H:%M")}] Bot is up, detected new commits:{string}')
    else:
        print(f'[{datetime.now().strftime("%H:%M")}] Bot is up, shore is clear: no new commits here')
    await bot.session.close()
