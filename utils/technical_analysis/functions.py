import logging
import pandas as pd
from sqlalchemy import text
import os

from utils.database.db import SessionLocal
from utils.database.functions import load_stock_starting_by
from utils.database.models import StockBar, StockBarAggregate, StockIndicator
from utils.logger.logger import get_logger_config
from utils.technical_analysis.indicators import *

logger = logging.getLogger("technical_analysis_functions")
get_logger_config(logging)

session = SessionLocal()

def run_technical_analysis(symbol):

    symbol_data = (
        session.query(StockBar)
        .filter(StockBar.symbol == symbol)
        .order_by(StockBar.created_at.desc())
        .limit(30)
        .all()
    )

    symbol_data_list = [
        {
            'symbol': row.symbol,
            'open': row.open,
            'high': row.high,
            'low': row.low,
            'close': row.close,
            'volume': row.volume,
            'created_at': row.created_at
        }
        for row in symbol_data
    ]

    # Crea el DataFrame
    df_symbol = pd.DataFrame(symbol_data_list)

    rsi = calculate_rsi(df_symbol)
    macd = calculate_macd(df_symbol)
    sma = calculate_sma(df_symbol, period=20)
    ema = calculate_ema(df_symbol, period=20)
    bollinger_bands = calculate_bollinger_bands(df_symbol, period=20, num_std_dev=2)
    stochastic_oscillator = calculate_stochastic_oscillator(df_symbol, period=14)
    atr = calculate_atr(df_symbol, period=14)
    adx = calculate_adx(df_symbol, period=14)

    symbol_total_indicators = {
        'RSI': rsi,
        'MACD': macd,
        'SMA': sma,
        'EMA': ema,
        'Bollinger Bands': bollinger_bands,
        'Stochastic Oscillator': stochastic_oscillator,
        'ATR': atr,
        'ADX': adx
    }

    return


def run_technical_analysis_sql(data_interval_start, data_interval_end):

    logger.info(f"Running technical analysis for symbols")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f'{current_dir}/indicators.sql', 'r') as file:
        sql_query = text(file.read())

    try:

        logger.info("Deleting existing data in StockIndicator table...")
        delete_stmt = StockIndicator.__table__.delete().where(
            StockIndicator.created_at == data_interval_end
        )
        session.execute(delete_stmt)
        session.commit()
        logger.info("Deleted existing data in StockIndicator table")

        logger.info("Running technical analysis SQL query...")
        session.execute(sql_query, {
            'start_date': data_interval_start,
            'end_date': data_interval_end
        })
        session.commit()
        logger.info(f"Technical analysis SQL query executed successfully for symbols from {data_interval_start} to {data_interval_end}")
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        session.rollback()
        raise


if __name__ == '__main__':
    symbol = "AMZN"
    run_technical_analysis(symbol)