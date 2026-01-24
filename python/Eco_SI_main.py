"""
Eco-aware Traveling Salesman Problem (TSP)
------------------------------------------

This script solves a Traveling Salesman Problem using a Successive Insertion
heuristic (cheapest insertion) on a transport-weighted cost matrix.

Geographic distances are taken from an Excel file.
Transport costs are derived from an eco-logistics model that accounts for
different transport modes (truck, ship, plane).

The resulting route is evaluated, analyzed, and visualized on a world map.
"""

from Eco_transport_model import TransportModel, interactive_eco_setup
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
# Successive Insertion heuristic for the TSP (cheapest insertion)
# -------------------------------------------------------------------
# The tour is built incrementally by inserting each new circuit at the
# position that causes the smallest increase in total tour cost.
def si_tsp(D, nodes, roundtrip=True):
    # Start with a trivial subtour
    tour = [nodes[0], nodes[1], nodes[0]]

    for k in nodes[2:]:
        best_cost = float("inf")
        best_pos = None

        # Try inserting k at every possible position
        for i in range(len(tour) - 1):
            a = tour[i]
            b = tour[i + 1]

            delta = (
                float(D.loc[a, k])
                + float(D.loc[k, b])
                - float(D.loc[a, b])
            )

            if delta < best_cost:
                best_cost = delta
                best_pos = i + 1

        tour.insert(best_pos, k)

    if not roundtrip:
        tour.pop()  # remove return to start

    # Compute total cost
    total = 0.0
    for i in range(len(tour) - 1):
        total += float(D.loc[tour[i], tour[i + 1]])

    return tour, total

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
# Solve TSP using Successive Insertion on eco-weighted costs
# -------------------------------------------------------------------
path, total = si_tsp(sub, nodes, roundtrip)

# -------------------------------------------------------------------
# Evaluation: pure geographic distance (baseline comparison)
# -------------------------------------------------------------------
# This metric ignores all transport weighting and reflects the actual
# physical distance traveled along the route.
pure_distance = 0.0
for i in range(len(path) - 1):
    pure_distance += float(D.loc[path[i], path[i + 1]])

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