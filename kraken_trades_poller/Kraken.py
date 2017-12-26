import logging
import time
from collections import Counter
from typing import List, Dict, Optional

import ccxt
from ccxt import ExchangeError

LOGGER = logging.getLogger(__name__)


class Kraken(object):
    def __init__(self):
        self.last_transaction = self.init_last_transaction()
        self.doc_count = Counter()
        self.market = ccxt.kraken()
        self.market.load_markets()

    def get_trades(self) -> Dict[str, List[dict]]:
        trades = {}
        for symbol in self.market.markets:
            time.sleep(self.market.rateLimit / 1000)  # time.sleep wants seconds
            last_transaction_timestamp = self.get_last_transaction(symbol=symbol)
            try:
                trades[symbol] = self.market.fetch_trades(symbol, since=last_transaction_timestamp)
            except ExchangeError as e:
                LOGGER.error("Error for symbol {} : {}".format(symbol, str(e)))
                continue
        return trades

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

    def init_last_transaction(self) -> dict:
        return {}
