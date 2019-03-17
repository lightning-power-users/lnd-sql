import hashlib
import hmac
import os
import time
from datetime import datetime, timedelta

import pytz
import requests

from lnd_sql import session_scope
from lnd_sql.models.contrib.exchange_rates import ExchangeRates


class BitcoinAverage(object):
    base_url = 'https://apiv2.bitcoinaverage.com'

    @property
    def signature(self):
        secret_key = os.environ['BITCOIN_AVERAGE_SECRET_KEY']
        encoded_secret_key = secret_key.encode()

        public_key = os.environ['BITCOIN_AVERAGE_PUBLIC_KEY']

        timestamp = int(time.time())

        payload = f'{timestamp}.{public_key}'
        encoded_payload = payload.encode()

        digest_module = hashlib.sha256

        hashing_object = hmac.new(key=encoded_secret_key,
                                  msg=encoded_payload,
                                  digestmod=digest_module)
        hex_hash = hashing_object.hexdigest()

        return f'{payload}.{hex_hash}'

    def get_price_by_date(self, date: datetime):
        timestamp = int(date.timestamp())
        return self.get_price(timestamp=timestamp)

    def get_price(self, timestamp: int):
        path = [self.base_url, 'indices', 'global', 'history', 'BTCUSD']
        url = '/'.join(path)
        url += f'?at={str(timestamp)}'
        headers = {'X-Signature': self.signature}
        result = requests.get(url=url, headers=headers)
        return result.json()

    def get_ticker(self):
        path = [self.base_url, 'indices', 'global', 'ticker', 'BTCUSD']
        url = '/'.join(path)
        headers = {'X-Signature': self.signature}
        result = requests.get(url=url, headers=headers)
        return result.json()


def cache_usd_price():
    with session_scope() as session:
        latest_price = (
            session.query(ExchangeRates)
            .order_by(ExchangeRates.timestamp.desc())
            .first()
        )
        if latest_price is not None:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            if latest_price.timestamp > one_hour_ago:
                return
    response = BitcoinAverage().get_ticker()
    usd_price = response['last']
    timestamp = response['timestamp']
    price_datetime = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    with session_scope() as session:
        rate = ExchangeRates()
        rate.timestamp = price_datetime
        rate.last = usd_price
        session.add(rate)
