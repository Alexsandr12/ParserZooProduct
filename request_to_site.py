import random
import time

import requests

from config import URL, MAX_RETRIES, DELAY_RAHGE_S
from logger import log
from myexceptions import MyRequestError


def retry(func, max_retry=MAX_RETRIES, delay=DELAY_RAHGE_S):
    """Декоратор для повторной отправки запроса."""
    def wrapper(*args, **kwargs):
        attempt = 1

        while attempt <= max_retry + 1:
            if delay:
                time.sleep(random.randint(delay[0], delay[1]))

            try:
                response = func(*args, **kwargs)
            except requests.RequestException as err:
                log.exception(f"Ошибка запроса, попытка-{attempt} {err}")
                attempt += 1
                continue

            if response.status_code not in [200]:
                log.exception(f"Некорректный статус ответа {response.status_code}, попытка-{attempt}")
                attempt += 1
                continue

            return response

        log.info(f"Не удалось получить ответ от сайта.")
        raise MyRequestError
    return wrapper


class SendRequest:
    req = requests.Session()

    @retry
    def send_request(self, url_append="", params=None, headers=None):
        return self.req.get(url=URL + url_append, params=params, headers=headers)


sendreq = SendRequest()
