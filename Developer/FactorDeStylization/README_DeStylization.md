# Factor De-Stylization and Orthogonalization Framework

This repository provides a **Factor De-Stylization and Orthogonalization Framework** designed to help quantitative researchers process financial factors for strategy development and evaluation. The framework allows users to clean and orthogonalize factors by removing extreme values and performing regression-based factor de-stylization in a systematic and modular way.

## Features

### 1. **De-Stylization of Factors**
- **Remove extreme values**: Handles extreme outliers using the Median Absolute Deviation (MAD) method, replacing values that are beyond 5 times the MAD from the median with boundary values.
- **Time-series based cleaning**: Applies outlier removal on each time slice (e.g., per `open_time`).

### 2. **Orthogonalization of Factors**
- **Regression-based de-stylization**: Removes the linear relationship between a factor (e.g., `alpha008`) and another market factor (e.g., `close`) by fitting a linear regression model and retaining the residuals.
- **Time-series based orthogonalization**: The process is applied per time slice, ensuring that the factor is de-stylized independently for each time segment.

### 3. **Modular and Extensible**
- The framework allows users to:
  - Easily integrate new financial factors.
  - Customize the outlier removal and orthogonalization processes.
  - Adapt the framework to different time series datasets.

### 4. **Efficient Implementation**
- Designed for large datasets and optimized for fast performance using `polars`, an efficient DataFrame library.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Key dependencies:
  - `polars`
  - `statsmodels`

The use of `polars` ensures fast data manipulation, especially on large datasets.

### Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt

