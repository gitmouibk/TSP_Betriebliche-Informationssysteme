import pandas as pd

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
PATH = "data/distance_matrix_f1.xlsx"   # change if needed

# ------------------------------------------------------------
# 1) Load the distance matrix from Excel
# ------------------------------------------------------------
D = pd.read_excel(PATH).set_index("Label")

# Clean row/column labels to avoid mismatches from extra whitespace
D.index = D.index.astype(str).str.strip()
D.columns = D.columns.astype(str).str.strip()

# ------------------------------------------------------------
# 2) Define the route order FROM THE DATA ITSELF
# ------------------------------------------------------------
route = list(D.index)

# Safety check: ensure every route name is also a column in the matrix
missing_cols = [name for name in route if name not in D.columns]
if missing_cols:
    raise ValueError(
        "These circuits exist in the 'Label' column but not as matrix columns:\n"
        + "\n".join(missing_cols)
    )

# ------------------------------------------------------------
# Ask user: roundtrip or not
# ------------------------------------------------------------
roundtrip = input("Roundtrip? y/n [n]: ").strip().lower() == "y"

# ------------------------------------------------------------
# 3) Calculate distances in the given order
# ------------------------------------------------------------
legs = []
total = 0.0

for i in range(len(route) - 1):
    a = route[i]
    b = route[i + 1]
    dist = float(D.loc[a, b])
    legs.append((a, b, dist))
    total += dist

# Optionally add return leg (last -> first)
if roundtrip and len(route) >= 2:
    a = route[-1]
    b = route[0]
    dist = float(D.loc[a, b])
    legs.append((a, b, dist))
    total += dist

# ------------------------------------------------------------
# 4) Output results
# ------------------------------------------------------------
print("Route order (from Excel row order):")
print(" -> ".join(route))

print("\nLeg distances:")
for a, b, dist in legs:
    print(f"{a} -> {b}: {dist}")

print("\nTotal distance:", total)
