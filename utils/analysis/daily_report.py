import time
from datetime import datetime as dt, timedelta
import datetime
import logging
import os
from dotenv import load_dotenv
import seaborn as sns

from utils.technical_analysis.indicators import *
from utils.telegram.telegram import send_telegram_message
from utils.logger.logger import get_logger_config

logger = logging.getLogger(__name__)  # Get logger for current module
get_logger_config(logging)  # Apply project-level logger config
load_dotenv()  # Load .env variables like API keys


# Generated a chart with the portfolio history and sends it to Telegram
def generate_daily_report(portfolio_history):

    sns.set_theme(style="darkgrid")
    ax = sns.lineplot(
        x=[dt.fromtimestamp(ts) for ts in portfolio_history.timestamp],
        y=portfolio_history.equity,
        label="Equity"
    )
    ax.set_title("Portfolio Equity Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity ($)")
    ax.figure.autofmt_xdate()  # Rotate x-axis labels for better readability

    profit_loss = portfolio_history.profit_loss
    profit_loss_changes = [round(profit_loss[i] - profit_loss[i - 1], 2) for i in range(1, len(profit_loss))]

    ax2 = sns.barplot(
        x=[dt.fromtimestamp(ts) for ts in portfolio_history.timestamp[1:]],
        y=profit_loss_changes,
        palette=["green" if change >= 0 else "red" for change in profit_loss_changes]
    )
    ax2.set_title("Daily Profit/Loss Changes")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Profit/Loss Change ($)")
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Draw a horizontal line at y=0
    ax2.figure.autofmt_xdate()  # Rotate x-axis labels for better readability

    report_data = {
        "total_profit_loss": round(profit_loss[-1], 2),
        "total_equity": round(portfolio_history.equity[-1], 2),
        "plots": []
    }

    # Save the plots to a temporary directory
    for plot in [ax.figure, ax2.figure]:
        plot_path = f"/tmp/{plot.get_label()}.png"
        plot.savefig(plot_path)
        report_data["plots"].append(plot_path)

    return report_data


if __name__ == "__main__":

    from utils.brokers.alpaca_market.alpaca_functions import get_daily_revenue

    portfolio_history = get_daily_revenue()

    generate_daily_report(portfolio_history)