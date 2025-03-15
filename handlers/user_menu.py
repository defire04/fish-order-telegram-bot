import random

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from data.config import ADMIN_IDS
from handlers.admin_menu import show_admin_menu
from handlers.cart import confirm_order, show_cart
from keyboards.inline import make_main_menu, make_products_list, make_brand_menu
from keyboards.reply import main_reply_keyboard
from services.order_service import get_user_orders, get_items_for_order
from services.product_service import get_all_brands, list_products_by_brand
from services.user_service import ensure_user_exists

user_router = Router()

greetings = [
    "Привіт, {}! Радий тебе бачити!",
    "Вітаю, {}! Сподіваюся, у тебе все добре!",
]

FRIENDLY_EMOJI = "👋"


@user_router.message(Command("start"))
async def cmd_start(message: Message):
    user_fullname = (message.from_user.first_name or '') + ' ' + (message.from_user.last_name or '')
    user_fullname = user_fullname.strip()
    ensure_user_exists(message.from_user.id, user_fullname)

    await message.answer(FRIENDLY_EMOJI)

    greet = random.choice(greetings).format(user_fullname)
    text = greet + "\nТут ти можеш переглянути наші квадроцикли, додати товар до кошика та оформити замовлення."

    await message.answer(
        text,
        reply_markup=main_reply_keyboard(message.from_user.id)
    )


@user_router.message(F.text.in_(["Головне меню", "Каталог", "Переглянути кошик", "Мої замовлення", "Адмін-меню"]))
async def on_reply_menu(message: Message):
    if message.text == "Головне меню":
        await message.answer(
            "Обери, що хочеш зробити:",
            reply_markup=make_main_menu()
        )

    elif message.text == "Каталог":
        brands = get_all_brands()
        if not brands:
            await message.answer(
                "Зараз товари відсутні. Повернись пізніше або запитай щось іще!",
                reply_markup=main_reply_keyboard(message.from_user.id)
            )
            return
        await message.answer(
            "Ось наші бренди. Обирай, будь ласка:",
            reply_markup=make_brand_menu(brands)
        )

    elif message.text == "Переглянути кошик":
        await show_cart(message)

    elif message.text == "Мої замовлення":
        orders = get_user_orders(message.from_user.id)

        if not orders:
            await message.answer(
                "У тебе поки немає замовлень. Може, зазирнемо в каталог?",
                reply_markup=main_reply_keyboard(message.from_user.id)
            )
        else:
            txt = "Ось твої попередні замовлення:\n"
            for o in orders:
                txt += f"№{o['id']} | сума {o['total_price']} грн | {o['created_at']}\n"
                items = get_items_for_order(o["id"])
                if items:
                    txt += "Товари:\n"
                    for it in items:
                        subtotal = it["product_price"] * it["quantity"]
                        txt += f"  {it['product_name']} x {it['quantity']} = {subtotal} грн\n"
                txt += "--------------------------------\n"
            txt += "\nЯкщо маєш питання, пиши нам!"

            await message.answer(
                txt,
                reply_markup=main_reply_keyboard(message.from_user.id)
            )

    elif message.text == "Адмін-меню":
        if message.from_user.id in ADMIN_IDS:
            await show_admin_menu(message)
        else:
            await message.answer("Недостатньо прав.")


@user_router.callback_query(F.data.in_(["menu_cart", "menu_order", "go_main"]))
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass

    if callback.data == "menu_cart":
        await show_cart(callback.message, callback.from_user.id)

    elif callback.data == "menu_order":
        await confirm_order(callback, state)

    elif callback.data == "go_main":
        await callback.message.answer(
            "Головне меню:",
            reply_markup=make_main_menu()
        )

    await callback.answer()


@user_router.callback_query(F.data.startswith("brand:"))
async def on_choose_brand(callback: CallbackQuery):
    brand = callback.data.split(":", 1)[1]
    products = list_products_by_brand(brand)

    try:
        await callback.message.delete()
    except:
        pass

    if not products:
        await callback.message.answer(
            f"Поки що товарів бренду {brand} немає.",
            reply_markup=main_reply_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return

    kb = make_products_list(products)
    await callback.message.answer(
        f"Товари бренду {brand}:",
        reply_markup=kb
    )

    await callback.answer()


@user_router.callback_query(F.data == "menu_catalog")
async def on_menu_catalog(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    brands = get_all_brands()
    if not brands:
        await callback.message.answer(
            "Товари відсутні.",
            reply_markup=main_reply_keyboard(callback.from_user.id)
        )
        await callback.answer()
        return

    kb = make_brand_menu(brands)
    await callback.message.answer(
        "Будь ласка, оберіть бренд:",
        reply_markup=kb
    )

    await callback.answer()


@user_router.callback_query(F.data.startswith("back_to_brand:"))
async def on_back_to_brand(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    brand = callback.data.split(":", 1)[1]
    products = list_products_by_brand(brand)

    if not products:
        await callback.message.answer(
            f"Поки що товарів бренду {brand} немає."
        )
        await callback.answer()
        return

    kb = make_products_list(products)
    await callback.message.answer(
        f"Товари бренду {brand}:",
        reply_markup=kb
    )

    await callback.answer()
