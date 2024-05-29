from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from cache.basic_cache import AsyncCacheStorage
from cache.redis_cache import RedisService
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Genre
from services.utils import BaseService
from storage.basic_storage import AsyncStorage
from storage.elastic_storage import ElasticService


class GenreService(BaseService):
    def __init__(self, cache: AsyncCacheStorage, storage: AsyncStorage):
        self.cache = cache
        self.storage = storage

    @property
    def index(self) -> str:
        return 'genre'

    @property
    def model(self):
        return Genre

    @property
    def model_id(self) -> str:
        return Genre

    def get_key(self, **kwargs) -> str:
        page_number = kwargs.get('page')
        page_size = kwargs.get('page_size')
        name = kwargs.get('name', None)
        redis_key = "{0}::{1}::{2}::{3}::{4}::{5}::{6}".format(self.index,
                                                               "page_size", page_size,
                                                               "page_number", page_number,
                                                               "name", name)
        return redis_key

    async def all_objects_from_storage(self, **kwargs) -> Optional[list[Genre]]:
        page_size = kwargs.get('page_size')
        page = kwargs.get('page') - 1
        name = kwargs.get('name', None)
        params = {'size': page_size, 'from': page}
        body = {'query': {'match_all': {}}}
        if name:
            body = {'query': {'match': {'name': {'query': name, 'fuzziness': 'auto'}}}}
        objects = await self.storage.get_all(index=self.index, body=body, params=params, model=self.model)
        return objects


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    cache = RedisService(redis)
    storage = ElasticService(elastic)
    return GenreService(cache, storage)
