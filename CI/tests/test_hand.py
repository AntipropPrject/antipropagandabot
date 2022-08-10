import os
from random import randint

from aiogram import Router, Bot, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.types import Message


class TestStates(StatesGroup):
    one = State()
    two = State()


router = Router()


@router.message((F.from_user.id == int(os.getenv('TEST_USER_ID'))), commands=['smoke_test'])
async def smoketesting(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(TestStates.one)
    numbear = randint(0, 66666)
    msg = await message.answer(f'{numbear}')
    if msg.text == str(numbear):
        await bot.delete_message(msg.chat.id, msg.message_id)
        msg = await message.answer(f'Bot {(await bot.get_me()).first_name}\nSmoketesting was successfull')
        await state.clear()
        await bot.session.close()
    return msg.text[-28:]
