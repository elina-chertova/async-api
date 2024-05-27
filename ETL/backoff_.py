import time
from functools import wraps

import requests
from config import logger


def backoff(logger, start_sleep_time: object = 0.5, factor: object = 2, border_sleep_time: object = 10) -> object:
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания
    (border_sleep_time)
    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param logger: логгер
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            cnt = 0
            max_tries = 5
            while True:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.ConnectionError as e:
                    logger.error('Connection refused during bulk request')
                except Exception as e:
                    logger.error('Connection error: {}'.format(func.__name__), e)

                sleep_time = sleep_time * factor if sleep_time < border_sleep_time else border_sleep_time
                cnt += 1
                time.sleep(sleep_time)

                if cnt > max_tries:
                    logger.error(f"Tries were finished {func.__name__}")
                    break

        return inner
    return func_wrapper
