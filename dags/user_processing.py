import json
from datetime import datetime

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.hooks.base import BaseHook

from pandas import json_normalize

default_args = {
    'start_date': datetime(2022, 4, 21)
}


def _processing_user(ti):
    users = ti.xcom_pull(task_ids=['extracting_user'])

    if not len(users) or 'results' not in users[0]:
        raise ValueError('User is empty')

    user = users[0]['results'][0]
    processed_user = json_normalize({
        'email': user['email'],
        'firstname': user['name']['first'],
        'lastname': user['name']['last'],
        'country': user['location']['country'],
        'username': user['login']['username'],
        'password': user['login']['password']
    })
    processed_user.to_csv('/tmp/processed_user.csv',
                          index=False,
                          header=False)


def _store_user():
    connection = BaseHook.get_connection('local_mysql')
    hook = MySqlHook(connection=connection)
    hook.bulk_load_custom(table='users', tmp_file='/tmp/processed_user.csv',
                          extra_options='FIELDS TERMINATED BY \',\' ENCLOSED BY \'"\' LINES TERMINATED BY \'\r\'')


with DAG(dag_id='user_processing',
         schedule_interval='@daily',
         default_args=default_args,
         catchup=True) as dag:
    # Define tasks/operators
    creating_table = MySqlOperator(
        task_id='creating_table',
        mysql_conn_id='local_mysql',
        sql='''
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(100) PRIMARY KEY NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        '''
    )

    is_api_available = HttpSensor(
        task_id='is_api_available',
        http_conn_id='user_api',
        endpoint='api/'
    )

    extracting_user = SimpleHttpOperator(
        task_id='extracting_user',
        http_conn_id='user_api',
        endpoint='api/',
        method='GET',
        response_filter=lambda response: json.loads(response.text),
        log_response=True
    )

    processing_user = PythonOperator(
        task_id='processing_user',
        python_callable=_processing_user
    )

    # storing_user = MySqlOperator(
    #     task_id='storing_user',
    #     mysql_conn_id='local_mysql',
    #     sql='''
    #         LOAD DATA LOCAL INFILE '/tmp/processed_user.csv'
    #         INTO TABLE users
    #         FIELDS TERMINATED BY ','
    #         ENCLOSED BY '"'
    #         LINES TERMINATED BY '\r';
    #     '''
    # )

    storing_user = PythonOperator(
        task_id='storing_user',
        python_callable=_store_user
    )

    display_results = BashOperator(
        task_id='display_results',
        bash_command='echo All tasks done.'
    )

    creating_table >> is_api_available >> extracting_user >> processing_user >> storing_user >> display_results
