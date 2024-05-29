import time
from functools import wraps

import requests
from elasticsearch import Elasticsearch
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
def wait_for_es():
    es_client = Elasticsearch(hosts=[f'{settings.es_host}:{settings.es_port}'], validate_cert=False, use_ssl=False)
    if es_client.ping():
        return es_client.ping()
    raise requests.exceptions.ConnectionError

