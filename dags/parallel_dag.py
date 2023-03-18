from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime

with DAG('parallel_dag', start_date=datetime(2023, 3, 9),
         schedule_interval='@hourly', catchup=False) as dag:
    extract_a = BashOperator(
        task_id='extract_a',
        bash_command='sleep 1'
    )

    extract_b = BashOperator(
        task_id='extract_b',
        bash_command='sleep 1'
    )

    load_a = BashOperator(
        task_id='load_a',
        bash_command='sleep 1'
    )

    load_b = BashOperator(
        task_id='load_b',
        bash_command='sleep 1'
    )

    transform = BashOperator(
        task_id='transform',
        bash_command='sleep 1'
    )

    extract_a >> load_a
    extract_b >> load_b
    [load_a, load_b] >> transform
