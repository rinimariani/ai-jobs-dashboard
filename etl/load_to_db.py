"""Load AI_Impact_on_Jobs_2030.csv into the `jobs` table in Postgres.

Safe to re-run: creates the table if missing, then upserts every row by
employee_id so repeated runs never create duplicates.
"""
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import (
    Column, Float, Integer, MetaData, String, Table, create_engine, text
)
from sqlalchemy.dialects.postgresql import insert as pg_insert

load_dotenv()

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "AI_Impact_on_Jobs_2030.csv"

COLUMN_MAP = {
    "Employee_ID": "employee_id",
    "Job_Title": "job_title",
    "Industry": "industry",
    "Country": "country",
    "Education_Level": "education_level",
    "Years_Experience": "years_experience",
    "AI_Replacement_Risk": "ai_replacement_risk",
    "Future_Demand_Score": "future_demand_score",
    "Remote_Work_Possibility": "remote_work_possibility",
    "Average_Salary_USD": "average_salary_usd",
    "Required_Skills": "required_skills",
    "Automation_Level": "automation_level",
    "Job_Growth_2030": "job_growth_2030",
    "Work_Hours_Per_Week": "work_hours_per_week",
    "Company_Size": "company_size",
    "AI_Tool_Usage": "ai_tool_usage",
    "Performance_Score": "performance_score",
    "Upskilling_Needed": "upskilling_needed",
    "Job_Satisfaction": "job_satisfaction",
    "Hiring_Trend_2026": "hiring_trend_2026",
}

metadata = MetaData()

jobs_table = Table(
    "jobs",
    metadata,
    Column("employee_id", String, primary_key=True),
    Column("job_title", String),
    Column("industry", String),
    Column("country", String),
    Column("education_level", String),
    Column("years_experience", Integer),
    Column("ai_replacement_risk", Float),
    Column("future_demand_score", Float),
    Column("remote_work_possibility", String),
    Column("average_salary_usd", Integer),
    Column("required_skills", String),
    Column("automation_level", String),
    Column("job_growth_2030", Integer),
    Column("work_hours_per_week", Integer),
    Column("company_size", String),
    Column("ai_tool_usage", String),
    Column("performance_score", Float),
    Column("upskilling_needed", String),
    Column("job_satisfaction", Float),
    Column("hiring_trend_2026", String),
)


def load_and_validate() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)

    missing_cols = set(COLUMN_MAP) - set(df.columns)
    if missing_cols:
        raise ValueError(f"CSV is missing expected columns: {missing_cols}")

    dup_ids = df["Employee_ID"].duplicated().sum()
    if dup_ids:
        raise ValueError(f"Found {dup_ids} duplicate Employee_ID values")

    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        raise ValueError(f"Found missing values:\n{nulls}")

    for col in ["AI_Replacement_Risk", "Future_Demand_Score"]:
        if not df[col].between(0, 1).all():
            raise ValueError(f"{col} has values outside the expected 0-1 range")

    for col in ["Performance_Score", "Job_Satisfaction"]:
        if not df[col].between(0, 5).all():
            raise ValueError(f"{col} has values outside the expected 0-5 range")

    return df.rename(columns=COLUMN_MAP)[list(COLUMN_MAP.values())]


def upsert(df: pd.DataFrame, engine) -> None:
    metadata.create_all(engine, tables=[jobs_table])

    records = df.to_dict(orient="records")
    with engine.begin() as conn:
        for i in range(0, len(records), 500):
            chunk = records[i : i + 500]
            stmt = pg_insert(jobs_table).values(chunk)
            stmt = stmt.on_conflict_do_update(
                index_elements=["employee_id"],
                set_={c: stmt.excluded[c] for c in COLUMN_MAP.values() if c != "employee_id"},
            )
            conn.execute(stmt)


def main() -> None:
    database_url = os.environ.get("ETL_DATABASE_URL")
    if not database_url:
        sys.exit("ETL_DATABASE_URL is not set. Copy .env.example to .env and fill it in.")

    df = load_and_validate()
    print(f"Validated {len(df)} rows from {CSV_PATH.name}")

    engine = create_engine(database_url)
    upsert(df, engine)

    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM jobs")).scalar()
    print(f"jobs table now has {count} rows")


if __name__ == "__main__":
    main()
