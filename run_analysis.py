import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

# We will check if scikit-learn is available for clustering
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

warnings.filterwarnings('ignore')

def run_analysis_pipeline():
    print("=====================================================================")
    print("STARTING FULL QUANTITATIVE ANALYSIS PIPELINE")
    print("=====================================================================")
    
    # 1. Load cleaned datasets
    sentiment_path = "cleaned_fear_greed_index.csv"
    trader_path = "cleaned_historical_data.csv"
    
    if not os.path.exists(sentiment_path) or not os.path.exists(trader_path):
        print("Error: Cleaned files not found. Running data_cleaning.py first...")
        import data_cleaning
        data_cleaning.run_cleaning()
        
    df_sent = pd.read_csv(sentiment_path)
    df_trade = pd.read_csv(trader_path)
    
    # Convert dates to datetime objects for matching
    df_sent['sentiment_date'] = pd.to_datetime(df_sent['sentiment_date'])
    df_sent['sentiment_date_only'] = df_sent['sentiment_date'].dt.date
    
    df_trade['datetime_utc'] = pd.to_datetime(df_trade['datetime_utc'])
    df_trade['trade_date'] = pd.to_datetime(df_trade['trade_date']).dt.date
    
    # =====================================================================
    # PHASE 4: DATA MERGING
    # =====================================================================
    print("\n--- PHASE 4: DATA MERGING ---")
    row_count_before = len(df_trade)
    print(f"Trader rows before merge: {row_count_before}")
    
    # Merge on trade_date (UTC) matching sentiment_date_only (UTC)
    df_merged = pd.merge(
        df_trade, 
        df_sent[['sentiment_date_only', 'sentiment_value', 'sentiment_class']], 
        left_on='trade_date', 
        right_on='sentiment_date_only', 
        how='left'
    )
    
    # Check unmatched rows
    unmatched_rows = df_merged['sentiment_value'].isnull().sum()
    print(f"Unmatched trade records: {unmatched_rows} ({unmatched_rows/len(df_merged)*100:.2f}%)")
    
    # If there are any missing sentiment values, drop them (or forward-fill, but dropping is cleaner since our analysis is sentiment-driven)
    if unmatched_rows > 0:
        df_merged = df_merged.dropna(subset=['sentiment_value'])
        print(f"Dropped unmatched rows. New row count: {len(df_merged)}")
        
    print(f"Merged dataset shape: {df_merged.shape}")
    
    # =====================================================================
    # PHASE 5: FEATURE ENGINEERING
    # =====================================================================
    print("\n--- PHASE 5: FEATURE ENGINEERING ---")
    
    # Net Profit (gross profit minus fee)
    df_merged['net_pnl'] = df_merged['closed_pnl'] - df_merged['fee']
    
    # Trade Value
    df_merged['trade_value'] = df_merged['size_usd']
    
    # Win / Loss / Neutral classification
    df_merged['is_profit'] = df_merged['closed_pnl'] > 0
    df_merged['win_loss'] = np.where(df_merged['closed_pnl'] > 0, 'WIN', np.where(df_merged['closed_pnl'] < 0, 'LOSS', 'NEUTRAL'))
    
    # Encoding sentiment
    sentiment_map = {
        'Extreme Fear': 1,
        'Fear': 2,
        'Neutral': 3,
        'Greed': 4,
        'Extreme Greed': 5
    }
    df_merged['sentiment_encoded'] = df_merged['sentiment_class'].map(sentiment_map)
    
    # Leverage/Risk Proxies (using Trade Size quintiles)
    df_merged['trade_size_category'] = pd.qcut(
        df_merged['trade_value'], 
        q=4, 
        labels=['MICRO', 'RETAIL', 'PRO', 'WHALE']
    )
    
    # Holding Period approximation:
    # Sort by account, coin, and time to find consecutive transaction times
    df_merged = df_merged.sort_values(by=['account', 'coin', 'datetime_utc'])
    # Time diff in minutes between consecutive trades for the same account + coin
    df_merged['time_diff_min'] = df_merged.groupby(['account', 'coin'])['datetime_utc'].diff().dt.total_seconds() / 60.0
    # Fill NaN for first trades of a sequence
    df_merged['time_diff_min'] = df_merged['time_diff_min'].fillna(0.0)
    
    # Trader ranks and categories
    trader_pnls = df_merged.groupby('account')['net_pnl'].sum().reset_index()
    trader_pnls['trader_rank'] = trader_pnls['net_pnl'].rank(ascending=False, method='min')
    
    # Classify traders into performance tiers
    q_high = trader_pnls['net_pnl'].quantile(0.85)
    q_low = trader_pnls['net_pnl'].quantile(0.15)
    
    def classify_trader_tier(pnl):
        if pnl >= q_high:
            return 'TOP_TRADER'
        elif pnl <= q_low:
            return 'BOTTOM_TRADER'
        else:
            return 'AVERAGE_TRADER'
            
    trader_pnls['trader_tier'] = trader_pnls['net_pnl'].apply(classify_trader_tier)
    
    # Merge trader details back to main dataframe
    df_merged = pd.merge(df_merged, trader_pnls[['account', 'trader_rank', 'trader_tier']], on='account', how='left')
    
    print("Features successfully engineered!")
    print(df_merged[['net_pnl', 'trade_value', 'trade_size_category', 'sentiment_encoded', 'trader_tier']].head(3))
    
    # Save merged & engineered dataset
    df_merged.to_csv("engineered_historical_data.csv", index=False)
    print("Saved engineered dataset to 'engineered_historical_data.csv'")
    
    # Create directory for plots
    os.makedirs("plots", exist_ok=True)
    
    # =====================================================================
    # PHASE 6: EXPLORATORY DATA ANALYSIS (EDA)
    # =====================================================================
    print("\n--- PHASE 6: EXPLORATORY DATA ANALYSIS ---")
    
    # Set styling
    sns.set_theme(style="darkgrid")
    
    # Plot 1: Profit Distribution (excluding neutral zeros for better resolution)
    plt.figure(figsize=(10, 6))
    non_zero_pnl = df_merged[df_merged['closed_pnl'] != 0]['closed_pnl']
    # Clip extreme values for visualization
    clipped_pnl = np.clip(non_zero_pnl, -200, 200)
    sns.histplot(clipped_pnl, bins=100, kde=True, color='purple')
    plt.title("Realized Closed PnL Distribution (Clipped at -$200 to +$200)", fontsize=14)
    plt.xlabel("Closed PnL (USD)", fontsize=12)
    plt.ylabel("Count of Trades", fontsize=12)
    plt.tight_layout()
    plt.savefig("plots/profit_distribution.png")
    plt.close()
    
    # Plot 2: Sentiment Class Distribution
    plt.figure(figsize=(8, 5))
    sentiment_counts = df_merged['sentiment_class'].value_counts()
    sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, palette='viridis')
    plt.title("Distribution of Trade Counts across Sentiment Regimes", fontsize=14)
    plt.xlabel("Sentiment Class", fontsize=12)
    plt.ylabel("Number of Trades", fontsize=12)
    plt.tight_layout()
    plt.savefig("plots/sentiment_distribution.png")
    plt.close()
    
    # Plot 3: Trade Size Category by Side
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df_merged, x='trade_size_category', hue='side', palette='muted')
    plt.title("Trade Size Categories Segmented by Side (BUY/SELL)", fontsize=14)
    plt.xlabel("Size Category", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.tight_layout()
    plt.savefig("plots/trade_size_by_side.png")
    plt.close()
    
    print("EDA Visualizations saved in './plots/' directory.")
    
    # =====================================================================
    # PHASE 7: SENTIMENT ANALYSIS (FEAR VS GREED)
    # =====================================================================
    print("\n--- PHASE 7: SENTIMENT COMPARISON (FEAR VS GREED) ---")
    
    # Calculate key metrics grouped by sentiment class
    sentiment_stats = df_merged.groupby('sentiment_class').agg(
        trade_count=('trade_id', 'count'),
        total_pnl=('net_pnl', 'sum'),
        mean_pnl=('net_pnl', 'mean'),
        median_pnl=('net_pnl', 'median'),
        mean_size_usd=('trade_value', 'mean'),
        total_fee=('fee', 'sum'),
        win_rate=('is_profit', lambda x: (x == True).sum() / len(x) * 100)
    ).reset_index()
    
    print("\nSentiment Class Statistics:")
    print(sentiment_stats.to_string(index=False))
    
    # T-test for Profitability difference: Fear vs. Greed
    pnl_fear = df_merged[df_merged['sentiment_class'].isin(['Fear', 'Extreme Fear'])]['net_pnl']
    pnl_greed = df_merged[df_merged['sentiment_class'].isin(['Greed', 'Extreme Greed'])]['net_pnl']
    
    t_stat, p_val = stats.ttest_ind(pnl_fear, pnl_greed, equal_var=False)
    print(f"\nStatistical Significance Test (Welch's T-Test) - Fear vs. Greed PnL:")
    print(f"  T-statistic: {t_stat:.4f}")
    print(f"  P-value:     {p_val:.6f}")
    if p_val < 0.05:
        print("  Result: Statistically SIGNIFICANT difference in PnL between Fear and Greed regimes!")
    else:
        print("  Result: No statistically significant difference in PnL between regimes.")
        
    # Plot 4: Boxplot of Profit by Sentiment Class
    plt.figure(figsize=(10, 6))
    # Filter out extreme outliers for visual clarity in the boxplot
    sns.boxplot(data=df_merged, x='sentiment_class', y='net_pnl', palette='Set2', 
                showfliers=False)
    plt.title("Net PnL Distribution by Sentiment Class (Outliers Hidden)", fontsize=14)
    plt.xlabel("Sentiment Class", fontsize=12)
    plt.ylabel("Net PnL (USD)", fontsize=12)
    plt.tight_layout()
    plt.savefig("plots/pnl_by_sentiment.png")
    plt.close()
    
    # =====================================================================
    # PHASE 8: TRADER BEHAVIOR ANALYSIS
    # =====================================================================
    print("\n--- PHASE 8: TRADER BEHAVIOR ANALYSIS ---")
    
    # Aggregate trader statistics
    trader_stats = df_merged.groupby(['account', 'trader_tier']).agg(
        trade_count=('trade_id', 'count'),
        total_net_pnl=('net_pnl', 'sum'),
        mean_trade_size=('trade_value', 'mean'),
        mean_fee=('fee', 'mean'),
        win_rate=('is_profit', lambda x: (x == True).sum() / len(x) * 100),
        preferred_side=('side', lambda x: x.mode()[0] if not x.empty else 'NONE')
    ).reset_index().sort_values(by='total_net_pnl', ascending=False)
    
    print("\nTop 5 Traders by Net PnL:")
    print(trader_stats.head(5).to_string(index=False))
    
    print("\nBottom 5 Traders by Net PnL:")
    print(trader_stats.tail(5).to_string(index=False))
    
    # Plot 5: Net PnL by Trader Tier under different sentiments
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_merged, x='trader_tier', y='net_pnl', hue='sentiment_class', ci=None, palette='deep')
    plt.title("Average Net PnL per Trade by Trader Tier and Sentiment Regime", fontsize=14)
    plt.xlabel("Trader Tier", fontsize=12)
    plt.ylabel("Average Net PnL (USD)", fontsize=12)
    plt.legend(title="Sentiment Class")
    plt.tight_layout()
    plt.savefig("plots/trader_tier_performance_sentiment.png")
    plt.close()
    
    # =====================================================================
    # PHASE 9: ADVANCED ANALYSIS (CLUSTERING & CORRELATION)
    # =====================================================================
    print("\n--- PHASE 9: ADVANCED ANALYSIS ---")
    
    # Correlation Matrix
    corr_cols = ['execution_price', 'trade_value', 'fee', 'closed_pnl', 'net_pnl', 'sentiment_value']
    corr_matrix = df_merged[corr_cols].corr()
    print("\nCorrelation Matrix:")
    print(corr_matrix)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".4f", linewidths=0.5)
    plt.title("Correlation Matrix of Financial Metrics and Sentiment", fontsize=14)
    plt.tight_layout()
    plt.savefig("plots/correlation_matrix.png")
    plt.close()
    
    # Clustering Traders
    if HAS_SKLEARN:
        print("\nPerforming K-Means Clustering on Traders...")
        # Prepare trader features: volume, trade count, win rate, average fee, net PnL, sentiment sensitivity (correlation with sentiment)
        trader_features_list = []
        for name, group in df_merged.groupby('account'):
            # Calculate correlation of this trader's PnL with daily sentiment value
            if group['sentiment_value'].nunique() > 1 and group['net_pnl'].nunique() > 1:
                sent_corr = group['net_pnl'].corr(group['sentiment_value'])
            else:
                sent_corr = 0.0
            if np.isnan(sent_corr):
                sent_corr = 0.0
                
            trader_features_list.append({
                'account': name,
                'trade_count': len(group),
                'total_pnl': group['net_pnl'].sum(),
                'avg_size': group['trade_value'].mean(),
                'win_rate': (group['is_profit'] == True).sum() / len(group),
                'avg_fee': group['fee'].mean(),
                'sentiment_sensitivity': sent_corr
            })
            
        df_trader_features = pd.DataFrame(trader_features_list)
        
        # Standardize features
        features = ['trade_count', 'total_pnl', 'avg_size', 'win_rate', 'avg_fee', 'sentiment_sensitivity']
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_trader_features[features])
        
        # K-Means
        kmeans = KMeans(n_clusters=3, random_state=42)
        df_trader_features['cluster'] = kmeans.fit_predict(scaled_features)
        
        # PCA for visualization
        pca = PCA(n_components=2)
        pca_features = pca.fit_transform(scaled_features)
        df_trader_features['pca_1'] = pca_features[:, 0]
        df_trader_features['pca_2'] = pca_features[:, 1]
        
        print("\nCluster Center Descriptions:")
        for cluster_id in range(3):
            cluster_data = df_trader_features[df_trader_features['cluster'] == cluster_id]
            print(f"Cluster {cluster_id} (n={len(cluster_data)}):")
            print(f"  Avg Trade Count: {cluster_data['trade_count'].mean():.1f}")
            print(f"  Avg Total PnL:   ${cluster_data['total_pnl'].mean():.2f}")
            print(f"  Avg Trade Size:  ${cluster_data['avg_size'].mean():.2f}")
            print(f"  Avg Win Rate:    {cluster_data['win_rate'].mean()*100:.2f}%")
            print(f"  Sentiment Sens:  {cluster_data['sentiment_sensitivity'].mean():.4f}")
            
        # Plot 6: PCA Clusters
        plt.figure(figsize=(10, 7))
        sns.scatterplot(data=df_trader_features, x='pca_1', y='pca_2', hue='cluster', palette='Set1', s=100, style='cluster')
        plt.title("K-Means Clustering of Traders based on Behavior Profiles (PCA projection)", fontsize=14)
        plt.xlabel("PCA Component 1", fontsize=12)
        plt.ylabel("PCA Component 2", fontsize=12)
        plt.tight_layout()
        plt.savefig("plots/trader_clusters.png")
        plt.close()
        
        df_trader_features.to_csv("trader_behavioral_clusters.csv", index=False)
        print("Clustering complete! Results saved to 'trader_behavioral_clusters.csv'")
    else:
        print("\nscikit-learn is not installed. Skipping K-Means trader clustering step.")
        
    print("\n=====================================================================")
    print("ANALYSIS COMPLETED SUCCESSFULLY! All artifacts and plots generated.")
    print("=====================================================================")

if __name__ == "__main__":
    run_analysis_pipeline()
