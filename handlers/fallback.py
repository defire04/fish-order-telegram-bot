from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import main_reply_keyboard

fallback_router = Router()

@fallback_router.message(F.text)
async def fallback_message(message: Message):
    await message.answer(
        "Невідоме повідомлення. Скористайтеся кнопками нижче:",
        reply_markup=main_reply_keyboard(message.from_user.id)
    )