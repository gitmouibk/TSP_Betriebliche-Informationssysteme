"""
Eco-aware Traveling Salesman Problem (TSP)
------------------------------------------

This script solves a Traveling Salesman Problem using a Nearest Neighbour
heuristic on a transport-weighted cost matrix.

Geographic distances are taken from an Excel file.
Transport costs are derived from an eco-logistics model that accounts for
different transport modes (truck, ship, plane).

The resulting route is evaluated, analyzed, and visualized on a world map.
"""

from Eco_transport_model import TransportModel
from Eco_transport_model import interactive_eco_setup
from Eco_transport_data import CIRCUIT_METADATA
from Eco_transport_plotter import TransportTSPPlotter
from Eco_io_utils import (
    load_distance_matrix,
    build_circuit_index,
    select_circuits,
    ask_roundtrip,
    analyze_transport_modes,
    report_results,
)

# -------------------------------------------------------------------
# Load geographic distance matrix and select circuits
# -------------------------------------------------------------------
D = load_distance_matrix()
names, num_to_name = build_circuit_index(D)
nodes = select_circuits(names, num_to_name)
roundtrip = ask_roundtrip()

# -------------------------------------------------------------------
# Nearest Neighbour heuristic for the TSP (greedy approach)
# -------------------------------------------------------------------
# Starting from an initial circuit, the algorithm always selects the
# nearest unvisited circuit based on the provided cost matrix.
def nn_tsp(D, nodes, roundtrip=True):
    unvisited = set(nodes[1:])
    path = [nodes[0]]
    total = 0.0
    cur = nodes[0]
    while unvisited:
        nxt = D.loc[cur, list(unvisited)].idxmin()
        total += float(D.loc[cur, nxt])
        path.append(nxt)
        unvisited.remove(nxt)
        cur = nxt
    if roundtrip:
        total += float(D.loc[cur, nodes[0]])
        path.append(nodes[0])
    return path, total

# -------------------------------------------------------------------
# Eco logistics model configuration
# -------------------------------------------------------------------
# Transport weighting factors and assumptions are defined interactively.
eco_factors = interactive_eco_setup()
tm = TransportModel(CIRCUIT_METADATA, factors=eco_factors)

# -------------------------------------------------------------------
# Construction of transport-weighted cost matrix
# -------------------------------------------------------------------
# The eco model is applied to the geographic distance matrix to obtain
# a cost matrix suitable for optimization.
sub = tm.build_cost_matrix(D.loc[nodes, nodes])

# -------------------------------------------------------------------
# Solve TSP using Nearest Neighbour on eco-weighted costs
# -------------------------------------------------------------------
path, total = nn_tsp(sub, nodes, roundtrip)

# -------------------------------------------------------------------
# Evaluation: pure geographic distance (baseline comparison)
# -------------------------------------------------------------------
# This metric ignores all transport weighting and reflects the actual
# physical distance traveled along the route.
pure_distance = 0.0
for i in range(len(path) - 1):
    a = path[i]
    b = path[i + 1]
    pure_distance += float(D.loc[a, b])

# -------------------------------------------------------------------
# Transport mode analysis and result reporting
# -------------------------------------------------------------------
edges, stats = analyze_transport_modes(path, D, tm)
report_results(path, pure_distance, total, stats)

# -------------------------------------------------------------------
# Visualization
# -------------------------------------------------------------------
# The route is visualized on a world map with transport-mode-specific
# coloring and directional arrows.
plotter = TransportTSPPlotter(CIRCUIT_METADATA)
plotter.plot_route_with_modes(path, edges)
