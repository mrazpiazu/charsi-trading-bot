import time
from datetime import datetime as dt, timedelta
import datetime
import logging
import pandas as pd
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


def get_daily_revenue(start_date=None, end_date=None, period_offset_days=7, timeframe="1D"):
    """
    Get daily revenue from Alpaca account.
    """

    client = create_client(paper=True)

    if start_date is None:
        start_date = dt.now() - timedelta(days=period_offset_days) # Default to 00:00:00 today

        if period_offset_days == 0:
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    if end_date is None:
        end_date = dt.now()

    request_history_filter = GetPortfolioHistoryRequest(
        start=start_date,
        end=end_date,
        timeframe=timeframe,
        extended_hours=False
    )

    # Fetch daily revenue data
    daily_revenue_data = client.get_portfolio_history(
        history_filter=request_history_filter  # Apply the request filter
    )

    daily_revenue_data_dict = {
        "timestamp": [int(ts) for ts in daily_revenue_data.timestamp],
        "datetime": [dt.fromtimestamp(ts) for ts in daily_revenue_data.timestamp],
        "equity": daily_revenue_data.equity,
        "profit_loss": daily_revenue_data.profit_loss
    }

    df = pd.DataFrame(daily_revenue_data_dict)

    if period_offset_days != 1:
        df['date'] = df['datetime'].dt.date
        df_daily_revenue = df.groupby('date').agg({
            'equity': 'mean',
            'profit_loss': 'mean'
        }).reset_index()
        df_daily_revenue['timestamp'] = df_daily_revenue['date'].apply(lambda x: int(dt.combine(x, dt.min.time()).timestamp()))
    else:
        df_daily_revenue = df

    daily_revenue_data_dict = df_daily_revenue.to_dict('list')

    return daily_revenue_data_dict


if __name__ == "__main__":
    # Example usage
    client = create_client(paper=True)  # Create a paper trading client
    # balance = get_account_balance(client)  # Get current account balance
    # equity = get_account_equity(client)  # Get current account equity
    # positions = get_account_positions(client)  # Get current account positions
    # orders = get_account_orders(client)  # Get current account orders
    daily_revenue = get_daily_revenue(period_offset_days=0, timeframe="1H")  # Get daily revenue
    monthly_revenue = get_daily_revenue(period_offset_days=30, timeframe="1D")  # Get daily revenue
    print("done")