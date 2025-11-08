from yookassa import Configuration, Payment
from os import getenv

Configuration.account_id = getenv('YOOKASSA_SHOP_ID')
Configuration.secret_key = getenv('YOOKASSA_SECRET')

def create_yookassa_payment(amount, period):
    payment = Payment.create({
        "amount": {"value": str(amount), "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://t.me/DiscountHunterBestBot"},
        "description": f"Премиум {period}"
    })
    return {"url": payment.confirmation.confirmation_url}