import pandas as pd

# Path to the Excel file that contains the distance matrix
PATH = "data/distance_matrix_f1.xlsx"

# -------------------------------------------------------------------
# LOAD AND CLEAN THE DISTANCE MATRIX
# -------------------------------------------------------------------

# Read the Excel file and set the "Label" column as the index (row names)
D = pd.read_excel(PATH).set_index("Label")

# Ensure row labels are clean strings (remove leading/trailing spaces)
D.index = D.index.astype(str).str.strip()

# Ensure column labels are clean strings (remove leading/trailing spaces)
D.columns = D.columns.astype(str).str.strip()

# -------------------------------------------------------------------
# CREATE NUMBERED MAPPING FOR CIRCUITS (1..N)
# -------------------------------------------------------------------

# Store circuit names in the same order as in the Excel file
names = list(D.index)

# Create a dictionary: number -> circuit name
num_to_name = {i: name for i, name in enumerate(names, start=1)}

# Print mapping so user knows which number corresponds to which circuit
print("\n# ===== CIRCUIT NUMBER MAPPING (enter ONLY numbers) =====")
for i, name in num_to_name.items():
    print(f"# {i:2d}: {name}")
print("# =====================================================\n")

# -------------------------------------------------------------------
# PARSE USER INPUT FOR CIRCUIT SELECTION
# -------------------------------------------------------------------
def parse_selection(inp: str, max_n: int):
    """
    Converts user input into a list of circuit numbers.

    Allows:
    - "ALL" or "*"
    - space-separated numbers: 1 3 5
    - comma-separated numbers: 1,3,5
    """

    s = inp.strip().upper()

    # Select all circuits
    if s in {"ALL", "*"}:
        return list(range(1, max_n + 1))

    # Allow commas and/or whitespace
    tokens = s.replace(",", " ").split()
    if not tokens:
        raise ValueError("Empty input.")

    nums = []
    for t in tokens:
        if not t.isdigit():
            raise ValueError(f"Non-numeric token: '{t}'")

        k = int(t)
        if not (1 <= k <= max_n):
            raise ValueError(f"Out of range: {k} (must be 1..{max_n})")

        nums.append(k)

    # Remove duplicates while preserving order
    seen = set()
    out = []
    for k in nums:
        if k not in seen:
            out.append(k)
            seen.add(k)

    return out

# -------------------------------------------------------------------
# INSERTION HEURISTIC (CHEAPEST INSERTION) - ONLY INSERTION
# -------------------------------------------------------------------
def cheapest_insertion_tsp(D: pd.DataFrame, nodes: list[str], roundtrip: bool = True):
    """
    Cheapest Insertion Heuristic.

    Builds a tour by repeatedly inserting the node that creates the smallest
    increase in total tour length.

    D         : distance matrix restricted to 'nodes'
    nodes     : list of circuit names to visit
    roundtrip : if True -> closed tour (ends where it starts)
               if False -> open path (tour opened at the cheapest break)
    """

    if len(nodes) < 2:
        raise ValueError("Need at least 2 circuits.")

    # Helper: compute length of a path (consecutive legs)
    def path_length(path: list[str]) -> float:
        return sum(float(D.loc[a, b]) for a, b in zip(path[:-1], path[1:]))

    # ----------------------------------------------------------------
    # 1) Initialize a small cycle:
    #    Start at nodes[0], connect to its nearest neighbor, and close the cycle.
    # ----------------------------------------------------------------
    start = nodes[0]
    others = [n for n in nodes if n != start]

    # Pick the second node as the nearest to start (only for initialization)
    second = D.loc[start, others].astype(float).idxmin()

    # Start with a closed cycle: start -> second -> start
    tour = [start, second, start]

    # Nodes not yet inserted into the tour
    unvisited = set(nodes)
    unvisited.remove(start)
    unvisited.remove(second)

    # ----------------------------------------------------------------
    # 2) Repeatedly insert the node/position with the minimum extra cost
    # ----------------------------------------------------------------
    while unvisited:
        best_x = None
        best_pos = None
        best_delta = float("inf")

        # Try inserting each unvisited node x into every edge (a -> b)
        for x in unvisited:
            for i in range(len(tour) - 1):
                a = tour[i]
                b = tour[i + 1]

                # extra cost if we replace a->b with a->x->b
                delta = float(D.loc[a, x]) + float(D.loc[x, b]) - float(D.loc[a, b])

                if delta < best_delta:
                    best_delta = delta
                    best_x = x
                    best_pos = i + 1

        # Insert the best candidate
        tour.insert(best_pos, best_x)
        unvisited.remove(best_x)

    # tour is a closed cycle (last element equals first element)
    if roundtrip:
        return tour, path_length(tour)

    # ----------------------------------------------------------------
    # 3) If NOT roundtrip: open the cycle at the best break
    #    We remove exactly one edge to get an open path with minimal loss.
    # ----------------------------------------------------------------
    best_break_i = None
    best_break_cost = float("inf")

    # Find the edge with the smallest distance to remove
    for i in range(len(tour) - 1):
        a = tour[i]
        b = tour[i + 1]
        cost = float(D.loc[a, b])
        if cost < best_break_cost:
            best_break_cost = cost
            best_break_i = i

    # Build open path by starting after the break and going around the cycle
    cycle_nodes = tour[:-1]  # remove repeated start at end
    open_path = cycle_nodes[best_break_i + 1 :] + cycle_nodes[: best_break_i + 1]

    return open_path, path_length(open_path)

# -------------------------------------------------------------------
# USER SELECTION LOOP (VALIDATED INPUT)
# -------------------------------------------------------------------
while True:
    try:
        raw = input(
            f"Enter circuit numbers (e.g. 1 3 7 or 1,3,7) or ALL [1..{len(names)}]: "
        )
        selected_nums = parse_selection(raw, len(names))

        if len(selected_nums) < 2:
            print("Please select at least 2 circuits.")
            continue

        break
    except ValueError as e:
        print(f"Invalid selection: {e}")

# Convert selected numbers to actual circuit names (in the order entered)
nodes = [num_to_name[i] for i in selected_nums]

# Ask user whether route should return to the start
roundtrip = (input("Roundtrip? y/n [y]: ").strip().lower() != "n")

# -------------------------------------------------------------------
# SOLVE TSP FOR THE SELECTED CIRCUITS (INSERTION HEURISTIC)
# -------------------------------------------------------------------

# Extract sub-matrix for selected circuits only
sub = D.loc[nodes, nodes]

# Run cheapest insertion heuristic
path, total = cheapest_insertion_tsp(sub, nodes, roundtrip=roundtrip)

# -------------------------------------------------------------------
# OUTPUT RESULTS
# -------------------------------------------------------------------
print("\nSelected circuits:")
print(", ".join(nodes))

print("\nRoute:")
print(" -> ".join(path))

print("Total distance:", total)
