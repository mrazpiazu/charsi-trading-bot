import logging
from sqlalchemy import text, insert, select, distinct
from sqlalchemy.sql import exists
import os
from datetime import datetime as dt

from utils.database.db import SessionLocal
from utils.database.models import StockBar, Stock
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
        return []
    finally:
        session.close()


def load_stock_table_list(group_by=None):
    """
    Load the Stock table from the database.
    Returns:
        list: List of Stock objects.
    """
    try:
        query = session.query(Stock)
        stock_table = query.all()

        stock_table_list = [symbol.symbol for symbol in stock_table]

        if group_by == 'alphabetical':
            # Group list by starting letter
            stock_table_list.sort()
            grouped_stock_table = []
            for symbol in stock_table_list:
                starting_letter = symbol[0].upper()
                if starting_letter not in grouped_stock_table:
                    grouped_stock_table.append(starting_letter)

            stock_table_list = grouped_stock_table

        return stock_table_list
    except Exception as e:
        logger.error(f"Error loading Stock table: {e}")
        return []
    finally:
        session.close()


def load_stock_starting_by(starting_letter):

    """
    Load the Stock table from the database.
    Args:
        starting_letter (str): Starting letter to filter symbols.
    Returns:
        list: List of Stock objects starting with the specified letter.
    """
    try:
        query = session.query(Stock).filter(Stock.symbol.like(f"{starting_letter}%"))
        stock_table = query.all()

        stock_table_list = [symbol.symbol for symbol in stock_table]

        return stock_table_list
    except Exception as e:
        logger.error(f"Error loading Stock table: {e}")
        return []
    finally:
        session.close()


def insert_new_stocks():
    """
    Inserts distinct symbols from StockBar into Stock table
    Returns:
    """

    stmt = insert(Stock).from_select(
        ['symbol'],
        select(distinct(StockBar.symbol)).where(
            ~StockBar.symbol.in_(select(Stock.symbol).scalar_subquery())
        )
    )

    session.execute(stmt)
    session.commit()


def backfill_stock_data(start_time, end_time):
    """
    Backfill data for a specific symbol.
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))

    with open(f"{current_dir}/stock_bar_backfill.sql", "r") as file:
        sql_query = text(file.read())

    try:
        session.execute(sql_query, {
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