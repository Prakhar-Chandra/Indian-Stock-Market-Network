
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent

RETURNS_FILE = PROJECT_DIR / "data/processed_returns/nifty184_log_returns_clean.csv"
PRICES_FILE = PROJECT_DIR / "data/processed_returns/nifty185_clean_prices.csv"

returns = pd.read_csv(RETURNS_FILE, index_col=0, parse_dates=True)
prices = pd.read_csv(PRICES_FILE, index_col=0, parse_dates=True)

# Identify observations with absolute log return above 0.20
extreme = returns.stack()
extreme = extreme[extreme.abs() > 0.20]

results = []

for (date, ticker), log_return in extreme.items():

    if ticker not in prices.columns or date not in prices.index:
        continue

    position = prices.index.get_loc(date)

    if position == 0:
        continue

    previous_date = prices.index[position - 1]

    previous_price = prices.loc[previous_date, ticker]
    current_price = prices.loc[date, ticker]

    ordinary_return = np.exp(log_return) - 1

    results.append({
        "Date": date.date(),
        "Ticker": ticker,
        "Log_Return": round(log_return, 4),
        "Ordinary_Return_%": round(ordinary_return * 100, 2),
        "Previous_Price": round(previous_price, 2),
        "Current_Price": round(current_price, 2)
    })

result_df = pd.DataFrame(results)
result_df = result_df.sort_values("Log_Return")

output = PROJECT_DIR / "outputs/tables/extreme_event_audit.csv"
result_df.to_csv(output, index=False)

print("\nExtreme observations investigated:", len(result_df))
print("\nLargest negative movements:")
print(result_df.head(10).to_string(index=False))

print("\nLargest positive movements:")
print(result_df.tail(5).to_string(index=False))

print("\nFull audit saved at:")
print(output)

