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

from indicators import *

logger = logging.getLogger(__name__)
load_dotenv()

STOCK_SYMBOLS = ["TSLA", "AAAPL", "GOOGL", "AMZN", "MSFT"]
FOREX_ITEMS = ["EUR/USD", "GBP/USD", "USD/JPY"]

def heartbeat():
    while True:
        with open("/tmp/heartbeat.txt", "w") as f:
            f.write(str(time.time()))
        time.sleep(5)


def run_stock_data():

    threading.Thread(target=heartbeat, daemon=True).start()

    try:

        client = StockHistoricalDataClient(
            api_key=os.getenv("APCA_API_KEY_ID"),
            secret_key=os.getenv("APCA_API_SECRET_KEY"),
            sandbox=False
        )

        request_params = StockBarsRequest(
            symbol_or_symbols=STOCK_SYMBOLS,
            timeframe=TimeFrame.Hour,
            start=dt.strftime(dt.now(datetime.timezone.utc) - timedelta(hours=24), '%Y-%m-%dT%H:%M:%S.%fZ')
        )

        bars = client.get_stock_bars(request_params)

        df = bars.df

        # Extract datetime from multiindex
        df.reset_index(inplace=True)

        df_indicators_total = pd.DataFrame()

        for symbol in STOCK_SYMBOLS:
            df_indicators = df[df['symbol'] == symbol]
            rsi = calculate_rsi(df_indicators, period=14)
            smna = calculate_sma(df_indicators, period=14)
            ema = calculate_ema(df_indicators, period=14)
            macd = calculate_macd(df_indicators, short_window=12, long_window=26, signal_window=9)
            df_indicators['RSI'] = rsi
            df_indicators['SMA'] = smna
            df_indicators['EMA'] = ema
            df_indicators['MACD'] = macd['MACD']
            df_indicators['Signal'] = macd['Signal']
            df_indicators['MACD_Hist'] = macd['MACD'] - macd['Signal']

            df_indicators_total = pd.concat([df_indicators_total, df_indicators], ignore_index=True)

        return

    except Exception as e:
        logger.exception(f"Exception in main loop: {e}")

    logger.info("Waiting 5 seconds before retrying connection...")
    time.sleep(5)


if __name__ == "__main__":
    run_stock_data()