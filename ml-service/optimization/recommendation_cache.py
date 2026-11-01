from functools import lru_cache
@lru_cache(maxsize=2048)
def cache_key(user_id, model_version): return f"{model_version}:{user_id}"
