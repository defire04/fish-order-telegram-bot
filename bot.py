import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from data.config import BOT_TOKEN
from data.db import init_db
from handlers.admin_menu import admin_router
from handlers.cart import cart_router
from handlers.fallback import fallback_router
from handlers.user_menu import user_router

logging.basicConfig(level=logging.INFO)


async def main():
    # Ініціалізація БД
    init_db()

    # Створюємо екземпляр бота
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties())

    # Створюємо диспетчер
    dp = Dispatcher()

    # Підключаємо (include) наші роутери
    dp.include_router(user_router)
    dp.include_router(cart_router)
    dp.include_router(admin_router)
    dp.include_router(fallback_router)

    # Запускаємо полінг
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
