from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from data.config import ADMIN_IDS

def main_reply_keyboard(user_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("Головне меню"), KeyboardButton("Каталог"))
    kb.add(KeyboardButton("Переглянути кошик"), KeyboardButton("Мої замовлення"))
    if user_id in ADMIN_IDS:
        kb.add(KeyboardButton("Адмін-меню"))
    return kb
