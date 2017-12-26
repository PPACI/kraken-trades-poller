import logging
import time
from collections import Counter
from typing import List, Optional, Tuple, Dict

import ccxt
from ccxt import ExchangeError, ExchangeNotAvailable
from elasticsearch_dsl import Search
from retrying import retry

LOGGER = logging.getLogger(__name__)


def retry_if_not_available(exception):
    return isinstance(exception, ExchangeNotAvailable)


class Kraken(object):
    def __init__(self):
        self.last_transaction = self._init_last_transaction()
        self.market = ccxt.kraken()
        self.market.load_markets()

    def get_trades(self) -> Tuple[Dict[str, List[dict]], Counter]:
        trades_count = Counter()
        trades = {}
        symbols = self._get_symbols()
        for symbol in symbols:
            time.sleep(self.market.rateLimit / 1000)  # time.sleep wants seconds
            last_transaction_timestamp = self._get_last_transaction(symbol=symbol)
            try:
                trades[symbol] = self._safe_fetch_trades(symbol=symbol, since=last_transaction_timestamp)
                self._update_last_transaction(symbol=symbol, trades=trades[symbol])
                trades_count.update({symbol: len(trades[symbol])})
                LOGGER.info(f"fetched {symbol}")
            except ExchangeError as e:
                LOGGER.error(f"Error for symbol {symbol} : {str(e)}")
                continue
        return trades, trades_count

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=30000, retry_on_exception=retry_if_not_available)
    def _safe_fetch_trades(self, symbol: str, since: int) -> List[dict]:
        try:
            return self.market.fetch_trades(symbol, since=since)
        except ExchangeNotAvailable as e:
            LOGGER.error(f"Exchange not available : {str(e)}")
            LOGGER.error("Retry in a few seconds...")
            raise e

    def _update_last_transaction(self, symbol: str, trades: List[dict]):
        for trade in trades:
            if symbol in self.last_transaction:
                if trade['timestamp'] < self.last_transaction[symbol]:
                    self.last_transaction[symbol] = trade['timestamp']
            else:
                self.last_transaction[symbol] = trade['timestamp']

    def _get_last_transaction(self, symbol: str) -> Optional[int]:
        if symbol in self.last_transaction:
            return self.last_transaction[symbol]
        else:
            return None

    @staticmethod
    def _init_last_transaction() -> dict:
        s = Search().filter('range', timestamp_transaction={'lte':'now'})
        s.aggs.bucket('pairs', 'terms', field='pair', size=50) \
            .metric('most_recent', 'max', field='timestamp_transaction')
        r = s.execute()
        last_transaction = {}
        for pair in r.aggs.pairs:
            last_transaction[pair.key] = pair.most_recent.value
        return last_transaction

    def _get_symbols(self) -> List[str]:
        filtered = []
        for symbol in self.market.symbols:
            for must_filter in ['EUR', 'USD']:
                if must_filter in symbol:
                    filtered.append(symbol)
        return filtered
