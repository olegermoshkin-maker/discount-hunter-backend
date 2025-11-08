from database import get_db_connection

def handle_referral(ref_code, new_user_id):
    # Парсим ref_code на referrer_id
    referrer_id = int(ref_code.split('_')[1])  # Пример
    conn = get_db_connection()
    cur = conn.cursor()
    # Добавь бонусы
    cur.execute("UPDATE users SET free_requests = free_requests + 5 WHERE id = %s", (referrer_id,))
    cur.execute("UPDATE users SET free_requests = free_requests + 5 WHERE id = %s", (new_user_id,))
    # Лог в таблицу
    cur.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (%s, %s)", (referrer_id, new_user_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"bonus": "Оба +5 премиум запросов! Делись дальше."}