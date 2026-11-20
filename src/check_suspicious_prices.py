
import yfinance as yf
import pandas as pd

tickers = ["MOTILALOFS.NS", "VEDL.NS", "TMPV.NS"]

dates = {
    "MOTILALOFS.NS": ("2023-12-26", "2024-01-05"),
    "VEDL.NS": ("2026-04-27", "2026-05-05"),
    "TMPV.NS": ("2025-10-09", "2025-10-20"),
}

for ticker in tickers:
    start, end = dates[ticker]

    print(f"\n========== {ticker} ==========")

    data = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=False,
        actions=True,
        progress=False
    )

    columns = ["Close", "Adj Close", "Stock Splits", "Dividends"]
    available = [c for c in columns if c in data.columns]

    print(data[available].to_string())

