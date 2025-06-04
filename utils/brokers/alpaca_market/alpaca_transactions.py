import time
from datetime import datetime as dt, timedelta
import datetime
import logging
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce

from utils.technical_analysis.indicators import *
from utils.database.db import *
from utils.database.models import *
from utils.logger.logger import get_logger_config

logger = logging.getLogger(__name__)
get_logger_config(logging)
load_dotenv()


def place_order(symbol, qty, take_profit, stop_loss):
    """
    Place an order with Alpaca API.
    """


    client = TradingClient(
        api_key=os.getenv("ALPACA_API_KEY_ID"),
        secret_key=os.getenv("ALPACA_API_SECRET_KEY"),
        paper=True
    )

    take_profit_request = TakeProfitRequest(
        limit_price=take_profit
    )

    stop_loss_request = StopLossRequest(
        stop_price=stop_loss
    )

    # preparing orders
    market_order_data = MarketOrderRequest(
                        symbol=symbol,
                        qty=qty,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.DAY,
                        order_type=OrderType.MARKET,
                        take_profit=take_profit_request,
                        stop_loss=stop_loss_request
                        )

    # Market order
    market_order = client.submit_order(
                    order_data=market_order_data
                   )

    return


def run_place_order_pipeline(trading_actions):
    """
    Run the pipeline to place orders based on trading actions.
    """

    for action in trading_actions:
        symbol = action["stock"]
        qty = action["position_size"]
        take_profit = action["target_price"]
        stop_loss = action["stop_loss"]

        logging.info(f"Placing order for {symbol} with qty={qty}, take_profit={take_profit}, stop_loss={stop_loss}")
        place_order(symbol, qty, take_profit, stop_loss)


if __name__ == "__main__":

    from utils.llm.xynth_finance.xynth_playwright import run
    import asyncio

    trading_actions = asyncio.run(run())

    run_place_order_pipeline(trading_actions)