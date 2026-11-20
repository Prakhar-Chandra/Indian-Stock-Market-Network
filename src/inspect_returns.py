
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRICE_FILE = (
    ROOT / "data" / "processed_returns"
    / "nifty185_clean_prices.csv"
)

RETURN_FILE = (
    ROOT / "data" / "processed_returns"
    / "nifty185_log_returns.csv"
)

prices = pd.read_csv(
    PRICE_FILE,
    index_col="Date",
    parse_dates=True
)

returns = pd.read_csv(
    RETURN_FILE,
    index_col="Date",
    parse_dates=True
)

# ------------------------------------------------
# 1. Find the 20 most extreme negative returns
# ------------------------------------------------

long_returns = returns.stack().reset_index()

long_returns.columns = [
    "Date", "Ticker", "Log_Return"
]

long_returns = long_returns.sort_values(
    "Log_Return"
)

print("\n========== 20 LARGEST NEGATIVE RETURNS ==========")

print(long_returns.head(20).to_string(index=False))


# ------------------------------------------------
# 2. Find the 20 largest positive returns
# ------------------------------------------------

print("\n========== 20 LARGEST POSITIVE RETURNS ==========")

print(
    long_returns.tail(20)
    .sort_values("Log_Return", ascending=False)
    .to_string(index=False)
)


# ------------------------------------------------
# 3. Identify the single most extreme observation
# ------------------------------------------------

worst = long_returns.iloc[0]

ticker = worst["Ticker"]
date = worst["Date"]

print("\n========== EXTREME RETURN INVESTIGATION ==========")

print("Company:", ticker)
print("Date:", date)
print("Log return:", worst["Log_Return"])

previous_date = prices.index[
    prices.index.get_loc(date) - 1
]

previous_price = prices.loc[previous_date, ticker]
current_price = prices.loc[date, ticker]

ordinary_return = np.exp(worst["Log_Return"]) - 1

print("Previous trading date:", previous_date)
print("Previous adjusted price:", previous_price)
print("Current adjusted price:", current_price)
print("Ordinary percentage return:", ordinary_return * 100)


# ------------------------------------------------
# 4. Check each company's return volatility
# ------------------------------------------------

volatility = returns.std().sort_values(
    ascending=False
)

print("\n========== TOP 10 VOLATILE COMPANIES ==========")

print(volatility.head(10).to_string())


# ------------------------------------------------
# 5. Check extreme observations in context
# ------------------------------------------------

print("\n========== PRICE HISTORY AROUND EXTREME DATE ==========")

window = prices.loc[
    previous_date - pd.Timedelta(days=5):
    date + pd.Timedelta(days=5),
    ticker
]

print(window.to_string())

