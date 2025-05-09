import datetime
from datetime import timedelta
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
import logging

from utils.database.functions import *
from utils.logger.logger import get_logger_config

logger = logging.getLogger("stock_update_dag")
get_logger_config(logging)


@dag(
    start_date=datetime.datetime(2025, 5, 5),
    schedule='*/5 12-18 * * 1-5',
    catchup=False,
    max_active_runs=1,
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': datetime.timedelta(minutes=5),
        'email_on_failure': False,
        'email_on_retry': False
    },
    tags=["stocks"]
)
def update_stocks_dag():
    task_id = "update_stocks"

    @task(task_id=task_id)
    def insert_new_stocks_task():
        insert_new_stocks()

    insert_new_stocks_task()

update_stocks_dag()