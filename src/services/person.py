import json
from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import parse_raw_as
from pydantic.json import pydantic_encoder

from core.config import logger
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Film, Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        logger.info('person {0} was in cache'.format(person))
        if not person:
            person = await self._get_person_from_elastic(person_id)
            logger.info('person {0} not in cache'.format(person))
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def get_film_by_person_id(self, person_id: str, **kwargs) -> Optional[Film]:
        films = await self._get_person_film_from_cache(person_id)
        # logger.info('Films {0} was in cache'.format(person))
        if not films:
            films = await self._get_person_film_from_elastic(person_id)
            # logger.info('Films {0} not in cache'.format(person))
            if not films:
                return None
            await self._put_person_film_to_cache(films, person_id)

        return films

    async def get_all_people(self, **kwargs) -> Optional[list[Person]]:
        people = await self._all_people_from_cache(**kwargs)
        if not people:
            people = await self._all_people_from_elastic(**kwargs)
            if not people:
                return None
            await self._put_people_to_cache(people, **kwargs)
        return people

    async def _all_people_from_elastic(self, **kwargs) -> Optional[list[Person]]:
        page_size = kwargs.get('page_size')
        page = kwargs.get('page') - 1
        name = kwargs.get('name', None)
        role = kwargs.get('role', None)
        body = {'query': {'match_all': {}}}
        if role:
            body = {'query': {'match': {'roles': {'query': role, 'fuzziness': 'auto'}}}}
        if name:
            body = {'query': {'match': {'full_name': {'query': name, 'fuzziness': 'auto'}}}}

        doc = await self.elastic.search(index="person",
                                        doc_type="_doc",
                                        body=body,
                                        params={
                                            'size': page_size,
                                            'from': page
                                        })

        people = [Person(**x['_source']) for x in doc['hits']['hits']]
        return people

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get('person', person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _get_person_film_from_elastic(self, person_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('person', person_id)
        except NotFoundError:
            return None
        film_id = Person(**doc['_source']).film_ids
        body = {"query": {"ids": {"values": film_id}}}
        doc = await self.elastic.search(index="movies",
                                        doc_type="_doc",
                                        body=body)
        films = [Film(**x['_source']) for x in doc['hits']['hits']]

        return films

    async def _get_person_film_from_cache(self, person_id):
        redis_key = "{0}::{1}::{2}::{3}".format("person", "films", "guid", person_id)
        data = await self.redis.get(redis_key)

        if not data:
            return None
        films = parse_raw_as(List[Film], data)
        logger.info("Movies in which people is was from cache {0}".format(data))
        return films

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        redis_key = "{0}::{1}::{2}".format("person", "guid", person_id)
        data = await self.redis.get(redis_key)
        logger.info("Person from cache {0}".format(data))
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _all_people_from_cache(self, **kwargs):
        redis_key = await self.get_redis_key(**kwargs)
        # redis_key = str(kwargs.get('request').url)
        data = await self.redis.get(redis_key)
        logger.info("People from cache {0}".format(data))
        if not data:
            return None
        person = parse_raw_as(List[Person], data)
        return person

    async def _put_person_film_to_cache(self, films: list[Film], person_id):
        redis_key = "{0}::{1}::{2}::{3}".format("person", "films", "guid", person_id)
        logger.info('redis_key::{0} : values::{1}'.format(redis_key, json.dumps(films, default=pydantic_encoder)))
        await self.redis.set(redis_key, json.dumps(films, default=pydantic_encoder),
                             expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_person_to_cache(self, person: Person):
        redis_key = "{0}::{1}::{2}".format("person", "guid", person.id)
        logger.info("Put person to cache {0} {1}".format(person.id, person.json()))
        await self.redis.set(redis_key, person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_people_to_cache(self, people: list[Person], **kwargs):
        redis_key = await self.get_redis_key(**kwargs)
        logger.info('redis_key::{0} : values::{1}'.format(redis_key, json.dumps(people, default=pydantic_encoder)))
        await self.redis.set(redis_key, json.dumps(people, default=pydantic_encoder),
                             expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    @staticmethod
    async def get_redis_key(**kwargs) -> str:
        page_number = kwargs.get('page')
        page_size = kwargs.get('page_size')
        role = kwargs.get('role', None)
        name = kwargs.get('name', None)
        redis_key = "{0}::{1}::{2}::{3}::{4}::{5}::{6}::{7}::{8}".format("person",
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
    return PersonService(redis, elastic)
