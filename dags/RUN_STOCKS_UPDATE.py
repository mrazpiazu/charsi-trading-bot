import datetime
from airflow.sdk import dag, task
from airflow.operators.python import get_current_context
import logging

from utils.database.functions import *
from utils.logger.logger import get_logger_config

logger = logging.getLogger("stock_update_dag")
get_logger_config(logging)


@dag(
    start_date=datetime.datetime(2025, 5, 1),
    schedule='*/5 * * * *',
    catchup=True,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'email_on_failure': False,
        'email_on_retry': False,
    },
    tags=["stocks"]
)
def update_stocks_dag():
    task_id = "update_stocks"

    @task(task_id=task_id)
    def update_stocks_task():
        update_stocks()

    update_stocks_task()

update_stocks_dag()