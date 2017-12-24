from elasticsearch_dsl import DocType, Index
from elasticsearch_dsl.field import *


def init_index(es_index: str):
    index = Index(es_index)
    index.doc_type(Trade)
    if not index.exists():
        index.create()


class Trade(DocType):
    pair = Keyword()
    price = Float()
    timestamp_transaction = Date()
    volume = Float()
