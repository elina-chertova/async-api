from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from cache.basic_cache import AsyncCacheStorage
from cache.redis_cache import RedisService
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Film, Person
from services.utils import BaseService
from storage.basic_storage import AsyncStorage
from storage.elastic_storage import ElasticService


class PersonService(BaseService):
    def __init__(self, cache: AsyncCacheStorage, storage: AsyncStorage):
        self.cache = cache
        self.storage = storage

    @property
    def index(self) -> str:
        return 'person'

    @property
    def model(self):
        return Person

    @property
    def model_id(self):
        return Person

    async def get_film_by_person_id(self, person_id: str) -> Optional[Film]:

        redis_key = "{0}::{1}::{2}::{3}".format(self.index, "films", "guid", person_id)
        films = await self.cache.all_objects_from_cache(Film, redis_key)
        if not films:
            films = await self._get_person_film_from_elastic(person_id)
            if not films:
                return None
            await self.cache.put_objects_to_cache(self.index, films, redis_key)

        return films

    async def all_objects_from_storage(self, **kwargs) -> Optional[list[Person]]:
        page_size = kwargs.get('page_size')
        page = kwargs.get('page') - 1
        name = kwargs.get('name', None)
        role = kwargs.get('role', None)
        if role and name:
            body = {
              "query": {"bool": {"must": [
                {
                  "match": {'roles': {'query': role, 'fuzziness': 'auto'}}
                },
                {
                  "match": {'full_name': {'query': name, 'fuzziness': 'auto'}}}]}}}
        elif role:
            body = {'query': {'match': {'roles': {'query': role, 'fuzziness': 'auto'}}}}
        elif name:
            body = {'query': {'match': {'full_name': {'query': name, 'fuzziness': 'auto'}}}}
        else:
            body = {'query': {'match_all': {}}}

        params = {
            'size': page_size,
            'from': page
        }
        objects = await self.storage.get_all(index=self.index, body=body, params=params, model=self.model)
        return objects

    async def _get_person_film_from_elastic(self, person_id: str) -> Optional[Film]:
        res = await self.storage.get(person_id, index=self.index, model=self.model)
        if not res:
            return None
        body = {"query": {"ids": {"values": res.film_ids}}}
        params = {}
        objects = await self.storage.get_all(index='movies', body=body, params=params, model=Film)
        return objects

    def get_key(self, **kwargs) -> str:
        page_number = kwargs.get('page')
        page_size = kwargs.get('page_size')
        role = kwargs.get('role', None)
        name = kwargs.get('name', None)
        redis_key = "{0}::{1}::{2}::{3}::{4}::{5}::{6}::{7}::{8}".format(self.index,
                                                                         "page_size", page_size,
                                                                         "page_number", page_number,
                                                                         "role", role,
                                                                         "name", name)
        return redis_key


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    cache = RedisService(redis)
    storage = ElasticService(elastic)
    return PersonService(cache, storage)
