import plotly.express as px
import streamlit as st

import db

st.set_page_config(page_title="AI Impact on Jobs 2030", layout="wide")

st.title("AI Impact on Jobs 2030")
st.caption(
    "Synthetic dataset for portfolio/demo purposes — not intended for real "
    "business decisions."
)

options = db.get_filter_options()

with st.sidebar:
    st.header("Filters")
    sel_industries = st.multiselect("Industry", options["industries"])
    sel_countries = st.multiselect("Country", options["countries"])
    sel_company_sizes = st.multiselect("Company Size", options["company_sizes"])

filters = dict(
    industries=tuple(sel_industries),
    countries=tuple(sel_countries),
    company_sizes=tuple(sel_company_sizes),
)

kpis = db.get_kpis(**filters)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", f"{kpis['total_rows']:,}")
col2.metric("Avg AI Replacement Risk", f"{kpis['avg_risk']:.0%}")
col3.metric("Avg Salary (USD)", f"${kpis['avg_salary']:,.0f}")
col4.metric("Need Upskilling", f"{kpis['pct_upskilling']:.0%}")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Risk & Automation", "Workforce Profile", "Compensation & Wellbeing", "Trends"]
)

with tab1:
    df = db.get_risk_by_industry(**filters)
    fig = px.box(df, x="industry", y="ai_replacement_risk", title="AI Replacement Risk by Industry")
    st.plotly_chart(fig, use_container_width=True)

    df = db.get_demand_vs_automation(**filters)
    fig = px.box(
        df, x="automation_level", y="future_demand_score",
        title="Future Demand Score by Automation Level",
        category_orders={"automation_level": ["Low", "Medium", "High"]},
    )
    st.plotly_chart(fig, use_container_width=True)

    df = db.get_risk_heatmap(**filters)
    pivot = df.pivot(index="country", columns="industry", values="avg_risk")
    fig = px.imshow(
        pivot, color_continuous_scale="Reds", aspect="auto",
        title="Avg AI Replacement Risk: Country x Industry",
        labels={"color": "Avg Risk"},
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df = db.get_workforce_profile(**filters)

    col1, col2 = st.columns(2)
    with col1:
        counts = df["education_level"].value_counts().reset_index()
        counts.columns = ["education_level", "count"]
        fig = px.pie(counts, names="education_level", values="count", title="Education Level")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(df, x="years_experience", nbins=20, title="Years of Experience")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        counts = df["company_size"].value_counts().reset_index()
        counts.columns = ["company_size", "count"]
        fig = px.bar(counts, x="company_size", y="count", title="By Company Size")
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        counts = df["country"].value_counts().reset_index()
        counts.columns = ["country", "count"]
        fig = px.bar(counts, x="country", y="count", title="By Country")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    df = db.get_salary_vs_risk(**filters)
    fig = px.scatter(
        df, x="ai_replacement_risk", y="average_salary_usd", color="industry",
        title="Average Salary vs AI Replacement Risk",
        labels={"ai_replacement_risk": "AI Replacement Risk", "average_salary_usd": "Average Salary (USD)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    df = db.get_satisfaction_vs_hours(**filters)
    fig = px.scatter(
        df, x="work_hours_per_week", y="job_satisfaction",
        title="Job Satisfaction vs Work Hours per Week",
        labels={"work_hours_per_week": "Work Hours / Week", "job_satisfaction": "Job Satisfaction"},
    )
    st.plotly_chart(fig, use_container_width=True)

    df = db.get_salary_by_industry(**filters)
    fig = px.box(df, x="industry", y="average_salary_usd", title="Salary Distribution by Industry")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    df = db.get_hiring_trend_breakdown(**filters)
    fig = px.pie(
        df, names="hiring_trend_2026", values="count", title="Hiring Trend 2026",
        category_orders={"hiring_trend_2026": ["Growing", "Stable", "Declining"]},
    )
    st.plotly_chart(fig, use_container_width=True)

    df = db.get_job_growth_by_industry(**filters)
    fig = px.bar(df, x="industry", y="avg_growth", title="Avg Job Growth 2030 by Industry")
    st.plotly_chart(fig, use_container_width=True)

    df = db.get_upskilling_by_risk_band(**filters)
    fig = px.bar(
        df, x="risk_band", y="count", color="upskilling_needed", barmode="group",
        title="Upskilling Needed by Risk Band",
        category_orders={"risk_band": ["Low (0-0.33)", "Medium (0.34-0.66)", "High (0.67-1.0)"]},
    )
    st.plotly_chart(fig, use_container_width=True)
