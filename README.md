Soda Core: Data Quality Demo
Pet-проект по настройке проверок качества данных (Data Quality) с помощью Soda Core.

🎯 Бизнес-задача
Настроить автоматические проверки для витрины fct_sales (e-commerce), чтобы выявлять проблемы с данными до того, как они попадут в отчеты.

🛠 Стек
Soda Core (3.5.6): Инструмент для проверки качества данных (аналог Great Expectations).

PostgreSQL: База данных, где лежит витрина fct_sales.

Apache Airflow (2.8.1): Оркестрация пайплайна (Часть 2).

📊 Что было сделано (Часть 1: ручной запуск Soda)
Установлен Soda Core и драйвер для PostgreSQL.

Настроено подключение к базе analytics_rfm (файл configuration.yml).

Написаны 4 проверки (файл checks.yml):

Таблица не пустая.

Нет пустых invoice_no.

Нет отрицательной выручки.

Нет дублей товара в чеке (invoice_no + stock_code).

🔍 Результаты (найденный инцидент)
При запуске проверок 3 из 4 прошли успешно. Проверка на дубликаты выявила 9120 случаев, когда один и тот же товар встречается в чеке несколько раз.

https://soda_scan_result.png/

Вывод: В реальном проекте это требует либо агрегации данных (SUM по количеству), либо разбирательства с источником (почему дублируются строки). Soda Core позволяет быстро находить такие аномалии.

🚀 Часть 2: Soda Core в Airflow (Data Quality в пайплайне)
В Части 1 Soda запускался вручную. В Части 2 те же проверки встроены в Airflow-пайплайн: если Soda находит провал — таск падает, DAG останавливается. Это стандартный паттерн Data Quality в оркестрации.

Что добавлено
dags/soda_quality_dag.py — DAG Airflow (BashOperator вызывает soda scan).

configuration.docker.yml — конфиг Soda для запуска из контейнера Airflow (хост 10.0.2.2, т.к. PostgreSQL на Windows).

requirements.txt — зависимости для установки в контейнер Airflow.

Как подключить к существующему Airflow (standalone в Docker)
Смонтировать папку проекта в контейнер Airflow. В docker-compose.yml standalone Airflow добавь volume к сервисам airflow-scheduler и airflow-webserver:
yaml
volumes:

/path/to/soda-data-quality-demo:/opt/airflow/soda-project

Затем docker compose up -d (пересоздаст контейнеры с новым volume).

Установить Soda в контейнеры:
bash
docker exec -it standalone-airflow-scheduler-1 pip install -r /opt/airflow/soda-project/requirements.txt
docker exec -it standalone-airflow-webserver-1 pip install -r /opt/airflow/soda-project/requirements.txt

Скопировать DAG в папку DAGs Airflow:
bash
cp dags/soda_quality_dag.py ~/airflow/standalone/dags/

Задать переменные окружения (DB_USER, DB_PASSWORD) в контейнере Airflow — через .env или environment в compose. Пример .env.example:
env
DB_USER=dwh_user
DB_PASSWORD=dwh_password

Запустить DAG в UI Airflow: soda_quality_fct_sales → Trigger DAG.

📉 Результат: пайплайн падает при проблемах с данными
При запуске DAG таск run_soda_scan упал (красный статус) — потому что Soda нашла провал проверки (дубли). Лог Airflow:

text
[04:03:21] Soda Core 3.5.6
[04:03:21] Scan summary:
[04:03:21] 3/4 checks PASSED:
[04:03:21] fct_sales in analytics_rfm
[04:03:21] Таблица не пустая [PASSED]
[04:03:21] Нет пустых invoice_no [PASSED]
[04:03:21] Нет отрицательной выручки [PASSED]
[04:03:21] 1/4 checks FAILED:
[04:03:21] fct_sales in analytics_rfm
[04:03:21] Нет дублей товара в чеке [FAILED]
[04:03:21] check_value: 9120
[04:03:21] Oops! 1 failures. 0 warnings. 0 errors. 3 pass.
[04:03:24] Command exited with return code 2
[04:03:24] airflow.exceptions.AirflowException: Bash command failed. The command returned a non-zero exit code 2.
[04:03:24] Marking task as FAILED.

Вывод: Data Quality в пайплайне работает — при провале проверки пайплайн останавливается, и проблема не уходит в отчёты незамеченной.

🚀 Как запустить (Часть 1)
Установить зависимости: pip install soda-core-postgres

Настроить configuration.yml (креды к БД).

Запустить: soda scan -d analytics_rfm -c configuration.yml checks.yml
