from airflow.models import DAG

from airflow.providers.mysql.operators.mysql import MySqlOperator

from datetime import datetime

default_args = {
    'start_date': datetime(2022, 1, 1)
}

with DAG(dag_id='user_processing',
         schedule_interval='@daily',
         default_args=default_args,
         catchup=False) as dag:

    # Define tasks/operators
    creating_table = MySqlOperator(
        task_id='creating_table',
        mysql_conn_id='local_mysql',
        sql='''
            CREATE TABLE IF NOT EXISTS user (
                email INTEGER PRIMARY KEY NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        '''
    )
