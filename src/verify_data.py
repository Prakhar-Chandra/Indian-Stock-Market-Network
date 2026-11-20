
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

constituents = pd.read_csv(
    ROOT / "data/nifty200_constituents.csv"
)

prices = pd.read_csv(
    ROOT / "data/raw_prices/nifty200_adjusted_close.csv",
    index_col="Date",
    parse_dates=True
)

quality = pd.read_csv(
    ROOT / "data/raw_prices/data_quality_report.csv"
)

print("\n========== DATASET OVERVIEW ==========")

print("Constituent companies:", len(constituents))
print("Price dataset shape:", prices.shape)

print("\n========== DATE INFORMATION ==========")

print("First date:", prices.index.min())
print("Last date:", prices.index.max())

print("\n========== MISSING DATA ==========")

missing = prices.isna().sum()

print("Total missing values:", missing.sum())
print("Companies with missing values:", (missing > 0).sum())

print("\n========== COMPANY COVERAGE ==========")

print(quality["Download_Status"].value_counts())

print("\n========== INDUSTRY DISTRIBUTION ==========")

print(
    constituents["Industry"]
    .value_counts()
    .head(15)
)

print("\n========== FIRST FIVE PRICE RECORDS ==========")

print(prices.head())

print("\nData verification completed.")

