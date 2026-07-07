import plotly.express as px
import streamlit as st

import db

st.set_page_config(page_title="AI Impact on Jobs 2030", page_icon="🤖", layout="wide")

PALETTE = [
    "#6366F1", "#22C55E", "#F59E0B", "#EF4444", "#06B6D4",
    "#EC4899", "#8B5CF6", "#84CC16", "#F97316", "#14B8A6",
]
RISK_SCALE = ["#EEF2FF", "#A5B4FC", "#6366F1", "#4338CA", "#312E81"]

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: 600; padding: 8px 4px; }
    .kpi-card {
        background: white; border-radius: 14px; padding: 18px 20px;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08);
        border-left: 5px solid var(--accent);
    }
    .kpi-icon { font-size: 24px; }
    .kpi-value { font-size: 28px; font-weight: 700; color: #0F172A; margin-top: 4px; }
    .kpi-label { font-size: 13px; color: #64748B; margin-top: 2px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="background: linear-gradient(90deg, #6366F1, #8B5CF6);
                padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
        <h1 style="color: white; margin: 0; font-size: 32px;">🤖 AI Impact on Jobs 2030</h1>
        <p style="color: #E0E7FF; margin: 6px 0 0 0;">
            Synthetic dataset for portfolio/demo purposes — not intended for real business decisions.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


def style_fig(fig, height=380):
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Inter, sans-serif", size=13, color="#0F172A"),
        title_font=dict(size=16, color="#0F172A"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        colorway=PALETTE,
    )
    return fig


def kpi_card(icon, label, value, accent):
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent: {accent};">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_card(fig):
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True)


options = db.get_filter_options()

with st.sidebar:
    st.markdown("### 🎛️ Filters")
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
with col1:
    kpi_card("📋", "Total Records", f"{kpis['total_rows']:,}", "#6366F1")
with col2:
    kpi_card("⚠️", "Avg AI Replacement Risk", f"{kpis['avg_risk']:.0%}", "#EF4444")
with col3:
    kpi_card("💰", "Avg Salary (USD)", f"${kpis['avg_salary']:,.0f}", "#22C55E")
with col4:
    kpi_card("🎓", "Need Upskilling", f"{kpis['pct_upskilling']:.0%}", "#F59E0B")

st.write("")

tab1, tab2, tab3, tab4 = st.tabs(
    ["🤖 Risk & Automation", "👥 Workforce Profile", "💰 Compensation & Wellbeing", "📈 Trends"]
)

with tab1:
    df = db.get_risk_by_industry(**filters)
    fig = px.box(df, x="industry", y="ai_replacement_risk", title="AI Replacement Risk by Industry",
                 color="industry", color_discrete_sequence=PALETTE)
    fig.update_layout(showlegend=False)
    chart_card(style_fig(fig))

    df = db.get_demand_vs_automation(**filters)
    fig = px.box(
        df, x="automation_level", y="future_demand_score",
        title="Future Demand Score by Automation Level",
        category_orders={"automation_level": ["Low", "Medium", "High"]},
        color="automation_level", color_discrete_sequence=PALETTE,
    )
    fig.update_layout(showlegend=False)
    chart_card(style_fig(fig))

    df = db.get_risk_heatmap(**filters)
    pivot = df.pivot(index="country", columns="industry", values="avg_risk")
    fig = px.imshow(
        pivot, color_continuous_scale=RISK_SCALE, aspect="auto",
        title="Avg AI Replacement Risk: Country x Industry",
        labels={"color": "Avg Risk"},
    )
    chart_card(style_fig(fig, height=420))

with tab2:
    df = db.get_workforce_profile(**filters)

    col1, col2 = st.columns(2)
    with col1:
        counts = df["education_level"].value_counts().reset_index()
        counts.columns = ["education_level", "count"]
        fig = px.pie(counts, names="education_level", values="count", title="Education Level",
                     color_discrete_sequence=PALETTE, hole=0.45)
        chart_card(style_fig(fig))
    with col2:
        fig = px.histogram(df, x="years_experience", nbins=20, title="Years of Experience",
                            color_discrete_sequence=[PALETTE[0]])
        chart_card(style_fig(fig))

    col3, col4 = st.columns(2)
    with col3:
        counts = df["company_size"].value_counts().reset_index()
        counts.columns = ["company_size", "count"]
        fig = px.bar(counts, x="company_size", y="count", title="By Company Size",
                      color="company_size", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        chart_card(style_fig(fig))
    with col4:
        counts = df["country"].value_counts().reset_index()
        counts.columns = ["country", "count"]
        fig = px.bar(counts, x="country", y="count", title="By Country",
                      color="country", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        chart_card(style_fig(fig))

with tab3:
    df = db.get_salary_vs_risk(**filters)
    fig = px.scatter(
        df, x="ai_replacement_risk", y="average_salary_usd", color="industry",
        title="Average Salary vs AI Replacement Risk", color_discrete_sequence=PALETTE,
        labels={"ai_replacement_risk": "AI Replacement Risk", "average_salary_usd": "Average Salary (USD)"},
    )
    chart_card(style_fig(fig, height=420))

    col1, col2 = st.columns(2)
    with col1:
        df = db.get_satisfaction_vs_hours(**filters)
        fig = px.scatter(
            df, x="work_hours_per_week", y="job_satisfaction",
            title="Job Satisfaction vs Work Hours per Week",
            color_discrete_sequence=[PALETTE[1]],
            labels={"work_hours_per_week": "Work Hours / Week", "job_satisfaction": "Job Satisfaction"},
        )
        chart_card(style_fig(fig))
    with col2:
        df = db.get_salary_by_industry(**filters)
        fig = px.box(df, x="industry", y="average_salary_usd", title="Salary Distribution by Industry",
                      color="industry", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        chart_card(style_fig(fig))

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        df = db.get_hiring_trend_breakdown(**filters)
        fig = px.pie(
            df, names="hiring_trend_2026", values="count", title="Hiring Trend 2026",
            category_orders={"hiring_trend_2026": ["Growing", "Stable", "Declining"]},
            color="hiring_trend_2026",
            color_discrete_map={"Growing": "#22C55E", "Stable": "#F59E0B", "Declining": "#EF4444"},
            hole=0.45,
        )
        chart_card(style_fig(fig))
    with col2:
        df = db.get_job_growth_by_industry(**filters)
        fig = px.bar(df, x="industry", y="avg_growth", title="Avg Job Growth 2030 by Industry",
                      color="avg_growth", color_continuous_scale=RISK_SCALE)
        chart_card(style_fig(fig))

    df = db.get_upskilling_by_risk_band(**filters)
    fig = px.bar(
        df, x="risk_band", y="count", color="upskilling_needed", barmode="group",
        title="Upskilling Needed by Risk Band",
        category_orders={"risk_band": ["Low (0-0.33)", "Medium (0.34-0.66)", "High (0.67-1.0)"]},
        color_discrete_map={"Yes": "#6366F1", "No": "#CBD5E1"},
    )
    chart_card(style_fig(fig))
