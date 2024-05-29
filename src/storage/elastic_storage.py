from typing import Optional, Union

from elasticsearch import AsyncElasticsearch, NotFoundError

from models.models import Film, FilmById, Genre, Person
from storage.basic_storage import AsyncStorage


class ElasticService(AsyncStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_all(self, index, model, body, params):
        doc = await self.elastic.search(index=index,
                                        doc_type="_doc",
                                        body=body,
                                        params=params)
        objects = [model(**x['_source']) for x in doc['hits']['hits']]
        return objects

    async def get(self, object_id, **kwargs) -> Optional[Union[Film, FilmById, Genre, Person]]:
        index = kwargs['index']
        model = kwargs['model']
        try:
            doc = await self.elastic.get(index, object_id)
        except NotFoundError:
            return None
        return model(**doc['_source'])
