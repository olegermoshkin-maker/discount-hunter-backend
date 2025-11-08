from database import get_db_connection
from celery_tasks import monitor_prices
from os import getenv

def add_to_wishlist(product_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT premium_status FROM users WHERE tg_id = %s", (user_id,))
    row = cur.fetchone()
    if not row or not row[0]:
        conn.close()
        return {"status": "Купи премиум для вишлиста!"}
    cur.execute("INSERT INTO wishlist (user_id, product_id, name, current_price) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", 
                (user_id, product_id, product_id, 0))
    conn.commit()
    cur.close()
    conn.close()
    monitor_prices.delay(user_id, product_id)
    return {"status": "Добавлено! Алерт на дропе."}

def get_wishlist(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM wishlist WHERE user_id = (SELECT id FROM users WHERE tg_id = %s)", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"wishlist": [dict(row) for row in rows]}