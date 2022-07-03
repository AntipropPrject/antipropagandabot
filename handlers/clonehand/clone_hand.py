import asyncio
from typing import List
from aiogram import Router, F
from aiogram import types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from bata import all_data
from data_base.DBuse import poll_get, redis_just_one_read
from data_base.DBuse import sql_safe_select, data_getter, sql_safe_update
from filters.MapFilters import WebPropagandaFilter, TVPropagandaFilter, PplPropagandaFilter, PoliticsFilter
from handlers import true_resons_hand
from keyboards.map_keys import antip_why_kb, antip_killme_kb
from resources.all_polls import web_prop
from resources.other_lists import channels
from states.antiprop_states import propaganda_victim
from stats.stat import mongo_update_stat
from utilts import simple_media


router = Router()

router.message.filter(state=propaganda_victim)