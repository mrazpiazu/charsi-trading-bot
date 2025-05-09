import datetime
from airflow.decorators import dag, task, task_group
from airflow.operators.python import get_current_context
import logging

from utils.database.functions import run_backfill_fact_stock_bars_api, run_backfill_fact_stock_bars, run_agg_stock_bars_candles, load_stock_table_list, run_agg_stock_bars
from utils.technical_analysis.functions import run_technical_analysis_sql
from utils.logger.logger import get_logger_config

logger = logging.getLogger("intraday_trading_pipeline_dag")
get_logger_config(logging)


@dag(
    dag_id="intraday_trading_pipeline_dag_v1",
    start_date=datetime(2025, 5, 6, 12),
    schedule='*/15 12-18 * * 1-5',
    catchup=True,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'depend_on_past': True,
        'email_on_failure': False,
        'email_on_retry': False,
    },
    tags=["analysis", "intraday", "trading"]
)
def intraday_trading_pipeline_dag():

    symbol_items_list = load_stock_table_list(group_by="alphabetical")

    @task(task_id="run_backfill_fact_stock_bars")
    def run_backfill_data_task():
        context = get_current_context()

        start_time = context["data_interval_start"]
        end_time = context["data_interval_end"]

        if end_time - start_time > datetime.timedelta(minutes=15):
            start_time = end_time - datetime.timedelta(minutes=15)

        run_backfill_fact_stock_bars(start_time, end_time)

    backfill_task = run_backfill_data_task()


    @task(task_id="run_agg_stock_bars")
    def run_aggregation_data_task():
        context = get_current_context()

        start_time = context["data_interval_start"]
        end_time = context["data_interval_end"]

        if end_time - start_time > datetime.timedelta(minutes=15):
            start_time = end_time - datetime.timedelta(minutes=15)

        run_agg_stock_bars(start_time, end_time, "15min")

    aggregation_task = run_aggregation_data_task()


    @task(task_id="run_technical_analysis")
    def run_technical_analysis_task():
        context = get_current_context()

        start_time = context["data_interval_start"]
        end_time = context["data_interval_end"]

        if end_time - start_time > datetime.timedelta(minutes=15):
            start_time = end_time - datetime.timedelta(minutes=15)

        run_technical_analysis_sql(start_time, end_time)

    technical_analysis_task = run_technical_analysis_task()

    backfill_task >> aggregation_task >> technical_analysis_task

intraday_trading_pipeline_dag()