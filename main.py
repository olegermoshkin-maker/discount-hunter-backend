from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from parsers import parse_all_markets
from wishlist import add_to_wishlist, get_wishlist
from payments import create_yookassa_payment
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

class SearchData(BaseModel):
    query: str
    user_id: int

@app.post("/search")
async def search_discounts(data: SearchData):
    # Лимит для free (добавь БД-чек)
    products = parse_all_markets(data.query)
    for p in products:
        aff = os.getenv('AFF_OZON') or 'test'  # Адаптируй по market
        p['affiliateLink'] = p['url'] + f'?aff={aff}'
    # AI recs (cosine dummy)
    query_vec = np.array([hash(w) % 100 for w in data.query.split()])
    # ... матчи с products
    return {"products": products}

@app.post("/wishlist")
async def wishlist_endpoint(data: dict):
    return add_to_wishlist(data['productId'], data['userId'])

@app.get("/wishlist/{user_id}")
async def get_wishlist_endpoint(user_id: int):
    return get_wishlist(user_id)

@app.get("/payment")
async def payment(amount: float, period: str):
    return create_yookassa_payment(amount, period)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 8000)))