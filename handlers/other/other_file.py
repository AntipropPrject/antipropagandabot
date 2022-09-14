# import asyncio
#
# from aiogram import Router
# from aiogram import types
#
# from utilts import simple_media
#
# flags = {"throttling_key": "True"}
# router = Router()
#
#
# @router.message()
# async def empty(message: types.Message):
#     if str(message.content_type) == 'pinned_message':
#         await asyncio.sleep(0.8)
#         await message.delete()
#     else:
#         await simple_media(message, 'other_text')
