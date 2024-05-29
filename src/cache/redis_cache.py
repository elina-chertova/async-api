import json
from typing import List, Optional, Union

from aioredis import Redis
from pydantic import parse_raw_as
from pydantic.json import pydantic_encoder

from cache.basic_cache import AsyncCacheStorage
from core.config import logger
from models.models import Film, FilmById, Genre, Person

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class RedisService(AsyncCacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key, **kwargs):
        return self.redis.get(key)

    async def set(self, key: str, value: str, expire: int, **kwargs):
        return self.redis.set(key, value, expire=expire)

    async def object_from_cache(self, index: str, model, redis_key) -> Optional[Union[Film, FilmById, Genre, Person]]:
        data = await self.redis.get(redis_key)
        logger.info("{0} from cache {1}".format(index, data))
        if not data:
            return None
        result = model.parse_raw(data)
        return result

    async def all_objects_from_cache(self, model, redis_key):
        data = await self.redis.get(redis_key)
        logger.info("Data from cache {0}".format(data))
        if not data:
            return None
        obj = parse_raw_as(List[model], data)
        return obj

    async def put_object_to_cache(self, object_, index, redis_key):
        logger.info("Put {2} to cache {0} {1}".format(object_.id, object_.json(), index))
        await self.redis.set(redis_key, object_.json(), expire=CACHE_EXPIRE_IN_SECONDS)

    async def put_objects_to_cache(self, index, objects, redis_key):
        logger.info('{2}::{0} : values::{1}'.format(redis_key, json.dumps(objects, default=pydantic_encoder), index))
        await self.redis.set(redis_key, json.dumps(objects, default=pydantic_encoder),
                             expire=CACHE_EXPIRE_IN_SECONDS)
