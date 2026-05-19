import datetime
import json

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import run_analytics_pipeline

# -------------------------------------------------------------
# หน้าแดชบอร์ดทดสอบ สีเขียว ธีมสดใส และจัด layout แบบ professional
# -------------------------------------------------------------
st.set_page_config(
    page_title="KU Gen AI Analytics Test Dashboard",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        :root {
            color-scheme: dark;
        }
        body {
            background: radial-gradient(circle at top left, #0f2a16 0%, #081407 45%, #061005 100%);
            color: #e7f8e9;
        }
        .stApp {
            background: transparent;
            color: #e7f8e9;
        }
        .css-18e3th9 {
            background-color: rgba(8, 20, 10, 0.92);
            color: #e7f8e9;
        }
        .css-1d391kg {
            background-color: rgba(12, 34, 16, 0.94);
        }
        .stButton>button {
            background-color: #1b5f2b;
            color: white;
            border-color: #2d7e44;
        }
        .stSidebar {
            background: linear-gradient(180deg, #081407 0%, #0b3118 100%);
            color: #d9f3d0;
        }
        .st-bf {
            background-color: rgba(11, 29, 14, 0.92);
        }
        .css-1dq8tca {
            background-color: rgba(16, 54, 24, 0.9);
        }
        .css-1khjlqm {
            color: #b8e5b1;
        }
        .css-1x5yf0l, .css-jn99sy, .css-1n8q08o {
            color: #e7f8e9;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #c6f0c5;
        }
        .stDataFrame td, .stDataFrame th {
            color: #e9f8e1;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner=False)
def load_analytics_data():
    analytics = run_analytics_pipeline()
    df = pd.read_csv("data/processed_analytics_data.csv", parse_dates=["Timestamp"])
    return analytics, df

analytics, processed_df = load_analytics_data()

# Sidebar controls
st.sidebar.header("Dashboard Controls")
selected_campus = st.sidebar.selectbox(
    "เลือกวิทยาเขต",
    options=["All"] + sorted(processed_df["Campus"].dropna().unique().tolist()),
)
selected_faculty = st.sidebar.selectbox(
    "เลือกคณะ",
    options=["All"] + sorted(processed_df["Faculty"].dropna().unique().tolist()),
)
selected_transaction = st.sidebar.multiselect(
    "ประเภทธุรกรรม",
    options=sorted(processed_df["TransactionType"].dropna().unique().tolist()),
    default=sorted(processed_df["TransactionType"].dropna().unique().tolist()),
)
show_raw = st.sidebar.checkbox("แสดงข้อมูลแหล่งข้อมูลดิบ", value=False)

filtered_df = processed_df.copy()
if selected_campus != "All":
    filtered_df = filtered_df[filtered_df["Campus"] == selected_campus]
if selected_faculty != "All":
    filtered_df = filtered_df[filtered_df["Faculty"] == selected_faculty]
if selected_transaction:
    filtered_df = filtered_df[filtered_df["TransactionType"].isin(selected_transaction)]

# Page header
st.title("🟢 KU Gen AI Professional Analytics Dashboard")
st.markdown(
    "ระบบรายงานผลการใช้งาน AI ของมหาวิทยาลัย พร้อมกราฟวิเคราะห์และค่า Metrics สำคัญทั้งหมด"
)
st.markdown("---")

# Top summary metrics
metric_cols = st.columns([1.25, 1.25, 1.25, 1.25])
metric_cols[0].metric("Total Records", f"{analytics['total_records']:,}")
metric_cols[1].metric("Unique Users", f"{analytics['unique_users']:,}")
metric_cols[2].metric("Usage Records", f"{analytics['usage_records']:,}")
metric_cols[3].metric("Top-up Records", f"{analytics['top_up_records']:,}")

metric_cols = st.columns([1.25, 1.25, 1.25, 1.25])
metric_cols[0].metric("Total Token Used", f"{analytics['total_token_used']:,}")
metric_cols[1].metric("Average Token/Usage", f"{analytics['avg_token_used']:.2f}")
metric_cols[2].metric("Average Processing Time", f"{analytics['avg_processing_time']:.2f} s")
metric_cols[3].metric("Success Rate", f"{analytics['success_rate']:.2%}")

st.markdown("---")

# Chart section
st.subheader("ภาพรวมกราฟ Analytics")
row_1_col1, row_1_col2 = st.columns(2)
row_2_col1, row_2_col2 = st.columns(2)

# Daily activity line
daily_activity_df = (
    pd.DataFrame.from_dict(analytics["daily_activity"], orient="index", columns=["Count"])
    .rename_axis("Date")
    .reset_index()
)
if not daily_activity_df.empty:
    fig_daily = px.line(
        daily_activity_df,
        x="Date",
        y="Count",
        title="Daily Activity Trend",
        markers=True,
        labels={"Date": "Date", "Count": "Total Events"},
        color_discrete_sequence=["#39b54a"],
        template="plotly_dark",
    )
    fig_daily.update_layout(
        plot_bgcolor="rgba(8, 20, 12, 0.75)",
        paper_bgcolor="rgba(8, 20, 12, 0.85)",
        font_color="#e7f8e9",
        legend_bgcolor="rgba(0,0,0,0.2)",
    )
    row_1_col1.plotly_chart(fig_daily, use_container_width=True)
else:
    row_1_col1.info("ไม่มีข้อมูลกิจกรรมรายวัน")

# Daily token usage area
daily_token_df = (
    pd.DataFrame.from_dict(analytics["daily_token_usage"], orient="index", columns=["Tokens"])
    .rename_axis("Date")
    .reset_index()
)
if not daily_token_df.empty:
    fig_token = px.area(
        daily_token_df,
        x="Date",
        y="Tokens",
        title="Daily Token Usage",
        labels={"Date": "Date", "Tokens": "Token Used"},
        color_discrete_sequence=["#2dc04d"],
        template="plotly_dark",
    )
    fig_token.update_layout(
        plot_bgcolor="rgba(8, 20, 12, 0.75)",
        paper_bgcolor="rgba(8, 20, 12, 0.85)",
        font_color="#e7f8e9",
        legend_bgcolor="rgba(0,0,0,0.2)",
    )
    row_1_col2.plotly_chart(fig_token, use_container_width=True)
else:
    row_1_col2.info("ไม่มีข้อมูล Token Usage รายวัน")

# Sentiment distribution
sentiment_df = (
    pd.DataFrame.from_dict(analytics["sentiment_counts"], orient="index", columns=["Count"])
    .rename_axis("Sentiment")
    .reset_index()
)
if not sentiment_df.empty:
    fig_sentiment = px.pie(
        sentiment_df,
        names="Sentiment",
        values="Count",
        title="Sentiment Distribution",
        color_discrete_sequence=["#2c8a4d", "#69b26d", "#8dca8f"],
        hole=0.4,
        template="plotly_dark",
    )
    fig_sentiment.update_layout(
        paper_bgcolor="rgba(8, 20, 12, 0.85)",
        font_color="#e7f8e9",
        legend_bgcolor="rgba(0,0,0,0.2)",
    )
    row_2_col1.plotly_chart(fig_sentiment, use_container_width=True)
else:
    row_2_col1.info("ไม่มีข้อมูล Sentiment")

# Status breakdown
status_df = (
    pd.DataFrame.from_dict(analytics["status_counts"], orient="index", columns=["Count"])
    .rename_axis("Status")
    .reset_index()
)
if not status_df.empty:
    fig_status = px.bar(
        status_df,
        x="Status",
        y="Count",
        text="Count",
        title="Transaction Status Breakdown",
        color="Status",
        color_discrete_sequence=["#2a7f4f", "#6ebf6d", "#8ccf91"],
        template="plotly_dark",
    )
    fig_status.update_traces(textposition="outside")
    fig_status.update_layout(
        plot_bgcolor="rgba(8, 20, 12, 0.75)",
        paper_bgcolor="rgba(8, 20, 12, 0.85)",
        font_color="#e7f8e9",
        legend_bgcolor="rgba(0,0,0,0.2)",
    )
    row_2_col2.plotly_chart(fig_status, use_container_width=True)
else:
    row_2_col2.info("ไม่มีข้อมูลสถานะการทำงาน")

st.markdown("---")

# Secondary charts
row_3_col1, row_3_col2, row_3_col3 = st.columns([1.1, 1.1, 1])

# Top faculty token usage
faculty_token_df = (
    pd.DataFrame.from_dict(analytics["top_faculty_token_usage"], orient="index", columns=["TokenUsed"])
    .rename_axis("Faculty")
    .reset_index()
)
if not faculty_token_df.empty:
    fig_faculty = px.bar(
        faculty_token_df.sort_values(by="TokenUsed", ascending=False).head(10),
        x="TokenUsed",
        y="Faculty",
        orientation="h",
        title="Top Faculty Token Usage",
        labels={"TokenUsed": "Token Used", "Faculty": "Faculty"},
        color_discrete_sequence=["#37a44e"],
        template="plotly_dark",
    )
    fig_faculty.update_layout(
        plot_bgcolor="rgba(8, 20, 12, 0.75)",
        paper_bgcolor="rgba(8, 20, 12, 0.85)",
        font_color="#e7f8e9",
        legend_bgcolor="rgba(0,0,0,0.2)",
    )
    row_3_col1.plotly_chart(fig_faculty, use_container_width=True)
else:
    row_3_col1.info("ไม่มีข้อมูลการใช้ Token ตามคณะ")

# Top apps usage
app_df = (
    pd.DataFrame.from_dict(analytics["app_usage_counts"], orient="index", columns=["Count"])
    .rename_axis("AppUsed")
    .reset_index()
)
if not app_df.empty:
    fig_app = px.bar(
        app_df.sort_values(by="Count", ascending=False).head(10),
        x="Count",
        y="AppUsed",
        orientation="h",
        title="Top App Usage",
        labels={"Count": "Usage Count", "AppUsed": "App"},
        color_discrete_sequence=["#39b54a"],
        template="plotly_dark",
    )
    fig_app.update_layout(
        plot_bgcolor="rgba(8, 20, 12, 0.75)",
        paper_bgcolor="rgba(8, 20, 12, 0.85)",
        font_color="#e7f8e9",
        legend_bgcolor="rgba(0,0,0,0.2)",
    )
    row_3_col2.plotly_chart(fig_app, use_container_width=True)
else:
    row_3_col2.info("ไม่มีข้อมูล App Usage")

# Top tags heatmap-like bar
tags_df = (
    pd.DataFrame.from_dict(analytics["top_tags"], orient="index", columns=["Count"])
    .rename_axis("Tag")
    .reset_index()
)
if not tags_df.empty:
    fig_tags = px.treemap(
        tags_df.sort_values(by="Count", ascending=False).head(25),
        path=["Tag"],
        values="Count",
        title="Top Tags by Frequency",
        color="Count",
        color_continuous_scale="Greens",
        template="plotly_dark",
    )
    fig_tags.update_layout(
        paper_bgcolor="rgba(8, 20, 12, 0.85)",
        font_color="#e7f8e9",
    )
    row_3_col3.plotly_chart(fig_tags, use_container_width=True)
else:
    row_3_col3.info("ไม่มีข้อมูลแท็ก")

st.markdown("---")

# Detailed analytics section
st.subheader("Analytics Insights และตัวชี้วัดทั้งหมด")


def safe_serialize(value):
    if isinstance(value, dict):
        return {str(k): safe_serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [safe_serialize(v) for v in value]
    if isinstance(value, (datetime.date, datetime.datetime, pd.Timestamp)):
        return str(value)
    return value

summary_data = {}
for key, value in analytics.items():
    if isinstance(value, dict):
        summary_data[key] = json.dumps(safe_serialize(value), ensure_ascii=False, indent=2)
    else:
        summary_data[key] = value

summary_df = pd.DataFrame.from_dict(summary_data, orient="index", columns=["Value"])
summary_df.index.name = "Metric"
summary_df = summary_df.reset_index()

st.dataframe(summary_df, use_container_width=True)

if show_raw:
    st.markdown("---")
    st.subheader("ข้อมูลดิบที่ถูกกรอง")
    st.dataframe(filtered_df, use_container_width=True)
    st.download_button(
        label="ดาวน์โหลด CSV ของข้อมูลที่กรอง",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_analytics_data.csv",
        mime="text/csv",
    )
