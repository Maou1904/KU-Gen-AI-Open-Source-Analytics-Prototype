import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from analytics import run_analytics_pipeline


st.set_page_config(page_title="KU AI Usage Dashboard", layout="wide")

st.title("KU AI Usage — Interactive Dashboard")

DATA_PATH = Path("data/processed_analytics_data.csv")


@st.cache_data(ttl=300)
def load_data():
    if not DATA_PATH.exists():
        run_analytics_pipeline()
    return pd.read_csv(DATA_PATH, parse_dates=["Timestamp"]) 


df = load_data()
analytics = run_analytics_pipeline() if st.sidebar.button("Recompute analytics") else None
if analytics is None:
    # load precomputed analytics from analytics.run_analytics_pipeline side-effect
    try:
        import json
        # fallback: compute minimal analytics from df
        analytics = {
            'total_records': len(df),
            'usage_rate': float((df['TransactionType'] == 'Usage').sum()) / len(df) if len(df) else 0.0,
            'avg_token_used': float(pd.to_numeric(df['TokenUsed'], errors='coerce').fillna(0).mean()),
            'daily_token_usage': df[df['TransactionType']=='Usage'].groupby(df['Timestamp'].dt.date)['TokenUsed'].sum().to_dict(),
            'top_faculty_token_usage': df[df['TransactionType']=='Usage'].groupby('Faculty')['TokenUsed'].sum().sort_values(ascending=False).to_dict(),
            'transaction_counts': df['TransactionType'].value_counts().to_dict(),
            'sentiment_counts': df.get('Sentiment', pd.Series()).value_counts().to_dict() if 'Sentiment' in df.columns else {},
            'top_tags': {},
        }
    except Exception:
        analytics = {}


st.sidebar.header("Controls")
st.sidebar.write("Data rows: ", len(df))
st.sidebar.write("Last timestamp:", df['Timestamp'].max())

# Metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", analytics.get('total_records', 0))
col2.metric("Usage Rate", f"{analytics.get('usage_rate',0):.2%}")
col3.metric("Avg Token / Usage", f"{analytics.get('avg_token_used',0):.1f}")
col4.metric("Unique Users", df['UserID'].nunique())


with st.expander("Line — Daily Token Usage"):
    daily = pd.Series(analytics.get('daily_token_usage', {})).sort_index()
    if not daily.empty:
        daily_df = daily.reset_index()
        daily_df.columns = ['date', 'tokens']
        fig = px.line(daily_df, x='date', y='tokens', title='Daily Token Usage')
        fig.update_layout(xaxis_title='Date', yaxis_title='Tokens')
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No daily token usage data available")

with st.expander("Bar — Token Usage by Faculty"):
    faculty = analytics.get('top_faculty_token_usage', {})
    if faculty:
        fac_df = pd.DataFrame.from_dict(faculty, orient='index', columns=['tokens']).reset_index().rename(columns={'index':'faculty'})
        fig = px.bar(fac_df, x='faculty', y='tokens', title='Token Usage by Faculty')
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No faculty token data available")

with st.expander("Pie — Transaction Type Distribution"):
    trans = analytics.get('transaction_counts', {})
    if trans:
        trans_df = pd.DataFrame.from_dict(trans, orient='index', columns=['count']).reset_index().rename(columns={'index':'transaction'})
        fig = px.pie(trans_df, names='transaction', values='count', title='Transaction Types')
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No transaction data available")

with st.expander("Bar — Top Tags"):
    tags = analytics.get('top_tags', {})
    if tags:
        tags_df = pd.DataFrame.from_dict(tags, orient='index', columns=['count']).reset_index().rename(columns={'index':'tag'})
        fig = px.bar(tags_df, x='count', y='tag', orientation='h', title='Top Tags')
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No tag data available")

st.markdown("---")
st.subheader("Raw data sample")
st.dataframe(df.head(200))
