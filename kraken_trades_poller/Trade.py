from elasticsearch_dsl import DocType, Index
from elasticsearch_dsl.field import *


def init_index(es_index: str):
    index = Index(es_index)
    index.doc_type(Trade)


class Trade(DocType):
    pair = Keyword()
    price = Float()
    tags = Keyword()
    timestamp_transaction = Date()
    volume = Float()

    class Meta:
        mapping = "trade"
