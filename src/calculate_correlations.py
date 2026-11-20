
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed_returns"
    / "nifty184_log_returns_clean.csv"
)

OUTPUT_DIR = PROJECT_DIR / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# Load cleaned returns
returns = pd.read_csv(
    INPUT_FILE,
    index_col=0,
    parse_dates=True
)

print("Returns dataset:", returns.shape)

# Calculate Pearson correlation matrix
correlation_matrix = returns.corr(method="pearson")

# Save correlation matrix
correlation_matrix.to_csv(
    TABLE_DIR / "pearson_correlation_matrix.csv"
)

print("\nCorrelation matrix calculated.")
print("Matrix shape:", correlation_matrix.shape)

# Extract unique pairwise correlations
upper_triangle = np.triu(
    np.ones(correlation_matrix.shape),
    k=1
).astype(bool)

correlations = correlation_matrix.where(upper_triangle).stack()

print("\nUnique pairwise correlations:", len(correlations))
print("Average correlation:", correlations.mean())
print("Minimum correlation:", correlations.min())
print("Maximum correlation:", correlations.max())

# Save correlation statistics
statistics = pd.DataFrame({
    "Measure": [
        "Mean correlation",
        "Median correlation",
        "Minimum correlation",
        "Maximum correlation",
        "Standard deviation"
    ],
    "Value": [
        correlations.mean(),
        correlations.median(),
        correlations.min(),
        correlations.max(),
        correlations.std()
    ]
})

statistics.to_csv(
    TABLE_DIR / "correlation_statistics.csv",
    index=False
)

# Plot correlation heatmap
plt.figure(figsize=(18, 15))

sns.heatmap(
    correlation_matrix,
    cmap="coolwarm",
    center=0,
    xticklabels=False,
    yticklabels=False
)

plt.title("Pearson Correlation Heatmap - Nifty 184")
plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "correlation_heatmap.png",
    dpi=300
)

plt.close()

print("\nCorrelation heatmap saved.")
print("All correlation files generated successfully.")

