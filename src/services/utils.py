from abc import abstractmethod
from typing import Optional, Type, Union

from cache.redis_cache import RedisService
from core.config import logger
from models.models import Film, FilmById, Genre, Person
from storage.elastic_storage import ElasticService


class BaseService:
    @property
    @abstractmethod
    def index(self) -> str:
        pass

    @property
    @abstractmethod
    def model_id(self) -> Type[Union[Film, FilmById, Genre, Person]]:
        pass

    @property
    @abstractmethod
    def model(self) -> Type[Union[Film, Genre, Person]]:
        pass

    @abstractmethod
    def get_key(self, **kwargs) -> str:
        pass

    @abstractmethod
    async def all_objects_from_storage(self, **kwargs) -> Optional[Union[list[Film], list[FilmById],
                                                                         list[Genre], list[Person]]]:
        pass

    def __init__(self, cache: RedisService, storage: ElasticService):
        self.cache = cache
        self.storage = storage

    async def get_by_id(self, object_id: str) -> Optional[Union[Film, FilmById,
                                                                Genre, Person]]:
        redis_key = "{0}::{1}::{2}".format(self.index, "guid", object_id)
        obj = await self.cache.object_from_cache(self.index, self.model_id, redis_key)
        logger.info('index {1} data {0} was in cache'.format(obj, self.index))
        if not obj:
            obj = await self.storage.get(object_id, index=self.index, model=self.model_id)
            logger.info('index {1} data {0} not in cache'.format(obj, self.index))
            if not obj:
                return None
            await self.cache.put_object_to_cache(obj, self.index, redis_key)
        return obj

    async def get_all_objects(self, **kwargs) -> Optional[Union[list[Film], list[FilmById],
                                                                list[Genre], list[Person]]]:
        redis_key = self.get_key(**kwargs)
        objects = await self.cache.all_objects_from_cache(self.model, redis_key)
        if not objects:
            objects = await self.all_objects_from_storage(**kwargs)
            if not objects:
                return None
            await self.cache.put_objects_to_cache(self.index, objects, redis_key)

        return objects





