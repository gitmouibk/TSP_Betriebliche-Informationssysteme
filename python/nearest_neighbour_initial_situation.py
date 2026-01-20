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
# NEAREST-NEIGHBOR TSP HEURISTIC
# -------------------------------------------------------------------
def nn_tsp(D, nodes, roundtrip=True):
    """
    Solves a TSP approximately using the nearest-neighbor heuristic.

    D         : pandas DataFrame (distance matrix)
    nodes     : list of circuit names to visit
    roundtrip : if True, return to starting circuit
    """

    # All nodes except the starting one are initially unvisited
    unvisited = set(nodes[1:])

    # Start path at the first node
    path = [nodes[0]]
    total = 0.0
    cur = nodes[0]

    # While there are still nodes left to visit
    while unvisited:
        # Choose the nearest unvisited neighbor (deterministic tie-break)
        candidates = sorted(unvisited)
        nxt = D.loc[cur, candidates].astype(float).idxmin()

        # Add distance to total
        total += float(D.loc[cur, nxt])

        # Update path and current node
        path.append(nxt)
        unvisited.remove(nxt)
        cur = nxt

    # If roundtrip is enabled, return to starting node
    if roundtrip:
        total += float(D.loc[cur, nodes[0]])
        path.append(nodes[0])

    return path, total

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

    # Normalize input
    s = inp.strip().upper()

    # If user wants all circuits, return full range
    if s in {"ALL", "*"}:
        return list(range(1, max_n + 1))

    # Replace commas with spaces, then split
    tokens = s.replace(",", " ").split()

    if not tokens:
        raise ValueError("Empty input.")

    nums = []
    for t in tokens:
        # Ensure token is numeric
        if not t.isdigit():
            raise ValueError(f"Non-numeric token: '{t}'")

        k = int(t)

        # Ensure number is within valid range
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
# USER SELECTION LOOP (VALIDATED INPUT)
# -------------------------------------------------------------------
while True:
    try:
        raw = input(
            f"Enter circuit numbers (e.g. 1 3 7 or 1,3,7) or ALL [1..{len(names)}]: "
        )

        # Convert input to a list of valid circuit numbers
        selected_nums = parse_selection(raw, len(names))

        # TSP requires at least 2 nodes
        if len(selected_nums) < 2:
            print("Please select at least 2 circuits.")
            continue

        break
    except ValueError as e:
        print(f"Invalid selection: {e}")

# Convert selected numbers to actual circuit names
nodes = [num_to_name[i] for i in selected_nums]

# Ask user whether route should return to the start
roundtrip = (input("Roundtrip? y/n [y]: ").strip().lower() != "n")

# -------------------------------------------------------------------
# SOLVE TSP FOR THE SELECTED CIRCUITS
# -------------------------------------------------------------------

# Extract sub-matrix for selected circuits only
sub = D.loc[nodes, nodes]

# Run nearest-neighbor TSP
path, total = nn_tsp(sub, nodes, roundtrip)

# -------------------------------------------------------------------
# OUTPUT RESULTS
# -------------------------------------------------------------------

print("\nSelected circuits:")
print(", ".join(nodes))

print("\nRoute:")
print(" -> ".join(path))
print("Total distance:", total)