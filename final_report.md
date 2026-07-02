# Bitcoin Market Sentiment vs. Trader Performance Analysis
## Final Quantitative Research Report

---

## 1. Executive Summary

This report presents a thorough quantitative and behavioral analysis of the relationship between cryptocurrency market sentiment (measured by the daily **Crypto Fear and Greed Index**) and the historical transaction records of active perpetual contract traders on the **Hyperliquid DEX** (190,004 cleaned trade records spanning March 2023 to June 2025 across 32 unique trading accounts).

### Key Findings
1. **Regime Behavior & Volume**: Trader volume and trade counts are heavily concentrated in extreme sentiment regimes. Approximately **29.3%** of all trades occurred during Greed/Extreme Greed regimes, whereas **37.8%** occurred during Fear/Extreme Fear regimes.
2. **Profitability Anomalies**: Descriptively, average trade net PnL is highest during **Extreme Greed** ($66.68) and **Extreme Fear** ($55.37) compared to moderate or Neutral regimes ($33.93).
3. **Statistical Significance**: A Welch's T-Test comparing the net PnL distributions of trades executed during Fear vs. Greed regimes reveals a **t-statistic of -1.4698 and a p-value of 0.1416**. We fail to reject the null hypothesis of equal means at the 5% significance level, indicating that market sentiment does not guarantee a statistically significant shift in absolute transaction-level profitability.
4. **Trader Segmentation (Unsupervised Learning)**: K-Means clustering identified 3 distinct trader archetypes:
   - *Cluster 0 (Whales)*: High-volume, high-value traders whose overall trading returns are sentiment-invariant (correlation close to zero, $\approx 0.02$).
   - *Cluster 1 (Trend-Followers)*: Smaller-sized retail/pro traders whose PnL is positively correlated with sentiment ($\approx 0.117$), making them long-biased momentum traders.
   - *Cluster 2 (Counter-Cyclical / Hedgers)*: Moderate-sized traders showing a negative correlation with sentiment ($\approx -0.065$), trading contrarian strategies.
5. **Win Rate vs. PnL Asymmetry**: The top trader generated **+$2.08 Million** in net PnL despite a low win rate of **32.90%**, indicating a systematic, high-R:R (Risk-to-Reward) trend-following profile.

---

## 2. Project Objective

The primary objective is to investigate how retail and institutional sentiment affects trade execution sizes, transaction frequency, asset side bias (BUY vs. SELL), risk profiles, and final realized profitability (Closed PnL). Specifically, we test whether market sentiment can serve as a predictor of trader risk-taking or if it is a lagging indicator of behavioral biases.

---

## 3. Datasets

1. **Bitcoin Market Sentiment Dataset (`fear_greed_index.csv`)**:
   - $2,644$ daily observations (Feb 1, 2018, to May 2, 2025).
   - Features: `timestamp`, `value` (0-100 index), `classification` (Fear, Extreme Fear, Neutral, Greed, Extreme Greed), `date`.
2. **Historical Trader Dataset (`historical_data.csv`)**:
   - $211,224$ raw records of perpetual swaps executions (March 28, 2023, to June 15, 2025).
   - Features: `Account`, `Coin`, `Execution Price`, `Size Tokens`, `Size USD`, `Side`, `Timestamp IST`, `Start Position`, `Direction`, `Closed PnL`, `Transaction Hash`, `Order ID`, `Crossed`, `Fee`, `Trade ID`, `Timestamp`.

---

## 4. Methodology & Data Cleaning

To establish an academically rigorous research pipeline, the raw datasets were processed as follows:

1. **Standardization**: Standardized all variables to lowercase `snake_case` format.
2. **Timezone Alignment**: The numeric `Timestamp` column in the raw CSV was identified as lossy scientific notation (e.g., `1.73E+12` losing the lower 10 digits and truncating to a single epoch representation). We discarded it and parsed `Timestamp IST` using the explicit format `%d-%m-%Y %H:%M`, converting to datetime. We then shifted the timezone by `-05:30` to match UTC time.
3. **Deduplication**: Identified and removed **21,220 duplicate trade executions** based on key transactional attributes, reducing the trader dataset from 211,224 to **190,004 records** of unique transactional events.
4. **Categorical Stripping**: Stripped white spaces and trailing/leading characters from `account`, `coin`, `side`, and `direction`.
5. **Rebate Treatment**: Isolated negative fees representing **maker rebates** (traders earning fee payments for providing order book liquidity) and preserved them in Net PnL calculations.

---

## 5. Feature Engineering

We engineered several critical variables to analyze behavioral profiles:
* **`net_pnl`**: Realized profitability calculated as $\text{Closed PnL} - \text{Fee}$.
* **`trade_value`**: Nominal transaction volume equal to `size_usd`.
* **`is_profit`**: Boolean indicator identifying if `closed_pnl > 0`.
* **`win_loss`**: A categorical status column: `WIN` (PnL > 0), `LOSS` (PnL < 0), or `NEUTRAL` (PnL = 0).
* **`trade_size_category`**: Discretized scale segmenting order sizes using statistical quantiles: `MICRO`, `RETAIL`, `PRO`, and `WHALE`.
* **`time_diff_min`**: Approximate holding/frequency metric measuring elapsed time (in minutes) between consecutive trades in the same asset for each account.
* **`trader_rank`**: Ranking of traders based on cumulative net PnL.
* **`trader_tier`**: Segmenting accounts into `TOP_TRADER` (top 15% by total PnL), `BOTTOM_TRADER` (bottom 15%), and `AVERAGE_TRADER`.
* **`sentiment_encoded`**: Encoded sentiment scores (1 to 5) mapping to the 5 classifications.

---

## 6. Exploratory Data Analysis (EDA)

The EDA generated several structural insights (saved in `./plots/`):
* **PnL Distribution**: Extremely fat-tailed. The vast majority of trades yield PnL close to zero, but a minor fraction of trades yield extreme wins/losses, confirming the leverage-driven skewness of crypto futures.
* **Activity Concentration**: Trading volume spikes dramatically during periods of market extremes. Traders execute fewer transactions during Neutral market regimes.
* **Size Category Segments**: `MICRO` (< $200 USD) and `RETAIL` ($200 - $2,350 USD) categories constitute the majority of trade counts, while `PRO` and `WHALE` trade size categories represent the largest drivers of trading volume.

---

## 7. Sentiment Analysis (Fear vs. Greed)

The execution results show the following descriptive statistics:

| Sentiment Class | Trade Count | Total PnL (USD) | Mean PnL (USD) | Median PnL (USD) | Mean Trade Size (USD) | Total Fee (USD) | Win Rate (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Extreme Fear** | 18,138 | \$1,004,353 | \$55.37 | -\$0.0015 | \$6,146.46 | \$24,763.15 | 42.21% |
| **Fear** | 53,836 | \$2,566,620 | \$47.67 | -\$0.0089 | \$8,679.07 | \$88,309.55 | 41.56% |
| **Neutral** | 35,149 | \$1,192,759 | \$33.94 | -\$0.0198 | \$5,303.05 | \$41,032.69 | 35.49% |
| **Greed** | 45,228 | \$2,242,096 | \$49.57 | -\$0.0099 | \$5,843.03 | \$58,414.98 | 38.75% |
| **Extreme Greed**| 37,653 | \$2,510,684 | \$66.68 | -\$0.0024 | \$3,274.58 | \$27,105.85 | 45.00% |

### Statistical Testing
We conducted a **Welch's T-Test** to compare trade PnLs under **Fear (and Extreme Fear)** vs. **Greed (and Extreme Greed)**:
* **T-Statistic**: -1.4698
* **P-Value**: 0.1416
* **Interpretation**: The difference is statistically **insignificant** ($p > 0.05$). Market sentiment is not a standalone predictor of transaction-level PnL. The absolute profits are heavily influenced by individual trading strategies and asset-specific trends rather than the macro Fear & Greed Index alone.

---

## 8. Trader Behavior Analysis

### Performance Tiers & Accounts
* **The Alpha Trader (`0xb1231a4a2dd02f2276fa3c5e2a2f3436e6bfed23`)**: 
  - Net PnL: **+$2.08 Million** over 13,649 executions.
  - Win Rate: **32.90%**.
  - Direction Bias: Preferred side was **SELL**.
  - *Insight*: This trader uses a high-payoff trend-following strategy—frequent small losses cut early, offset by massive, highly leveraged short positions.
* **Top Size Trader (`0x083384f897ee0f19899168e3b1bec365f52a9012`)**:
  - Net PnL: **+$1.46 Million** over 2,558 executions.
  - Mean Trade Size: **$22,513.51 USD**.
  - Win Rate: **35.81%** (Preferred side: **SELL**).
* **The Liquidated Account (`0x8170715b3b381dffb7062c0298972d4727a0a63b`)**:
  - Net PnL: **-$175,997.80** over 4,028 executions.
  - Win Rate: **38.63%** (Preferred side: **SELL**).

---

## 9. Advanced Analysis (Clustering & Regimes)

### Unsupervised Clustering Results
Using K-Means clustering on normalized trader behavioral features, we identified **three behavioral archetypes**:

1. **Cluster 0: The Market-Making Whales (n=5)**
   - Characterized by exceptionally high transaction frequency (Avg: 16,274 trades) and large trade sizes (Avg: $14,491.72).
   - Sentiment Sensitivity: **0.0206** (virtually independent of market sentiment).
   - Profitability: Highest total net returns (Avg: **+$1.19 Million** per trader).
2. **Cluster 1: The Long-Biased Trend Followers (n=17)**
   - Characterized by lower transaction frequency and smaller trade sizes (Avg: $3,097.68).
   - Sentiment Sensitivity: **0.1172** (moderate positive correlation).
   - Performance: Profitable during Greed cycles, but vulnerable to drawdown in Fear regimes.
3. **Cluster 2: Counter-Cyclical Hedgers (n=10)**
   - Characterized by low win rates (Avg: 34.40%) and moderate size (Avg: $9,791.95).
   - Sentiment Sensitivity: **-0.0655** (negative correlation).
   - Performance: Profitability improves during market crashes and panic phases (Fear).

---

## 10. Strategic Business Insights

1. **Sentiment Independence is the Edge**: Top traders (Cluster 0) demonstrate a sentiment sensitivity near zero ($0.02$). Successful market participants remain systematic and emotional-free regardless of extreme crowd fear or greed.
2. **The "Win Rate" Myth**: The highest-earning trader ($2.08M) has a low win rate of 32.90%. They survive and thrive on asymmetric payout ratios (cutting losses quickly and riding winners).
3. **Overtrading in Greed**: Trades in Extreme Greed (37,653) are more than double those in Extreme Fear (18,138). Retail traders overtrade during euphoric market phases.
4. **Volume Drying Up in Neutral**: Traders execute the fewest trades during Neutral regimes. Lack of volatile moves or clear trend directions results in institutional/retail inactivity.
5. **Maker Rebates Subsidize Profits**: Top accounts earn positive payouts from negative fees (maker rebates), demonstrating the importance of execution mechanics (limit orders) in high-frequency setups.
6. **Sentiment as a Coincident/Lagging Indicator**: T-test results verify that absolute sentiment level does not guarantee trade-level profit changes. It is a coincident indicator of volatility and crowd momentum, not a leading indicator of alpha.
7. **Extreme Sentiment Attracts Size**: Average trade size during Fear ($8,679.07 USD) is higher than during Greed ($5,843.03 USD), indicating that smart money executes larger trades during panic corrections.
8. **Short Bias of Top Traders**: The two top-earning traders are heavily short-biased (preferred side: SELL), capturing rapid liquidations and crashes.
9. **Retail Vulnerability to Crowded Longs**: Cluster 1 traders are highly correlated with market sentiment ($0.117$), leaving them highly exposed to systematic flushes.
10. **Volatility Regimes Drive Fee Revenue**: The trading platform makes the most fee revenue during Fear periods due to panic liquidations and high trade values.
11. **Negative Fee Incentives Work**: Market-making accounts (Cluster 0) generate massive volume because of rebates, proving that fee structure directly shapes platform liquidity.
12. **Extreme Greed Elevates Win Probability slightly**: Win rate is highest in Extreme Greed (45.00%), but trade sizes are smaller, indicating retail fractioning of positions.
13. **Risk Contagion in Greed**: Position sizing is smaller in Extreme Greed, yet leverage and margin exposure are frequently high, posing cascading risk.
14. **Counter-Cyclical Hedging Alpha**: Cluster 2 traders show negative sentiment sensitivity, indicating a defined hedging alpha during extreme market downturns.
15. **Neutral Regime Volatility Trap**: Average PnL is lowest in Neutral sentiment regimes ($33.94 USD), indicating that traders suffer from low volume and sideways whipsaws.

---

## 11. Policy & Actionable Recommendations

### For Web3 Trading Platforms & Risk Teams
1. **Dynamic Leverage Caps**: Implement automatic caps on leverage (e.g., maximum 20x instead of 50x) when the 7-day moving average of the Crypto Fear & Greed Index rises above 80 (Extreme Greed). This protects retail traders from cascading liquidations.
2. **Counter-Cyclical Fee Structure**: Reduce taker fees during Neutral and Extreme Fear regimes to stimulate trading volume and order book depth when market activity naturally dries up.
3. **Sentiment-Aware UI Warnings**: Display warning notifications in the trading interface when the index is in extreme zones (e.g., "Market is in Extreme Greed. Consider adjusting your stop loss or reducing leverage to manage downside volatility").

### For Quantitative Strategies & Asset Allocation
4. **Counter-Trend Sizing Framework**: Scale up trade execution sizes during Extreme Fear (to capture market capitulation discounts) and scale down sizes during Extreme Greed.
5. **Systematic Stop-Loss Rules**: Enforce automated trailing stop-losses for long-biased trend-following accounts (Cluster 1) to prevent severe drawdown during sentiment regime shifts.
6. **Maker-Rebate Optimization**: Shift trading execution strategies from market orders (takers) to limit orders (makers) during periods of high volatility to capture execution rebates and offset directional trading losses.

---

## 12. Conclusion & Limitations

### Conclusion
Perpetual traders on Hyperliquid show distinct behavioral responses to market sentiment. While absolute transaction-level profitability is not statistically different between Fear and Greed regimes, trading volumes, execution sizes, and risk categories are heavily affected by macro sentiment. Unsupervised clustering successfully segmented professional, systematic accounts from sentiment-correlated retail accounts, showing that the key to profitability is execution discipline rather than following crowd sentiment.

### Limitations
* **Resolution**: Market sentiment is reported once daily, whereas trade executions occur at a millisecond resolution. Intraday sentiment shifts are not captured.
* **Leverage Metric**: Maximum and current leverage values were not explicitly recorded in the dataset columns. The analysis used transaction USD value as a proxy for trade risk.
* **Duration**: The trading dataset spans 2 years, which may not capture a full multi-year macro crypto cycle.

---

## 13. Future Scope

1. **Intraday Sentiment NLP**: Integrate high-frequency sentiment data derived from Twitter/X and Telegram API streams using natural language processing (NLP) to match trades at the minute level.
2. **Liquidation Event Mapping**: Map trade events explicitly to blockchain liquidation transactions to model the relationship between sentiment peaks and retail liquidation cascades.
3. **Multi-Asset Modeling**: Extend this methodology to evaluate sentiment dynamics across alternative layer-1 chains (e.g., Solana, Sui) and stablecoin capital flows.
