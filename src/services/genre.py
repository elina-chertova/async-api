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
from models.models import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        logger.info('genre {0} was in cache'.format(genre))
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            logger.info('genre {0} not in cache'.format(genre))
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def get_all_genres(self, **kwargs) -> Optional[list[Genre]]:
        genres = await self._all_genres_from_cache(**kwargs)
        if not genres:
            genres = await self._all_genres_from_elastic(**kwargs)
            if not genres:
                return None
            await self._put_genres_to_cache(genres, **kwargs)

        return genres

    async def _all_genres_from_elastic(self, **kwargs) -> Optional[list[Genre]]:
        page_size = kwargs.get('page_size')
        page = kwargs.get('page') - 1
        name = kwargs.get('name', None)
        body = {'query': {'match_all': {}}}
        if name:
            body = {'query': {'match': {'name': {'query': name, 'fuzziness': 'auto'}}}}

        doc = await self.elastic.search(index="genre",
                                        doc_type="_doc",
                                        body=body,
                                        params={
                                            'size': page_size,
                                            'from': page
                                        })
        genres = [Genre(**x['_source']) for x in doc['hits']['hits']]
        return genres

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get('genre', genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        redis_key = "{0}::{1}::{2}".format("genre", "guid", genre_id)
        data = await self.redis.get(redis_key)
        logger.info("Genre from cache {0}".format(data))
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _all_genres_from_cache(self, **kwargs):
        redis_key = await self.get_redis_key(**kwargs)
        data = await self.redis.get(redis_key)
        logger.info("Genres from cache {0}".format(data))
        if not data:
            return None
        genre = parse_raw_as(List[Genre], data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        logger.info("Put genre to cache {0} {1}".format(genre.id, genre.json()))
        redis_key = "{0}::{1}::{2}".format("genre", "guid", genre.id)
        await self.redis.set(redis_key, genre.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _put_genres_to_cache(self, genres: list[Genre], **kwargs):
        redis_key = await self.get_redis_key(**kwargs)
        logger.info('genres::{0} : values::{1}'.format(redis_key, json.dumps(genres, default=pydantic_encoder)))
        await self.redis.set(redis_key, json.dumps(genres, default=pydantic_encoder),
                             expire=GENRE_CACHE_EXPIRE_IN_SECONDS)


    @staticmethod
    async def get_redis_key(**kwargs) -> str:
        page_number = kwargs.get('page')
        page_size = kwargs.get('page_size')
        name = kwargs.get('name', None)
        redis_key = "{0}::{1}::{2}::{3}::{4}::{5}::{6}".format("person",
                                                                         "page_size", page_size,
                                                                         "page_number", page_number,
                                                                         "name", name)
        return redis_key

@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
