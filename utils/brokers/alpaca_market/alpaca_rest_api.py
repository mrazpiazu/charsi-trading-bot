import time
import threading
from datetime import datetime as dt, timedelta
import datetime
import logging
import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from utils.technical_analysis.indicators import *

logger = logging.getLogger(__name__)
load_dotenv()


def get_stock_data(start_time, end_time, stock_symbols: list):

    try:

        client = StockHistoricalDataClient(
            api_key=os.getenv("APCA_API_KEY_ID"),
            secret_key=os.getenv("APCA_API_SECRET_KEY"),
            sandbox=False
        )

        request_params = StockBarsRequest(
            symbol_or_symbols=stock_symbols,
            timeframe=TimeFrame.Minute,
            start=dt.strftime(start_time - timedelta(minutes=30), '%Y-%m-%dT%H:%M:%S.%fZ'),
            end=dt.strftime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ'),
        )

        bars = client.get_stock_bars(request_params)

        return

    except Exception as e:
        logger.exception(f"Exception in main loop: {e}")

    logger.info("Waiting 5 seconds before retrying connection...")
    time.sleep(5)


if __name__ == "__main__":

    from utils.database.functions import load_stock_table_list

    symbols = load_stock_table_list()

    get_stock_data()