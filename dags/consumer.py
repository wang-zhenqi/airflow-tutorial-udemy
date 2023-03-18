from airflow import DAG
from airflow.datasets import Dataset
from airflow.decorators import task

from datetime import datetime

my_file = Dataset('dags/tmp/my_file.txt')

with DAG(
    dag_id='consumer',
    schedule=[my_file],
    start_date=datetime(2023, 3, 18),
    catchup=False
):

    @task
    def read_dataset():
        with open(my_file.uri, 'a+') as f:
            f.write('consumer read\n')

    read_dataset()
