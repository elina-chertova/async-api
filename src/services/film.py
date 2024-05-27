import json
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import parse_raw_as
from pydantic.json import pydantic_encoder

from core.config import logger
from db.elastic import get_elastic
from db.redis import get_redis
from models.models import Film, FilmById

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[FilmById]:
        film = await self._film_from_cache(film_id)
        logger.info('film {0} was in cache'.format(film))
        if not film:
            film = await self._get_film_from_elastic(film_id)
            logger.info('film {0} not in cache'.format(film))
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_all_films(self, **kwargs) -> Optional[list[Film]]:
        films = await self._all_films_from_cache(**kwargs)
        if not films:
            films = await self._all_films_from_elastic(**kwargs)
            if not films:
                return None
            await self._put_films_to_cache(films, **kwargs)
        return films

    async def _all_films_from_elastic(self, **kwargs) -> Optional[list[Film]]:
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

        doc = await self.elastic.search(index="movies",
                                        doc_type="_doc",
                                        body=body,
                                        params={
                                            'size': page_size,
                                            'from': page,
                                            'sort': sort
                                        })

        films = [Film(**x['_source']) for x in doc['hits']['hits']]
        return films

    async def _get_film_from_elastic(self, film_id: str) -> Optional[FilmById]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return FilmById(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[FilmById]:
        redis_key = "{0}::{1}::{2}".format("movies", "guid", film_id)
        data = await self.redis.get(redis_key)
        if not data:
            return None

        film = FilmById.parse_raw(data)
        return film

    async def _all_films_from_cache(self, **kwargs):
        redis_key = await self.get_redis_key(**kwargs)
        data = await self.redis.get(redis_key)
        logger.info("Films from cache {0}".format(data))
        if not data:
            return None
        films = parse_raw_as(list[Film], data)
        return films

    async def _put_film_to_cache(self, film: FilmById):
        redis_key = "{0}::{1}::{2}".format("movies", "guid", film.id)
        await self.redis.set(redis_key, film.json(), expire=int(FILM_CACHE_EXPIRE_IN_SECONDS))

    async def _put_films_to_cache(self, films: list[Film], **kwargs):
        redis_key = await self.get_redis_key(**kwargs)
        logger.info('redis_key::{0} : values::{1}'.format(redis_key, json.dumps(films, default=pydantic_encoder)))
        await self.redis.set(redis_key, json.dumps(films, default=pydantic_encoder),
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    @staticmethod
    async def get_redis_key(**kwargs) -> str:
        page_number = kwargs.get('page')
        page_size = kwargs.get('page_size')
        title = kwargs.get('title', None)
        genre = kwargs.get('genre', None)
        sort = kwargs.get('sort', 'imdb_rating:desc')
        redis_key = "{0}::{1}::{2}::{3}::{4}::{5}::{6}::{7}::{8}::{9}::{10}".format("person",
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
    return FilmService(redis, elastic)
