
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def make_main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Каталог", callback_data="menu_catalog"))
    kb.add(InlineKeyboardButton("Мій кошик", callback_data="menu_cart"))
    kb.add(InlineKeyboardButton("Оформити замовлення", callback_data="menu_order"))
    return kb

def make_admin_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Додати товар", callback_data="admin_add_product"))
    kb.add(InlineKeyboardButton("Видалити товар", callback_data="admin_del_product"))
    kb.add(InlineKeyboardButton("Статистика", callback_data="admin_stats"))
    kb.add(InlineKeyboardButton("Вихід", callback_data="go_main"))
    return kb

def make_brand_menu(brands):

    kb = InlineKeyboardMarkup()
    for b in brands:
        kb.add(InlineKeyboardButton(b, callback_data=f"brand:{b}"))
    kb.add(InlineKeyboardButton("Назад", callback_data="go_main"))
    return kb

def make_products_list(products):

    kb = InlineKeyboardMarkup()
    for p in products:
        text = f"{p['name']} - {p['price']} грн"
        kb.add(InlineKeyboardButton(text, callback_data=f"viewprod:{p['id']}"))
    kb.add(InlineKeyboardButton("Назад", callback_data="go_main"))
    return kb