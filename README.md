# Bitcoin Market Sentiment vs. Trader Performance Analysis

An end-to-end quantitative data science and behavior analytics research project. This project explores the mathematical and behavioral relationships between Bitcoin market sentiment (as measured by the Crypto Fear and Greed Index) and multi-asset perpetual trader transaction data from Hyperliquid.

This repository serves as a submission for the Web3 Quantitative Analyst / Data Scientist hiring assignment.

---

## 📂 Project Repository Structure

```directory
├── README.md                      <- Project summary, roadmap, and setup instructions.
├── requirements.txt               <- List of Python library dependencies.
├── fear_greed_index.csv           <- Raw Bitcoin market sentiment index daily dataset (2018-2025).
├── historical_data.csv            <- Raw Hyperliquid trade-by-trade transaction history (211k+ records).
├── data_cleaning.py               <- Automated pipeline for standardized timezone and deduplication checks.
├── run_analysis.py                <- Core quantitative analysis, clustering, and charting pipeline.
├── cleaned_fear_greed_index.csv     <- Output: Standardized daily sentiment timeseries data.
├── cleaned_historical_data.csv      <- Output: Cleaned and deduplicated high-frequency transaction data.
├── engineered_historical_data.csv   <- Output: Merged dataset containing PnL and size categories.
├── trader_behavioral_clusters.csv  <- Output: K-Means trader clustering categorization results.
├── submission_checklist.md         <- List of required deliverables and verified results.
├── final_report.md                <- Detailed quantitative report containing 15 strategic insights.
└── plots/                         <- Directory containing generated analytical visualizations.
    ├── profit_distribution.png
    ├── sentiment_distribution.png
    ├── trade_size_by_side.png
    ├── pnl_by_sentiment.png
    ├── trader_tier_performance_sentiment.png
    ├── correlation_matrix.png
    └── trader_clusters.png
```

---

## 📊 Business Problem & Project Objective

In crypto markets, trader behavior is strongly driven by psychological shifts. Extreme sentiment—quantified by indicators like the **Fear & Greed Index**—drives market volatility. However, a major question remains:
> Do traders act rationally across different sentiment regimes, or do psychological biases (e.g., FOMO, panic selling, excessive leverage) lead to systematically poor risk-adjusted returns?

### Objective
To analyze the correlation between Bitcoin market sentiment and trader performance (PnL, win rates, leverage utilization, and asset preferences) to:
1. Identify behavioral patterns and risk tendencies during market extremes.
2. Formulate counter-cyclical trading insights.
3. Establish parameter recommendations for trading platform risk frameworks.

---

## 🔬 Core Quantitative Hypotheses & Verified Results

| ID | Hypothesis | Quantitative Indicator | Empirical Result / Verdict |
| :--- | :--- | :--- | :--- |
| **$\text{H}_1$** | **Profitability Regime Shift** | Mean/Median PnL under Fear vs. Greed | **FAIL TO REJECT**: Welch's T-Test yielded a p-value of `0.1416` (statistically insignificant at 5%). Extreme sentiment alone does not guarantee a change in trade-level PnL. |
| **$\text{H}_2$** | **Leverage & Risk Escalation** | Position Size Category Distribution | **SUPPORTED**: Traders execute larger average transaction values during Fear ($8,679.07 USD) vs. Greed ($5,843.03 USD), reflecting contrarian size-scaling by smart money. |
| **$\text{H}_3$** | **Overtrading Behavior** | Daily Trades per active account | **SUPPORTED**: Trading frequency spikes heavily during Greed and Extreme Greed regimes, accounting for over double the activity of Extreme Fear. |
| **$\text{H}_4$** | **Trader Archetypes** | PnL-to-Sentiment Correlation | **SUPPORTED**: K-Means clustering identified that Whales (Cluster 0) are sentiment-invariant (correlation of 0.02), whereas retail trend-followers (Cluster 1) are highly sentiment-correlated (0.117). |
| **$\text{H}_5$** | **Win-Loss Asymmetry** | Win Rate vs. Average Drawdown | **SUPPORTED**: The top trader generated **+$2.08M** with only a **32.90%** win rate, showing huge positive payoff asymmetry. |
| **$\text{H}_6$** | **Directional Herding** | Buy/Sell Order Imbalance | **SUPPORTED**: Overwhelming SELL side bias was observed during Extreme Fear, while BUY volume surged during Greed cycles. |

---

## 🛠️ Data Pipeline & Cleaning Methodology

The raw datasets present several formatting and structural challenges which are resolved in the initial pipeline phases:

### 1. Timestamp Standardization & UTC Alignment
* **Issue**: The trader dataset records timestamps in Indian Standard Time (IST) strings (`DD-MM-YYYY HH:MM`), while the daily sentiment index is aligned in UTC (`YYYY-MM-DD`). Additionally, the numeric `Timestamp` column in the raw CSV was saved in lossy scientific notation (e.g., `1.73E+12` losing critical precision digits).
* **Fix**: The numeric `Timestamp` was discarded. We parsed `Timestamp IST` using the explicit format `%d-%m-%Y %H:%M` and shifted the datetime index by `-05:30` to establish a precise `trade_date` in UTC for matching.

### 2. Deduplication & Stripping
* **Issue**: Spaces and special character sequences inside string fields (e.g., accounts, coins, transaction hashes) can cause matching fragmentation.
* **Fix**: Whitespaces are stripped across string features. Transactional entries matching on key execution metrics (`account`, `coin`, `execution_price`, `size_tokens`, `timestamp_ist`, `side`, `direction`) were deduplicated, removing **21,220 double-reported records** to preserve statistical independence.

### 3. Fee & Rebate Processing
* **Insight**: Negative transaction fees are identified. In perpetual exchanges, negative fees represent **maker rebates** paid to liquidity-providing traders. These are preserved and analyzed as positive earnings.

---

## 🚀 Getting Started

### Prerequisites
Installs required packages for data loading, processing, and visual modeling:
```bash
pip install -r requirements.txt
```
*Dependencies: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `scikit-learn`, `plotly`*

### Step 1: Run Data Cleaning
To process the raw files and generate the standardized, cleaned datasets:
```bash
python data_cleaning.py
```

### Step 2: Run Analysis & Modeling
To merge datasets, calculate features, run statistical testing, perform K-Means clustering, and save visualizations:
```bash
python run_analysis.py
```

### Step 3: Launch Web-based Interactive Dashboard
An interactive web-based dashboard is provided to explore findings, plots, and statistical outcomes in a premium interface:
* **Option A**: Double-click the [index.html](file:///c:/Users/vk557/Downloads/EDA%20+%20feature%20engineering%20+%20insight%20generation%20+%20storytelling/index.html) file inside this folder to open it directly in any web browser.
* **Option B**: Run a local web server (e.g., if using VS Code, use "Live Server", or run `python -m http.server 8000` in this directory and navigate to `http://localhost:8000`).


---

## 📈 Assignment Execution Roadmap
- [x] **Phase 1**: Project Understanding, Hypothesis Formulation, and Business Mapping.
- [x] **Phase 2**: Initial Data Loading and Structural Profiling.
- [x] **Phase 3**: Data Cleaning (Timezone shifting, Deduplication, and Rebate profiling).
- [x] **Phase 4**: Data Merging (Deterministic Sentiment Mapping).
- [x] **Phase 5**: Feature Engineering (Win rates, trader tiers, leverage metrics).
- [x] **Phase 6**: Exploratory Data Analysis & Visualization (Clipped PnL curves, sentiment counts).
- [x] **Phase 7**: Sentiment Impact Comparison (Fear vs. Greed performance statistics & Welch's T-Test).
- [x] **Phase 8**: Detailed Trader Behavior Analysis (Top & Bottom performers).
- [x] **Phase 9**: Advanced Clustering & Correlation Regime Analysis (K-Means on trader profiles).
- [x] **Phase 10**: Strategic Business Insights (15 core findings).
- [x] **Phase 11**: Policy & Actionable Recommendations (Dynamic leverage caps, contrarian sizing).
- [x] **Phase 12**: Final Professional Report (`final_report.md`).
- [x] **Phase 13**: Notebook Optimization & Submission Checklist (`submission_checklist.md`).
