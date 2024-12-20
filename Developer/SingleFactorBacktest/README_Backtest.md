# Single-Factor Backtesting Framework

This repository contains the implementation of a **Single-Factor Backtesting Framework**, designed to support quantitative financial research and strategy development. The framework is modular, efficient, and extensible, providing users with the tools needed to evaluate single-factor strategies in a robust and systematic manner.

## Features

### 1. **Customizable Backtesting Logic**
- Define and test single-factor strategies.
- Support for long, short, and combined portfolio testing.

### 2. **Preprocessing and Factor Neutralization**
- Built-in functions for factor preprocessing, including:
  - Winsorization to remove outliers.
  - Z-score normalization.
- Neutralization options for industry or other risk factors.

### 3. **Performance Metrics**
- Generate detailed performance reports, including:
  - Annualized returns.
  - Sharpe ratio.
  - Maximum drawdown.
  - Information ratio.
- Time-series analysis of factor efficacy.

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
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `scipy`

### Installation
Clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/single-factor-backtesting.git
cd single-factor-backtesting
pip install -r requirements.txt
```

---

## Usage

### 1. Load Data
Ensure your data is in the required format:
- **Columns**:
  - `date`: Timestamps of data points.
  - `symbol`: Asset identifiers.
  - `factor_value`: Single-factor values to be tested.
  - Additional columns for returns and auxiliary data.

Example:
```python
import pandas as pd

data = pd.read_csv('sample_data.csv')
data.head()
```

### 2. Initialize Framework
Import and initialize the backtesting module:

```python
from backtesting_framework import Backtest

backtest = Backtest(data=data, factor_col='factor_value', returns_col='returns')
```

### 3. Preprocess Factor
Apply winsorization and normalization:
```python
backtest.preprocess_factor(winsorize=True, normalize=True)
```

Optional: Neutralize factors by industry:
```python
backtest.neutralize_factor(neutralize_by='industry')
```

### 4. Run Backtest
Run the backtest and generate performance metrics:
```python
results = backtest.run()
backtest.plot_cumulative_returns()
```

### 5. Analyze Results
Access detailed metrics:
```python
print(results.summary())
```

---

## Example

Here's a full example using sample data:

```python
import pandas as pd
from backtesting_framework import Backtest

# Load sample data
data = pd.read_csv('sample_data.csv')

# Initialize backtesting framework
backtest = Backtest(data=data, factor_col='factor_value', returns_col='returns')

# Preprocess factor
backtest.preprocess_factor(winsorize=True, normalize=True)

# Run backtest
results = backtest.run()

# Plot cumulative returns
backtest.plot_cumulative_returns()

# Print performance summary
print(results.summary())
```

---

## Roadmap
Future improvements:
- Multi-factor testing support.
- Advanced visualization (e.g., factor correlation heatmaps).
- Integration with live trading platforms.

---

## Contributing
We welcome contributions! Please read our [contribution guidelines](CONTRIBUTING.md) for details on how to get involved.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

---

## Acknowledgments
- Inspiration from widely used financial libraries.
- Special thanks to our research and development team for their insights and support.


