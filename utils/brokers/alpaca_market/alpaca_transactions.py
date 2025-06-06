import time
from datetime import datetime as dt, timedelta
import datetime
import logging
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest, StopLimitOrderRequest, LimitOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce, OrderClass

from utils.technical_analysis.indicators import *
from utils.database.db import *
from utils.telegram.telegram import send_telegram_message
from utils.database.models import *
from utils.logger.logger import get_logger_config

logger = logging.getLogger(__name__)
get_logger_config(logging)
load_dotenv()


def place_order(symbol, qty, take_profit, stop_loss, paper=True):
    """
    Place an order with Alpaca API.
    """


    client = TradingClient(
        api_key=os.getenv("ALPACA_API_KEY_ID"),
        secret_key=os.getenv("ALPACA_API_SECRET_KEY"),
        paper=paper
    )

    take_profit_request = TakeProfitRequest(
        limit_price=float(take_profit)
    )

    stop_loss_request = StopLossRequest(
        stop_price=float(stop_loss)
    )

    # preparing orders
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        order_class=OrderClass.BRACKET,
        order_type=OrderType.MARKET,
        take_profit=take_profit_request,
        stop_loss=stop_loss_request
    )

    # Market order
    market_order = client.submit_order(
        order_data=market_order_data
    )

    return market_order


def run_place_order_pipeline(trading_actions):
    """
    Run the pipeline to place orders based on trading actions.
    """

    market_orders = []

    for action in trading_actions:

        try:

            symbol = action["stock"]
            qty = action["position_size"]
            take_profit = action["target_price"]
            stop_loss = action["stop_loss"]

            logging.info(f"Placing order for {symbol} with qty={qty}, take_profit={take_profit}, stop_loss={stop_loss}")
            market_order = place_order(symbol, qty, take_profit, stop_loss)
            logging.info(f"Order placed - order_id: {market_order.id.urn}")

            telegram_message = (
                f"{dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Order placed for {symbol}:\n"
                f"Entry Point: {action['entry_point']}\n"
                f"Position Size: {qty}\n"
                f"Take Profit: {take_profit}\n"
                f"Stop Loss: {stop_loss}\n"
                f"Expected Duration: {action['expected_duration']}\n"
                f"Potential Profit/Loss: {action['potential_profit_loss']}\n"
                f"Risk/Reward Ratio: {action['risk_reward_ratio']}\n"
                f"Order ID: {market_order.id.urn}\n"
            )

            send_telegram_message(telegram_message)

        except Exception as e:
            logging.error(f"Error placing order for {symbol}: {e}")
            telegram_message = (
                f"{dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Error placing order for {symbol}:\n"
                f"Error: {str(e)}\n"
            )
            send_telegram_message(telegram_message)
            continue


if __name__ == "__main__":

    from utils.llm.xynth_finance.xynth_playwright import run_xynth_consultation_pipeline
    import asyncio

    trading_actions = asyncio.run(run_xynth_consultation_pipeline())

    # trading_actions = [{'entry_point': 118.96, 'expected_duration': '12 days', 'position_size': 4, 'potential_profit_loss': 88.18, 'risk_reward_ratio': 2.5, 'stock': 'AMD', 'stop_loss': 110.14, 'target_price': 141.01}, {'entry_point': 83.84, 'expected_duration': '6 days', 'position_size': 3, 'potential_profit_loss': 25.1, 'risk_reward_ratio': 1.78, 'stock': 'UBER', 'stop_loss': 79.15, 'target_price': 92.21}, {'entry_point': 137.97, 'expected_duration': '6 days', 'position_size': 1, 'potential_profit_loss': 12.6, 'risk_reward_ratio': 2.0, 'stock': 'NVDA', 'stop_loss': 131.67, 'target_price': 150.58}]

    run_place_order_pipeline(trading_actions)