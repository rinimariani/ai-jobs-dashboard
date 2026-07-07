# AI Impact on Jobs 2030 — Dashboard

Interactive dashboard exploring a synthetic dataset (3,000 rows) on AI automation
risk, future demand, compensation, and workforce trends across industries and
countries.

> **Note:** the dataset is synthetic/simulated. This project is a portfolio/demo
> piece, not a source for real business decisions.

**Live demo:** _TBD after deployment_

## Architecture

```
CSV -> Python ETL (etl/load_to_db.py) -> PostgreSQL (Supabase)
    -> query layer (dashboard/db.py) -> Streamlit dashboard (dashboard/app.py)
    -> Streamlit Community Cloud
```

## Local setup

1. Clone the repo and create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your Supabase connection strings
   (`ETL_DATABASE_URL` for the write role, `DATABASE_URL` for the read-only role
   used by the dashboard).
3. Load the data into Postgres:
   ```
   python etl/load_to_db.py
   ```
4. Run the dashboard:
   ```
   streamlit run dashboard/app.py
   ```

## Deployment

Deployed on Streamlit Community Cloud, connected directly to this GitHub repo.
Database credentials are set as Streamlit Cloud secrets (`DATABASE_URL`), never
committed to the repo.

## Data

`data/AI_Impact_on_Jobs_2030.csv` — 3,000 rows, 20 columns covering job title,
industry, country, education, AI replacement risk, future demand, salary,
work hours, satisfaction, and hiring trends.
