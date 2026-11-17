"""
DAG: Soda Core Data Quality checks in Airflow.
Проект: soda-data-quality-demo (Часть 2).
Проверяет витрину fct_sales в analytics_rfm (PostgreSQL на Windows, доступ через 10.0.2.2).
Если Soda находит провал проверки — таск падает (стандартный паттерн Data Quality в пайплайне).
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

SODA_PROJECT_DIR = "/opt/airflow/soda-project"
SODA_CONFIG = f"{SODA_PROJECT_DIR}/configuration.docker.yml"
SODA_CHECKS = f"{SODA_PROJECT_DIR}/checks.yml"

default_args = {
    "owner": "pavel",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="soda_quality_fct_sales",
    description="Soda Core checks for fct_sales (e-commerce DWH)",
    default_args=default_args,
    start_date=datetime(2026, 11, 17),
    schedule_interval="@daily",
    catchup=False,
    tags=["data-quality", "soda", "dwh"],
) as dag:

    run_soda_scan = BashOperator(
        task_id="run_soda_scan",
        bash_command=(
            f"/root/.local/bin/soda scan -d analytics_rfm "
            f"-c {SODA_CONFIG} "
            f"{SODA_CHECKS}"
        ),
    )

    run_soda_scan
