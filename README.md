# Score Risk System (SRS)

## Project Overview
The **Score Risk System** is a high-frequency, event-driven quantitative trading engine developed in Python. It is designed to navigate the high-volatility environments of Bitcoin (BTC) and Ethereum (ETH) by utilizing a proprietary multi-factor **Risk Score** to dictate position sizing and direction.

## Latest Performance Summary
*As of March 2026*

| Metric | Value |
| :--- | :--- |
| **Final Equity** | $42,395.78 |
| **Total Return** | **323.96%** |
| **Max Drawdown (MDD)** | **61.40%** |
| **Sharpe Ratio** | 0.79 |
| **Total Periods** | 210,280 (15m Candles) |



## Core Technical Architecture

### 1. Synthetic Risk Scoring
The engine calculates a real-time risk metric (0-100) based on four primary sub-factors:
* **Distance from ATH:** Quantifies the "discount" or "overextension" of the asset.
* **Trend Momentum:** Measures price velocity relative to the 50-day EMA.
* **Volatility (ATR):** Adjusts entry spacing and sizing based on market chaos.
* **ETH/BTC Divergence:** Used as a leading indicator for market-wide regime shifts.

### 2. Execution Engine
* **Regime Filter:** A 50-day Exponential Moving Average (EMA) acts as the primary switch between "Bull" (Long-biased) and "Bear" (Short-biased/Defensive) modes.
* **Inventory Management:** Utilizes a **Bi-directional FIFO Queue** to manage layered DCA (Dollar Cost Averaging) entries and exits.
* **Position Sizing:** Tiered entry logic (e.g., 15% / 8%) to ensure capital is deployed at optimal risk levels.

### 3. Institutional Risk Management
* **Volatility Normalization:** Pre-calculates 24-hour and 30-day ATR baselines to prevent "buying the cliff" during cascading liquidations.
* **Dynamic Step Logic:** Spaces entries based on ATR-multipliers (e.g., 1.5x ATR) to ensure mathematical distribution of risk.
* **Circuit Breakers:** Implements equity-based stops to protect the principal during "black swan" events.



## Project Structure
```text
score-risk-system/
├── data/               # local h5/csv cache for btc/eth history
├── src/
│   ├── engine.py       # core event-driven simulation logic
│   ├── indicators.py   # synthetic risk score & ema calculations
│   └── execution.py    # fifo queue & order management
├── results/            # backtest charts and csv reports
└── main.py             # entry point for backtest simulation