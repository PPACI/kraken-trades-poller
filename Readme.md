# Kraken Trades Poller

This project will store each trade of each fiat pairs from kraken to an elasticsearch database !

## Features
* Fetch all trades from fiat pairs (XXX/EUR or XXX/USD)
* Store price, volume, timestamp and pair for each trades
* Poll every 5 minutes
* Store each transaction only once, even after a restart of the poller
* Dead simple to use with Docker
* Auto create a new elasticsearch index each month for easy deletion of old trades

## Base Elasticsearch index
As said, the project with create a new index each month based on a base elasticsearch index.
For example if you set your base index to "trades", you will have index like "trades-18-01".
This pattern will allow you to use wildcard in your future search/kibana/whatever like "trades*"

## Use with Docker
```
git clone https://github.com/PPACI/kraken-trades-poller.git
cd kraken-trades-poller
docker build -t kraken-trades-poller .
docker run -d -e "ES_HOST=URL_OF_ELASTICSEARCH" -e "ES_INDEX=NAME_OF_ELASTICSEARCH_BASE_INDEX_YOU_WANT" --name kraken-trades-poller kraken-trades-poller
```

## Use with Python directly
**Warning. This project require python > 3.5**
```
git clone https://github.com/PPACI/kraken-trades-poller.git
cd kraken-trades-poller
pip install -r requirements.txt
```
Just define `ES_HOST` and `ES_INDEX` as environment variable. If they don't already are, just run the following
```
ES_HOST=URL_OF_ELASTICSEARCH ES_INDEX=NAME_OF_ELASTICSEARCH_BASE_INDEX_YOU_WANT python main.py
```
else simply `python main.py`