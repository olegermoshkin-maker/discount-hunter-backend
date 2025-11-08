import requests
from bs4 import BeautifulSoup
import redis
from datetime import timedelta
from os import getenv
import os  # Для load_dotenv, если нужно

# Загружаем .env, на всякий
from dotenv import load_dotenv
load_dotenv()

redis_url = getenv('REDIS_URL')
if not redis_url or not redis_url.startswith(('redis://', 'rediss://')):
    print("🛡️ REDIS_URL хуёвый или отсутствует! Использую dummy (для теста, но в проде фикс env)")
    r = None  # Отключаем кэш, чтоб не падал
else:
    print(f"🔥 Redis подключён: {redis_url[:20]}...")  # Дебаг в логах Render
    r = redis.from_url(redis_url)

# Остальной код без изменений (parse_all_markets и функции)
def parse_all_markets(query):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    markets = {
        'Ozon': lambda: parse_ozon(query, headers),
        'Wildberries': lambda: parse_wb(query, headers),
        'Yandex Market': lambda: parse_yandex(query, headers),
        'Avito': lambda: parse_avito(query, headers),
        'AliExpress': lambda: parse_aliexpress(query, headers),
        'Lamoda': lambda: parse_lamoda(query, headers),
        'M.Video': lambda: parse_mvideo(query, headers)
    }
    products = []
    for market, func in markets.items():
        try:
            data = func()
            if data['price'] < 999999:
                data['market'] = market
                products.append(data)
        except Exception as e:
            print(f"{market} error: {e}")
    products.sort(key=lambda x: x['price'])
    return products[:10]

def parse_ozon(query, headers):
    url = f'https://www.ozon.ru/search/?text={query}'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    price_el = soup.find('span', {'data-widget': 'webPricePrice'})
    price = float(price_el.text.replace('₽', '').replace(' ', '')) if price_el else 999999
    return {'name': query, 'price': price, 'discount': 10, 'url': url, 'id': f'{query}_ozon'}

# Аналогично для остальных (адаптируй селекторы по свежим докам, 2025)
def parse_wb(query, headers):
    url = f'https://www.wildberries.ru/catalog/0/search.aspx?search={query}'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    price_el = soup.find('ins', class_='price__lower-price')
    price = float(price_el.text.replace('₽', '')) if price_el else 999999
    return {'name': query, 'price': price, 'discount': 15, 'url': url, 'id': f'{query}_wb'}

def parse_yandex(query, headers):
    url = f'https://market.yandex.ru/search?text={query}'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    price_el = soup.find('span', class_='snippet-card__price')
    price = float(price_el.text.replace('₽', '')) if price_el else 999999
    return {'name': query, 'price': price, 'discount': 20, 'url': url, 'id': f'{query}_yandex'}

def parse_avito(query, headers):
    url = f'https://www.avito.ru/all?q={query}'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    price_el = soup.find('span', class_='price-price-value_string')
    price = float(price_el.text.replace('₽', '')) if price_el else 999999
    return {'name': query, 'price': price, 'discount': 5, 'url': url, 'id': f'{query}_avito'}

def parse_aliexpress(query, headers):
    url = f'https://www.aliexpress.com/w/wholesale-{query.replace(" ", "-")}.html'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    price_el = soup.find('span', class_='multi--price--current')
    price = float(price_el.text.replace('$', '')) * 90 if price_el else 999999  # $ to ₽
    return {'name': query, 'price': price, 'discount': 30, 'url': url, 'id': f'{query}_ali'}

def parse_lamoda(query, headers):
    url = f'https://www.lamoda.ru/search/?q={query}'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    price_el = soup.find('span', class_='price')
    price = float(price_el.text.replace('₽', '')) if price_el else 999999
    return {'name': query, 'price': price, 'discount': 25, 'url': url, 'id': f'{query}_lamoda'}

def parse_mvideo(query, headers):
    url = f'https://www.mvideo.ru/search?q={query}'
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    price_el = soup.find('span', class_='price-num')
    price = float(price_el.text.replace('₽', '')) if price_el else 999999
    return {'name': query, 'price': price, 'discount': 10, 'url': url, 'id': f'{query}_mvideo'}