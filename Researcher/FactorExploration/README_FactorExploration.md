# Factor Exploration Portfolio

This repository contains a collection of **financial factors** that I have developed and explored for quantitative research. These factors are designed to be used in the development and evaluation of financial strategies. The factors are provided in their most **raw form**, and some may exhibit high correlations with common **style factors** (e.g., `return`, `close`, `volume`), so please keep this in mind when applying them.

## Features

### 1. **Factor Collection**
- **Frequency**: Factors include both **daily** and **hourly** frequency data, suitable for a variety of time-based strategies.
- **Raw Data**: The factors in this repository are presented in their **raw form**, and may not yet be cleaned or processed. Some factors might be highly correlated with market style factors such as returns, price, or volume.
- **Potential for Strategy Development**: While these factors have not yet been optimized or filtered, they provide a solid foundation for factor-based research and strategy development.

### 2. **Factor Evaluation Criteria**
- **Sharpe Ratio**: The effectiveness of a factor is evaluated based on its **historical backtest performance**, with a minimum target **Sharpe ratio of 0.7**.
- **Backtest Framework**: I used the backtest framework outlined in the [Developer Documentation](#) to evaluate the factors. The historical backtest involves trading based on the factor values, and the Sharpe ratio is calculated to measure the factor's risk-adjusted return.

### 3. **Correlation with Style Factors**
- Some of the factors in this portfolio may exhibit high correlations with commonly used **style factors**, such as:
  - **Return**: The difference in asset price over time.
  - **Close Price**: The closing price of the asset.
  - **Volume**: The total trading volume during a period.
- It's important to note that these correlations are inherent to many financial factors, and should be considered when building strategies.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Key dependencies:
  - `polars`
  - `numpy`
  - `pandas`
  - `scipy`
  - `statsmodels`

To install the necessary libraries, you can use `pip`:
```bash
pip install polars numpy pandas scipy statsmodels

