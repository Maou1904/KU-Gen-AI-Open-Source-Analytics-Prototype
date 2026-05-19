import pandas as pd
from textblob import TextBlob


def analyze_sentiment(text):
    #No Top-up
    if not isinstance(text, str) or text == "Top-up":
        return "Neutral"
    
    blob = TextBlob(text)
    pol = blob.sentiment.polarity
    if pol > 0:
        return "Positive"
    elif pol < 0:
        return "Negative"
    else:
        return "Neutral"

def run_analytics_pipeline():
    df = pd.read_csv("data/mock_data.csv", parse_dates=["Timestamp"])
    df = df.copy()
    df = df.sort_values(by="Timestamp").reset_index(drop=True)

    usage_df = df[df["TransactionType"] == "Usage"]
    topup_df = df[df["TransactionType"] == "Top-up"]
    success_df = df[df["Status"] == "Success"]
    failed_df = df[df["Status"] == "Failed"]

    avg_token_used = usage_df["TokenUsed"].mean() if not usage_df.empty else 0.0
    max_token_used = usage_df["TokenUsed"].max() if not usage_df.empty else 0
    min_token_used = usage_df["TokenUsed"].min() if not usage_df.empty else 0

    avg_processing_time = usage_df["ProcessingTime"].mean() if not usage_df.empty else 0.0
    max_processing_time = usage_df["ProcessingTime"].max() if not usage_df.empty else 0.0
    min_processing_time = usage_df["ProcessingTime"].min() if not usage_df.empty else 0.0

    df["Sentiment"] = df["Message/Prompt"].apply(analyze_sentiment)
    sentiment_counts = df["Sentiment"].value_counts().to_dict()

    tag_series = (
        usage_df["Tags"].dropna().astype(str)
        .str.split(', ')
        .explode()
        .loc[lambda s: s != '']
    )

    analytics = {
        'total_records': int(len(df)),
        'unique_users': int(df['UserID'].nunique()),
        'usage_records': int(usage_df.shape[0]),
        'top_up_records': int(topup_df.shape[0]),
        'usage_rate': float(len(usage_df)) / len(df) if len(df) else 0.0,
        'success_rate': float(success_df.shape[0]) / len(df) if len(df) else 0.0,
        'failure_rate': float(failed_df.shape[0]) / len(df) if len(df) else 0.0,
        'avg_token_used': float(avg_token_used),
        'max_token_used': int(max_token_used),
        'min_token_used': int(min_token_used),
        'avg_processing_time': float(avg_processing_time),
        'max_processing_time': float(max_processing_time),
        'min_processing_time': float(min_processing_time),
        'total_token_used': int(usage_df['TokenUsed'].sum()) if not usage_df.empty else 0,
        'top_faculty_token_usage': usage_df.groupby('Faculty')['TokenUsed'].sum().sort_values(ascending=False).to_dict(),
        'top_department_usage': usage_df['Department'].value_counts().head(10).to_dict(),
        'role_counts': df['Role'].value_counts().to_dict(),
        'education_counts': df['EducationLevel'].value_counts().to_dict(),
        'status_counts': df['Status'].value_counts().to_dict(),
        'transaction_counts': df['TransactionType'].value_counts().to_dict(),
        'campus_counts': df['Campus'].value_counts().to_dict(),
        'app_usage_counts': usage_df['AppUsed'].value_counts().to_dict(),
        'top_tags': tag_series.value_counts().head(10).to_dict(),
        'sentiment_counts': sentiment_counts,
        'top_users': df['UserID'].value_counts().head(10).to_dict(),
    }

    def _to_bool_series(s: pd.Series) -> pd.Series:
        return s.fillna(False).astype(str).str.contains('True')

    df['TokenUsed'] = pd.to_numeric(df['TokenUsed'], errors='coerce').fillna(0).astype(int)
    df['ProcessingTime'] = pd.to_numeric(df['ProcessingTime'], errors='coerce').fillna(0.0)

    df['_IsCopied'] = _to_bool_series(df.get('IsCopied', pd.Series(False, index=df.index)))
    df['_IsShared'] = _to_bool_series(df.get('IsShared', pd.Series(False, index=df.index)))
    df['_IsSaved'] = _to_bool_series(df.get('IsSaved', pd.Series(False, index=df.index)))

    analytics.update({
        'copy_count': int(df['_IsCopied'].sum()),
        'share_count': int(df['_IsShared'].sum()),
        'save_count': int(df['_IsSaved'].sum()),
        'copy_rate': float(df['_IsCopied'].sum()) / len(df) if len(df) else 0.0,
        'share_rate': float(df['_IsShared'].sum()) / len(df) if len(df) else 0.0,
        'save_rate': float(df['_IsSaved'].sum()) / len(df) if len(df) else 0.0,
        'daily_activity': df.groupby(df['Timestamp'].dt.date).size().to_dict(),
        'daily_token_usage': df[df['TransactionType'] == 'Usage'].groupby(df['Timestamp'].dt.date)['TokenUsed'].sum().to_dict(),
    })

    print("[1/4] Calculating Basic Statistics...")
    print(f"   - Total Records: {analytics['total_records']}")
    print(f"   - Unique Users: {analytics['unique_users']}")
    print(f"   - Usage Records: {analytics['usage_records']}")
    print(f"   - Top-up Records: {analytics['top_up_records']}")
    print(f"   - Usage Rate: {analytics['usage_rate']:.2%}")
    print(f"   - Success Rate: {analytics['success_rate']:.2%}")
    print(f"   - Failure Rate: {analytics['failure_rate']:.2%}")
    print(f"   - Average Token Used: {analytics['avg_token_used']:.2f}")
    print(f"   - Average Processing Time: {analytics['avg_processing_time']:.2f} seconds")

    print("[2/4] Running Sentiment Analysis...")
    print("   - Sentiment Distribution:")
    for sentiment, count in analytics['sentiment_counts'].items():
        print(f"     - {sentiment}: {count}")

    print("[3/4] Action Interaction Summary...")
    print(f"   - Copied: {analytics['copy_count']} ({analytics['copy_rate']:.2%})")
    print(f"   - Shared: {analytics['share_count']} ({analytics['share_rate']:.2%})")
    print(f"   - Saved: {analytics['save_count']} ({analytics['save_rate']:.2%})")

    print("[4/4] Generating Dashboard Insights...")
    print("   - Top Faculty Token Usage:")
    for faculty, token in analytics['top_faculty_token_usage'].items():
        print(f"     - {faculty}: {token}")
    print("   - Top Departments:")
    for dept, count in analytics['top_department_usage'].items():
        print(f"     - {dept}: {count}")
    print("   - Top Tags:")
    for tag, count in analytics['top_tags'].items():
        print(f"     - {tag}: {count}")

    processed_path = "data/processed_analytics_data.csv"
    df.to_csv(processed_path, index=False)
    print(f"✅ Analytics completed! Processed data saved to {processed_path}")


    return analytics


def compute_analytics_from_df(df: pd.DataFrame) -> dict:
    """Compute analytics dictionary from an already-loaded DataFrame.
    This mirrors the calculations in run_analytics_pipeline but does not read/write files.
    """
    df = df.copy()
    # ensure Timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["Timestamp"]):
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    usage_df = df[df["TransactionType"] == "Usage"]
    topup_df = df[df["TransactionType"] == "Top-up"]
    success_df = df[df["Status"] == "Success"]
    failed_df = df[df["Status"] == "Failed"]

    avg_token_used = usage_df["TokenUsed"].mean() if not usage_df.empty else 0.0
    max_token_used = usage_df["TokenUsed"].max() if not usage_df.empty else 0
    min_token_used = usage_df["TokenUsed"].min() if not usage_df.empty else 0

    avg_processing_time = usage_df["ProcessingTime"].mean() if not usage_df.empty else 0.0
    max_processing_time = usage_df["ProcessingTime"].max() if not usage_df.empty else 0.0
    min_processing_time = usage_df["ProcessingTime"].min() if not usage_df.empty else 0.0

    df["Sentiment"] = df["Message/Prompt"].apply(analyze_sentiment)
    sentiment_counts = df["Sentiment"].value_counts().to_dict()

    tag_series = (
        usage_df["Tags"].dropna().astype(str)
        .str.split(', ')
        .explode()
        .loc[lambda s: s != '']
    )

    analytics = {
        'total_records': int(len(df)),
        'unique_users': int(df['UserID'].nunique()),
        'usage_records': int(usage_df.shape[0]),
        'top_up_records': int(topup_df.shape[0]),
        'usage_rate': float(len(usage_df)) / len(df) if len(df) else 0.0,
        'success_rate': float(success_df.shape[0]) / len(df) if len(df) else 0.0,
        'failure_rate': float(failed_df.shape[0]) / len(df) if len(df) else 0.0,
        'avg_token_used': float(avg_token_used),
        'max_token_used': int(max_token_used),
        'min_token_used': int(min_token_used),
        'avg_processing_time': float(avg_processing_time),
        'max_processing_time': float(max_processing_time),
        'min_processing_time': float(min_processing_time),
        'total_token_used': int(usage_df['TokenUsed'].sum()) if not usage_df.empty else 0,
        'top_faculty_token_usage': usage_df.groupby('Faculty')['TokenUsed'].sum().sort_values(ascending=False).to_dict(),
        'top_department_usage': usage_df['Department'].value_counts().head(10).to_dict(),
        'role_counts': df['Role'].value_counts().to_dict(),
        'education_counts': df['EducationLevel'].value_counts().to_dict(),
        'status_counts': df['Status'].value_counts().to_dict(),
        'transaction_counts': df['TransactionType'].value_counts().to_dict(),
        'campus_counts': df['Campus'].value_counts().to_dict(),
        'app_usage_counts': usage_df['AppUsed'].value_counts().to_dict(),
        'top_tags': tag_series.value_counts().head(10).to_dict(),
        'sentiment_counts': sentiment_counts,
        'top_users': df['UserID'].value_counts().head(10).to_dict(),
    }

    def _to_bool_series(s: pd.Series) -> pd.Series:
        return s.fillna(False).astype(str).str.contains('True')

    df['TokenUsed'] = pd.to_numeric(df['TokenUsed'], errors='coerce').fillna(0).astype(int)
    df['ProcessingTime'] = pd.to_numeric(df['ProcessingTime'], errors='coerce').fillna(0.0)

    df['_IsCopied'] = _to_bool_series(df.get('IsCopied', pd.Series(False, index=df.index)))
    df['_IsShared'] = _to_bool_series(df.get('IsShared', pd.Series(False, index=df.index)))
    df['_IsSaved'] = _to_bool_series(df.get('IsSaved', pd.Series(False, index=df.index)))

    analytics.update({
        'copy_count': int(df['_IsCopied'].sum()),
        'share_count': int(df['_IsShared'].sum()),
        'save_count': int(df['_IsSaved'].sum()),
        'copy_rate': float(df['_IsCopied'].sum()) / len(df) if len(df) else 0.0,
        'share_rate': float(df['_IsShared'].sum()) / len(df) if len(df) else 0.0,
        'save_rate': float(df['_IsSaved'].sum()) / len(df) if len(df) else 0.0,
        'daily_activity': df.groupby(df['Timestamp'].dt.date).size().to_dict(),
        'daily_token_usage': df[df['TransactionType'] == 'Usage'].groupby(df['Timestamp'].dt.date)['TokenUsed'].sum().to_dict(),
    })

    return analytics

def filter_data(df, campus=None, faculty=None, department=None, role=None, education_level=None, transaction_type=None):
    filtered_df = df.copy()
    if campus and campus != "All":
        filtered_df = filtered_df[filtered_df['Campus'] == campus]
    if faculty and faculty != "All":
        filtered_df = filtered_df[filtered_df['Faculty'] == faculty]
    if department and department != "All":
        filtered_df = filtered_df[filtered_df['Department'] == department]
    if role and role != "All":
        filtered_df = filtered_df[filtered_df['Role'] == role]
    if education_level and education_level != "All":
        filtered_df = filtered_df[filtered_df['EducationLevel'] == education_level]
    if transaction_type and transaction_type != "All":
        filtered_df = filtered_df[filtered_df['TransactionType'] == transaction_type]
    
    return filtered_df

if __name__ == "__main__":
    run_analytics_pipeline()