import os

from kraken_trades_poller.Poller import Poller

if __name__ == '__main__':
    poller = Poller(es_host=os.getenv('ES_HOST', 'localhost').split(" "),
                    es_index=os.getenv('ES_INDEX', 'krakenbeat'))
    poller.start_loop()