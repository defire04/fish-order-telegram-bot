import telebot
from telebot.types import Message
from keyboards.reply import main_reply_keyboard

def register_fallback(bot: telebot.TeleBot):
    @bot.message_handler(content_types=['text'], func=lambda m: True)
    def fallback_message(message: Message):
        bot.send_message(
            message.chat.id,
            "Невідоме повідомлення. Скористайтеся кнопками нижче:",
            reply_markup=main_reply_keyboard(message.from_user.id)
        )
