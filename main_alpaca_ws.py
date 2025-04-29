import time
import threading
from datetime import datetime as dt, timedelta
import logging
import os
from dotenv import load_dotenv
import json
import hmac
import hashlib
from alpaca.data.live.stock import StockDataStream
from alpaca.data.enums import DataFeed
from alpaca.data.models.bars import Bar
from indicators import *

logger = logging.getLogger(__name__)
load_dotenv()

STOCK_SYMBOLS = ["TSLA", "AAAPL", "GOOGL", "AMZN", "MSFT"]
FOREX_ITEMS = ["EUR/USD", "GBP/USD", "USD/JPY"]
WS_URL = os.getenv('APLACA_WS_URL')
API_KEY = os.getenv('APCA_API_KEY_ID')
API_SECRET = os.getenv('APCA_API_SECRET_KEY')


def heartbeat():
    while True:
        with open("/tmp/heartbeat.txt", "w") as f:
            f.write(str(time.time()))
        time.sleep(5)


async def bar_handler(bar):
    print(bar)


def run_stream():

    ws = StockDataStream(
        api_key=API_KEY,
        secret_key=API_SECRET,
        raw_data=True,
        feed=DataFeed.IEX # DataFeed.IEX | DataFeed.SIP
    )

    ws.subscribe_bars(
        bar_handler,
        "*" # "*" for all stocks, STOCK_SYMBOLS for specific stocks
    )

    ws.run()


if __name__ == "__main__":

    run_stream()