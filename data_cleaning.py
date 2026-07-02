import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

def run_cleaning():
    print("=====================================================================")
    print("PHASE 3: DATA CLEANING PIPELINE")
    print("=====================================================================")
    
    # Paths to raw files
    sentiment_path = "fear_greed_index.csv"
    trader_path = "historical_data.csv"
    
    # 1. Load Raw Datasets
    print("[1/7] Loading raw datasets...")
    df_sentiment = pd.read_csv(sentiment_path)
    df_trader = pd.read_csv(trader_path)
    
    # 2. Standardize Column Names (convert to lower_snake_case)
    print("[2/7] Standardizing column names...")
    df_sentiment_cleaned = df_sentiment.rename(columns={
        'timestamp': 'sentiment_timestamp',
        'value': 'sentiment_value',
        'classification': 'sentiment_class',
        'date': 'sentiment_date'
    })
    
    df_trader_cleaned = df_trader.rename(columns={
        'Account': 'account',
        'Coin': 'coin',
        'Execution Price': 'execution_price',
        'Size Tokens': 'size_tokens',
        'Size USD': 'size_usd',
        'Side': 'side',
        'Timestamp IST': 'timestamp_ist',
        'Start Position': 'start_position',
        'Direction': 'direction',
        'Closed PnL': 'closed_pnl',
        'Transaction Hash': 'tx_hash',
        'Order ID': 'order_id',
        'Crossed': 'crossed',
        'Fee': 'fee',
        'Trade ID': 'trade_id',
        'Timestamp': 'lossy_timestamp'
    })
    
    # 3. Handle Formatting & Whitespace Issues
    print("[3/7] Cleaning string fields and removing whitespaces...")
    # Strip any trailing/leading whitespaces from categorical and hash columns
    for col in ['account', 'coin', 'side', 'direction', 'tx_hash']:
        df_trader_cleaned[col] = df_trader_cleaned[col].astype(str).str.strip()
    df_sentiment_cleaned['sentiment_class'] = df_sentiment_cleaned['sentiment_class'].astype(str).str.strip()
    
    # 4. Convert Timestamps and Extract ISO Dates
    print("[4/7] Parsing dates and converting timezones...")
    # Sentiment date: parse string to datetime (date-only)
    df_sentiment_cleaned['sentiment_date'] = pd.to_datetime(df_sentiment_cleaned['sentiment_date'])
    
    # Trader date: Parse Indian Standard Time (IST) timestamp
    df_trader_cleaned['datetime_ist'] = pd.to_datetime(df_trader_cleaned['timestamp_ist'], format='%d-%m-%Y %H:%M')
    
    # Convert IST to UTC (subtract 5 hours 30 mins) to align with UTC sentiment index dates
    df_trader_cleaned['datetime_utc'] = df_trader_cleaned['datetime_ist'] - pd.Timedelta(hours=5, minutes=30)
    
    # Extract trade_date (UTC) for final merging alignment
    df_trader_cleaned['trade_date'] = df_trader_cleaned['datetime_utc'].dt.date
    df_sentiment_cleaned['sentiment_date_only'] = df_sentiment_cleaned['sentiment_date'].dt.date
    
    # 5. Check for and Handle Duplicate Records
    print("[5/7] Analyzing duplicates...")
    # In the raw datasets, there are 0 exact row-level duplicates.
    # However, let's check for row-level duplicates after stripping whitespaces.
    full_duplicates = df_trader_cleaned.duplicated().sum()
    print(f"  Exact row-level duplicates in trader dataset: {full_duplicates}")
    
    # Let's inspect duplicates based on key transactional fields (excluding lossy fields or transaction hashes)
    key_cols = ['account', 'coin', 'execution_price', 'size_tokens', 'timestamp_ist', 'side', 'direction']
    subset_duplicates = df_trader_cleaned.duplicated(subset=key_cols).sum()
    print(f"  Duplicates based on key transactional columns: {subset_duplicates}")
    
    if subset_duplicates > 0:
        print(f"  Removing {subset_duplicates} redundant/double-reported transaction entries...")
        df_trader_cleaned = df_trader_cleaned.drop_duplicates(subset=key_cols, keep='first')
    
    # 6. Outlier Diagnostics
    print("[6/7] Running outlier diagnostics using the IQR method...")
    for col in ['closed_pnl', 'size_usd', 'fee']:
        q1 = df_trader_cleaned[col].quantile(0.25)
        q3 = df_trader_cleaned[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df_trader_cleaned[(df_trader_cleaned[col] < lower_bound) | (df_trader_cleaned[col] > upper_bound)]
        print(f"  {col:10s} -> Q1: {q1:10.4f} | Q3: {q3:10.4f} | IQR: {iqr:10.4f} | Bounds: [{lower_bound:10.4f}, {upper_bound:10.4f}]")
        print(f"               Outlier count: {len(outliers):6d} ({len(outliers)/len(df_trader_cleaned)*100:5.2f}%)")
    
    # Confirming no negative prices
    neg_prices = (df_trader_cleaned['execution_price'] <= 0).sum()
    print(f"  Trades with negative or zero execution price: {neg_prices}")

    # 7. Save Cleaned Data to CSV files
    print("[7/7] Saving cleaned datasets...")
    cleaned_sentiment_file = "cleaned_fear_greed_index.csv"
    cleaned_trader_file = "cleaned_historical_data.csv"
    
    df_sentiment_cleaned.to_csv(cleaned_sentiment_file, index=False)
    df_trader_cleaned.to_csv(cleaned_trader_file, index=False)
    
    print("\nData cleaning phase complete!")
    print(f"Cleaned Sentiment shape: {df_sentiment_cleaned.shape}")
    print(f"Cleaned Trader shape:    {df_trader_cleaned.shape}")
    print(f"Files saved: '{cleaned_sentiment_file}', '{cleaned_trader_file}'\n")

if __name__ == "__main__":
    run_cleaning()
