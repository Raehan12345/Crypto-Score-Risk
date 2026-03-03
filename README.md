# Quantitative Trading: The Score Risk System

## Project Overview
This repository contains an event-driven backtesting framework for a systematic trading strategy dubbed "The Score Risk". Instead of relying on raw price action or single indicators, this model dynamically calculates a synthetic risk probability using a linear combination of four normalized market factors. Capital deployment is inversely correlated to the calculated risk score.

## Strategic Architecture

### 1. The Synthetic Risk Engine
The core of the system is a proprietary risk score ranging from 0 to 100. It is calculated by weighting four distinct market pillars:

* **ATH Score:** Measures the normalized distance from the asset's all time high, identifying value zones.
* **Trend Score:** Evaluates market structure using a boolean weighted stack of fast, medium, and slow Exponential Moving Averages.
* **Volatility Score:** Analyases rolling 30 period standard deviations normalized against a one year lookback to detect panic or complacency.
* **Ratio Score:** Tracks the relative strength of the ETH/BTC pair to gauge macro risk appetite in the cryptocurrency ecosystem.

The final risk probability is aggregated via the following formula:

$$Risk_{Total} = (w_1 \cdot S_{ATH}) + (w_2 \cdot S_{Trend}) + (w_3 \cdot S_{Vol}) + (w_4 \cdot S_{Ratio})$$

### 2. Execution Logic
The execution layer separates signal generation from capital management.

* **Tiered Dollar Cost Averaging (DCA):** The system scales into positions aggressively when the risk score is low (below 30) and conservatively when medium (below 50). To prevent aggressive capital depletion during sharp drawdowns, a 0.5% price step requirement is enforced between executions.
* **Laddered Scale Out:** Profit taking is managed via a Custom FIFO (First In First Out) queue. When the risk score exceeds 70, the system liquidates 20% of the active inventory, ensuring the oldest and cheapest lots are realized first.

## Backtest Results

The framework was tested on 15 minute OHLCV data to simulate high frequency systemic execution. After iterative recalibration of position sizing and price step parameters, the model achieved the following performance metrics over a 1000 period test:

* **Total Return:** 2.73%
* **Max Drawdown:** 4.53%
* **Sharpe Ratio (Annualized):** 3.76

The high Sharpe ratio and strictly capped Max Drawdown demonstrate the system's strict adherence to capital preservation over reckless alpha generation.

## Repository Structure
* `src/data_loader.py`: Handles anonymous historical data extraction via the CCXT library.
* `src/indicators.py`: Contains the mathematical logic for the four risk pillars.
* `src/engine.py`: The event driven simulator managing the FIFO inventory queue and capital tracking.
* `main.py`: The central orchestrator for data ingestion, backtesting, and Matplotlib performance visualization.

## Technologies Used
* Python
* Pandas & NumPy (Quantitative Analysis)
* CCXT (Market Data Ingestion)
* Matplotlib (Performance Visualization)