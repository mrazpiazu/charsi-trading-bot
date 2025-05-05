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
from sqlalchemy import delete, tuple_

from utils.technical_analysis.indicators import *
from utils.database.db import *
from utils.database.models import *

logger = logging.getLogger(__name__)
load_dotenv()


def get_stock_data(start_time, end_time, stock_symbols: list):

    session = SessionLocal()

    try:

        client = StockHistoricalDataClient(
            api_key=os.getenv("ALPACA_API_KEY_ID"),
            secret_key=os.getenv("ALPACA_API_SECRET_KEY"),
            sandbox=False
        )

        request_params = StockBarsRequest(
            symbol_or_symbols=stock_symbols,
            timeframe=TimeFrame.Minute,
            start=dt.strftime(start_time - timedelta(minutes=30), '%Y-%m-%dT%H:%M:%S.%fZ'),
            end=dt.strftime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ'),
        )

        bars = client.get_stock_bars(request_params)

        df_bar = bars.df
        df_bar.reset_index(inplace=True)

        logger.info(f"Loading {df_bar.shape[0]} bars from Alpaca API")

        keys_to_delete = [(row['timestamp'], row['symbol']) for _, row in df_bar.iterrows()]

        delete_stmt = delete(StockBar).where(
            tuple_(StockBar.created_at, StockBar.symbol).in_(keys_to_delete)
        )
        session.execute(delete_stmt)

        new_bars = [
            StockBar(
                created_at=row['timestamp'],
                symbol=row['symbol'],
                open=float(row['open']),
                close=float(row['close']),
                high=float(row['high']),
                low=float(row['low']),
                volume=float(row['volume']),
                number_trades=int(row['trade_count']),
                volume_weighted_average_price=float(row['vwap']),
                is_imputed=False
            )
            for _, row in df_bar.iterrows()
        ]

        session.bulk_save_objects(new_bars)
        session.commit()
    except Exception as e:
        logging.exception(f"Error storing bar in DB: {e}")
        session.rollback()
        raise
    finally:
        session.close()

    return


if __name__ == "__main__":

    from utils.database.functions import load_stock_table_list
    from utils.database.db import *
    from utils.database.models import *

    session = SessionLocal()

    start_time = dt(2025, 4, 30, 00, 0, 0)
    end_time = dt(2025, 5, 5, 14, 15, 0)

    symbols = session.query(StockBar).distinct(StockBar.symbol).all()
    symbols_list = [symbol.symbol for symbol in symbols][1:]

    get_stock_data(start_time, end_time, symbols_list)