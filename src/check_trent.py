
from pathlib import Path
import yfinance as yf

data = yf.download(
    "TRENT.NS",
    start="2025-12-26",
    end="2026-01-07",
    auto_adjust=False,
    actions=True,
    progress=False
)

print(data.to_string())

