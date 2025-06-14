# dags/example_dag.py
from datetime import datetime, timedelta
import random

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "airflow_user",
    "depends_on_past": False,
    "email_on_failure": False,
    "retry_delay": timedelta(minutes=5),
    "retries": 1,
}

def print_date():
    """Print the current UTC time."""
    print(f"Current date/time: {datetime.utcnow()}")

def gen_number(ti):
    """Generate a random integer and push it via XCom."""
    num = random.randint(1, 100)
    ti.xcom_push(key="my_number", value=num)
    print(f"Generated {num} and pushed to XCom")

def print_number(ti):
    """Pull the random integer from XCom and print it."""
    num = ti.xcom_pull(task_ids="gen_number", key="my_number")
    print(f"Pulled via XCom: {num}")

with DAG(
    dag_id="example_dag",
    default_args=default_args,
    description="Week 1 demo: bash → python → XCom chain",
    start_date=datetime(2025, 6, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    t1 = BashOperator(
        task_id="say_hello",
        bash_command="echo '👋 Hello from Airflow!'"
    )

    t2 = PythonOperator(
        task_id="print_date",
        python_callable=print_date
    )

    t3 = PythonOperator(
        task_id="gen_number",
        python_callable=gen_number
    )

    t4 = PythonOperator(
        task_id="print_number",
        python_callable=print_number
    )

    t1 >> t2 >> t3 >> t4

