import time
from datetime import datetime as dt, timedelta
import datetime
import logging
import os
from dotenv import load_dotenv
import seaborn as sns
from io import BytesIO
import base64

from utils.technical_analysis.indicators import *
import matplotlib.pyplot as plt
from utils.telegram.telegram import send_telegram_message, send_telegram_report
from utils.logger.logger import get_logger_config

logger = logging.getLogger(__name__)  # Get logger for current module
get_logger_config(logging)  # Apply project-level logger config
load_dotenv()  # Load .env variables like API keys


# Generated a chart with the portfolio history and sends it to Telegram
def generate_revenue_report(portfolio_history, timeframe="Day"):

    fig1, ax1 = plt.subplots()
    sns.set_theme(style="darkgrid")
    sns.lineplot(
        x=[dt.fromtimestamp(ts) for ts in portfolio_history["timestamp"]],
        y=portfolio_history["equity"],
        label="Equity"
    )
    ax1.set_title(f"Portfolio Equity Over Last {timeframe}")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Equity ($)")
    ax1.set_label("equity_plot")
    fig1.autofmt_xdate()  # Rotate x-axis labels for better readability

    profit_loss = portfolio_history["profit_loss"]
    profit_loss_changes = [round(profit_loss[i] - profit_loss[i - 1], 2) for i in range(1, len(profit_loss))]

    fig2, ax2 = plt.subplots()
    sns.barplot(
        x=[dt.fromtimestamp(ts) for ts in portfolio_history["timestamp"][1:]],
        y=profit_loss_changes,
        palette=["green" if change >= 0 else "red" for change in profit_loss_changes]
    )
    ax2.set_title(f"Profit/Loss Changes Over Last {timeframe}")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Profit/Loss Change ($)")
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Draw a horizontal line at y=0
    ax2.set_label("profit_loss_plot")
    fig2.autofmt_xdate()  # Rotate x-axis labels for better readability

    report_data = {
        "total_profit_loss": round(profit_loss[-1], 2),
        "total_equity": round(portfolio_history["equity"][-1], 2),
        "plots": {}
    }

    # Save the plots to a temporary directory
    for plot in [ax1, ax2]:
        buffer = BytesIO()
        plot.figure.savefig(buffer, format='png')
        buffer.seek(0)
        image_bytes = buffer.read()
        report_data["plots"][plot.get_label()] = base64.b64encode(image_bytes).decode('utf-8')

    return report_data


if __name__ == "__main__":

    from utils.brokers.alpaca_market.alpaca_functions import get_daily_revenue

    portfolio_history = get_daily_revenue()

    report_data = generate_daily_report(portfolio_history)

    send_telegram_report(report_data)