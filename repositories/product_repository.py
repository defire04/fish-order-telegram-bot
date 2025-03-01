
from data.db import get_connection

def create_product(name, price, brand, photo_url):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (name, price, brand, photo_url)
        VALUES (?, ?, ?, ?)
    """, (name, price, brand, photo_url))
    conn.commit()
    conn.close()

def get_all_brands():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT brand FROM products ORDER BY brand ASC")
    rows = cur.fetchall()
    conn.close()
    return [r["brand"] for r in rows]

def get_products_by_brand(brand):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE brand = ?", (brand,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_product_by_id(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id=?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return row

def delete_product(product_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
