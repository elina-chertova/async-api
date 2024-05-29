from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from cache.basic_cache import AsyncCacheStorage
from cache.redis_cache import RedisService
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Film, FilmById
from services.utils import BaseService
from storage.basic_storage import AsyncStorage
from storage.elastic_storage import ElasticService


class FilmService(BaseService):
    def __init__(self, cache: AsyncCacheStorage, storage: AsyncStorage):
        self.cache = cache
        self.storage = storage

    @property
    def index(self) -> str:
        return 'movies'

    @property
    def model(self):
        return Film

    @property
    def model_id(self) -> str:
        return FilmById

    async def all_objects_from_storage(self, **kwargs) -> Optional[list[Film]]:
        page_size = kwargs.get('page_size')
        page = kwargs.get('page') - 1
        sort = kwargs.get('sort', 'imdb_rating:desc')
        title = kwargs.get('title', None)
        genre = kwargs.get('genre', None)
        body = {'query': {'match_all': {}}}
        if genre:
            body = {'query': {'match': {'genre': {'query': genre, 'fuzziness': 'auto'}}}}
        if title:
            body = {'query': {'match': {'title': {'query': title, 'fuzziness': 'auto'}}}}
        params = {
            'size': page_size,
            'from': page,
            'sort': sort
        }
        objects = await self.storage.get_all(index=self.index, body=body, params=params, model=self.model)
        return objects

    def get_key(self, **kwargs) -> str:
        page_number = kwargs.get('page')
        page_size = kwargs.get('page_size')
        title = kwargs.get('title', None)
        genre = kwargs.get('genre', None)
        sort = kwargs.get('sort', 'imdb_rating:desc')
        redis_key = "{0}::{1}::{2}::{3}::{4}::{5}::{6}::{7}::{8}::{9}::{10}".format(self.index,
                                                                                    "page_size", page_size,
                                                                                    "page_number", page_number,
                                                                                    "title", title,
                                                                                    "genre", genre,
                                                                                    "sort", sort)
        return redis_key


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    cache = RedisService(redis)
    storage = ElasticService(elastic)
    return FilmService(cache, storage)
