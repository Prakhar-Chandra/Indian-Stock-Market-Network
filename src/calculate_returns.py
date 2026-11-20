
# ============================================================
# NETWORK SCIENCE PROJECT
# Phase 3: Logarithmic Return Calculation
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------------------------------------
# 1. PROJECT PATHS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

PRICE_FILE = (
    ROOT / "data" / "processed_returns"
    / "nifty185_clean_prices.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed_returns"

FIGURE_DIR = ROOT / "outputs" / "figures"

TABLE_DIR = ROOT / "outputs" / "tables"

FIGURE_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. LOAD CLEANED STOCK PRICES
# ------------------------------------------------------------

print("\nLoading cleaned stock prices...")

prices = pd.read_csv(
    PRICE_FILE,
    index_col="Date",
    parse_dates=True
)

prices = prices.sort_index()

print("Price matrix shape:", prices.shape)


# ------------------------------------------------------------
# 3. CALCULATE LOGARITHMIC RETURNS
# ------------------------------------------------------------

print("\nCalculating logarithmic returns...")

# Formula: ln(Pt / Pt-1)

returns = np.log(prices / prices.shift(1))

# Remove the first row because it has no previous price
returns = returns.iloc[1:]

# Verify return matrix
assert not returns.isna().any().any()

assert np.isfinite(returns.to_numpy()).all()


# ------------------------------------------------------------
# 4. SAVE RETURN DATASET
# ------------------------------------------------------------

returns.to_csv(
    OUTPUT_DIR / "nifty185_log_returns.csv",
    index_label="Date"
)

print("Return dataset saved successfully.")


# ------------------------------------------------------------
# 5. CALCULATE DESCRIPTIVE STATISTICS
# ------------------------------------------------------------

print("\nCalculating descriptive statistics...")

statistics = pd.DataFrame(index=returns.columns)

statistics["Mean_Return"] = returns.mean()

statistics["Median_Return"] = returns.median()

statistics["Std_Deviation"] = returns.std()

statistics["Minimum_Return"] = returns.min()

statistics["Maximum_Return"] = returns.max()

statistics["Variance"] = returns.var()

statistics["Skewness"] = returns.skew()

statistics["Kurtosis"] = returns.kurtosis()

# Save descriptive statistics
statistics.to_csv(
    TABLE_DIR / "return_descriptive_statistics.csv"
)


# ------------------------------------------------------------
# 6. OVERALL RETURN DISTRIBUTION
# ------------------------------------------------------------

all_returns = returns.to_numpy().flatten()

plt.figure(figsize=(10, 6))

plt.hist(
    all_returns,
    bins=80,
    edgecolor="black",
    alpha=0.75
)

plt.title("Distribution of Daily Logarithmic Returns")

plt.xlabel("Logarithmic Return")

plt.ylabel("Frequency")

plt.grid(alpha=0.25)

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "overall_return_distribution.png",
    dpi=300
)

plt.close()


# ------------------------------------------------------------
# 7. FINAL SUMMARY
# ------------------------------------------------------------

print("\n========== RETURN DATASET SUMMARY ==========")

print("Number of companies:", returns.shape[1])

print("Number of observations:", returns.shape[0])

print("Total return observations:", returns.size)

print("Missing values:", returns.isna().sum().sum())

print("First return date:", returns.index.min())

print("Last return date:", returns.index.max())

print("\n========== OVERALL STATISTICS ==========")

print("Average return:", all_returns.mean())

print("Return standard deviation:", all_returns.std())

print("Minimum return:", all_returns.min())

print("Maximum return:", all_returns.max())

print("\n========== TOP 10 VOLATILE COMPANIES ==========")

print(
    statistics.sort_values(
        "Std_Deviation",
        ascending=False
    )["Std_Deviation"].head(10)
)

print("\n========== VALIDATION ==========")

assert returns.shape == (738, 185)

assert returns.isna().sum().sum() == 0

print("All return calculations verified!")

print("\nPHASE 3 RETURN CALCULATION COMPLETED.")

