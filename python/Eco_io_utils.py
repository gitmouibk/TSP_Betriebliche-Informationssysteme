from pathlib import Path
import pandas as pd

def load_distance_matrix():
    """
    Load and clean the geographic distance matrix from Excel.

    Returns
    -------
    pandas.DataFrame
        Cleaned distance matrix with circuit names as index and columns.
    """
    base_dir = Path(__file__).resolve().parent
    project_root = base_dir.parent
    path = project_root / "data" / "distance_matrix_f1.xlsx"

    D = pd.read_excel(path).set_index("Label")
    D.index = D.index.astype(str).str.strip()
    D.columns = D.columns.astype(str).str.strip()

    return D


def build_circuit_index(D):
    """
    Build numeric index mappings for user-friendly circuit selection.
    Returns tuple (names, num_to_name)
    """
    names = list(D.index)
    num_to_name = {str(i + 1): name for i, name in enumerate(names)}

    print("\n# ===== CIRCUIT NUMBER MAPPING (enter ONLY numbers) =====")
    for i, name in enumerate(names, start=1):
        print(f"# {i:2d}: {name}")
    print("# =====================================================\n")

    return names, num_to_name


def select_circuits(names, num_to_name):
    """
    Interactive circuit selection by number or name.

    Returns
    -------
    list[str]
        Ordered list of selected circuit names.
    """
    raw_n = input(
        "How many circuits? (Press Enter or type 'all' for all circuits): "
    ).strip()

    if raw_n == "" or raw_n.lower() == "all":
        return names.copy()

    n = int(raw_n)
    nodes = []

    for i in range(n):
        while True:
            x = input(f"Circuit {i+1} (number or name): ").strip()

            if x in num_to_name:
                nodes.append(num_to_name[x])
                break

            if x in names:
                nodes.append(x)
                break

            print("Not found. Enter a valid number (1–N) or copy/paste a name.")

    return nodes


def ask_roundtrip():
    return input("Roundtrip? y/n [y]: ").strip().lower() != "n"


def analyze_transport_modes(path, D, tm):
    """
    Analyze transport mode usage along a route.

    Parameters
    ----------
    path : list[str]
        Ordered TSP route.
    D : pandas.DataFrame
        Geographic distance matrix.
    tm : TransportModel
        Transport model instance.

    Returns
    -------
    tuple
        edges : list of (from, to, mode)
        stats : dict with counts and distances per transport mode
    """
    edges = []

    stats = {
        "truck": {"count": 0, "km": 0.0},
        "ship": {"count": 0, "km": 0.0},
        "plane": {"count": 0, "km": 0.0},
    }

    for i in range(len(path) - 1):
        a = path[i]
        b = path[i + 1]
        d = float(D.loc[a, b])

        _, mode = tm.transport_cost_with_mode(a, b, d)
        edges.append((a, b, mode))

        stats[mode]["count"] += 1
        stats[mode]["km"] += d

    return edges, stats


def report_results(path, pure_distance, total_cost, stats):
    """
    Print route, distance metrics, and transport mode summary.
    """
    print("\nRoute:")
    print(" -> ".join(path))

    print("\nResults:")
    print(f"Pure geographic distance: {pure_distance:.1f} km")
    print(f"Transport-weighted cost:  {total_cost:.1f}")

    avg_factor = total_cost / pure_distance if pure_distance > 0 else 0
    print(f"Average transport factor: {avg_factor:.2f}")

    print("\nTRANSPORT MODE SUMMARY")
    print("-" * 40)
    for m, s in stats.items():
        print(f"{m.upper():6s}: {s['count']:2d} legs, {s['km']:8.0f} km")
