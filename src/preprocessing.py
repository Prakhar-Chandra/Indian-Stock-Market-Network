
# ============================================================
# NETWORK SCIENCE PROJECT
# Phase 3: Data Cleaning and Preparation
# ============================================================

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------
# 1. PROJECT PATHS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

PRICE_FILE = (
    ROOT / "data" / "raw_prices"
    / "nifty200_adjusted_close.csv"
)

CONSTITUENT_FILE = (
    ROOT / "data" / "nifty200_constituents.csv"
)

PROCESSED_DIR = ROOT / "data" / "processed_returns"
TABLE_DIR = ROOT / "outputs" / "tables"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 2. LOAD ORIGINAL DATA
# ------------------------------------------------------------

print("\nLoading original datasets...")

prices = pd.read_csv(
    PRICE_FILE,
    index_col="Date",
    parse_dates=True
)

constituents = pd.read_csv(CONSTITUENT_FILE)

# Ensure chronological order
prices = prices.sort_index()

print("Original price matrix:", prices.shape)


# ------------------------------------------------------------
# 3. IDENTIFY COMPLETE AND INCOMPLETE COMPANIES
# ------------------------------------------------------------

# Companies with zero missing price observations
complete_tickers = prices.columns[
    prices.notna().all()
].tolist()

# Companies with one or more missing observations
incomplete_tickers = prices.columns[
    prices.isna().any()
].tolist()

print("\nComplete companies:", len(complete_tickers))
print("Incomplete companies:", len(incomplete_tickers))


# ------------------------------------------------------------
# 4. CREATE CLEAN PRICE MATRIX
# ------------------------------------------------------------

clean_prices = prices[complete_tickers].copy()

# Verify that the cleaned dataset has no missing values
assert clean_prices.isna().sum().sum() == 0

# Save cleaned prices
clean_prices.to_csv(
    PROCESSED_DIR / "nifty185_clean_prices.csv",
    index_label="Date"
)


# ------------------------------------------------------------
# 5. CREATE EXCLUDED COMPANY REPORT
# ------------------------------------------------------------

excluded = constituents[
    constituents["Yahoo_Ticker"].isin(incomplete_tickers)
].copy()

excluded["Missing_Observations"] = [
    int(prices[ticker].isna().sum())
    for ticker in excluded["Yahoo_Ticker"]
]

excluded["First_Available_Date"] = [
    prices[ticker].first_valid_index()
    for ticker in excluded["Yahoo_Ticker"]
]

excluded["Last_Available_Date"] = [
    prices[ticker].last_valid_index()
    for ticker in excluded["Yahoo_Ticker"]
]

excluded.to_csv(
    TABLE_DIR / "excluded_companies.csv",
    index=False
)


# ------------------------------------------------------------
# 6. CREATE CLEANED CONSTITUENT LIST
# ------------------------------------------------------------

clean_constituents = constituents[
    constituents["Yahoo_Ticker"].isin(complete_tickers)
].copy()

clean_constituents.to_csv(
    PROCESSED_DIR / "nifty185_constituents.csv",
    index=False
)


# ------------------------------------------------------------
# 7. VERIFY FINAL DATASET
# ------------------------------------------------------------

print("\n========== FINAL CLEAN DATASET ==========")

print("Number of companies:", clean_prices.shape[1])

print("Number of trading dates:", clean_prices.shape[0])

print("Total price observations:", clean_prices.size)

print("Missing observations:", clean_prices.isna().sum().sum())

print("First date:", clean_prices.index.min())

print("Last date:", clean_prices.index.max())

print("\n========== SECTOR DISTRIBUTION ==========")

print(
    clean_constituents["Industry"]
    .value_counts()
)

print("\n========== VALIDATION ==========")

assert clean_prices.shape == (739, 185)

assert len(clean_constituents) == 185

assert len(excluded) == 15

print("All validation checks passed!")

print("\nClean dataset saved successfully.")

