import asyncio

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch

# import settings
import testdata.index_map as index_map
import utils.helper as util
from settings import TestSettings

settings = TestSettings()


@pytest.fixture(scope='session', autouse=True)
async def index_init(es_client):
    await util.create_index(es_client, index_map.ind_map)
    yield
    await util.remove_index(es_client, index_map.ind_map)


@pytest.fixture(scope='session')
async def redis_client():
    redis = await aioredis.create_redis_pool((settings.redis_host, settings.redis_port), minsize=10, maxsize=20)
    yield redis
    redis.close()


@pytest.fixture(scope='session', autouse=True)
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{settings.es_host}:{settings.es_port}'])
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
