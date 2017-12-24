from datetime import date
from typing import List

from elasticsearch_dsl.connections import connections

from .Trade import init_index


class Poller(object):
    def __init__(self, es_host: List[str], es_index: str):
        today = date.today()
        es_index = es_index + '-{}.{}'.format(today.year, today.month)
        connections.create_connection(hosts=es_host)
        init_index(es_index=es_index)

    def start_loop(self):
        raise NotImplementedError
