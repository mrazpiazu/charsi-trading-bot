import datetime
from airflow.decorators import dag, task, task_group
from airflow.operators.python import get_current_context
import logging

from utils.database.functions import *
from utils.technical_analysis.functions import *
from utils.logger.logger import get_logger_config

logger = logging.getLogger("intraday_trading_pipeline_dag")
get_logger_config(logging)


@dag(
    dag_id="RELOAD_BACKFILL_INDICATORS",
    start_date=datetime.datetime(2025, 4, 30, 15),
    schedule='* 12-19 * * *',
    catchup=True,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'email_on_failure': False,
        'email_on_retry': False,
        'depend_on_past': True
    },
    tags=["analysis", "intraday", "trading", "reload"]
)
def intraday_trading_pipeline_dag():

    @task(task_id="run_backfill_fact_stock_bars")
    def run_backfill_data_task():
        context = get_current_context()
        run_backfill_fact_stock_bars(context["data_interval_start"], context["data_interval_end"])

    backfill_task = run_backfill_data_task()


    @task(task_id="run_agg_stock_bars")
    def run_aggregation_data_task():
        context = get_current_context()
        run_agg_stock_bars(context["data_interval_start"], context["data_interval_end"], "15min")

    aggregation_task = run_aggregation_data_task()


    @task(task_id="run_technical_analysis")
    def run_technical_analysis_task():
        context = get_current_context()
        run_technical_analysis_sql(context["data_interval_start"], context["data_interval_end"])

    technical_analysis_task = run_technical_analysis_task()

    backfill_task >> aggregation_task >> technical_analysis_task

intraday_trading_pipeline_dag()