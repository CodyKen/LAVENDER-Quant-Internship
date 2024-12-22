# Factor Correlation Analysis Framework

This repository provides a **Factor Correlation Analysis Framework** designed to calculate and analyze correlations between financial factors. It allows users to compute several types of correlation matrices (Spearman, Kendall, MINE) across multiple time slices and returns the average correlations over all time periods. This framework is particularly useful for quantitative researchers and analysts working with financial data to assess the relationships between different factors.

## Features

### 1. **Factor Data Alignment**
- **Data Alignment**: Aligns multiple factor datasets based on common timestamps (`open_time`) and symbols (`symbol`) to ensure that the factors are consistently matched across time.
- **Flexible Input**: Works with any financial dataset where factors are presented as `DataFrame` objects, with `open_time` and `symbol` as key identifiers.

### 2. **Correlation Computation**
- **Spearman Rank Correlation**: Computes the Spearman rank correlation matrix, measuring the monotonic relationship between factors.
- **Kendall Tau Correlation**: Computes the Kendall Tau correlation matrix, which assesses the ordinal association between factors.
- **MINE (Maximal Information-based Nonparametric Exploration)**: Computes the MINE correlation matrix, which identifies non-linear relationships between factors based on mutual information.

### 3. **Modular**
- The framework is designed to be modular, allowing users to:
  - Integrate new factors or datasets.

### 4. **Dataset Partitioning**
- **Data Partitioning**: Break up datasets into training set and testing set based on specific time stamps.

### 5. **Efficient Implementation**
- Optimized for fast performance using `polars`, a high-performance DataFrame library, making it suitable for large-scale financial datasets.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Key dependencies:
  - `polars`
  - `scipy`
  - `minepy`

