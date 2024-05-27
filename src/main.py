import logging

import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core import config
from core.logger import LOGGING
from db import elastic, redis
from api.v1 import films, genres, people

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    description="Service to get information about people, genres and movies from any films.",
    version="1.0.0"
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)
    elastic.es = AsyncElasticsearch(hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    redis.redis.close()
    await redis.redis.wait_closed()
    await elastic.es.close()


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(people.router, prefix='/api/v1/people', tags=['people'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])

#
# if __name__ == '__main__':
#     uvicorn.run(
#         'main:app',
#         host='0.0.0.0',
#         port=8000,
#         log_config=LOGGING,
#         log_level=logging.DEBUG,
#     )
