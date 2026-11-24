from functools import lru_cache

from langfuse import get_client


@lru_cache(maxsize=1)
def get_langfuse():
    return get_client()
