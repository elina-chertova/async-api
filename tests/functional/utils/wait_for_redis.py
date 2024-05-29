import time
from functools import wraps

import aioredis
import requests
from tests.functional.settings import TestSettings

settings = TestSettings()


def backoff(start_sleep_time: object = 0.5, factor: object = 2, border_sleep_time: object = 10) -> object:
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            cnt = 0
            max_tries = 5
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    sleep_time = sleep_time * factor if sleep_time < border_sleep_time else border_sleep_time
                    cnt += 1
                    time.sleep(sleep_time)

                if cnt > max_tries:
                    break

        return inner

    return func_wrapper


@backoff
async def redis():
    client = await aioredis.create_redis_pool((settings.redis_host, settings.redis_port), minsize=10, maxsize=20)
    if await client.ping():
        return await client.ping()
    raise requests.exceptions.ConnectionError



