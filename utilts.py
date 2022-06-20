import asyncio
from typing import Optional, Union

from aiogram import Router, F
from aiogram import types, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, ReplyKeyboardMarkup, ForceReply
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import bata
from data_base.DBuse import data_getter, poll_write, sql_safe_select, sql_safe_update, redis_delete_from_list, poll_get
from filters.All_filters import NaziFilter, RusHate_pr, NotNaziFilter
from handlers import true_resons_hand
from middleware import CounterMiddleware
from resources.all_polls import nazizm, nazizm_pr


async def simple_media(message: Message, tag: str,
                       reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                                           ReplyKeyboardRemove, ForceReply, None] = None):
    """
    You can use one tag. If there text with that tag, it will become caption
    """
    text = await sql_safe_select("text", "texts", {"name": tag})
    media = await sql_safe_select("t_id", "assets", {"name": tag})
    if text is not None:
        try:
            await message.answer_photo(media, caption=text, reply_markup=reply_markup)
        except TelegramBadRequest:
            await message.answer_video(media, caption=text, reply_markup=reply_markup)
    else:
        try:
            await message.answer_photo(media, reply_markup=reply_markup)
        except TelegramBadRequest:
            await message.answer_video(media, reply_markup=reply_markup)
