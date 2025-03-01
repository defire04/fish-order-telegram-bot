
from data.db import get_connection

def get_all_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def create_order_ext(user_id, total_price, delivery_method, address, phone, comment, full_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (
            user_id, total_price,
            delivery_method, address,
            phone, comment, full_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, total_price, delivery_method, address, phone, comment, full_name))
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id


def add_order_item(order_id, product_id, quantity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO order_items (order_id, product_id, quantity)
        VALUES (?, ?, ?)
    """, (order_id, product_id, quantity))
    conn.commit()
    conn.close()

def get_orders_by_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_orders_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM orders")
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0

def get_total_revenue():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(total_price) as total FROM orders")
    row = cur.fetchone()
    conn.close()
    return row["total"] if row["total"] else 0.0

def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    rows = cur.fetchall()
    conn.close()
    return rows
