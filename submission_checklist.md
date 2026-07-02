# Web3 Hiring Assignment - Submission Checklist

Use this checklist to verify that all project components have been successfully prepared and run prior to submission.

## 📁 Repository Contents & Deliverables
- [x] **Raw Datasets**:
  - `fear_greed_index.csv` (Daily sentiment scores, 2,644 rows)
  - `historical_data.csv` (Hyperliquid executions, 211,224 rows)
- [x] **Data Cleaning & Pipeline Script**:
  - `data_cleaning.py` (Standardizes timezone, handles duplicates, processes fees and rebates)
- [x] **Quantitative Analysis & Modeling Pipeline**:
  - `run_analysis.py` (Performs data merging, feature engineering, statistical Welch's T-Test, K-Means clustering, and saves plots)
- [x] **Processed/Engineered Data Outputs**:
  - `cleaned_fear_greed_index.csv`
  - `cleaned_historical_data.csv`
  - `engineered_historical_data.csv` (Merged dataset with PnL, sizes, and trader categories)
  - `trader_behavioral_clusters.csv` (K-Means trader classification table)
- [x] **Analytical Visualizations** (`plots/` directory):
  - `plots/profit_distribution.png` (Fat-tailed PnL curve)
  - `plots/sentiment_distribution.png` (Trade counts by sentiment)
  - `plots/trade_size_by_side.png` (Categorized sizes vs buy/sell)
  - `plots/pnl_by_sentiment.png` (Boxplot comparing PnLs across regimes)
  - `plots/trader_tier_performance_sentiment.png` (Tiers vs sentiment returns)
  - `plots/correlation_matrix.png` (Financial feature correlations)
  - `plots/trader_clusters.png` (PCA visualization of behavioral groups)
- [x] **Comprehensive Documentation**:
  - `README.md` (Project overview, structured instructions, hypothesis table)
  - `final_report.md` (Senior Data Scientist report containing statistical findings, Welch's T-test, K-Means findings, and 15 strategic insights)
  - `requirements.txt` (List of library dependencies)

---

## 🔬 Core Quantitative Outcomes Verified
1. **Deduplication Validation**: 21,220 duplicate transactions successfully removed.
2. **Date Alignment**: IST timestamps converted to UTC to align with the daily sentiment indices.
3. **Statistical Integrity**: Welch's T-test run to compare PnL across regimes ($T = -1.4698, P = 0.1416$), confirming no statistically significant difference at the 5% level.
4. **Behavioral Archetypes**: Identified 3 K-Means clusters representing (0) Sentiment-Invariant Whales, (1) Long-Biased Trend Followers, and (2) Counter-Cyclical Hedgers.
5. **Win Rate vs. PnL Asymmetry**: Top trader generated **+$2.08 Million** with a **32.90%** win rate, showing massive positive asymmetry.
