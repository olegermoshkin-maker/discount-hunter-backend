from celery import Celery
import requests
import time
from os import getenv
from dotenv import load_dotenv
from parsers import parse_all_markets

load_dotenv(dotenv_path='.env')

broker_url = getenv('REDIS_URL') or 'redis://localhost:6379/0'
celery_app = Celery('tasks', broker=broker_url)

@celery_app.task
def monitor_prices(user_id, product_id):
    while True:
        prices = parse_all_markets(product_id)  # Парсим по ID как query
        min_price = min(p['price'] for p in prices)
        # Сравни с БД, если дроп >10% — алерт
        send_alert.delay(user_id, f"Дроп цены на {product_id}! Теперь {min_price}₽")
        time.sleep(900)  # 15 мин

@celery_app.task
def send_alert(user_id, message):
    bot_token = getenv('BOT_TOKEN')
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', 
                  data={'chat_id': user_id, 'text': message})