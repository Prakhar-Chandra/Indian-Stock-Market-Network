# Topological and Structural Analysis of the Indian Stock Market

A Network Science project that studies relationships among Nifty 200 companies by constructing and analysing a Pearson-correlation network from daily stock returns.

**Course:** ECS414/614 — Network Science: Theory and Applications  
**Student:** Prakhar Chandra  
**Faculty guide:** Prof. Kundan Kandhway  
**Academic term:** 2026–27 (I)  
**Report submission date:** 20 November 2026

---

## 1. Project Overview

Financial markets are complex systems in which companies may move together because of common market conditions, industry-specific factors, economic policies and investor sentiment. This project uses Network Science to examine these relationships at the company level.

Each company is represented as a **node**. An undirected edge is created between two companies when the Pearson correlation between their daily logarithmic returns meets the selected threshold. The main network uses a correlation threshold of **0.6**.

## 2. Objectives

- Collect historical adjusted closing prices for Nifty 200 companies.
- Calculate daily logarithmic returns and pairwise Pearson correlations.
- Construct an undirected, unweighted correlation network.
- Study degree distribution, connectivity and centrality.
- Examine clustering and sector homophily.
- Test network changes at different correlation thresholds.

## 3. Data

| Item | Description |
|---|---|
| Market | Indian stock market |
| Universe | Nifty 200 constituents |
| Initial companies | 200 |
| Price-data period | 1 November 2023 – 31 October 2026 |
| Frequency | Daily |
| Price field | Adjusted closing price (`yfinance` with `auto_adjust=True`) |
| Data source | Yahoo Finance |
| Final companies | 184 |
| Final return observations | 735 common daily observations |

The constituent list was obtained from the official [Nifty Indices website](https://www.niftyindices.com/). Historical prices were retrieved through [Yahoo Finance](https://finance.yahoo.com/) using the Python `yfinance` package.

### Data-cleaning note

Fifteen companies with incomplete price histories were excluded to create a common observation panel. After calculating returns, MOTILALOFS was also excluded following an unusually large price-series discontinuity. Three selected dates were removed across the common return panel: 14 October 2025, 1 January 2026 and 30 April 2026. These decisions may remove genuine market or corporate-event information and are discussed in the report.

## 4. Methodology

### Daily logarithmic returns

For company i, daily logarithmic return is:

`r_i(t) = ln(P_i(t) / P_i(t-1))`

### Pearson correlation

Pearson correlation is calculated for each pair of company return series:

`rho_ij = Cov(r_i, r_j) / (sigma_i * sigma_j)`

### Network construction

The network is undirected and unweighted. An edge is included when:

`A_ij = 1 if rho_ij >= r; otherwise A_ij = 0`

The primary threshold is `r = 0.6`. Threshold sensitivity is examined at `0.5`, `0.6`, `0.7` and `0.8`.

### Network measures

- Number of nodes and edges, density and connected components.
- Largest connected component and average degree.
- Degree distribution.
- Degree, betweenness and eigenvector centrality.
- Local and average clustering coefficients.
- Same-sector edge proportion and sector assortativity.
- Average path length within the largest connected component.

## 5. Main Findings

At the primary correlation threshold of 0.6:

| Measure | Result |
|---|---:|
| Nodes | 184 |
| Edges | 126 |
| Network density | 0.0075 |
| Connected components | 122 |
| Largest connected component | 25 companies |
| Average degree | 1.3696 |
| Average clustering coefficient | 0.1962 |
| Mean pairwise correlation | 0.2684 |
| Same-sector edges | 103 of 126 (81.75%) |
| Sector assortativity | 0.7774 |

### Centrality highlights

- **Degree centrality:** CANBK and RECLTD share the highest score.
- **Betweenness centrality:** RECLTD ranks highest.
- **Eigenvector centrality:** CANBK ranks highest.

Financial Services companies appear frequently among highly ranked nodes. The network is sparse and fragmented at the selected threshold, and same-sector connections make up a large share of its edges.

### Threshold sensitivity

The project compares thresholds of 0.5, 0.6, 0.7 and 0.8. As the threshold increases, fewer company pairs qualify as edges and the largest connected component becomes smaller. Consult the report and threshold sensitivity output table for measured values.

## 6. Repository Structure

```text
Indian_Stock_Market_Network/
├── data/
│   ├── raw_prices/
│   └── processed_returns/
├── notebooks/
├── src/
│   ├── collect_data.py
│   ├── recover_failed.py
│   ├── verify_data.py
│   ├── preprocessing.py
│   ├── calculate_returns.py
│   ├── inspect_returns.py
│   ├── clean_extreme_returns.py
│   ├── audit_clean_returns.py
│   ├── calculate_correlations.py
│   ├── build_network.py
│   ├── network_analysis.py
│   └── threshold_sensitivity.py
├── outputs/
│   ├── figures/
│   └── tables/
├── report/
│   └── report.tex
├── requirements.txt
└── README.md
```

The exact files present may vary depending on which intermediate datasets and generated outputs are retained.

## 7. Visualisations and Outputs

The `outputs/figures/` directory contains visualisations of:
- Daily logarithmic return distribution.
- Pearson correlation heatmap.
- Nifty 184 network at threshold 0.6.
- Degree distribution on linear and log-log scales.
- Threshold versus number of edges.
- Threshold versus largest connected component.
- Threshold versus average path length.

The `outputs/tables/` directory contains analysis tables such as the correlation matrix, network edge and node lists, centrality rankings, clustering results, sector homophily results and threshold sensitivity results.

The LaTeX report provides the full explanation of the data pipeline, methodology, results, discussion, limitations and references.

## 8. Tools and Technologies

Python, pandas, NumPy, yfinance, NetworkX, Matplotlib, Seaborn, SciPy, Jupyter Notebook and LaTeX.

## 9. Setup

Python 3 is required. From the project root, create and activate a virtual environment.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the main packages:

```bash
pip install yfinance pandas numpy networkx matplotlib seaborn scipy jupyter openpyxl
```

## 10. Reproducing the Analysis

Run scripts from the project root in the logical order below. Check each script's arguments and expected input/output paths before running it.

```bash
python src/collect_data.py
python src/recover_failed.py
python src/verify_data.py
python src/preprocessing.py
python src/calculate_returns.py
python src/inspect_returns.py
python src/clean_extreme_returns.py
python src/audit_clean_returns.py
python src/calculate_correlations.py
python src/build_network.py
python src/network_analysis.py
python src/threshold_sensitivity.py
```

Some stages use files generated by earlier stages. If you are using the already processed datasets and outputs, you do not need to rerun data collection.

## 11. Limitations

- The current Nifty 200 constituent list was applied retrospectively to the full study period; historical index membership was not reconstructed. This introduces possible survivorship or selection bias.
- Historical prices were obtained from Yahoo Finance, and corporate-action adjustments may differ across data providers.
- Some selected extreme observations and dates were removed, although some may represent genuine market information.
- Pearson correlation captures linear relationships and may not capture nonlinear dependence.
- The network is static over the combined study period; relationships may change over time.
- Network structure and centrality rankings depend on the selected correlation threshold.

The network measures describe structural relationships in this dataset. They are not investment recommendations or predictions of future stock performance.

## 12. References

1. Chi, K. T., Tse, C. K., Liu, J., & Lau, F. C. M. (2010). A network perspective of the stock market. *Journal of Empirical Finance, 17*(4), 659–667.
2. Moghadam, M. K., et al. (2019). Complex networks analysis in Iran stock market: The application of centrality. *Physica A: Statistical Mechanics and its Applications, 531*, 121800.
3. [NSE Indices](https://www.niftyindices.com/)
4. [Yahoo Finance](https://finance.yahoo.com/)
5. [NetworkX Documentation](https://networkx.org/documentation/stable/)
6. [Python](https://www.python.org/)

---

**Author:** Prakhar Chandra  
**Project:** Network Science — Topological and Structural Analysis of the Indian Stock Market
