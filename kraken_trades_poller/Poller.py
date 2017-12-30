import logging
import time
from typing import List

import elasticsearch.helpers
from elasticsearch_dsl.connections import connections

from kraken_trades_poller.Kraken import Kraken
from kraken_trades_poller.Trade import Trade
from .Trade import init_index

LOGGER = logging.getLogger(__name__)


class Poller(object):
    def __init__(self, es_host: List[str], es_index: str):
        connections.create_connection(hosts=es_host)
        self.es_index = es_index
        self.kraken_client = Kraken()

    def start_loop(self):
        while True:
            init_index(es_index=self.es_index)
            bulk_trades = []
            trades_dict, stats = self.kraken_client.get_trades()
            for symbol, trades in trades_dict.items():
                for trade in trades:
                    es_trade = Trade(pair=symbol,
                                     price=trade['price'],
                                     timestamp_transaction=trade['datetime'],
                                     volume=trade['amount'])
                    bulk_trades.append(es_trade.to_dict(include_meta=True))

            LOGGER.info(f"Sending bulk index : {len(bulk_trades)} items to index")
            elasticsearch.helpers.bulk(client=connections.get_connection(), actions=bulk_trades, max_retries=3)
            LOGGER.info("Indexation done. Indexation stats :")
            LOGGER.info(stats)
            LOGGER.info("Will now sleep for 5 minutes")
            time.sleep(60 * 5)
