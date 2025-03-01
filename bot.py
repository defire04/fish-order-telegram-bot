import telebot

from data.config import BOT_TOKEN
from data.db import init_db
from handlers.admin_menu import register_admin_menu
from handlers.cart import register_cart_handlers
from handlers.fallback import register_fallback
from handlers.user_menu import register_user_menu


def main():
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

    init_db()

    register_user_menu(bot)
    register_cart_handlers(bot)
    register_admin_menu(bot)
    register_fallback(bot)

    print("Bot started...")
    bot.infinity_polling()


if __name__ == "__main__":
    main()
