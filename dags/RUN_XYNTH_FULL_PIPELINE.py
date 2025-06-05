import datetime
from airflow.decorators import dag, task
import logging
import asyncio

from utils.logger.logger import get_logger_config
from utils.llm.xynth_finance.xynth_playwright import run_xynth_consultation_pipeline
from utils.brokers.alpaca_market.alpaca_transactions import run_place_order_pipeline

logger = logging.getLogger("run_xynth_full_pipeline_dag")
get_logger_config(logging)


@dag(
    dag_id="RUN_XYNTH_FULL_PIPELINE",
    start_date=datetime.datetime(2025, 6, 4, 15),
    schedule='11 14,15 * * 1-5',  # Every day at 14:00 and 16:00 on weekdays
    catchup=False,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'email_on_failure': False,
        'email_on_retry': False,
        'depend_on_past': False
    },
    tags=["order", "trading", "xynth"]
)
def xynth_full_pipeline_dag():

    @task(task_id="run_xynth_consultation")
    def run_xynth_consultation():
        trading_actions = asyncio.run(run_xynth_consultation_pipeline())
        return trading_actions

    @task(task_id="place_orders")
    def place_orders(trading_actions):
        run_place_order_pipeline(trading_actions)

    trading_actions = run_xynth_consultation()
    place_orders(trading_actions)

xynth_full_pipeline_dag()