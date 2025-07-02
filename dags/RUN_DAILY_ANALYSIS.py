import datetime
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowSkipException
import logging

from utils.brokers.alpaca_market.alpaca_functions import get_daily_revenue
from utils.analysis.daily_report import generate_revenue_report
from utils.telegram.telegram import send_telegram_report
from utils.logger.logger import get_logger_config

logger = logging.getLogger("daily_analysis_dag")
get_logger_config(logging)


@dag(
    dag_id="RUN_DAILY_ANALYSIS",
    start_date=datetime.datetime(2025, 6, 9),
    schedule='15 10 * * *',
    catchup=False,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'email_on_failure': False,
        'email_on_retry': False
    },
    tags=["analysis", "daily", "stocks"]
)
def daily_analysis_dag():

    @task(task_id="profit_loss_daily_analysis")
    def get_portfolio_history_task(period_offset_days=0, time_unit="D", time_unit_value=1, timeframe="1H", budget=False):
        execution_date = get_current_context()["logical_date"] + datetime.timedelta(days=1)
        weekday = execution_date.weekday()
        if weekday in [0, 6]:  # Monday or Sunday
            logger.info("Skipping daily analysis on Sunday or Monday.")
            raise AirflowSkipException("Daily analysis skipped on Sunday or Monday")
        return get_daily_revenue(
            period_offset_days=period_offset_days,
            time_unit=time_unit,
            time_unit_value=time_unit_value,
            timeframe=timeframe,
            budget=budget
        )

    @task(task_id="generate_daily_report")
    def generate_report_task(portfolio_history, timeframe="Day"):
        return generate_revenue_report(portfolio_history, timeframe)

    @task(task_id="send_telegram_report")
    def send_telegram_report_task(report_data):
        send_telegram_report(report_data)
        return

    portfolio_history_daily = get_portfolio_history_task()
    report_data_daily = generate_report_task(portfolio_history_daily)
    send_report_daily = send_telegram_report_task(report_data_daily)

    portfolio_history_monthly = get_portfolio_history_task(period_offset_days=30, time_unit="M", time_unit_value=1, timeframe="1D")
    report_data_monthly = generate_report_task(portfolio_history_monthly, "Month")
    send_report_monthly = send_telegram_report_task(report_data_monthly)

    portfolio_history_daily_budget = get_portfolio_history_task(budget=True)
    report_data_daily_budget = generate_report_task(portfolio_history_daily_budget)
    send_report_daily_budget = send_telegram_report_task(report_data_daily_budget)

    portfolio_history_monthly_budget = get_portfolio_history_task(period_offset_days=30, time_unit="M", time_unit_value=1, timeframe="1D", budget=True)
    report_data_monthly_budget = generate_report_task(portfolio_history_monthly_budget, "Month")
    send_report_monthly_budget = send_telegram_report_task(report_data_monthly_budget)

    send_report_monthly >> portfolio_history_daily
    send_report_daily >> send_report_monthly_budget >> portfolio_history_daily_budget

daily_analysis_dag()