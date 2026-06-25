import requests
import os

try:
    from config import GOLD_API_KEY
except ImportError:
    GOLD_API_KEY ="goldapi-a2afe631f501f135c2f77f4ab2ae3cef-io"

class GoldApiService:
    API_URL = "https://www.goldapi.io/api/XAU/USD"
    API_KEY = GOLD_API_KEY

    TROY_OUNCE_TO_GRAM = 31.1034768

    @staticmethod
    def get_live_price_per_gram():
        headers = {
            "x-access-token": GoldApiService.API_KEY,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(GoldApiService.API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            price_per_ounce_usd = data.get("price")

            EXCHANGE_RATE = 16000

            price_per_gram_usd = price_per_ounce_usd / GoldApiService.TROY_OUNCE_TO_GRAM
            price_per_gram_idr = price_per_gram_usd * EXCHANGE_RATE

            return price_per_gram_idr
        except Exception as e:
            raise Exception(f"Failed to fetch gold price: {str(e)}")
