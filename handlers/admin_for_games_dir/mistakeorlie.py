from aiogram import Router

from states.admin_states import admin

router = Router()
router.message.filter(state=admin)




