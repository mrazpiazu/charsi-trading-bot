import time
from datetime import datetime as dt, timedelta
import datetime
import logging
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetPortfolioHistoryRequest

from utils.technical_analysis.indicators import *
from utils.database.db import *
from utils.telegram.telegram import send_telegram_message
from utils.database.models import *
from utils.logger.logger import get_logger_config

logger = logging.getLogger(__name__)  # Get logger for current module
get_logger_config(logging)  # Apply project-level logger config
load_dotenv()  # Load .env variables like API keys


# Create client
def create_client(paper=True):
    """
    Create an Alpaca TradingClient instance.
    """
    return TradingClient(
        api_key=os.getenv("ALPACA_API_KEY_ID"),  # API key from environment
        secret_key=os.getenv("ALPACA_API_SECRET_KEY"),  # Secret key from environment
        paper=paper  # Use paper trading if True
    )


# Get the current account balance from Alpaca
def get_account_balance(client):
    """
    Get the current account balance from Alpaca.
    """
    account = client.get_account()  # Fetch account details
    return float(account.cash)  # Return available cash balance as float


def get_account_equity(client):
    """
    Get the current account equity from Alpaca.
    """
    account = client.get_account()  # Fetch account details
    return float(account.equity)  # Return total equity as float


def get_account_positions(client):
    """
    Get the current account positions from Alpaca.
    """
    positions = client.get_all_positions()  # Fetch all positions
    return positions


def get_account_orders(client):
    """
    Get the current account orders from Alpaca.
    """
    orders = client.get_orders()  # Fetch all orders
    return orders


def get_daily_revenue(start_date=None, end_date=None, days=1):
    """
    Get daily revenue from Alpaca account.
    """

    client = create_client(paper=True)

    if start_date is None:
        start_date = dt.now().replace(hour=0, minute=0, second=0, microsecond=0) # Default to 00:00:00 today
    if end_date is None:
        end_date = dt.now()  # Default to today

    request_history_filter = GetPortfolioHistoryRequest(
        period=f"{days}D",  # Daily data
        start=start_date,  # Start date
        # date_end=end_date,  # End date
        extended_hours=True,
        timeframe="1H",  # Timeframe for daily data
    )

    # Fetch daily revenue data
    daily_revenue = client.get_portfolio_history(
        history_filter=request_history_filter  # Apply the request filter
    )

    return daily_revenue.__dict__


if __name__ == "__main__":
    # Example usage
    client = create_client(paper=True)  # Create a paper trading client
    # balance = get_account_balance(client)  # Get current account balance
    # equity = get_account_equity(client)  # Get current account equity
    # positions = get_account_positions(client)  # Get current account positions
    # orders = get_account_orders(client)  # Get current account orders
    daily_revenue = get_daily_revenue()  # Get daily revenue
    print("done")