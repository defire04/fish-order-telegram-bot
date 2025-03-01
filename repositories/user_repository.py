from data.db import get_connection

def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

def create_user(user_id, full_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (id, full_name) VALUES (?, ?)",
                (user_id, full_name))
    conn.commit()
    conn.close()
