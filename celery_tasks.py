from celery import Celery
import requests
import time
from os import getenv
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

broker_url = getenv('REDIS_URL')
if not broker_url or not broker_url.startswith(('redis://', 'rediss://')):
    raise ValueError("🛡️ REDIS_URL invalid! Fix env vars, бро.")

celery_app = Celery('tasks', broker=broker_url)

@celery_app.task
def monitor_prices(user_id, product_id):
    print(f"🤑 Мониторим {user_id} на {product_id}")
    time.sleep(900)  # 15 мин, заглушка
    send_alert.delay(user_id, f"Дроп на {product_id}! 🤑")

@celery_app.task
def send_alert(user_id, message):
    bot_token = getenv('BOT_TOKEN')
    if bot_token:
        requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', 
                      data={'chat_id': user_id, 'text': message})
    print(f"📱 Алерту {user_id}: {message}")