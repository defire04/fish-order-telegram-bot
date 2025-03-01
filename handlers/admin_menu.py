
import telebot
from telebot.types import Message, CallbackQuery
from data.config import ADMIN_IDS
from services.product_service import add_new_product, remove_product, list_all_products
from services.order_service import get_stats, get_all_orders

def register_admin_menu(bot: telebot.TeleBot):

    @bot.message_handler(func=lambda m: m.text == "Адмін-меню")
    def admin_menu_text(message: Message):
        if message.from_user.id not in ADMIN_IDS:
            return
        show_admin_menu(bot, message.chat.id)

    @bot.message_handler(commands=['admin'])
    def cmd_admin(message: Message):
        if message.from_user.id not in ADMIN_IDS:
            return
        show_admin_menu(bot, message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
    def callback_admin(call: CallbackQuery):
        if call.from_user.id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "Недостатньо прав.")
            return

        d = call.data
        if d == "admin_add_product":
            msg = bot.send_message(call.message.chat.id, "Введіть: Назва|Ціна|Бренд|Фото URL")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.register_next_step_handler(msg, process_add_product)

        elif d == "admin_list_products":
            products = list_all_products()
            txt = "Список товарів:\n"
            if not products:
                txt += "Порожньо."
            else:
                for p in products:
                    txt += f"ID {p['id']}: {p['name']} ({p['brand']}) - {p['price']} грн\n"
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(call.message.chat.id, txt)
            show_admin_menu(bot, call.message.chat.id)

        elif d == "admin_del_product":
            msg = bot.send_message(call.message.chat.id, "Введіть ID товару:")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.register_next_step_handler(msg, process_del_product)

        elif d == "admin_stats":
            c, t = get_stats()
            txt = f"Статистика:\nЗамовлень: {c}\nСума: {t}"
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(call.message.chat.id, txt)
            show_admin_menu(bot, call.message.chat.id)

        elif d == "admin_list_orders":
            orders = get_all_orders()
            text = "Список замовлень:\n"
            if not orders:
                text += "Немає."
            else:
                for o in orders:
                    text += (
                        f"Order №{o['id']}\n"
                        f"User id: {o['user_id']}\n"
                        f"User: {o['full_name']}\n"
                        f"Sum: {o['total_price']}\n"
                        f"Delivery: {o['delivery_method']}\n"
                        f"Address: {o['address']}\n"
                        f"Phone: {o['phone']}\n"
                        f"Comment: {o['comment']}\n"
                        f"Date: {o['created_at']}\n"
                        "--------------------------------\n"
                    )
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(call.message.chat.id, text)
            show_admin_menu(bot, call.message.chat.id)

        elif d == "admin_exit":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(call.message.chat.id, "Вихід з адмін-меню.")

    def process_add_product(msg: Message):
        if msg.from_user.id not in ADMIN_IDS:
            return
        arr = msg.text.split("|")
        if len(arr) < 4:
            bot.send_message(msg.chat.id, "Невірний формат.")
            show_admin_menu(bot, msg.chat.id)
            return
        n = arr[0].strip()
        pr = float(arr[1].strip())
        br = arr[2].strip()
        ph = arr[3].strip()
        add_new_product(n, pr, br, ph)
        bot.send_message(msg.chat.id, "Товар додано.")
        show_admin_menu(bot, msg.chat.id)

    def process_del_product(msg: Message):
        if msg.from_user.id not in ADMIN_IDS:
            return
        try:
            pid = int(msg.text)
        except:
            bot.send_message(msg.chat.id, "Невірний ID.")
            show_admin_menu(bot, msg.chat.id)
            return
        remove_product(pid)
        bot.send_message(msg.chat.id, "Товар видалено.")
        show_admin_menu(bot, msg.chat.id)

def show_admin_menu(bot: telebot.TeleBot, chat_id, old_msg_id=None):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Додати товар", callback_data="admin_add_product"))
    kb.add(InlineKeyboardButton("Список товарів", callback_data="admin_list_products"))
    kb.add(InlineKeyboardButton("Видалити товар", callback_data="admin_del_product"))
    kb.add(InlineKeyboardButton("Статистика", callback_data="admin_stats"))
    kb.add(InlineKeyboardButton("Замовлення", callback_data="admin_list_orders"))
    kb.add(InlineKeyboardButton("Вийти", callback_data="admin_exit"))
    txt = "Адмін-меню:"
    if old_msg_id:
        try:
            bot.delete_message(chat_id, old_msg_id)
        except:
            pass
        bot.send_message(chat_id, txt, reply_markup=kb)
    else:
        bot.send_message(chat_id, txt, reply_markup=kb)
