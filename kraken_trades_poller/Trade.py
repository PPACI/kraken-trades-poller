from elasticsearch_dsl import DocType, Index
from elasticsearch_dsl.field import *
from datetime import date


def init_index(es_index: str):
    today = date.today()
    es_index = es_index + '-{}.{}'.format(today.year, today.month)
    index = Index(es_index)
    Trade.reset_index()
    index.doc_type(Trade)
    if not index.exists():
        index.create()


class Trade(DocType):
    pair = Keyword()
    price = Float()
    timestamp_transaction = Date()
    volume = Float()

    @classmethod
    def reset_index(cls):
        cls._doc_type.index = None
