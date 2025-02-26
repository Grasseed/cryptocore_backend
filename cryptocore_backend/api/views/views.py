import requests
import json
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# 使用 CoinGecko API 來查詢加密貨幣價格
COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

@api_view(['GET'])
def get_crypto_price(request, symbol):
    """
    查詢加密貨幣價格，並將結果快取到 Redis（60秒）
    param symbol: Currency symbol(e.g. BTC, ETH, etc)
    """
    symbol = symbol.lower()
    cache_key = f"crypto_price_{symbol}" # Redis cache key
    cached_price = cache.get(cache_key) # 嘗試從 Redis 讀取數據
    
    if cached_price:
        print('從Redis取得資料')
        return Response(cached_price, status=status.HTTP_200_OK) # 若有快取到，返回結果
    
    # 若快取不存在，則向 CoinGecko API 發送請求
    params = {
        'ids': symbol.lower(), # CoinGecko API 使用小寫
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(COINGECKO_API, params=params)
    
        if response.status_code == status.HTTP_200_OK:
            price_data = response.json()
            cache.set(cache_key, price_data, timeout=60) # 存入Redis，60秒過期
            print('將資料存入Redis，60秒後過期')
            return Response(price_data)
        else:
            return Response({"error": "Failed to fetch crypto price"}, status=response.status_code)
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Request failed: {str(e)}"}, status=status.HTTP_INTERNAL_SERVER_ERROR)