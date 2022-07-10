from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from filters.isAdmin import IsAdmin
from keyboards.admin_keys import main_admin_keyboard
from log import logg
from states.admin_states import admin

router = Router()


@router.message(IsAdmin(), commands=["testadmingames"])
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Вошел в режим редактирования игр")
    await message.answer("Добро пожаловать в режим редактирования игр, выберете игру.",
                         reply_markup=main_admin_keyboard(message.from_user.id))

@router.message(IsAdmin(), (F.text.contains('Ошибка или ложь(пропагандисты)')))
async def admin_home(message: types.Message, state: FSMContext):
    await state.clear()
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Ошибка или ложь(пропагандисты) - выбор пропагандиста")
    nmrkup = ReplyKeyboardBuilder()
    nmrkup.row(types.KeyboardButton(text="Назад"))
    await message.answer("Отправьте фамилию пропагандиста без опечаток(ТОЛЬКО ФАМИЛИЮ)",
                         reply_markup=nmrkup.as_markup(resize_keyboard=True))
    await state.set_state(admin.addingMistakeOrLie)



@router.message(IsAdmin(), state=admin.addingMistakeOrLie)
async def menu(message: types.Message, state: FSMContext):
    await logg.admin_logs(message.from_user.id, message.from_user.username, "Ошибка или ложь(пропагандисты) - редактирование")
    await state.clear()
    await message.answer("Отправьте новый медиафайл. В качестве подписи отправьте фамилию пропагандиста без опечаток(ТОЛЬКО ФАМИЛИЮ)", reply_markup=main_admin_keyboard(message.from_user.id))
    await state.set_state(admin.addingMistakeOrLie)


