import datetime
from airflow.sdk import dag, task, task_group
from airflow.sdk import get_current_context
import logging

from utils.database.functions import *
from utils.technical_analysis.functions import *
from utils.logger.logger import get_logger_config

logger = logging.getLogger("technical_analysis_dag")
get_logger_config(logging)


@dag(
    start_date=datetime.datetime(2025, 5, 1),
    schedule='0 * * * *',
    catchup=True,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'email_on_failure': False,
        'email_on_retry': False,
    },
    tags=["technical", "analysis"]
)
def technical_analysis_dag():
    symbols = get_active_symbols()

    for symbol in symbols:
        group_id = f"trading_task_group_{symbol.replace('.', '_')}"
        task_id_backfill = f"run_backfill_symbol_data_{symbol}"
        task_id_technical_analysis = f"run_technical_analysis_{symbol}"

        @task_group(group_id=group_id)
        def trading_task_group(symbol=symbol):

            @task(task_id=task_id_backfill)
            def run_backfill_symbol_data_task(symbol=symbol):
                context = get_current_context()

                backfill_symbol_data(context["data_interval_start"], context["data_interval_end"], symbol)

            @task(task_id=task_id_technical_analysis)
            def run_technical_analysis_task(symbol=symbol):
                context = get_current_context()

                run_technical_analysis_sql(context["data_interval_start"], context["data_interval_end"], symbol)

            run_backfill_symbol_data_task(symbol=symbol) >> run_technical_analysis_task(symbol=symbol)

        trading_task_group(symbol=symbol)

technical_analysis_dag()