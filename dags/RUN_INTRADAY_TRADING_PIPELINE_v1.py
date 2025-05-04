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
    dag_id="intraday_trading_pipeline_dag_v1",
    start_date=datetime.datetime(2025, 5, 1),
    schedule='*/30 * * * *',
    catchup=True,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'email_on_failure': False,
        'email_on_retry': False,
    },
    tags=["analysis", "intraday", "trading"]
)
def intraday_trading_pipeline_dag():

    symbol_items_list = load_stock_table_list(group_by="alphabetical")

    @task(task_id="run_backfill_symbol_data")
    def run_backfill_data_task():
        context = get_current_context()
        backfill_stock_data(context["data_interval_start"], context["data_interval_end"])

    backfill_task = run_backfill_data_task()

    @task(task_id="run_technical_analysis")
    def run_technical_analysis_task():
        context = get_current_context()
        run_technical_analysis_sql(context["data_interval_start"], context["data_interval_end"])

    technical_analysis_task = run_technical_analysis_task()

    backfill_task >> technical_analysis_task

intraday_trading_pipeline_dag()