from django.core.cache import cache
from core.models import APIKey

CACHE_KEY = "api_key_value"

def get_api_key():
    # Try to get the key from cache
    key = cache.get(CACHE_KEY)
    if key is None:
        # If cache is empty, query the model
        obj = APIKey.get_solo()
        key = obj.api_key if obj else None
        cache.set(CACHE_KEY, key, None)  # None = no expiration
    return key
