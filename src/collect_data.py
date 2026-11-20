
# ============================================================
# NETWORK SCIENCE PROJECT
# Phase 2: Nifty 200 Data Collection
# ============================================================

import time
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf


# ------------------------------------------------------------
# 1. PROJECT PATHS AND RESEARCH PARAMETERS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw_prices"

RAW_DIR.mkdir(parents=True, exist_ok=True)

CONSTITUENT_URL = (
    "https://www.niftyindices.com/IndexConstituent/"
    "ind_nifty200list.csv"
)

START_DATE = "2023-11-01"

# Yahoo Finance treats the end date as exclusive.
# Therefore, 1 November includes data through 31 October.
END_DATE = "2026-11-01"

BATCH_SIZE = 20
MAX_RETRIES = 3


# ------------------------------------------------------------
# 2. DOWNLOAD OFFICIAL NIFTY 200 CONSTITUENTS
# ------------------------------------------------------------

def download_constituents():

    print("\nDownloading Nifty 200 constituent list...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        CONSTITUENT_URL,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    from io import StringIO

    df = pd.read_csv(StringIO(response.text))

    # Remove accidental spaces in column names
    df.columns = df.columns.str.strip()

    required_columns = [
        "Company Name",
        "Industry",
        "Symbol"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Required columns missing: {missing}"
        )

    df["Symbol"] = df["Symbol"].astype(str).str.strip()
    df["Company Name"] = (
        df["Company Name"].astype(str).str.strip()
    )
    df["Industry"] = (
        df["Industry"].astype(str).str.strip()
    )

    # Remove invalid symbols and duplicates
    df = df.dropna(subset=["Symbol"])
    df = df[df["Symbol"] != ""]
    df = df.drop_duplicates(subset=["Symbol"])

    # Generate Yahoo Finance ticker symbols
    df["Yahoo_Ticker"] = df["Symbol"] + ".NS"

    output_file = DATA_DIR / "nifty200_constituents.csv"

    df.to_csv(output_file, index=False)

    print("Constituent file saved:", output_file)
    print("Number of unique companies:", len(df))

    return df


# ------------------------------------------------------------
# 3. DOWNLOAD HISTORICAL ADJUSTED CLOSING PRICES
# ------------------------------------------------------------

def download_prices(tickers):

    print("\nStarting historical price downloads...")

    all_prices = pd.DataFrame()
    successful_tickers = []
    failed_tickers = []

    for start in range(0, len(tickers), BATCH_SIZE):

        batch = tickers[start:start + BATCH_SIZE]

        print(
            f"\nDownloading batch "
            f"{start // BATCH_SIZE + 1}: "
            f"{len(batch)} companies"
        )

        batch_data = None

        for attempt in range(1, MAX_RETRIES + 1):

            try:

                downloaded = yf.download(
                    tickers=batch,
                    start=START_DATE,
                    end=END_DATE,
                    interval="1d",
                    auto_adjust=True,
                    group_by="column",
                    progress=False,
                    threads=True,
                    timeout=30
                )

                if downloaded is not None and not downloaded.empty:

                    # Extract adjusted Close prices.
                    # With auto_adjust=True, Close is adjusted.
                    if isinstance(downloaded.columns, pd.MultiIndex):

                        if "Close" in downloaded.columns.get_level_values(0):
                            batch_data = downloaded["Close"]

                        elif "Close" in downloaded.columns.get_level_values(1):
                            batch_data = downloaded.xs(
                                "Close",
                                axis=1,
                                level=1
                            )

                    elif "Close" in downloaded.columns:

                        batch_data = downloaded[["Close"]]
                        batch_data.columns = [batch[0]]

                    if batch_data is not None:
                        break

            except Exception as error:

                print(
                    f"Attempt {attempt} failed: {error}"
                )

            if attempt < MAX_RETRIES:
                time.sleep(5 * attempt)

        if batch_data is None:

            print("Batch download failed:", batch)
            failed_tickers.extend(batch)
            continue

        # Make sure all requested ticker columns exist
        batch_data = batch_data.reindex(columns=batch)

        for ticker in batch:

            series = batch_data[ticker].dropna()

            if not series.empty:

                all_prices[ticker] = series
                successful_tickers.append(ticker)

            else:

                failed_tickers.append(ticker)
                print("No usable data:", ticker)

        time.sleep(2)

    return all_prices, successful_tickers, failed_tickers


# ------------------------------------------------------------
# 4. MAIN EXECUTION
# ------------------------------------------------------------

def main():

    print("=" * 55)
    print("NIFTY 200 STOCK MARKET DATA COLLECTION")
    print("=" * 55)

    constituents = download_constituents()

    tickers = constituents["Yahoo_Ticker"].tolist()

    print("\nTotal tickers to download:", len(tickers))

    prices, successful, failed = download_prices(tickers)

    # Sort observations chronologically
    prices = prices.sort_index()

    # Save raw historical price data
    price_file = RAW_DIR / "nifty200_adjusted_close.csv"

    prices.to_csv(price_file, index_label="Date")

    # Save failed ticker list
    failed_file = RAW_DIR / "failed_tickers.csv"

    pd.DataFrame({
        "Failed_Ticker": failed
    }).to_csv(failed_file, index=False)

    # Generate data quality report
    quality = constituents[
        ["Company Name", "Industry", "Symbol", "Yahoo_Ticker"]
    ].copy()

    quality["Download_Status"] = quality["Yahoo_Ticker"].apply(
        lambda ticker: (
            "Successful" if ticker in successful
            else "Failed"
        )
    )

    quality["Observations"] = quality["Yahoo_Ticker"].apply(
        lambda ticker: (
            int(prices[ticker].notna().sum())
            if ticker in prices.columns
            else 0
        )
    )

    quality_file = RAW_DIR / "data_quality_report.csv"

    quality.to_csv(quality_file, index=False)

    # Print final summary
    print("\n" + "=" * 55)
    print("DATA COLLECTION SUMMARY")
    print("=" * 55)

    print("Companies in constituent list:", len(constituents))
    print("Successful downloads:", len(successful))
    print("Failed downloads:", len(failed))
    print("Trading observations:", len(prices))
    print("Date range:", prices.index.min(), "to", prices.index.max())

    print("\nSaved files:")
    print(price_file)
    print(failed_file)
    print(quality_file)

    print("\nDATA COLLECTION COMPLETED")


if __name__ == "__main__":
    main()

