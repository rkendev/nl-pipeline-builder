# AI Data Pipeline

[![CI Status](https://github.com/YourUsername/ai-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/YourUsername/ai-data-pipeline/actions)

**Natural‐language to data pipeline generator**  
_Convert plain‐English descriptions into runnable Python scripts or Airflow DAGs._

## Getting Started

```bash
git clone https://github.com/YourUsername/ai-data-pipeline.git
cd ai-data-pipeline
poetry install
docker compose up -d

https://github.com/YourUsername/ai-data-pipeline/actions/workflows/ci.yml/badge.svg
``` :contentReference[oaicite:3]{index=3} 



 # DAG Info

## Week 1: Example DAG & Dockerized Airflow + Streamlit

### Quickstart

1. **Bring up infrastructure**  
   ```bash
   # Terminal 1 — Long-running services
    docker compose down --volumes
    docker compose up -d postgres
    docker compose up -d --no-deps --build airflow-init
    docker compose run --rm airflow-init `
    airflow users create --username admin `
                        --firstname Admin `
                        --lastname User `
                        --role Admin `
                        --email admin@example.com `
                        --password admin

   # Terminal 2 — Bring Up Webserver, Worker & Streamlit  
   docker compose up -d airflow-web airflow-worker streamlit                    
   ```


# Terminal 2 — one-off commands
# 1) Trigger the DAG
docker compose run --rm airflow-web \
  airflow dags trigger example_dag

# 2) View recent runs
docker compose run --rm airflow-web \
  airflow dags list-runs --dag-id example_dag --no-backfill

# 3) Inspect the state of a task
docker compose run --rm airflow-web \
  airflow tasks state example_dag say_hello 2025-06-14T14:58:36+00:00

# 4) Run a task locally
docker compose run --rm airflow-web \
  airflow tasks run example_dag print_date \
    2025-06-14T14:58:36+00:00 --local



