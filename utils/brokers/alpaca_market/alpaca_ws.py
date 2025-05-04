import logging
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime as dt
from datetime import timezone
import utils.logger.logger

from alpaca.data.live.stock import StockDataStream
from alpaca.data.enums import DataFeed
from utils.database.db import SessionLocal
from utils.database.models import *
from utils.logger.logger import get_logger_config

logger = logging.getLogger(__name__)
get_logger_config(logging)
load_dotenv()

STOCK_SYMBOLS = ["TSLA", "AAAPL", "GOOGL", "AMZN", "MSFT"]
WS_URL = os.getenv('ALPACA_WS_URL')
API_KEY = os.getenv('ALPACA_API_KEY_ID')
API_SECRET = os.getenv('ALPACA_API_SECRET_KEY')


def store_bar_sync(bar):
    session = SessionLocal()
    try:
        new_bar = StockBar(
            created_at=dt.fromtimestamp(bar['t'].seconds, tz=timezone.utc),
            symbol=bar['S'],
            open=bar['o'],
            close=bar['c'],
            high=bar['h'],
            low=bar['l'],
            volume=bar['v'],
            number_trades=bar['n'],
            volume_weighted_average_price=bar['vw'],
            is_imputed=False
        )
        session.merge(new_bar)
        session.commit()
    except Exception as e:
        logging.exception(f"Error storing bar in DB: {e}")
        session.rollback()
    finally:
        session.close()


async def bar_handler(bar):

    await asyncio.to_thread(store_bar_sync, bar)


def run_stream():

    logging.info("Starting Alpaca WebSocket stream...")

    ws = StockDataStream(
        api_key=API_KEY,
        secret_key=API_SECRET,
        raw_data=True,
        feed=DataFeed.IEX # DataFeed.IEX | DataFeed.SIP
    )

    logging.info("Connecting to Alpaca WebSocket...")
    ws.subscribe_bars(
        bar_handler,
        "*" # "*" for all stocks, STOCK_SYMBOLS for specific stocks
    )

    ws.run()


if __name__ == "__main__":

    run_stream()

    # websocket(Alpaca.Markets) > database > Indicators > Filtro ATR,RSI... > model(ChatGPT) > broker(Alpaca.Markets)


