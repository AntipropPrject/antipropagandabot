import asyncio
import os
import re
from datetime import datetime
from typing import Union

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramForbiddenError
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, ReplyKeyboardMarkup, ForceReply, \
    FSInputFile, InputFile, InputMediaVideo, InputMediaPhoto, BotCommandScopeChat, BotCommandScopeDefault, \
    BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, BotCommandScopeAllChatAdministrators, \
    BotCommandScopeChatAdministrators, BotCommandScopeChatMember, BotCommand, User

import bata
from data_base.DBuse import sql_safe_select, sql_safe_insert, sql_safe_update, data_getter, sql_select_row_like, \
    mongo_ez_find_one, mongo_count_docs, mongo_select_info, mongo_select_admin_levels
from log import logg
from utils.spacebot import SpaceBot

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import git


async def simple_media(message: Message, tag: str,
                       reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                                           ReplyKeyboardRemove, ForceReply, None] = None,
                       custom_caption: str = None):
    """
    You can use one tag. If there text with that tag, it will become caption. You can pass custom caption
    """
    try:
        if custom_caption:
            text = custom_caption
        else:
            text = await sql_safe_select("text", "texts", {"name": tag})
        media = await sql_safe_select("t_id", "assets", {"name": tag})
        if text is not False:
            try:
                return await message.answer_photo(media, caption=text, reply_markup=reply_markup)
            except TelegramBadRequest:
                try:
                    return await message.answer_video(media, caption=text, reply_markup=reply_markup)
                except TelegramBadRequest:
                    media = await sql_safe_select("t_id", "assets", {"name": 'ERROR_SORRY'})
                    await logg.get_error(f'NO {tag}')
                    await message.answer_photo(media, caption=text, reply_markup=reply_markup)
        else:
            try:
                return await message.answer_photo(media, reply_markup=reply_markup)
            except TelegramBadRequest:
                try:
                    return await message.answer_video(media, reply_markup=reply_markup)
                except TelegramBadRequest:
                    media = await sql_safe_select("t_id", "assets", {"name": 'ERROR_SORRY'})
                    await logg.get_error(f'NO {tag}')
                    await message.answer_photo(media, reply_markup=reply_markup)
    except TelegramBadRequest as err:
        print(err)


async def simple_media_bot(bot: Bot, chat_id: int, tag: str,
                           reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                                               ReplyKeyboardRemove, ForceReply, None] = None,
                           custom_caption: str = None):
    """
    You can use one tag. If there text with that tag, it will become caption. You can pass custom caption
    """
    try:
        if custom_caption:
            text = custom_caption
        else:
            text = await sql_safe_select("text", "texts", {"name": tag})
        media = await sql_safe_select("t_id", "assets", {"name": tag})
        if text is not False:
            try:
                return await bot.send_photo(chat_id, media, caption=text, reply_markup=reply_markup)
            except TelegramBadRequest:
                try:
                    return await bot.send_video(chat_id, media, caption=text, reply_markup=reply_markup)
                except TelegramBadRequest:
                    media = await sql_safe_select("t_id", "assets", {"name": 'ERROR_SORRY'})
                    await logg.get_error(f'NO {tag}')
                    await bot.send_photo(chat_id, media, caption=text, reply_markup=reply_markup)
        else:
            try:
                return await bot.send_photo(chat_id, media, reply_markup=reply_markup)
            except TelegramBadRequest:
                try:
                    return await bot.send_video(chat_id, media, reply_markup=reply_markup)
                except TelegramBadRequest:
                    media = await sql_safe_select("t_id", "assets", {"name": 'ERROR_SORRY'})
                    await logg.get_error(f'NO {tag}')
                    await bot.send_photo(chat_id, media, reply_markup=reply_markup)
    except TelegramBadRequest as err:
        print(err)


async def simple_video_album(message: Message, bot: Bot, tags: list[str], text_tag: str = None):
    media_list, caption = list(), str()
    if text_tag:
        caption = await sql_safe_select("text", "texts", {"name": text_tag})
    media_ids = await data_getter(f'SELECT t_id FROM assets WHERE name IN {*tags,}')
    for media in media_ids:
        media_list.append(InputMediaVideo(media=media[0]))
    if media_list:
        if caption:
            media_list[-1].caption = caption
        try:
            await message.answer_media_group(media_list)
        except TelegramBadRequest as err:
            await simple_media(message, 'ERROR_SORRY')


async def game_answer(message: Message, telegram_media_id: Union[int, str, InputFile] = None, text: str = None,
                      reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                                          ReplyKeyboardRemove, ForceReply, None] = None):
    if telegram_media_id is not None:
        try:
            return await message.answer_photo(telegram_media_id, caption=text, reply_markup=reply_markup)
        except TelegramBadRequest:
            try:
                return await message.answer_video(telegram_media_id, caption=text, reply_markup=reply_markup)
            except TelegramBadRequest as error:
                print(error)
    else:
        await message.answer(text, reply_markup=reply_markup, disable_web_page_preview=True)


def percentage_replace(text: str, symbol: str, part: int, base: int):
    try:
        perc = part / base * 100
    except ZeroDivisionError:
        perc = 0
    return text.replace(symbol, str(round(perc)))


def change_number_format(number:int):
    return '{0:,}'.format(number).replace(',', ' ')


class CoolPercReplacer:
    """
    Easy replacer for percentage.\n
    text: text where replace is needed\n
    base: base number to calculate (100%)
    """
    def __init__(self, text: str, base: int):
        self.text = text
        self.base = base

    def __repr__(self):
        return self.text

    def __call__(self, *args, **kwargs):
        return str(self.text)

    def replace(self, symbol: str, part: int, *args, temp_base: int = None, just_replace: bool = False):
        """symbol: placeholder needed to be replaced ('AA')\n
        part: number to calculate percent from base\n
        temp_base: replace object base (100%) for this calculation"""
        temp_base = 100 if just_replace else temp_base
        perc = self.perc(part, temp_base=temp_base)
        self.text = self.text.replace(symbol, str(perc))

    def perc(self, part, *args, temp_base: int = None):
        whole = temp_base if temp_base else self.base
        try:
            perc = part / whole * 100
        except ZeroDivisionError:
            perc = 0
        return round(perc, 1)




    @staticmethod
    async def make_sorted_statistics_dict(new_statistics_column: str, full_list: list, reverse: bool = True):
        base_number = await mongo_count_docs('database', 'statistics_new', {new_statistics_column: {'$exists': True}})
        main_dict = dict()
        for item in full_list:
            item_number = await mongo_count_docs('database', 'statistics_new', {new_statistics_column: item})
            main_dict[item] = round(item_number / base_number * 100) if base_number else 0
        return dict(sorted(main_dict.items(), key=lambda x: x[1], reverse=reverse))

async def get_time_from_war_started():
    now = datetime.now().date()
    old = datetime(year=2022, month=2, day=24).date()
    day = now-old
    return day.days

async def bot_send_spam(bot: Bot, user_id: Union[int, str], telegram_media_id: Union[int, InputFile] = None,
                        text: str = None, reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                                                              ReplyKeyboardRemove, ForceReply, None] = None):
    try:
        if telegram_media_id is not None:
            try:
                return await bot.send_photo(user_id, photo=telegram_media_id, caption=text, reply_markup=reply_markup)
            except TelegramBadRequest as error:
                print(error)
                try:
                    return await bot.send_video(user_id, video=telegram_media_id, caption=text,
                                                reply_markup=reply_markup)
                except TelegramBadRequest as error:
                    print(error)
        else:
            await bot.send_message(user_id, text=text, reply_markup=reply_markup, disable_web_page_preview=True)
    except TelegramForbiddenError as er:
        await logg.get_error(f'{er}')


async def dynamic_media_answer(message: Message, similarity_tag: str, row_number: int,
                               reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                                                   ForceReply, None] = None):
    media = (await sql_select_row_like('assets', row_number, {'name': similarity_tag}))[0]
    try:
        text = (await sql_select_row_like('texts', row_number, {'name': similarity_tag}))[0]
    except TypeError:
        text = None
    print(text)
    await game_answer(message, media, text, reply_markup)


async def ref_master(bot: Bot, link: str | int):
    return f'https://t.me/{(await bot.get_me()).username.replace(" ", "_")}?start={str(link)}'


async def day_counter(user: User):
    user_info = await mongo_select_info(user.id)
    date_start = user_info['datetime']
    time_now = datetime.now()
    result_time = time_now - date_start
    days, seconds = result_time.days, result_time.seconds
    hs = days * 24 + seconds // 3600
    hours = hs - days * 24
    minutes = (seconds % 3600) // 60

    if days >= 1:
        time = f"{days} д. {hours} ч. {minutes} мин"
    else:
        time = f"{hours} ч. {minutes} мин"
    return time


async def ref_spy_sender(bot: Bot, child_telegram_id: str | int, message_to_send: str, replace_dict: dict):
    data = await mongo_ez_find_one('database', 'userinfo', {'_id': int(child_telegram_id)})
    parent_id, name_surname, username = data['ref_parent'], data['name_surname'], data['username']
    if name_surname:
        replace_dict['[CHILD_NAME]'] = name_surname
    elif username:
        replace_dict['[CHILD_NAME]'] = username
    else:
        replace_dict['[CHILD_NAME]'] = f'пользователь с id {child_telegram_id}'
    for key in replace_dict:
        message_to_send = message_to_send.replace(key, replace_dict[key])
    try:
        await bot.send_message(parent_id, message_to_send)
    except TelegramBadRequest as error:
        await logg.get_error(f"Bad referal parent!! | {error}", __file__)


class MasterCommander:

    def __init__(self, bot: Bot, scope_lvl: str = 'default', chat_id: int = None, user_id: int = None):
        self.bot = bot
        if scope_lvl == 'default':
            self.scope = BotCommandScopeDefault()
        elif scope_lvl == 'all_private_chats':
            self.scope = BotCommandScopeAllPrivateChats()
        elif scope_lvl == 'all_group_chats':
            self.scope = BotCommandScopeAllGroupChats()
        elif scope_lvl == 'all_chat_administrators':
            self.scope = BotCommandScopeAllChatAdministrators()
        elif scope_lvl == 'chat' and chat_id:
            self.scope = BotCommandScopeChat(chat_id=chat_id)
        elif scope_lvl == 'chat_administrators' and chat_id:
            self.scope = BotCommandScopeChatAdministrators(chat_id=chat_id)
        elif scope_lvl == 'chat_member' and chat_id and user_id:
            self.scope = BotCommandScopeChatMember(chat_id=chat_id, user_id=user_id)

    async def clear(self):
        await self.bot.delete_my_commands(scope=self.scope)

    async def add(self, new_commands: dict, check_default_scope: bool = True):
        """Pass to this method dictionaty, where keys are commands and values is commands descriptions:\n
        new_commands = {'comm1': 'comm1 description', 'comm2': 'comm1 description'}"""
        command_list = await self.bot.get_my_commands(scope=self.scope)
        if check_default_scope:
            command_list.extend(await self.bot.get_my_commands(scope=BotCommandScopeDefault()))
        for command in new_commands:
            command_list.append(BotCommand(command=command, description=new_commands[command]))
        await self.bot.set_my_commands(commands=command_list, scope=self.scope)

    async def rewrite(self, new_commands: dict):
        """This method is similar to .add but will rewrite all commands listm no matter what commands are avaliable"""
        command_list = list()
        for command in new_commands:
            command_list.append(BotCommand(command=command, description=new_commands[command]))
        await self.bot.set_my_commands(commands=command_list, scope=self.scope)


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
            except Exception as err:
                print(err)
        await message.answer('Это все медиа в базе данных. Для всех медиа, '
                             'для которых не было выдана ошибка, теги теперь привязаны к этому боту.')

    @staticmethod
    async def fire(message: Message, bot: Bot):
        all_media_names = await data_getter('SELECT name FROM assets;')
        for name in all_media_names:
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
        await message.answer(
            'Все имеющиеся в базе медиа, для которых удалось найти валидный тег, '
            'были сохрнены в папку /resources/media директории бота')

    @staticmethod
    async def roost(message: Message, bot: Bot):
        await message.answer('----------------------ПОСЛЕ ЭТОЙ ЧЕРТЫ МЕДИА----------------------')
        all_media = await data_getter('SELECT * FROM assets;')
        for media in all_media:
            try:
                await bot.send_video(message.from_user.id, media[0], caption=media[1])
                await asyncio.sleep(0.5)
            except TelegramBadRequest:
                try:
                    await bot.send_photo(message.from_user.id, media[0], caption=media[1])
                    await asyncio.sleep(0.5)
                except TelegramBadRequest:
                    print(f'There no {media[0]} name')
        await message.answer('----------------------ЭТО ЧЕРТА, ЗА КОТОРОЙ КОНЧАЮТСЯ МЕДИА----------------------')


async def happy_tester(bot):
    redis = bata.all_data().get_data_red()
    g = git.Git(os.getcwd())
    # Вот это форматирование создает проблемы, его надо бы убрать
    loginfo = g.log('--pretty=format:%s || %an')
    old_log_set = redis.smembers('LastCommies')
    new_log_set = set([commname for commname in loginfo.split('\n') if commname.find('OTPOR-') != -1])
    redis.sadd('LastCommies', *new_log_set)
    diff = new_log_set - old_log_set
    botname = (await bot.get_me()).username
    # s_bot = await SpaceBot.rise()
    if len(diff) != 0:
        string, space_string, count = '', '', 0
        message_list = list()
        for comm in diff:
            count += 1
            string = string + '\n' + str(count) + '. ' + comm
            space_string = space_string + '\n' + str(count) + '. ' + comm[:comm.find("||")]
            if count % 13 == 0 or count == len(diff):
                message_list.append(string)
                string = ''
        try:
            await bot.send_message(bata.all_data().commichannel,
                                   f'[{datetime.now().strftime("%H:%M")}] Bot @{botname} is up, detected new commits:')
            for msg in message_list:
                await bot.send_message(bata.all_data().commichannel, msg)
        except TelegramBadRequest as exc:
            print(f'BOT NOT IN CHANNEL AND THIS MESSAGE NEED TO BE IN LOGS\n{exc}')
        print(f'[{datetime.now().strftime("%H:%M")}] Bot is up, detected new commits:{message_list}')
    else:
        print(f'[{datetime.now().strftime("%H:%M")}] Bot is up, shore is clear: no new commits here')
        try:
            await bot.send_message(bata.all_data().commichannel, f'Bot {botname}'
                                                                 f' was restarted without interesting commits')
        except TelegramBadRequest:
            print('Bot thinks there is no commits, and cant write it to channel')
    await bot.session.close()
