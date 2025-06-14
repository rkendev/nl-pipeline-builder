# DAG Info

## Week 1: Example DAG & Dockerized Airflow + Streamlit

### Quickstart

1. **Bring up infrastructure**  
   ```bash
   # Terminal 1 — long-running services
   docker compose down --remove-orphans --volumes
   docker compose up -d postgres
   docker compose up -d --no-deps --build airflow-init
   docker compose up -d airflow-web airflow-worker streamlit
