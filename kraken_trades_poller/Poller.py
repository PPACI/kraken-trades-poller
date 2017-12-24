import time
from datetime import date
from typing import List, Optional, Counter

import ccxt
from elasticsearch_dsl.connections import connections

from kraken_trades_poller.Trade import Trade
from .Trade import init_index


class Poller(object):
    def __init__(self, es_host: List[str], es_index: str):
        today = date.today()
        es_index = es_index + '-{}.{}'.format(today.year, today.month)
        connections.create_connection(hosts=es_host)
        init_index(es_index=es_index)
        self.last_transaction = {}

    def start_loop(self):
        kraken = ccxt.kraken()
        while True:
            trade_counter = Counter()
            kraken.load_markets()
            for symbol in kraken.markets:
                time.sleep(kraken.rateLimit / 1000)  # time.sleep wants seconds
                for trade in kraken.fetch_trades(symbol, since=self.get_last_transaction(symbol=symbol)):
                    es_trade = Trade(pair=symbol,
                                     price=trade['price'],
                                     timestamp_transaction=trade['datetime'],
                                     volume=trade['amount'])
                    es_trade.save()
                    trade_counter.update([symbol])
                    self.update_last_transaction(timestamp=trade['timestamp'], symbol=symbol)
            print(trade_counter)
            time.sleep(60*5)

    def update_last_transaction(self, timestamp: int, symbol: str):
        if symbol in self.last_transaction:
            if timestamp < self.last_transaction[symbol]:
                self.last_transaction[symbol] = timestamp
        else:
            self.last_transaction[symbol] = timestamp

    def get_last_transaction(self, symbol: str) -> Optional[int]:
        if symbol in self.last_transaction:
            return self.last_transaction[symbol]
        else:
            return None


