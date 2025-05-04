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

    task_id_backfill = f"run_backfill_symbol_data"

    @task(task_id=task_id_backfill)
    def run_backfill_data_task():
        context = get_current_context()

        backfill_stock_data(context["data_interval_start"], context["data_interval_end"])

    backfill_task = run_backfill_data_task()

    trading_task_groups = []

    for symbol_item in symbol_items_list:
        group_id = f"trading_task_group_{symbol_item.replace('.', '_')}"
        task_id_technical_analysis = f"run_technical_analysis_{symbol_item}"

        @task_group(group_id=group_id)
        def trading_task_group(symbol=symbol_item):

            @task(task_id=task_id_technical_analysis)
            def run_technical_analysis_task(symbol=symbol_item):
                context = get_current_context()

                run_technical_analysis_sql(context["data_interval_start"], context["data_interval_end"], symbol)

            run_technical_analysis_task(symbol=symbol_item)

        trading_task_group = trading_task_group(symbol=symbol_item)
        trading_task_groups.append(trading_task_group)

    backfill_task >> trading_task_groups

intraday_trading_pipeline_dag()