import datetime
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
import logging

from utils.brokers.alpaca_market.alpaca_functions import get_daily_revenue
from utils.analysis.daily_report import generate_daily_report
from utils.telegram.telegram import send_telegram_report
from utils.logger.logger import get_logger_config

logger = logging.getLogger("daily_analysis_dag")
get_logger_config(logging)


@dag(
    dag_id="RUN_DAILY_ANALYSIS",
    start_date=datetime.datetime(2025, 6, 9),
    schedule='15 20 * * 1-5',
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
    def get_portfolio_history_task():
        return get_daily_revenue()

    @task(task_id="generate_daily_report")
    def generate_daily_report_task(portfolio_history):
        report_data = generate_daily_report(portfolio_history)
        return report_data

    @task(task_id="send_telegram_report")
    def send_telegram_report_task(report_data):
        context = get_current_context()
        report_data = report_data.resolve(context)
        send_telegram_report(report_data)

    portfolio_history = get_portfolio_history_task()
    report_data = generate_daily_report_task(portfolio_history)
    send_telegram_report(report_data)

daily_analysis_dag()