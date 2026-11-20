
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRICE_FILE = (
    ROOT / "data" / "raw_prices"
    / "nifty200_adjusted_close.csv"
)

OUTPUT_DIR = ROOT / "outputs" / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load price data
prices = pd.read_csv(
    PRICE_FILE,
    index_col="Date",
    parse_dates=True
)

total_dates = len(prices)

# ------------------------------------------------
# 1. Missing values for each company
# ------------------------------------------------

report = pd.DataFrame(index=prices.columns)

report["Total_Observations"] = total_dates

report["Available_Prices"] = prices.notna().sum()

report["Missing_Prices"] = prices.isna().sum()

report["Missing_Percentage"] = (
    report["Missing_Prices"] / total_dates * 100
)

report["First_Available_Date"] = prices.apply(
    lambda x: x.first_valid_index()
)

report["Last_Available_Date"] = prices.apply(
    lambda x: x.last_valid_index()
)

# Missing values between first and last valid prices
report["Interior_Missing"] = [
    prices[ticker].loc[
        report.loc[ticker, "First_Available_Date"]:
        report.loc[ticker, "Last_Available_Date"]
    ].isna().sum()
    if pd.notna(report.loc[ticker, "First_Available_Date"])
    else 0
    for ticker in prices.columns
]

# Sort by missing percentage
report = report.sort_values(
    "Missing_Percentage",
    ascending=False
)

# Save complete report
report.to_csv(
    OUTPUT_DIR / "missing_data_diagnostic.csv"
)

# ------------------------------------------------
# 2. Identify companies with missing prices
# ------------------------------------------------

print("\n========== MISSING DATA REPORT ==========")

print(
    report[report["Missing_Prices"] > 0].to_string()
)

# ------------------------------------------------
# 3. Overall data statistics
# ------------------------------------------------

print("\n========== OVERALL STATISTICS ==========")

print("Total companies:", len(prices.columns))

print("Total observations:", total_dates)

print("Total possible values:", prices.size)

print("Total missing values:", prices.isna().sum().sum())

print(
    "Overall missing percentage:",
    round(prices.isna().mean().mean() * 100, 2),
    "%"
)

# ------------------------------------------------
# 4. Complete historical coverage
# ------------------------------------------------

complete = prices.columns[
    prices.notna().all()
]

print("\nCompanies with complete price history:", len(complete))

print("Companies with incomplete price history:",
      len(prices.columns) - len(complete))

# ------------------------------------------------
# 5. Check whether missing values are at the beginning
# or end of the available series
# ------------------------------------------------

print("\n========== INTERIOR MISSING VALUES ==========")

print(
    report[
        report["Interior_Missing"] > 0
    ][
        ["Missing_Prices", "Interior_Missing",
         "First_Available_Date", "Last_Available_Date"]
    ].to_string()
)

print("\nDiagnostic report saved successfully.")

