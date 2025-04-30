import time
import logging
import os
from dotenv import load_dotenv
from alpaca.data.live.stock import StockDataStream
from alpaca.data.enums import DataFeed
from indicators import *

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
load_dotenv()

STOCK_SYMBOLS = ["TSLA", "AAAPL", "GOOGL", "AMZN", "MSFT"]
WS_URL = os.getenv('APLACA_WS_URL')
API_KEY = os.getenv('APCA_API_KEY_ID')
API_SECRET = os.getenv('APCA_API_SECRET_KEY')


async def bar_handler(bar):
    logging.info(bar)


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


