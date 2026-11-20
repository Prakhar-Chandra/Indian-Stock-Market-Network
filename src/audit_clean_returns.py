
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent

FILE = (
    PROJECT_DIR
    / "data"
    / "processed_returns"
    / "nifty184_log_returns_clean.csv"
)

returns = pd.read_csv(FILE, index_col=0, parse_dates=True)

# Convert data to numeric
returns = returns.apply(pd.to_numeric, errors="coerce")

# Find the 15 largest negative returns
negative = returns.stack().sort_values().head(15)

# Find the 15 largest positive returns
positive = returns.stack().sort_values(ascending=False).head(15)

print("\n========== 15 LARGEST NEGATIVE RETURNS ==========")
print(negative.to_string())

print("\n========== 15 LARGEST POSITIVE RETURNS ==========")
print(positive.to_string())

# Overall return statistics
print("\n========== RETURN SUMMARY ==========")
print("Minimum:", returns.min().min())
print("Maximum:", returns.max().max())
print("Mean:", returns.stack().mean())
print("Standard deviation:", returns.stack().std())

# Check for extreme absolute returns above 20%
extreme = returns.where(returns.abs() > 0.20).stack()

# Show only genuine extreme returns above 20%
extreme = returns.stack()
extreme = extreme[extreme.abs() > 0.20]

print("\n========== EXTREME RETURNS ABOVE 20% ==========")

if extreme.empty:
    print("No extreme returns found.")
else:
    print(extreme.sort_values().to_string())

print("\nTotal extreme observations:", len(extreme))
