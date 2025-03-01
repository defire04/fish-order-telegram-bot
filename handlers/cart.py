import telebot
from telebot.types import CallbackQuery, Message
from services.product_service import get_product
from services.order_service import create_new_order_ext
from keyboards.inline import make_main_menu
from data.config import ADMIN_IDS

user_carts = {}
temp_quantities = {}
user_flow = {}

def register_cart_handlers(bot: telebot.TeleBot):

    @bot.callback_query_handler(func=lambda call: call.data.startswith("viewprod:"))
    def callback_view_product(call: CallbackQuery):
        pid = int(call.data.split(":")[1])
        p = get_product(pid)
        if not p:
            bot.answer_callback_query(call.id, "Товар не знайдено.")
            return
        temp_quantities[(call.from_user.id, pid)] = 1
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        send_product_view(bot, call.message.chat.id, p, 1)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("qty:"))
    def callback_change_quantity(call: CallbackQuery):
        parts = call.data.split(":")
        action = parts[1]
        pid = int(parts[2])
        key = (call.from_user.id, pid)
        if key not in temp_quantities:
            temp_quantities[key] = 1
        qty = temp_quantities[key]
        pr = get_product(pid)
        if not pr:
            bot.answer_callback_query(call.id, "Товар не знайдено.")
            return

        if action == "inc":
            qty += 1
            temp_quantities[key] = qty
            bot.answer_callback_query(call.id, f"Кількість: {qty}")
            send_updated_product_view(bot, call.message.chat.id, call.message.message_id, pr, qty)
        elif action == "dec":
            if qty > 1:
                qty -= 1
                temp_quantities[key] = qty
                bot.answer_callback_query(call.id, f"Кількість: {qty}")
                send_updated_product_view(bot, call.message.chat.id, call.message.message_id, pr, qty)
            else:
                bot.answer_callback_query(call.id, "Мінімальна кількість 1")
        elif action == "add":
            if call.from_user.id not in user_carts:
                user_carts[call.from_user.id] = {}
            if pid not in user_carts[call.from_user.id]:
                user_carts[call.from_user.id][pid] = 0
            user_carts[call.from_user.id][pid] += qty
            temp_quantities.pop(key, None)
            bot.answer_callback_query(call.id, f"Додано в кошик x{qty}")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(call.message.chat.id, "Товар додано до кошика!", reply_markup=make_main_menu())

    @bot.callback_query_handler(func=lambda call: call.data == "cart_clear")
    def on_cart_clear(call: CallbackQuery):
        user_carts[call.from_user.id] = {}
        bot.answer_callback_query(call.id, "Кошик очищено!")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, "Кошик очищено.", reply_markup=make_main_menu())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delivery:"))
    def handle_delivery_method(call: CallbackQuery):
        m = call.data.split(":", 1)[1]
        if call.from_user.id not in user_flow:
            user_flow[call.from_user.id] = {}
        user_flow[call.from_user.id]["delivery_method"] = m

        if m == "samov":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            finalize_order(bot, call.from_user.id, call.message.chat.id, "Самовивіз")
        elif m == "cur":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            ms = bot.send_message(call.message.chat.id, "Вкажіть адресу для кур'єра:")
            bot.register_next_step_handler(ms, lambda mm: handle_address(bot, mm, "cur"))
        elif m in ["nova", "ukr"]:
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            ms2 = bot.send_message(call.message.chat.id, "Вкажіть номер відділення:")
            bot.register_next_step_handler(ms2, lambda mm: handle_address(bot, mm, m))

    def handle_address(bot: telebot.TeleBot, msg: Message, method):
        user_flow[msg.from_user.id]["address"] = msg.text.strip()
        finalize_order(bot, msg.from_user.id, msg.chat.id, method)

    def finalize_order(bot: telebot.TeleBot, user_id: int, chat_id: int, method):
        c = user_carts.get(user_id, {})
        if not c:
            bot.send_message(chat_id, "Кошик порожній. Скасовано.", reply_markup=make_main_menu())
            return
        phone = user_flow[user_id].get("phone", "")
        comment = user_flow[user_id].get("comment", "")
        fn = user_flow[user_id].get("full_name", "")
        addr = ""
        if method == "samov":
            addr = "Самовивіз"
        else:
            addr = user_flow[user_id].get("address", "")

        from services.order_service import create_new_order_ext
        oid = create_new_order_ext(
            user_id, c,
            method, addr,
            phone, comment,
            fn  # pass full_name
        )
        user_carts[user_id] = {}
        user_flow.pop(user_id, None)
        bot.send_message(chat_id, f"Вітаю, замовлення №{oid} оформлено! Дякуємо!\n Оператор з вами зв'яжеться для уточнення деталей.", reply_markup=make_main_menu())

def show_cart(bot: telebot.TeleBot, user_id: int, chat_id: int):
    c = user_carts.get(user_id, {})
    if not c:
        bot.send_message(chat_id, "Ваш кошик порожній.", reply_markup=make_main_menu())
        return
    text = "Ваш кошик:\n"
    total = 0
    from services.product_service import get_product
    for pid, q in c.items():
        pr = get_product(pid)
        if pr:
            s = pr["price"] * q
            total += s
            text += f"{pr['name']} x {q} = {s} грн\n"
    text += f"\nЗагальна сума: {total} грн"

    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("Очистити кошик", callback_data="cart_clear"))
    kb.add(telebot.types.InlineKeyboardButton("Оформити замовлення", callback_data="menu_order"))
    kb.add(telebot.types.InlineKeyboardButton("Назад", callback_data="go_main"))
    bot.send_message(chat_id, text, reply_markup=kb)

def send_product_view(bot: telebot.TeleBot, chat_id: int, prod, qty: int):
    brand = prod['brand']
    cap = f"<b>{prod['name']}</b> ({brand})\nЦіна: {prod['price']} грн\n\nКількість: {qty}"

    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(
        telebot.types.InlineKeyboardButton("–", callback_data=f"qty:dec:{prod['id']}"),
        telebot.types.InlineKeyboardButton(str(qty), callback_data="none"),
        telebot.types.InlineKeyboardButton("+", callback_data=f"qty:inc:{prod['id']}")
    )
    kb.add(telebot.types.InlineKeyboardButton("Додати в кошик", callback_data=f"qty:add:{prod['id']}"))

    kb.add(telebot.types.InlineKeyboardButton("Назад", callback_data=f"back_to_brand:{brand}"))

    if prod['photo_url']:
        bot.send_photo(chat_id, prod['photo_url'], caption=cap, parse_mode="HTML", reply_markup=kb)
    else:
        bot.send_message(chat_id, cap, parse_mode="HTML", reply_markup=kb)


def send_updated_product_view(bot: telebot.TeleBot, chat_id: int, message_id: int, prod, qty: int):
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass
    send_product_view(bot, chat_id, prod, qty)

def confirm_order(bot: telebot.TeleBot, call: CallbackQuery):
    c = user_carts.get(call.from_user.id, {})
    if not c:
        bot.answer_callback_query(call.id, "Кошик порожній.")
        return
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    user_flow[call.from_user.id] = {}
    msg = bot.send_message(call.message.chat.id, "Вкажіть ваше ПІБ (повне ім'я):")
    bot.register_next_step_handler(msg, lambda m: ask_fio(bot, m))

def ask_fio(bot: telebot.TeleBot, msg: Message):
    user_flow[msg.from_user.id]["full_name"] = msg.text.strip()
    nxt = bot.send_message(msg.chat.id, "Вкажіть свій номер телефону:")
    bot.register_next_step_handler(nxt, lambda mm: ask_comment(bot, mm))

def ask_comment(bot: telebot.TeleBot, msg: Message):
    user_flow[msg.from_user.id]["phone"] = msg.text.strip()
    nxt = bot.send_message(msg.chat.id, "Якщо маєте коментар, напишіть тут (або «Немає»):")
    bot.register_next_step_handler(nxt, lambda mm: ask_delivery_method(bot, mm))

def ask_delivery_method(bot: telebot.TeleBot, msg: Message):
    user_flow[msg.from_user.id]["comment"] = msg.text.strip()
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("Нова Пошта", callback_data="delivery:nova"),
        telebot.types.InlineKeyboardButton("УкрПошта", callback_data="delivery:ukr")
    )
    kb.add(
        telebot.types.InlineKeyboardButton("Кур'єр", callback_data="delivery:cur"),
        telebot.types.InlineKeyboardButton("Самовивіз", callback_data="delivery:samov")
    )
    bot.send_message(msg.chat.id, "Оберіть спосіб доставки:", reply_markup=kb)
