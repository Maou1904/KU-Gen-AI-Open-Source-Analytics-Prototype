import datetime
import json

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import run_analytics_pipeline, compute_analytics_from_df

st.set_page_config(
    page_title="University Insights Dashboard",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        :root {
            color-scheme: dark;
            font-family: Inter, sans-serif;
        }

        body {
            background: #131313;
            color: #e5e2e1;
        }

        .stApp {
            background: #131313;
        }

        .main .block-container {
            padding-top: 24px;
            padding-left: 24px;
            padding-right: 24px;
            padding-bottom: 32px;
        }

        .glass-panel {
            background: rgba(32, 31, 31, 0.85);
            border: 1px solid rgba(88, 176, 98, 0.18);
            border-radius: 16px;
            backdrop-filter: blur(18px);
            box-shadow: 0 20px 80px rgba(0, 0, 0, 0.25);
        }

        .neon-border {
            border: 1px solid rgba(0, 230, 57, 0.4);
            box-shadow: 0 0 20px rgba(0, 230, 57, 0.12);
        }

        .title-top {
            color: #e5e2e1;
            font-size: 3rem;
            font-weight: 700;
            letter-spacing: -0.03em;
        }

        .subtitle-top {
            color: #b9ccb2;
            font-size: 1rem;
            margin-top: 0.5rem;
        }

        .metric-card {
            background: rgba(20, 24, 18, 0.85);
            border: 1px solid rgba(0, 230, 57, 0.15);
            border-radius: 18px;
            padding: 24px;
            color: #e5e2e1;
        }

        .metric-label {
            color: #b9ccb2;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            color: #ebffe2;
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1.1;
        }

        .metric-note {
            color: #94b986;
            margin-top: 0.75rem;
            font-size: 0.95rem;
        }

        .card-border-left {
            border-left: 4px solid #00ff41;
            padding-left: 18px;
        }

        .chart-card {
            padding: 24px;
        }

        .section-header {
            color: #e5e2e1;
            margin-bottom: 16px;
            font-size: 1.25rem;
            font-weight: 700;
        }

        .small-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border-radius: 999px;
            background: rgba(0, 230, 57, 0.08);
            border: 1px solid rgba(0, 230, 57, 0.18);
            color: #c8c6c5;
            font-size: 0.86rem;
        }

        .pill-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #00ff41;
        }

        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 24px;
        }

        .dashboard-header .left {
            max-width: 680px;
        }

        .dashboard-header .right {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .dashboard-button {
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.16), rgba(0, 255, 65, 0.04));
            border: 1px solid rgba(0, 255, 65, 0.18);
            color: #e5e2e1;
            padding: 12px 20px;
            border-radius: 999px;
            font-weight: 700;
            cursor: pointer;
        }

        .dashboard-button:hover {
            background: rgba(0, 255, 65, 0.16);
        }

        .custom-legend {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 16px;
        }

        .custom-legend div {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }

        .custom-legend span:first-child {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            color: #e5e2e1;
        }

        .custom-legend strong {
            color: #b9ccb2;
        }

        .flex-inline {
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }
        .text-Bold {
            color: #00d900;
            font-size: 1.2rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin-right: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

#@st.cache_data(show_spinner=False)
def load_analytics():
    analytics = run_analytics_pipeline()
    df = pd.read_csv("data/processed_analytics_data.csv", parse_dates=["Timestamp"])
    return analytics, df

analytics, df = load_analytics()

# Sidebar filters
st.sidebar.markdown("## University Insights")
st.sidebar.markdown("---")
selected_campus = st.sidebar.selectbox(
    "Campus",
    options=["All"] + sorted(df["Campus"].dropna().unique().tolist()),
    index=0,
    key="selected_campus",
)
selected_faculty = st.sidebar.selectbox(
    "Faculty",
    options=["All"] + sorted(df["Faculty"].dropna().unique().tolist()),
    index=0,
    key="selected_faculty",
)

# Get departments for selected faculty
if selected_faculty == "All":
    available_departments = sorted(df["Department"].dropna().unique().tolist())
else:
    available_departments = sorted(df[df["Faculty"] == selected_faculty]["Department"].dropna().unique().tolist())

selected_department = st.sidebar.selectbox(
    "Department",
    options=["All"] + available_departments,
    index=0,
    key="selected_department",
)

selected_role = st.sidebar.selectbox(
    "Role",
    options=["All"] + sorted(df["Role"].dropna().unique().tolist()),
    index=0,
    key="selected_role",
)

selected_transaction = st.sidebar.selectbox(
    "Transaction Type",
    options=["All"] + sorted(df["TransactionType"].dropna().unique().tolist()),
)

selected_frequency = st.sidebar.radio(
    "Time Granularity",
    options=["Daily", "Weekly", "Monthly", "Yearly"],
    index=0,
)

min_date = df["Timestamp"].dt.date.min()
max_date = df["Timestamp"].dt.date.max()

if selected_frequency == "Daily":
    selected_date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Choose a start and end date for the dashboard",
    )
    if isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
    else:
        start_date, end_date = min_date, max_date

elif selected_frequency == "Weekly":
    week_options = pd.date_range(
        start=min_date - datetime.timedelta(days=min_date.weekday()),
        end=max_date,
        freq="W-MON",
    ).date
    selected_week_start = st.sidebar.selectbox(
        "Start week",
        options=week_options,
        index=0,
        format_func=lambda d: d.strftime("%Y-%m-%d"),
        key="selected_week_start",
    )
    selected_week_end = st.sidebar.selectbox(
        "End week",
        options=week_options,
        index=len(week_options) - 1,
        format_func=lambda d: d.strftime("%Y-%m-%d"),
        key="selected_week_end",
    )
    start_date = selected_week_start
    end_date = selected_week_end + datetime.timedelta(days=6)

elif selected_frequency == "Monthly":
    month_options = pd.date_range(
        start=min_date.replace(day=1),
        end=max_date.replace(day=1),
        freq="MS",
    ).date
    selected_month_start = st.sidebar.selectbox(
        "Start month",
        options=month_options,
        index=0,
        format_func=lambda d: d.strftime("%Y-%m"),
        key="selected_month_start",
    )
    selected_month_end = st.sidebar.selectbox(
        "End month",
        options=month_options,
        index=len(month_options) - 1,
        format_func=lambda d: d.strftime("%Y-%m"),
        key="selected_month_end",
    )
    start_date = selected_month_start
    end_date = (pd.Timestamp(selected_month_end) + pd.offsets.MonthEnd(0)).date()

else:
    year_options = sorted(df["Timestamp"].dt.year.unique())
    selected_year_start = st.sidebar.selectbox(
        "Start year",
        options=year_options,
        index=0,
        key="selected_year_start",
    )
    selected_year_end = st.sidebar.selectbox(
        "End year",
        options=year_options,
        index=len(year_options) - 1,
        key="selected_year_end",
    )
    start_date = datetime.date(selected_year_start, 1, 1)
    end_date = datetime.date(selected_year_end, 12, 31)

if start_date > end_date:
    start_date, end_date = end_date, start_date

include_raw = st.sidebar.checkbox("Show raw data", value=False, key="include_raw")

filtered_df = df.copy()

if selected_campus != "All":
    filtered_df = filtered_df[filtered_df["Campus"] == selected_campus]
if selected_faculty != "All":
    filtered_df = filtered_df[filtered_df["Faculty"] == selected_faculty]
if selected_department != "All":
    filtered_df = filtered_df[filtered_df["Department"] == selected_department]
if selected_role != "All":
    filtered_df = filtered_df[filtered_df["Role"] == selected_role]
if selected_transaction != "All":
    filtered_df = filtered_df[filtered_df["TransactionType"] == selected_transaction]

filtered_df = filtered_df[
    (filtered_df["Timestamp"].dt.date >= start_date)
    & (filtered_df["Timestamp"].dt.date <= end_date)
]

analytics = compute_analytics_from_df(filtered_df)


def build_period_activity(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    if frequency == "Daily":
        series = df.groupby(df["Timestamp"].dt.date).size()
        period_df = series.reset_index(name="Records")
        period_df["Date"] = pd.to_datetime(period_df["Timestamp"])
    elif frequency == "Weekly":
        series = df.groupby(pd.Grouper(key="Timestamp", freq="W-MON")).size()
        period_df = series.reset_index(name="Records")
        period_df["Date"] = period_df["Timestamp"].dt.to_period("W").dt.start_time
    elif frequency == "Monthly":
        series = df.groupby(pd.Grouper(key="Timestamp", freq="M")).size()
        period_df = series.reset_index(name="Records")
        period_df["Date"] = period_df["Timestamp"].dt.to_period("M").dt.to_timestamp()
    else:
        series = df.groupby(pd.Grouper(key="Timestamp", freq="Y")).size()
        period_df = series.reset_index(name="Records")
        period_df["Date"] = period_df["Timestamp"].dt.to_period("Y").dt.to_timestamp()

    return period_df

period_activity = build_period_activity(filtered_df, selected_frequency)


# Header
st.markdown(
    "<div class='dashboard-header'>"
    "<div class='left'>"
    "<div class='title-top'>University Insights</div>"
    "<div class='subtitle-top'>Dashboard for AI usage and academic analytics</div>"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)



topics = ""

for _ in list(analytics['top_tags'].keys())[:5]:
    topics += f"<div class='small-pill'><span class='pill-dot'></span>{_}</div>\n"

st.markdown(f"""
<div class='flex-inline'>
    <div class='text-Bold'>Top Topics</div>
    {topics}
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Top metrics
metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.markdown(
    "<div class='metric-card card-border-left'>"
    "<div class='metric-label'>Total Records</div>"
    f"<div class='metric-value'>{analytics['total_records']:,}</div>"
    "<div class='metric-note'>Data points collected</div>"
    "</div>",
    unsafe_allow_html=True,
)
metric_2.markdown(
    "<div class='metric-card card-border-left'>"
    "<div class='metric-label'>Unique Users</div>"
    f"<div class='metric-value'>{analytics['unique_users']:,}</div>"
    "<div class='metric-note'>User identities tracked</div>"
    "</div>",
    unsafe_allow_html=True,
)
metric_3.markdown(
    "<div class='metric-card card-border-left'>"
    "<div class='metric-label'>Success Rate</div>"
    f"<div class='metric-value'>{analytics['success_rate']:.2%}</div>"
    "<div class='metric-note'>System reliability</div>"
    "</div>",
    unsafe_allow_html=True,
)
metric_4.markdown(
    "<div class='metric-card card-border-left'>"
    "<div class='metric-label'>Total Token Usage</div>"
    f"<div class='metric-value'>{analytics['total_token_used']:,}</div>"
    "<div class='metric-note'>Total tokens used</div>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# Charts layout
col_a, col_b = st.columns([1.2, 1])
with col_a:
    st.markdown(
        f"<div class='section-header'>{selected_frequency} Activity & Usage Trend</div>",
        unsafe_allow_html=True,
    )
    period_activity['Date'] = pd.to_datetime(period_activity['Date'])
    fig_activity = px.line(
        period_activity,
        x='Date',
        y='Records',
        markers=True,
        color_discrete_sequence=['#00ff41'],
        template='plotly_dark',
    )
    fig_activity.update_layout(
        plot_bgcolor='rgba(19,19,19,0.85)',
        paper_bgcolor='rgba(19,19,19,0.85)',
        font_color='#e5e2e1',
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig_activity, width='stretch', theme='streamlit')

    st.markdown("<div class='section-header'>Top Faculty Token Usage</div>", unsafe_allow_html=True)
    faculty_usage = pd.DataFrame(
        list(analytics['top_faculty_token_usage'].items()), columns=['Faculty', 'Tokens']
    )
    faculty_usage = faculty_usage.sort_values('Tokens', ascending=False).head(6)
    fig_faculty = px.bar(
        faculty_usage,
        x='Tokens',
        y='Faculty',
        orientation='h',
        color='Faculty',
        color_discrete_sequence=px.colors.qualitative.T10,
        template='plotly_dark',
    )
    fig_faculty.update_layout(
        height=70*len(faculty_usage),
        plot_bgcolor='rgba(19,19,19,0.85)',
        paper_bgcolor='rgba(19,19,19,0.85)',
        font_color='#e5e2e1',
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig_faculty, width='stretch', theme='streamlit')

with col_b:
    st.markdown(f"<div class='section-header'>Sentiment Distribution</div>", unsafe_allow_html=True)
    sentiment_df = pd.DataFrame(
        list(analytics['sentiment_counts'].items()), columns=['Sentiment', 'Count']
    )
    fig_sentiment = px.pie(
        sentiment_df,
        names='Sentiment',
        values='Count',
        hole=0.45,
        color='Sentiment',
        color_discrete_sequence=['#00ff41', '#6fbf83', '#ff8a8a'],
        template='plotly_dark',
    )
    fig_sentiment.update_layout(
        plot_bgcolor='rgba(19,19,19,0.85)',
        paper_bgcolor='rgba(19,19,19,0.85)',
        font_color='#e5e2e1',
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_sentiment, width='stretch', theme='streamlit')

    st.markdown(f"<div class='section-header'>Top App Usage</div>", unsafe_allow_html=True)
    app_usage = pd.DataFrame(
        list(analytics['app_usage_counts'].items()), columns=['App', 'Count']
    )
    app_usage = app_usage.sort_values('Count', ascending=False).head(6)
    fig_apps = px.bar(
        app_usage,
        x='Count',
        y='App',
        orientation='h',
        color='App',
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template='plotly_dark',
    )
    fig_apps.update_layout(
        height=70*len(app_usage),
        plot_bgcolor='rgba(19,19,19,0.85)',
        paper_bgcolor='rgba(19,19,19,0.85)',
        font_color='#e5e2e1',
        margin=dict(l=0, r=0, t=0, b=0),
    )
    st.plotly_chart(fig_apps, width='stretch', theme='streamlit')

st.markdown("---")

# Lower info panels
metric_1, metric_2, metric_3 = st.columns(3)
metric_1.markdown(
    "<div class='metric-card card-border-left'>"
    "<div class='metric-label'>Total Copies</div>"
    f"<div class='metric-value'>{analytics['copy_count']:,}</div>"
    "<div class='metric-note'>Data points collected</div>"
    "</div>",
    unsafe_allow_html=True,
)
metric_2.markdown(
    "<div class='metric-card card-border-left'>"
    "<div class='metric-label'>Total Saves</div>"
    f"<div class='metric-value'>{analytics['save_count']:,}</div>"
    "<div class='metric-note'>Data points collected</div>"
    "</div>",
    unsafe_allow_html=True,
)
metric_3.markdown(
    "<div class='metric-card card-border-left'>"
    "<div class='metric-label'>Total Shares</div>"
    f"<div class='metric-value'>{analytics['share_count']:,}</div>"
    "<div class='metric-note'>Data points collected</div>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# Raw or summary data
if include_raw:
    st.subheader("Filtered Raw Data")
    st.dataframe(filtered_df, width='stretch')

# Summary table
summary_data = {}
for key, value in analytics.items():
    if isinstance(value, dict):
        summary_data[key] = json.dumps({str(k): v for k, v in value.items()}, ensure_ascii=False, indent=2)
    elif isinstance(value, (datetime.date, datetime.datetime, pd.Timestamp)):
        summary_data[key] = str(value)
    else:
        summary_data[key] = value

summary_df = pd.DataFrame.from_dict(summary_data, orient='index', columns=['Value'])
summary_df.index.name = 'Metric'
summary_df = summary_df.reset_index()

st.markdown("<div class='section-header'>Analytics Summary</div>", unsafe_allow_html=True)
st.dataframe(summary_df, width='stretch')
