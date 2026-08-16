import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Layoffs Tracker", page_icon="📉", layout="wide")

DATA_PATH = "data/layoffs.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
    df = df.dropna(subset=["date"])
    df["industry"] = df["industry"].fillna("Unknown")
    df["country"] = df["country"].fillna("Unknown")
    df["stage"] = df["stage"].fillna("Unknown")
    df["total_laid_off"] = df["total_laid_off"].fillna(0)
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


df = load_data(DATA_PATH)

st.title("📉 Tech Layoffs Tracker")
st.caption(
    "Exploring layoffs.fyi-sourced data via Kaggle (swaptr/layoffs-2022) — "
    f"{len(df):,} events from {df['date'].min():%b %Y} to {df['date'].max():%b %Y}."
)

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")

min_date, max_date = df["date"].min().date(), df["date"].max().date()

# Quick-range presets anchored to the dataset's actual last date (not the
# system clock) — the data currently ends before "today", so Streamlit's
# built-in relative presets ("past week", "past 2 years") would otherwise
# compute an end date past max_date and error out.
QUICK_RANGES = {
    "All time": None,
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "Last 6 months": 182,
    "Last 1 year": 365,
    "Last 2 years": 730,
}


def _apply_quick_range():
    days = QUICK_RANGES[st.session_state.quick_range]
    if days is None:
        st.session_state.date_range = (min_date, max_date)
    else:
        start = max(min_date, max_date - datetime.timedelta(days=days))
        st.session_state.date_range = (start, max_date)


st.sidebar.selectbox(
    "Quick range (relative to latest data, not today)",
    list(QUICK_RANGES.keys()),
    key="quick_range",
    on_change=_apply_quick_range,
)

# Allow picking dates a bit past the data's max so Streamlit's own built-in
# range shortcuts (in the calendar popover) don't hard-error if used instead
# of the quick-range selectbox above; filtering below naturally yields no
# rows for any span past max_date.
widget_max = max(max_date, datetime.date.today())

st.session_state.setdefault("date_range", (min_date, max_date))
date_range = st.sidebar.date_input(
    "Date range",
    min_value=min_date,
    max_value=widget_max,
    key="date_range",
)

industries = sorted(df["industry"].unique())
selected_industries = st.sidebar.multiselect("Industry", industries, default=[])

countries = sorted(df["country"].unique())
selected_countries = st.sidebar.multiselect("Country", countries, default=[])

stages = sorted(df["stage"].unique())
selected_stages = st.sidebar.multiselect("Stage", stages, default=[])

filtered = df.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = sorted(date_range)
    filtered = filtered[
        (filtered["date"].dt.date >= start) & (filtered["date"].dt.date <= end)
    ]
if selected_industries:
    filtered = filtered[filtered["industry"].isin(selected_industries)]
if selected_countries:
    filtered = filtered[filtered["country"].isin(selected_countries)]
if selected_stages:
    filtered = filtered[filtered["stage"].isin(selected_stages)]

st.sidebar.markdown(f"**{len(filtered):,}** events match your filters")

if filtered.empty:
    st.warning("No data matches the current filters. Try widening your selection.")
    st.stop()

# ---------------- KPI row ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Employees Laid Off", f"{int(filtered['total_laid_off'].sum()):,}")
col2.metric("Companies Affected", f"{filtered['company'].nunique():,}")
col3.metric("Countries", f"{filtered['country'].nunique():,}")
avg_pct = filtered["percentage_laid_off"].dropna()
col4.metric(
    "Avg % of Workforce Cut",
    f"{avg_pct.mean() * 100:.1f}%" if not avg_pct.empty else "N/A",
)

st.divider()

tab_overview, tab_trends, tab_companies = st.tabs(
    ["📊 Overview", "📈 Trends", "🏢 Company Drilldown"]
)

# ---------------- Overview ----------------
with tab_overview:
    c1, c2 = st.columns(2)

    with c1:
        by_industry = (
            filtered.groupby("industry")["total_laid_off"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        fig = px.bar(
            by_industry,
            x="total_laid_off",
            y="industry",
            orientation="h",
            title="Top 10 Industries by Employees Laid Off",
            labels={"total_laid_off": "Employees Laid Off", "industry": "Industry"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        by_country = (
            filtered.groupby("country")["total_laid_off"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        fig = px.bar(
            by_country,
            x="total_laid_off",
            y="country",
            orientation="h",
            title="Top 10 Countries by Employees Laid Off",
            labels={"total_laid_off": "Employees Laid Off", "country": "Country"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    by_stage = (
        filtered.groupby("stage")["total_laid_off"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig = px.pie(
        by_stage,
        names="stage",
        values="total_laid_off",
        title="Layoffs by Company Funding Stage",
        hole=0.4,
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Trends ----------------
with tab_trends:
    monthly = (
        filtered.groupby("month")["total_laid_off"].sum().reset_index().sort_values("month")
    )
    fig = px.line(
        monthly,
        x="month",
        y="total_laid_off",
        markers=True,
        title="Monthly Layoffs Over Time",
        labels={"month": "Month", "total_laid_off": "Employees Laid Off"},
    )
    st.plotly_chart(fig, use_container_width=True)

    monthly_events = filtered.groupby("month").size().reset_index(name="events")
    fig = px.bar(
        monthly_events,
        x="month",
        y="events",
        title="Number of Layoff Events per Month",
        labels={"month": "Month", "events": "Layoff Events"},
    )
    st.plotly_chart(fig, use_container_width=True)

    top_industries = filtered.groupby("industry")["total_laid_off"].sum().nlargest(6).index
    trend_df = filtered[filtered["industry"].isin(top_industries)]
    monthly_industry = (
        trend_df.groupby(["month", "industry"])["total_laid_off"].sum().reset_index()
    )
    fig = px.line(
        monthly_industry,
        x="month",
        y="total_laid_off",
        color="industry",
        title="Monthly Layoff Trend — Top 6 Industries",
        labels={"month": "Month", "total_laid_off": "Employees Laid Off"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Company Drilldown ----------------
with tab_companies:
    top_companies = (
        filtered.groupby("company")
        .agg(
            total_laid_off=("total_laid_off", "sum"),
            events=("company", "size"),
            industry=("industry", "first"),
            country=("country", "first"),
        )
        .sort_values("total_laid_off", ascending=False)
        .head(30)
        .reset_index()
    )
    fig = px.treemap(
        top_companies,
        path=["industry", "company"],
        values="total_laid_off",
        title="Top 30 Companies by Employees Laid Off (grouped by industry)",
        color="total_laid_off",
        color_continuous_scale="Reds",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Search Companies")
    search = st.text_input("Filter by company name")
    table_df = filtered[
        ["date", "company", "location", "country", "industry", "stage", "total_laid_off",
         "percentage_laid_off", "funds_raised", "source"]
    ].sort_values("date", ascending=False)
    if search:
        table_df = table_df[table_df["company"].str.contains(search, case=False, na=False)]
    st.dataframe(table_df, use_container_width=True, height=400)
