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
def generate_revenue_report(portfolio_history, timeframe="Day", test=False):

    sns.set_theme(style="darkgrid")

    # CHART 1 (equity_plot)
    fig1, ax1 = plt.subplots()

    timestamps = [dt.fromtimestamp(ts) for ts in portfolio_history["timestamp"]]
    y = np.array(portfolio_history["equity"])
    x = np.arange(len(timestamps))

    sns.lineplot(x=timestamps, y=y, label="Equity", ax=ax1)

    slope, intercept = np.polyfit(x, y, 1)
    trend = slope * x + intercept
    sns.lineplot(x=timestamps, y=trend, label="Tendency", color='orange', linestyle='--', ax=ax1)

    ax1.set_title(f"Portfolio Equity Over Last {timeframe}")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Equity ($)")
    ax1.set_label("equity_plot")
    fig1.autofmt_xdate()
    if test == True:
        plt.show()


    # CHART 2 (profit_loss)
    profit_loss = portfolio_history["profit_loss"]
    profit_loss_changes = [round(profit_loss[i] - profit_loss[i - 1], 2) for i in range(1, len(profit_loss))]

    fig2, ax2 = plt.subplots()

    raw_timestamps = portfolio_history["timestamp"][1:]
    readable_dates = [dt.fromtimestamp(ts).strftime('%Y-%m-%d') for ts in raw_timestamps]
    y = np.array(profit_loss_changes)
    x = np.arange(len(y))

    sns.barplot(
        x=x,
        y=y,
        palette=["green" if change >= 0 else "red" for change in y],
        ax=ax2
    )

    slope, intercept = np.polyfit(x, y, 1)
    trend = slope * x + intercept
    sns.lineplot(x=x, y=trend, label="Tendency", color='orange', linestyle='--', ax=ax2)

    # Chart 2
    ax2.set_xticks(x)
    ax2.set_xticklabels(readable_dates, rotation=45)
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax2.set_title(f"Profit/Loss Changes Over Last {timeframe}")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Profit/Loss Change ($)")
    ax2.set_label("profit_loss_plot")
    plt.tight_layout()

    if test == True:
        plt.show()

    # Interest rate per cycle time serie
    interest_rates = [
        round((portfolio_history["equity"][i] / portfolio_history["equity"][i - 1] - 1) * 100, 2)
        for i in range(1, len(portfolio_history["equity"]))
    ]

    report_data = {
        "total_profit_loss": round(portfolio_history["profit_loss"][-1] - portfolio_history["profit_loss"][0], 2),
        "total_equity": round(portfolio_history["equity"][-1], 2),
        "max_equity": round(max(portfolio_history["equity"]), 2),
        "min_equity": round(min(portfolio_history["equity"]), 2),
        "avg_equity": round(sum(portfolio_history["equity"]) / len(portfolio_history["equity"]), 2),
        "max_profit_loss": round(max(profit_loss_changes), 2),
        "min_profit_loss": round(min(profit_loss_changes), 2),
        "avg_profit_loss": round(sum(profit_loss_changes) / len(profit_loss_changes), 2),
        "avg_interest_rate": round(sum(interest_rates) / len(interest_rates), 2),
        "final_interest_rate": round(((portfolio_history["equity"][-1] / portfolio_history["equity"][0]) - 1) * 100, 2),
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

    # portfolio_history = get_daily_revenue(period_offset_days=0, time_unit="D", time_unit_value=1, timeframe="1H", budget=False)
    portfolio_history = get_daily_revenue(period_offset_days=30, time_unit="M", time_unit_value=1, timeframe="1D", budget=False)

    report_data = generate_revenue_report(portfolio_history, test=True)

    send_telegram_report(report_data)