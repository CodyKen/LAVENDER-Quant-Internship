# Single-Factor Backtesting Framework

This repository contains the implementation of a **Single-Factor Backtesting Framework**, designed to support quantitative financial research and strategy development. The framework is modular, efficient, and extensible, providing users with the tools needed to evaluate single-factor strategies in a robust and systematic manner.

## Features

### 1. **Customizable Backtesting Logic**
- Define and test single-factor strategies.
- Support for long, short, and combined portfolio testing based on the factor values.

### 3. **Performance Metrics**
- Generate detailed performance reports, including:
  - Annualized returns.
  - Sharpe ratio.
  - Maximum drawdown.
  - calmar ratio.
- Time-series analysis of factor effectiveness.

### 4. **Visualization Tools**
- Plot key results:
  - Cumulative returns.
  - Factor returns by quantile.
  - Rolling performance metrics.

### 5. **Extensibility**
- Modular design makes it easy to:
  - Integrate new datasets.
  - Test customized factor definitions.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Key dependencies:
  - `polars`
  - `matplotlib`
  - `scipy`

Here we use polars instead of numpy to make the program run faster.

## Acknowledgments
- Inspiration from widely used financial libraries.
- Special thanks to our research and development team for their insights and support.


