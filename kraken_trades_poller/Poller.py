import time
from datetime import date
from typing import List, Optional, Counter

import ccxt
import elasticsearch.helpers
from ccxt import ExchangeError
from elasticsearch_dsl.connections import connections

from kraken_trades_poller.Trade import Trade
from .Trade import init_index


class Poller(object):
    def __init__(self, es_host: List[str], es_index: str):
        today = date.today()
        es_index = es_index + '-{}.{}'.format(today.year, today.month)
        connections.create_connection(hosts=es_host)
        init_index(es_index=es_index)


    def start_loop(self):
        kraken = ccxt.kraken()
        while True:
            bulk_docs = []
            trade_counter = Counter()
            kraken.load_markets()
            eur_usd_market = [symbol for symbol in kraken.markets if 'EUR' in symbol or 'USD' in symbol]
            print(eur_usd_market)
            for symbol in eur_usd_market:

                try:
                    for trade in kraken.fetch_trades(symbol, since=self.get_last_transaction(symbol=symbol)):
                        es_trade = Trade(pair=symbol,
                                         price=trade['price'],
                                         timestamp_transaction=trade['datetime'],
                                         volume=trade['amount'])
                        bulk_docs.append(es_trade.to_dict(include_meta=True))
                        trade_counter.update([symbol])
                        self.update_last_transaction(timestamp=trade['timestamp'], symbol=symbol)
                    print('{} Done'.format(symbol))
                except ExchangeError as e:
                    print("problem with {}".format(symbol))
                    continue
            print('Now Indexing')
            elasticsearch.helpers.bulk(client=connections.get_connection(), actions=bulk_docs, max_retries=3)
            print(trade_counter)
            time.sleep(60 * 5)


