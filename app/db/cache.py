from decimal import Decimal
from hashlib import sha256

from redis import Redis, RedisError
from app.core.config import settings
from app.core.enums import SortBy, Order

redis_client = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_timeout=1,
    socket_connect_timeout=1,
)


def build_products_cache_key(
        page: int,
        limit: int,
        search: str | None,
        min_price: Decimal,
        max_price: Decimal,
        min_rating: float,
        sort_by: SortBy,
        order: Order,
) -> str:
    key_string = (
        f"page={page}:"
        f"limit={limit}:"
        f"search={search.lower() if search else ''}:"
        f"min_price={min_price}:"
        f"max_price={max_price}:"
        f"min_rating={min_rating}:"
        f"sort_by={sort_by}:"
        f"order={order}"
    ).encode('utf-8')

    return "products:" + sha256(key_string).hexdigest()


def get_cached(cache_key: str):
    try:
        return redis_client.get(cache_key)
    except RedisError:
        print("Redis error")
        return None


def set_cached(cache_key, response):
    try:
        redis_client.setex(cache_key, settings.cache_ttl, response.model_dump_json())
    except RedisError:
        print("Redis error")


def invalidate_products_cache(batch_size: int = 100) -> None:
    try:
        batch = []

        for key in redis_client.scan_iter(match="products:*"):
            batch.append(key)

            if len(batch) >= batch_size:
                redis_client.delete(*batch)
                batch.clear()

        if batch:
            redis_client.delete(*batch)

    except RedisError:
        print("Redis error")
