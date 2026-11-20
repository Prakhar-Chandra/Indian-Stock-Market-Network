
import pandas as pd
import yfinance as yf
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw_prices"

PRICE_FILE = RAW_DIR / "nifty200_adjusted_close.csv"
FAILED_FILE = RAW_DIR / "failed_tickers.csv"
QUALITY_FILE = RAW_DIR / "data_quality_report.csv"

ticker = "AUROPHARMA.NS"

print("Recovering missing stock:", ticker)

# Retry individual download
for attempt in range(1, 4):

    try:
        data = yf.download(
            ticker,
            start="2023-11-01",
            end="2026-11-01",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
            timeout=30
        )

        if data.empty:
            raise ValueError("No historical data returned")

        # Extract adjusted Close prices
        if isinstance(data.columns, pd.MultiIndex):
            prices = data["Close"]

            if isinstance(prices, pd.DataFrame):
                prices = prices.iloc[:, 0]

        else:
            prices = data["Close"]

        prices = prices.rename(ticker)
        prices.index.name = "Date"

        if prices.dropna().empty:
            raise ValueError("Price series is empty")

        # Merge recovered data with existing dataset
        existing = pd.read_csv(
            PRICE_FILE,
            index_col="Date",
            parse_dates=True
        )

        existing[ticker] = prices
        existing = existing.sort_index()

        existing.to_csv(PRICE_FILE)

        # Update failed ticker list
        failed = pd.read_csv(FAILED_FILE)

        failed = failed[
            failed["Failed_Ticker"] != ticker
        ]

        failed.to_csv(FAILED_FILE, index=False)

        # Update data quality report
        quality = pd.read_csv(QUALITY_FILE)

        quality.loc[
            quality["Yahoo_Ticker"] == ticker,
            "Download_Status"
        ] = "Successful"

        quality.loc[
            quality["Yahoo_Ticker"] == ticker,
            "Observations"
        ] = prices.notna().sum()

        quality.to_csv(QUALITY_FILE, index=False)

        print("\nRecovery successful!")
        print("Ticker:", ticker)
        print("Observations:", prices.notna().sum())

        break

    except Exception as error:

        print(f"Attempt {attempt} failed:", error)

        if attempt < 3:
            time.sleep(10)

else:
    print("\nRecovery unsuccessful.")
    print("We will investigate the download issue.")

