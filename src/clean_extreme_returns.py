
from pathlib import Path
import pandas as pd
import numpy as np

# --------------------------------------------------
# 1. SET PROJECT PATHS
# --------------------------------------------------

# Automatically identify the main project folder
PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed_returns"
    / "nifty185_log_returns.csv"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed_returns"
    / "nifty184_log_returns_clean.csv"
)

# --------------------------------------------------
# 2. CHECK WHETHER INPUT FILE EXISTS
# --------------------------------------------------

print("Looking for input file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput file not found: {INPUT_FILE}\n"
        "Check the filename inside data/processed_returns."
    )

# --------------------------------------------------
# 3. LOAD ORIGINAL LOG RETURNS
# --------------------------------------------------

returns = pd.read_csv(
    INPUT_FILE,
    index_col=0,
    parse_dates=True
)

print("\nOriginal dataset loaded successfully.")
print("Original shape:", returns.shape)

# --------------------------------------------------
# 4. REMOVE MOTILALOFS
# --------------------------------------------------

if "MOTILALOFS.NS" in returns.columns:
    returns = returns.drop(columns=["MOTILALOFS.NS"])
    print("\nRemoved MOTILALOFS.NS due to inconsistent price data.")

# --------------------------------------------------
# 5. REMOVE CORPORATE-ACTION EVENT DATES
# --------------------------------------------------

event_dates = [
    "2025-10-14",  # TMPV corporate-action date
    "2026-04-30",  # VEDL corporate-action date
    "2026-01-01"
]

for event_date in event_dates:
    event_date = pd.Timestamp(event_date)

    if event_date in returns.index:
        returns = returns.drop(index=event_date)
        print("Removed event date:", event_date.date())
    else:
        print("Event date not found:", event_date.date())

# --------------------------------------------------
# 6. VALIDATE CLEANED DATA
# --------------------------------------------------

# Convert values to numeric, if necessary
returns = returns.apply(pd.to_numeric, errors="coerce")

# Check missing values
missing_values = returns.isna().sum().sum()

# Check infinite values
infinite_values = np.isinf(returns.to_numpy()).sum()

print("\n========== DATA VALIDATION ==========")
print("Missing values:", missing_values)
print("Infinite values:", infinite_values)

if missing_values > 0 or infinite_values > 0:
    raise ValueError(
        "The cleaned dataset contains missing or infinite values."
    )

# --------------------------------------------------
# 7. SAVE CLEANED DATASET
# --------------------------------------------------

returns.to_csv(OUTPUT_FILE)

print("\n========== FINAL DATASET ==========")
print("Companies:", returns.shape[1])
print("Return observations:", returns.shape[0])
print("Total observations:", returns.size)
print("First date:", returns.index.min().date())
print("Last date:", returns.index.max().date())
print("Final shape:", returns.shape)

print("\nCleaned dataset saved at:")
print(OUTPUT_FILE)

