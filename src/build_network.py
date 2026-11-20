
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

CORR_FILE = PROJECT_DIR / "outputs/tables/pearson_correlation_matrix.csv"
CONSTITUENTS_FILE = PROJECT_DIR / "data/processed_returns/nifty185_constituents.csv"

TABLE_DIR = PROJECT_DIR / "outputs/tables"
FIGURE_DIR = PROJECT_DIR / "outputs/figures"

# --------------------------------------------------
# 2. LOAD CORRELATION MATRIX
# --------------------------------------------------

corr = pd.read_csv(CORR_FILE, index_col=0)

# Calculate unique pair count correctly
upper = corr.where(
    np.triu(np.ones(corr.shape), k=1).astype(bool)
).stack()

print("Companies:", corr.shape[0])
print("Unique pairs:", len(upper))
print("Average pairwise correlation:", round(upper.mean(), 4))

# --------------------------------------------------
# 3. LOAD COMPANY SECTORS
# --------------------------------------------------

companies = pd.read_csv(CONSTITUENTS_FILE)

print("\nConstituent file columns:")
print(companies.columns.tolist())

# Identify ticker and sector columns
ticker_col = next(
    (c for c in companies.columns if c.lower() in ["symbol", "ticker"]),
    None
)

sector_col = next(
    (c for c in companies.columns if c.lower() in ["industry", "sector"]),
    None
)

if ticker_col is None or sector_col is None:
    raise ValueError("Could not identify ticker and sector columns.")

# Use the actual Yahoo Finance ticker from the constituent file
sector_map = dict(
    zip(
        companies["Yahoo_Ticker"].astype(str),
        companies["Industry"].astype(str)
    )
)

# --------------------------------------------------
# 4. BUILD NETWORK AT THRESHOLD 0.6
# --------------------------------------------------

THRESHOLD = 0.6

G = nx.Graph()
G.add_nodes_from(corr.columns)

# Add sector information to each node
for node in G.nodes():
    G.nodes[node]["sector"] = sector_map.get(node, "Unknown")

# Add edges when correlation >= 0.6
for i, stock1 in enumerate(corr.columns):
    for j in range(i + 1, len(corr.columns)):
        stock2 = corr.columns[j]
        correlation = corr.iloc[i, j]

        if correlation >= THRESHOLD:
            G.add_edge(
                stock1,
                stock2,
                weight=float(correlation)
            )

# --------------------------------------------------
# 5. NETWORK STATISTICS
# --------------------------------------------------

print("\n========== NETWORK SUMMARY ==========")
print("Threshold:", THRESHOLD)
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())
print("Density:", round(nx.density(G), 4))
print("Connected components:", nx.number_connected_components(G))

largest_component = max(
    nx.connected_components(G),
    key=len
)

print("Largest component size:", len(largest_component))

# Average degree
degrees = dict(G.degree())
print("Average degree:", round(np.mean(list(degrees.values())), 4))

# --------------------------------------------------
# 6. SAVE NETWORK FILES
# --------------------------------------------------

edge_data = nx.to_pandas_edgelist(G)
edge_data.to_csv(TABLE_DIR / "network_edges_r06.csv", index=False)

nx.write_graphml(G, TABLE_DIR / "nifty184_network_r06.graphml")

node_data = pd.DataFrame({
    "Ticker": list(G.nodes()),
    "Sector": [G.nodes[n]["sector"] for n in G.nodes()],
    "Degree": [G.degree(n) for n in G.nodes()]
})

node_data.to_csv(TABLE_DIR / "network_nodes_r06.csv", index=False)

# --------------------------------------------------
# 7. DRAW NETWORK
# --------------------------------------------------

plt.figure(figsize=(16, 12))

pos = nx.spring_layout(
    G,
    seed=42,
    k=0.35
)

sectors = sorted(set(
    nx.get_node_attributes(G, "sector").values()
))

sector_numbers = {
    sector: i for i, sector in enumerate(sectors)
}

node_colors = [
    sector_numbers[G.nodes[node]["sector"]]
    for node in G.nodes()
]

nx.draw_networkx_edges(
    G, pos,
    alpha=0.20,
    width=0.6
)

nx.draw_networkx_nodes(
    G, pos,
    node_color=node_colors,
    cmap=plt.cm.tab20,
    node_size=65
)

plt.title("Nifty 184 Stock Market Network (Correlation ≥ 0.6)")
plt.axis("off")
plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "nifty184_network_r06.png",
    dpi=300
)

plt.close()

print("\nNetwork files and visualization saved successfully.")

