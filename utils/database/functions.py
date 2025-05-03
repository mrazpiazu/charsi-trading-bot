import logging
from sqlalchemy import text

from utils.database.db import SessionLocal
from utils.database.models import StockBar
from utils.logger.logger import get_logger_config

logger = logging.getLogger("db_functions")
get_logger_config(logging)

session = SessionLocal()

def get_active_symbols():
    """
    Load active symbols from the database.
    """
    try:
        query = session.query(StockBar)
        active_symbols = query.distinct(StockBar.symbol).all()
        symbols = [symbol.symbol for symbol in active_symbols]

        return symbols
    except Exception as e:
        logger.error(f"Error loading active symbols: {e}")
        return ["test1"]
    finally:
        session.close()


def backfill_symbol_data(start_time, end_time, symbol):
    """
    Backfill data for a specific symbol.
    """

    with open("utils/database/stock_bar_backfill.sql", "r") as file:
        sql_query = text(file.read())

    try:
        session.execute(sql_query, {
            "symbol": symbol,
            "start_time": start_time,
            "end_time": end_time
        })
        session.commit()
    except Exception as e:
        logger.error(f"Error backfilling symbol data: {e}")
        session.rollback()
        raise(e)


if __name__ == "__main__":
    symbols = get_active_symbols()
    print(symbols)