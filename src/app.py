import datetime
import json

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import run_analytics_pipeline, compute_analytics_from_df

st.set_page_config(
    page_title="KU Gen AI Dashboard",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: #131313;
            color: #e5e2e1;
            color-scheme: dark;
            font-family: Inter, sans-serif;
            overflow-y: auto !important; /* ปล่อยให้เลื่อนได้ตามธรรมชาติ */
        }

        .main .block-container {
            padding-top: 16px !important;
            padding-left: 24px !important;
            padding-right: 24px !important;
            padding-bottom: 16px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            gap: 4px !important;
            min-height: 800px !important; /* ความสูงเซฟโซน ถ้าจอตื้นกว่านี้จะเกิด Scrollbar */
        }

        @media screen and (min-height: 801px) {
            html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
                max-height: 100vh !important;
                height: 100vh !important;
                overflow: hidden !important; /* ซ่อนสกรอลบาร์ */
            }
            .main .block-container {
                height: 100vh !important;
                max-height: 100vh !important;
                overflow: hidden !important;
            }
        }

        div[data-testid="stVerticalBlock"] { gap: 8px !important; }
        div[data-testid="element-container"] { margin-bottom: 0px !important; }
        hr { margin: 0.5em 0 !important; }

        .title-top {
            color: #e5e2e1;
            font-size: 2.2rem !important;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1.1;
        }

        .subtitle-top {
            color: #b9ccb2;
            font-size: 0.9rem !important;
            margin-top: 0.2rem;
        }

        .metric-card {
            background: rgba(20, 24, 18, 0.85);
            border: 1px solid rgba(0, 230, 57, 0.15);
            border-radius: 12px !important;
            padding: 12px 16px !important;
            color: #e5e2e1;
            margin-bottom: 16px !important;
            margin-top: 16px !important;
        }

        .metric-label {
            color: #b9ccb2;
            font-size: 0.85rem !important;
            margin-bottom: 0.2rem !important;
        }

        .metric-value {
            color: #ebffe2;
            font-size: 1.8rem !important;
            font-weight: 700;
            line-height: 1.1;
        }

        .metric-note {
            color: #94b986;
            margin-top: 0.4rem !important;
            font-size: 0.8rem !important;
        }

        .card-border-left {
            border-left: 4px solid #00ff41;
            padding-left: 14px !important;
        }

        .section-header {
            color: #e5e2e1;
            margin-bottom: 4px !important;
            font-size: 1.05rem !important;
            font-weight: 700;
        }

        .small-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(0, 230, 57, 0.08);
            border: 1px solid rgba(0, 230, 57, 0.18);
            color: #c8c6c5;
            font-size: 0.8rem !important;
        }

        .pill-dot {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            background: #00ff41;
        }

        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px !important;
        }

        .flex-inline {
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .text-Bold {
            color: #00d900;
            font-size: 1rem !important;
            font-weight: 800;
            margin-right: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def load_analytics():
    analytics = run_analytics_pipeline()
    df = pd.read_csv("data/processed_analytics_data.csv", parse_dates=["Timestamp"])
    return analytics, df

analytics, df = load_analytics()

# ================= Sidebar =================
st.sidebar.markdown("## KU Gen AI Analytics Dashboard")
st.sidebar.markdown("---")
selected_campus = st.sidebar.selectbox("Campus", options=["All"] + sorted(df["Campus"].dropna().unique().tolist()), index=0)
selected_faculty = st.sidebar.selectbox("Faculty", options=["All"] + sorted(df["Faculty"].dropna().unique().tolist()), index=0)

if selected_faculty == "All":
    available_departments = sorted(df["Department"].dropna().unique().tolist())
else:
    available_departments = sorted(df[df["Faculty"] == selected_faculty]["Department"].dropna().unique().tolist())

selected_department = st.sidebar.selectbox("Department", options=["All"] + available_departments, index=0)
selected_role = st.sidebar.selectbox("Role", options=["All"] + sorted(df["Role"].dropna().unique().tolist()), index=0)
selected_transaction = st.sidebar.selectbox("Transaction Type", options=["All"] + sorted(df["TransactionType"].dropna().unique().tolist()))
selected_frequency = st.sidebar.radio("Time Granularity", options=["Daily", "Weekly", "Monthly", "Yearly"], index=0)

min_date = df["Timestamp"].dt.date.min()
max_date = df["Timestamp"].dt.date.max()

if selected_frequency == "Daily":
    selected_date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
    else:
        start_date, end_date = min_date, max_date
elif selected_frequency == "Weekly":
    week_options = pd.date_range(start=min_date - datetime.timedelta(days=min_date.weekday()), end=max_date, freq="W-MON").date
    selected_week_start = st.sidebar.selectbox("Start week", options=week_options, index=0, format_func=lambda d: d.strftime("%Y-%m-%d"))
    selected_week_end = st.sidebar.selectbox("End week", options=week_options, index=len(week_options) - 1, format_func=lambda d: d.strftime("%Y-%m-%d"))
    start_date = selected_week_start
    end_date = selected_week_end + datetime.timedelta(days=6)
elif selected_frequency == "Monthly":
    month_options = pd.date_range(start=min_date.replace(day=1), end=max_date.replace(day=1), freq="MS").date
    selected_month_start = st.sidebar.selectbox("Start month", options=month_options, index=0, format_func=lambda d: d.strftime("%Y-%m"))
    selected_month_end = st.sidebar.selectbox("End month", options=month_options, index=len(month_options) - 1, format_func=lambda d: d.strftime("%Y-%m"))
    start_date = selected_month_start
    end_date = (pd.Timestamp(selected_month_end) + pd.offsets.MonthEnd(0)).date()
else:
    year_options = sorted(df["Timestamp"].dt.year.unique())
    selected_year_start = st.sidebar.selectbox("Start year", options=year_options, index=0)
    selected_year_end = st.sidebar.selectbox("End year", options=year_options, index=len(year_options) - 1)
    start_date = datetime.date(selected_year_start, 1, 1)
    end_date = datetime.date(selected_year_end, 12, 31)

if start_date > end_date:
    start_date, end_date = end_date, start_date

include_raw = st.sidebar.checkbox("Show raw data (in Sidebar)", value=False)

# ================= Filter Data =================
filtered_df = df.copy()
if selected_campus != "All": filtered_df = filtered_df[filtered_df["Campus"] == selected_campus]
if selected_faculty != "All": filtered_df = filtered_df[filtered_df["Faculty"] == selected_faculty]
if selected_department != "All": filtered_df = filtered_df[filtered_df["Department"] == selected_department]
if selected_role != "All": filtered_df = filtered_df[filtered_df["Role"] == selected_role]
if selected_transaction != "All": filtered_df = filtered_df[filtered_df["TransactionType"] == selected_transaction]

filtered_df = filtered_df[(filtered_df["Timestamp"].dt.date >= start_date) & (filtered_df["Timestamp"].dt.date <= end_date)]

analytics = compute_analytics_from_df(filtered_df)

def build_period_activity(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    if frequency == "Daily":
        series = df.groupby(df["Timestamp"].dt.date).size()
        period_df = series.reset_index(name="Records")
        period_df["Date"] = pd.to_datetime(period_df["Timestamp"])
    elif frequency == "Weekly":
        series = df.groupby(pd.Grouper(key="Timestamp", freq="W-MON")).size()
        period_df = series.reset_index(name="Records")
        period_df["Date"] = period_df["Timestamp"].dt.to_period("W").dt.start_time
    elif frequency == "Monthly":
        series = df.groupby(pd.Grouper(key="Timestamp", freq="ME")).size()
        period_df = series.reset_index(name="Records")
        period_df["Date"] = period_df["Timestamp"].dt.to_period("M").dt.to_timestamp()
    else:
        series = df.groupby(pd.Grouper(key="Timestamp", freq="YE")).size()
        period_df = series.reset_index(name="Records")
        period_df["Date"] = period_df["Timestamp"].dt.to_period("Y").dt.to_timestamp()
    return period_df

period_activity = build_period_activity(filtered_df, selected_frequency)

# ================= Header & Topics =================
st.markdown(
    "<div class='dashboard-header'>"
    "<div class='left'>"
    "<div class='title-top'>KU Gen AI Analytics</div>"
    "<div class='subtitle-top'>Dashboard for AI usage and academic analytics</div>"
    "</div></div>",
    unsafe_allow_html=True,
)

topics = "".join([f"<div class='small-pill'><span class='pill-dot'></span>{_}</div>" for _ in list(analytics['top_tags'].keys())[:5]])
st.markdown(f"<div class='flex-inline'><div class='text-Bold'>Top Topics</div>{topics}</div>", unsafe_allow_html=True)

# Faculty Graph (Dynamic Top-up/Usage)
if selected_transaction == "Top-up":
    header_text = "Top Faculty Token Top-up"
    x_label = "Total Tokens Top-up"
else:
    header_text = "Top Faculty Token Usage"
    x_label = "Total Tokens Used"

# ================= Top Metrics =================
m1, m2, m3, m4 = st.columns(4)
m1.markdown(f"<div class='metric-card card-border-left'><div class='metric-label'>Total Records</div><div class='metric-value'>{analytics['total_records']:,}</div></div>", unsafe_allow_html=True)
m2.markdown(f"<div class='metric-card card-border-left'><div class='metric-label'>Users</div><div class='metric-value'>{analytics['unique_users']:,}</div></div>", unsafe_allow_html=True)
m3.markdown(f"<div class='metric-card card-border-left'><div class='metric-label'>Success Rate</div><div class='metric-value'>{analytics['success_rate']:.2%}</div></div>", unsafe_allow_html=True)
m4.markdown(f"<div class='metric-card card-border-left'><div class='metric-label'>{x_label}</div><div class='metric-value'>{analytics['total_token_used']:,}</div></div>", unsafe_allow_html=True)

# ================= Charts Layout =================
col_a, col_b = st.columns([1.2, 1])

# --- Column A: Trend & Faculty ---
with col_a:
    st.markdown(f"<div class='section-header'>{selected_frequency} Activity Trend</div>", unsafe_allow_html=True)
    if not period_activity.empty:
        period_activity['Date'] = pd.to_datetime(period_activity['Date'])
        fig_activity = px.line(period_activity, x='Date', y='Records', markers=True, color_discrete_sequence=['#00ff41'], template='plotly_dark')
        fig_activity.update_layout(height=220, plot_bgcolor='rgba(19,19,19,0.85)', paper_bgcolor='rgba(19,19,19,0.85)', font_color='#e5e2e1', margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_activity, width='stretch', theme='streamlit')
    else:
        st.info("No activity data available.")

    

    st.markdown(f"<div class='section-header'>{header_text}</div>", unsafe_allow_html=True)
    faculty_usage = pd.DataFrame(list(analytics['top_faculty_token_usage'].items()), columns=['Faculty', 'Tokens'])
    faculty_usage = faculty_usage.sort_values('Tokens', ascending=False).head(6)

    if faculty_usage.empty:
        st.info("No transaction data available for the selected filters.")
    else:
        fig_faculty = px.bar(faculty_usage, x='Tokens', y='Faculty', orientation='h', color='Faculty', color_discrete_sequence=px.colors.qualitative.T10, template='plotly_dark', labels={'Tokens': x_label, 'Faculty': 'Faculty'})
        fig_faculty.update_layout(height=220, plot_bgcolor='rgba(19,19,19,0.85)', paper_bgcolor='rgba(19,19,19,0.85)', font_color='#e5e2e1', margin=dict(l=0, r=0, t=10, b=0), yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_faculty, width='stretch', theme='streamlit')

# --- Column B: Sentiment & Apps ---
with col_b:
    st.markdown(f"<div class='section-header'>Sentiment Distribution</div>", unsafe_allow_html=True)
    sentiment_df = pd.DataFrame(list(analytics['sentiment_counts'].items()), columns=['Sentiment', 'Count'])
    if not sentiment_df.empty:
        fig_sentiment = px.pie(sentiment_df, names='Sentiment', values='Count', hole=0.45, color='Sentiment', color_discrete_sequence=['#00ff41', '#6fbf83', '#ff8a8a'], template='plotly_dark')
        fig_sentiment.update_layout(height=220, plot_bgcolor='rgba(19,19,19,0.85)', paper_bgcolor='rgba(19,19,19,0.85)', font_color='#e5e2e1', margin=dict(l=0, r=0, t=20, b=0), legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig_sentiment, width='stretch', theme='streamlit')
    else:
        st.info("No sentiment data available.")

    if selected_transaction != "Top-up":
        st.markdown(f"<div class='section-header'>Top App Usage</div>", unsafe_allow_html=True)
        app_usage = pd.DataFrame(list(analytics['app_usage_counts'].items()), columns=['App', 'Count'])
        app_usage = app_usage.sort_values('Count', ascending=False).head(6)
        
        if app_usage.empty:
            st.info("No app usage data available.")
        else:
            fig_apps = px.bar(app_usage, x='Count', y='App', orientation='h', color='App', color_discrete_sequence=px.colors.qualitative.Pastel, template='plotly_dark')
            fig_apps.update_layout(height=220, plot_bgcolor='rgba(19,19,19,0.85)', paper_bgcolor='rgba(19,19,19,0.85)', font_color='#e5e2e1', margin=dict(l=0, r=0, t=10, b=0), yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_apps, width='stretch', theme='streamlit')

# ================= Lower Info Panels =================
im1, im2, im3 = st.columns(3)
im1.markdown(f"<div class='metric-card card-border-left'><div class='metric-label'>Total Copies</div><div class='metric-value'>{analytics['copy_count']:,}</div></div>", unsafe_allow_html=True)
im2.markdown(f"<div class='metric-card card-border-left'><div class='metric-label'>Total Saves</div><div class='metric-value'>{analytics['save_count']:,}</div></div>", unsafe_allow_html=True)
im3.markdown(f"<div class='metric-card card-border-left'><div class='metric-label'>Total Shares</div><div class='metric-value'>{analytics['share_count']:,}</div></div>", unsafe_allow_html=True)

# ================= ตารางข้อมูลดิบและสรุปผล (Sidebar) =================
if include_raw:
    st.sidebar.subheader("Filtered Raw Data")
    st.sidebar.dataframe(filtered_df, use_container_width=True)