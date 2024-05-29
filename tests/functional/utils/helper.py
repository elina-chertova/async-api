import json

from elasticsearch import AsyncElasticsearch


async def get_es_bulk_query(data, index):
    bulk_query = []
    for row in data:
        bulk_query.extend([
            json.dumps({'index': {'_index': index, '_id': row['id']}}),
            json.dumps(row)
        ])
    return bulk_query


async def create_index(es_client: AsyncElasticsearch, index: dict):
    for i in index.keys():
        if not await es_client.indices.exists(i):
            await es_client.indices.create(
                index=i,
                body=index[i]
            )


async def remove_index(es_client: AsyncElasticsearch, index: dict):
    for i in index.keys():
        await es_client.indices.delete(index=i)


