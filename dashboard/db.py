"""Read-only query layer for the dashboard. Every query is cached since the
underlying data is static (loaded once via etl/load_to_db.py)."""
import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _get_database_url() -> str | None:
    value = os.environ.get("DATABASE_URL")
    if value:
        return value
    try:
        return st.secrets["DATABASE_URL"]
    except Exception:
        return None


@st.cache_resource
def get_engine():
    database_url = _get_database_url()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set (checked environment and st.secrets)")
    return create_engine(database_url, pool_pre_ping=True)


def _where_clause(industries, countries, company_sizes):
    clauses = []
    params = {}
    if industries:
        clauses.append("industry = ANY(:industries)")
        params["industries"] = list(industries)
    if countries:
        clauses.append("country = ANY(:countries)")
        params["countries"] = list(countries)
    if company_sizes:
        clauses.append("company_size = ANY(:company_sizes)")
        params["company_sizes"] = list(company_sizes)
    sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return sql, params


def _query(sql: str, params: dict) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


@st.cache_data
def get_filter_options() -> dict:
    df = _query(
        "SELECT DISTINCT industry, country, company_size FROM jobs", {}
    )
    return {
        "industries": sorted(df["industry"].dropna().unique().tolist()),
        "countries": sorted(df["country"].dropna().unique().tolist()),
        "company_sizes": sorted(df["company_size"].dropna().unique().tolist()),
    }


@st.cache_data
def get_kpis(industries=(), countries=(), company_sizes=()) -> dict:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"""
        SELECT
            COUNT(*) AS total_rows,
            AVG(ai_replacement_risk) AS avg_risk,
            AVG(average_salary_usd) AS avg_salary,
            AVG(CASE WHEN upskilling_needed = 'Yes' THEN 1.0 ELSE 0.0 END) AS pct_upskilling
        FROM jobs
        {where}
    """
    row = _query(sql, params).iloc[0]
    return {
        "total_rows": int(row["total_rows"]),
        "avg_risk": float(row["avg_risk"]) if row["total_rows"] else 0.0,
        "avg_salary": float(row["avg_salary"]) if row["total_rows"] else 0.0,
        "pct_upskilling": float(row["pct_upskilling"]) if row["total_rows"] else 0.0,
    }


@st.cache_data
def get_risk_by_industry(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"SELECT industry, ai_replacement_risk FROM jobs {where}"
    return _query(sql, params)


@st.cache_data
def get_demand_vs_automation(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"SELECT future_demand_score, automation_level FROM jobs {where}"
    return _query(sql, params)


@st.cache_data
def get_risk_heatmap(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"""
        SELECT country, industry, AVG(ai_replacement_risk) AS avg_risk
        FROM jobs
        {where}
        GROUP BY country, industry
    """
    return _query(sql, params)


@st.cache_data
def get_workforce_profile(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"""
        SELECT education_level, years_experience, company_size, country
        FROM jobs
        {where}
    """
    return _query(sql, params)


@st.cache_data
def get_salary_vs_risk(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"SELECT average_salary_usd, ai_replacement_risk, industry FROM jobs {where}"
    return _query(sql, params)


@st.cache_data
def get_satisfaction_vs_hours(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"SELECT job_satisfaction, work_hours_per_week FROM jobs {where}"
    return _query(sql, params)


@st.cache_data
def get_salary_by_industry(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"SELECT industry, average_salary_usd FROM jobs {where}"
    return _query(sql, params)


@st.cache_data
def get_hiring_trend_breakdown(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"""
        SELECT hiring_trend_2026, COUNT(*) AS count
        FROM jobs
        {where}
        GROUP BY hiring_trend_2026
    """
    return _query(sql, params)


@st.cache_data
def get_job_growth_by_industry(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"""
        SELECT industry, AVG(job_growth_2030) AS avg_growth
        FROM jobs
        {where}
        GROUP BY industry
    """
    return _query(sql, params)


@st.cache_data
def get_upskilling_by_risk_band(industries=(), countries=(), company_sizes=()) -> pd.DataFrame:
    where, params = _where_clause(industries, countries, company_sizes)
    sql = f"""
        SELECT
            CASE
                WHEN ai_replacement_risk < 0.34 THEN 'Low (0-0.33)'
                WHEN ai_replacement_risk < 0.67 THEN 'Medium (0.34-0.66)'
                ELSE 'High (0.67-1.0)'
            END AS risk_band,
            upskilling_needed,
            COUNT(*) AS count
        FROM jobs
        {where}
        GROUP BY risk_band, upskilling_needed
    """
    return _query(sql, params)
