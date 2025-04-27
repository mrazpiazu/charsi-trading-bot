import time
import threading
from datetime import datetime as dt, timedelta
import logging
import os
from dotenv import load_dotenv
from lightstreamer.client import *
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from models import SubListener

logger = logging.getLogger(__name__)
load_dotenv()

ENV = "LIVE" # "DEMO" or "LIVE"

LS_URL = "https://push.lightstreamer.com"
API_URL = os.getenv(f"IG_API_URL_{ENV}")
USERNAME = os.getenv("IG_SERVICE_USERNAME")
PASSWORD = os.getenv("IG_SERVICE_PASSWORD")
API_KEY = os.getenv(f"IG_SERVICE_API_KEY_{ENV}")
ACCOUNT_ID = os.getenv(f"IG_SERVICE_ACCOUNT_ID_{ENV}")

IG_ITEMS = ["CS.D.EURUSD.CFD.IP", "CS.D.GBPUSD.CFD.IP", "CS.D.USDJPY.CFD.IP"]


def wait_for_input():
    input("{0:-^80}\n".format("HIT CR TO UNSUBSCRIBE AND DISCONNECT FROM LIGHTSTREAMER"))


def heartbeat():
    while True:
        with open("/tmp/heartbeat.txt", "w") as f:
            f.write(str(time.time()))
        time.sleep(5)


def generate_sub():
    sub = Subscription("MERGE", IG_ITEMS, ["stock_name", "last_price", "time", "bid", "ask"])
    sub.setDataAdapter("QUOTE_ADAPTER")

    return sub


def run():

    threading.Thread(target=heartbeat, daemon=True).start()

    try:

        client = StockHistoricalDataClient(
            api_key=os.getenv("APCA_API_KEY_ID"),
            secret_key=os.getenv("APCA_API_SECRET_KEY"),
            sandbox=False
        )

        request_params = StockBarsRequest(
            symbol_or_symbols=["AAPL"],
            timeframe=TimeFrame.Hour,
            start=dt.strftime(dt.now() - timedelta(days=30), '%Y-%m-%dT%H:%M:%S.%fZ')
        )

        bars = client.get_stock_bars(request_params)

        df = bars.df

        return

    except Exception as e:
        logger.exception(f"Exception in main loop: {e}")

    logger.info("Waiting 5 seconds before retrying connection...")
    time.sleep(5)


if __name__ == "__main__":
    run()
