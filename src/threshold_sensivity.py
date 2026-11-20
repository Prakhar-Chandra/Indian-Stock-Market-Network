
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

CORR_FILE = (
    PROJECT_DIR
    / "outputs"
    / "tables"
    / "pearson_correlation_matrix.csv"
)

TABLE_DIR = PROJECT_DIR / "outputs" / "tables"
FIGURE_DIR = PROJECT_DIR / "outputs" / "figures"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD CORRELATION MATRIX
# --------------------------------------------------

corr = pd.read_csv(CORR_FILE, index_col=0)

# Thresholds required by the assignment
thresholds = [0.5, 0.6, 0.7, 0.8]

results = []

# --------------------------------------------------
# 3. BUILD NETWORK AT EACH THRESHOLD
# --------------------------------------------------

for threshold in thresholds:

    G = nx.Graph()

    G.add_nodes_from(corr.columns)

    for i, stock1 in enumerate(corr.columns):

        for j in range(i + 1, len(corr.columns)):

            stock2 = corr.columns[j]
            correlation = corr.iloc[i, j]

            if correlation >= threshold:

                G.add_edge(stock1, stock2)

    # Number of edges
    edges = G.number_of_edges()

    # Density
    density = nx.density(G)

    # Connected components
    components = list(nx.connected_components(G))

    # Largest connected component
    largest_component = max(
        components,
        key=len
    )

    giant_size = len(largest_component)

    # Average path length calculated within
    # the largest connected component
    giant_graph = G.subgraph(largest_component).copy()

    if giant_size > 1:
        avg_path_length = nx.average_shortest_path_length(
            giant_graph
        )
    else:
        avg_path_length = 0

    results.append({
        "Threshold": threshold,
        "Nodes": G.number_of_nodes(),
        "Edges": edges,
        "Density": density,
        "Connected_Components": len(components),
        "Giant_Component_Size": giant_size,
        "Average_Path_Length_Giant": avg_path_length
    })

    print(f"\nThreshold: {threshold}")
    print("Edges:", edges)
    print("Connected components:", len(components))
    print("Giant component size:", giant_size)
    print("Average path length:", round(avg_path_length, 4))

# --------------------------------------------------
# 4. SAVE RESULTS
# --------------------------------------------------

results_df = pd.DataFrame(results)

results_df.to_csv(
    TABLE_DIR / "threshold_sensitivity.csv",
    index=False
)

print("\n========== THRESHOLD COMPARISON ==========")
print(results_df.to_string(index=False))

# --------------------------------------------------
# 5. PLOT EDGE COUNT
# --------------------------------------------------

plt.figure(figsize=(8, 5))

plt.plot(
    results_df["Threshold"],
    results_df["Edges"],
    marker="o"
)

plt.xlabel("Correlation Threshold")
plt.ylabel("Number of Edges")
plt.title("Threshold vs Number of Edges")
plt.xticks(thresholds)
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "threshold_vs_edges.png",
    dpi=300
)

plt.close()

# --------------------------------------------------
# 6. PLOT GIANT COMPONENT SIZE
# --------------------------------------------------

plt.figure(figsize=(8, 5))

plt.plot(
    results_df["Threshold"],
    results_df["Giant_Component_Size"],
    marker="o"
)

plt.xlabel("Correlation Threshold")
plt.ylabel("Giant Component Size")
plt.title("Threshold vs Giant Component Size")
plt.xticks(thresholds)
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "threshold_vs_giant_component.png",
    dpi=300
)

plt.close()

# --------------------------------------------------
# 7. PLOT AVERAGE PATH LENGTH
# --------------------------------------------------

plt.figure(figsize=(8, 5))

plt.plot(
    results_df["Threshold"],
    results_df["Average_Path_Length_Giant"],
    marker="o"
)

plt.xlabel("Correlation Threshold")
plt.ylabel("Average Path Length")
plt.title("Threshold vs Average Path Length")
plt.xticks(thresholds)
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "threshold_vs_average_path_length.png",
    dpi=300
)

plt.close()

print("\nThreshold sensitivity analysis completed.")
print("All tables and figures saved successfully.")

