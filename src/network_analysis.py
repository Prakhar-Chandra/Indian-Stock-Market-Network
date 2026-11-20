
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# ==================================================
# 1. PROJECT PATHS AND SETTINGS
# ==================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

CORR_FILE = PROJECT_DIR / "outputs/tables/pearson_correlation_matrix.csv"
CONSTITUENTS_FILE = PROJECT_DIR / "data/processed_returns/nifty185_constituents.csv"

TABLE_DIR = PROJECT_DIR / "outputs/tables"
FIGURE_DIR = PROJECT_DIR / "outputs/figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

THRESHOLD = 0.6

# ==================================================
# 2. LOAD DATA
# ==================================================

corr = pd.read_csv(CORR_FILE, index_col=0)
companies = pd.read_csv(CONSTITUENTS_FILE)

sector_map = dict(
    zip(
        companies["Yahoo_Ticker"].astype(str),
        companies["Industry"].astype(str)
    )
)

print("Correlation matrix:", corr.shape)
print("Constituent records:", len(companies))

# Correct unique pair count
upper_values = corr.to_numpy()[
    np.triu_indices(len(corr), k=1)
]

print("Unique company pairs:", len(upper_values))
print("Average correlation:", round(upper_values.mean(), 4))

# ==================================================
# 3. CONSTRUCT NETWORK
# ==================================================

G = nx.Graph()

for ticker in corr.columns:
    G.add_node(
        ticker,
        sector=sector_map.get(ticker, "Unknown")
    )

for i, stock1 in enumerate(corr.columns):
    for j in range(i + 1, len(corr.columns)):
        stock2 = corr.columns[j]
        value = corr.iloc[i, j]

        if value >= THRESHOLD:
            G.add_edge(
                stock1,
                stock2,
                weight=float(value)
            )

print("\n========== NETWORK ==========")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())
print("Density:", round(nx.density(G), 4))
print("Connected components:", nx.number_connected_components(G))

# ==================================================
# 4. A. DEGREE DISTRIBUTION
# ==================================================

degrees = dict(G.degree())
degree_values = list(degrees.values())

degree_distribution = (
    pd.Series(degree_values)
    .value_counts()
    .sort_index()
)

degree_distribution = degree_distribution.rename_axis(
    "Degree"
).reset_index(name="Number_of_Companies")

degree_distribution.to_csv(
    TABLE_DIR / "degree_distribution.csv",
    index=False
)

# Linear scale
plt.figure(figsize=(9, 6))
plt.bar(
    degree_distribution["Degree"],
    degree_distribution["Number_of_Companies"]
)
plt.xlabel("Degree")
plt.ylabel("Number of Companies")
plt.title("Degree Distribution - Linear Scale")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "degree_distribution_linear.png", dpi=300)
plt.close()

# Log-log scale: omit zero values
positive_degree = degree_distribution[
    degree_distribution["Degree"] > 0
]

plt.figure(figsize=(9, 6))
plt.scatter(
    positive_degree["Degree"],
    positive_degree["Number_of_Companies"]
)
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Degree (log scale)")
plt.ylabel("Number of Companies (log scale)")
plt.title("Degree Distribution - Log-Log Scale")
plt.tight_layout()
plt.savefig(FIGURE_DIR / "degree_distribution_loglog.png", dpi=300)
plt.close()

# ==================================================
# 5. B. CENTRALITY MEASURES
# ==================================================

degree_centrality = nx.degree_centrality(G)
betweenness = nx.betweenness_centrality(G, normalized=True)

try:
    eigenvector = nx.eigenvector_centrality(
        G,
        max_iter=2000,
        tol=1e-8
    )
except nx.PowerIterationFailedConvergence:
    eigenvector = {node: 0 for node in G.nodes()}

centrality_df = pd.DataFrame({
    "Ticker": list(G.nodes()),
    "Sector": [G.nodes[n]["sector"] for n in G.nodes()],
    "Degree": [G.degree(n) for n in G.nodes()],
    "Degree_Centrality": [
        degree_centrality[n] for n in G.nodes()
    ],
    "Betweenness_Centrality": [
        betweenness[n] for n in G.nodes()
    ],
    "Eigenvector_Centrality": [
        eigenvector[n] for n in G.nodes()
    ]
})

centrality_df.to_csv(
    TABLE_DIR / "all_centrality_measures.csv",
    index=False
)

for measure in [
    "Degree_Centrality",
    "Betweenness_Centrality",
    "Eigenvector_Centrality"
]:
    top10 = centrality_df.sort_values(
        measure,
        ascending=False
    ).head(10)

    top10.to_csv(
        TABLE_DIR / f"top10_{measure.lower()}.csv",
        index=False
    )

    print(f"\nTop 10 by {measure}:")
    print(top10[["Ticker", "Sector", measure]].to_string(index=False))

# ==================================================
# 6. C. CLUSTERING COEFFICIENT
# ==================================================

average_clustering = nx.average_clustering(G)
local_clustering = nx.clustering(G)

print("\n========== CLUSTERING ==========")
print("Average clustering coefficient:", round(average_clustering, 4))

clustering_df = pd.DataFrame({
    "Ticker": list(G.nodes()),
    "Sector": [G.nodes[n]["sector"] for n in G.nodes()],
    "Local_Clustering": [
        local_clustering[n] for n in G.nodes()
    ]
})

clustering_df.to_csv(
    TABLE_DIR / "local_clustering_coefficients.csv",
    index=False
)

# ==================================================
# 7. D. SECTOR HOMOPHILY
# ==================================================

same_sector_edges = 0

for u, v in G.edges():
    if G.nodes[u]["sector"] == G.nodes[v]["sector"]:
        same_sector_edges += 1

if G.number_of_edges() > 0:
    same_sector_fraction = (
        same_sector_edges / G.number_of_edges()
    )
else:
    same_sector_fraction = 0

try:
    sector_assortativity = nx.attribute_assortativity_coefficient(
        G,
        "sector"
    )
except ZeroDivisionError:
    sector_assortativity = np.nan

print("\n========== SECTOR HOMOPHILY ==========")
print("Same-sector edges:", same_sector_edges)
print("Total edges:", G.number_of_edges())
print("Same-sector edge fraction:", round(same_sector_fraction, 4))
print("Sector assortativity:", round(sector_assortativity, 4))

sector_results = pd.DataFrame({
    "Measure": [
        "Same-sector edges",
        "Total edges",
        "Same-sector edge fraction",
        "Sector assortativity"
    ],
    "Value": [
        same_sector_edges,
        G.number_of_edges(),
        same_sector_fraction,
        sector_assortativity
    ]
})

sector_results.to_csv(
    TABLE_DIR / "sector_homophily.csv",
    index=False
)

# ==================================================
# 8. SAVE NETWORK SUMMARY
# ==================================================

summary = pd.DataFrame({
    "Measure": [
        "Nodes",
        "Edges",
        "Density",
        "Average degree",
        "Connected components",
        "Largest component size",
        "Average clustering coefficient"
    ],
    "Value": [
        G.number_of_nodes(),
        G.number_of_edges(),
        nx.density(G),
        np.mean(list(degrees.values())),
        nx.number_connected_components(G),
        max(map(len, nx.connected_components(G))),
        average_clustering
    ]
})

summary.to_csv(
    TABLE_DIR / "network_summary_r06.csv",
    index=False
)

print("\nAll network analysis files generated successfully.")

