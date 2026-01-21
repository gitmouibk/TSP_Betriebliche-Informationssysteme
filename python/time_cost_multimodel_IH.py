import pandas as pd
import sys
import math
import os

# -------------------------------------------------------------------
# 1. SETTING UP THE SYSTEM
# -------------------------------------------------------------------
# NOTE FOR PROFESSOR: All the parameters below like weights and costs can be 
# changed manually in the terminal when you run the code. 
# Except for the "Fuel Ferry Paradox" which has to be manually changed in the code itself because we thought 
# it to be a little overkill to add as an input option too
def interactive_setup():
    print("\n" + "="*60)
    print("LOGISTICS SYSTEM SETUP: Press ENTER to use [Fair Default]")
    print("="*60)
    
    def get_val(prompt, default):
        val = input(f"{prompt} [{default}]: ").strip()
        try:
            return float(val) if val else default
        except ValueError:
            print(f"  Invalid input. Using default: {default}")
            return default

    # We allow the user to balance if they care more about Time or the Budget
    print("\n--- 1. STRATEGIC WEIGHTS ---")
    w_dist = get_val("Weight for Time/Distance (0.0 to 1.0)", 0.5)
    w_cost = get_val("Weight for Budget/Cost (0.0 to 1.0)", 0.5)
    
    # This part stops the high Euro costs from 
    # drowning out the kilometer distances in the math.
    print("\n--- 2. MATHEMATICAL NORMALIZER ---")
    print("Logic: Balances different units (km vs €) so weights work fairly.")
    print("Example: Without this, a €300,000 cost would mathematically make a 1,000 km distance completely irrelevant")
    print("         because 0.5 * 1000 (km) = 500 while 0.5 * 300.000 (€) = 150.000.        total score = 500 (km) + 150.000 (€) = 150.500") 
    print("         With this normalizer (300,000 / 500) = 600. Then 0.5 * 600 = 300.       with normalizer: 500 (km) + 300 (€) = 800")
    norm = get_val("Cost Normalizer Value", 500)

    # These are the baseline costs we found during our research
    print("\n--- 3. TRANSPORT PARAMETERS ---")
    p_speed = get_val("Plane Time Factor (0.15 = 85% faster than road)", 0.15)
    p_fix = get_val("Plane Fixed Cost (Base fees)", 250000)
    p_var = get_val("Plane Variable Cost (Rate per km)", 80)
    t_fix = get_val("Truck Fixed Cost (Base fees)", 2000)
    t_var = get_val("Truck Variable Cost (Rate per km)", 3)

    return w_dist, w_cost, norm, p_speed, p_fix, p_var, t_fix, t_var

# Initializing all the parameters for the rest of the script
(W_DIST, W_COST, COST_NORMALIZER, 
 P_SPEED_MULT, P_FIX, P_VAR, 
 T_FIX, T_VAR) = interactive_setup()

T_SPEED_MULT = 1.0  
FILENAME = "distance_matrix_f1_extended.xlsx"
PATH = os.path.join(os.getcwd(), FILENAME)

# -------------------------------------------------------------------
# 2. LOADING OUR DATA
# -------------------------------------------------------------------
try:
    # We load the excel and set the 'Label' column as our index
    raw_df = pd.read_excel(PATH).set_index("Label")
    regions_map = raw_df["Region"].to_dict()
    D = raw_df.drop(columns=["Region"])
    # Cleaning up names so there are no accidental spaces
    D.index = D.index.astype(str).str.strip()
    D.columns = D.columns.astype(str).str.strip()
    names = list(D.index)
except Exception as e:
    print(f"\nERROR: Could not load file '{FILENAME}': {e}")
    sys.exit()

# -------------------------------------------------------------------
# 3. THE LOGISTICS BRAIN (SCORING)
# -------------------------------------------------------------------
def get_metrics(dist, reg1, reg2):
    # TRUCK: Costs scale linearly with distance
    t_cost = T_FIX + (dist * T_VAR)
    t_score = (W_DIST * dist * T_SPEED_MULT) + (W_COST * (t_cost / COST_NORMALIZER))

    # PLANE: We use Logarithmic Tapering for distance and a "Fuel Paradox" 
    # penalty for ultra-long trips using the exponent (dist ** 2.5).
    log_c = math.log(dist + 1) * 500 * P_VAR
    fuel_penalty = 0.000001 * (dist ** 2.5)
    p_cost = P_FIX + log_c + fuel_penalty
    
    # We combine 'Time' (speed mult) and 'Cost' (divided by normalizer)
    p_score = (W_DIST * dist * P_SPEED_MULT) + (W_COST * (p_cost / COST_NORMALIZER))
    
    # CONTINENT GUARD: If the race moves between regions, we force a plane.
    if reg1 != reg2:
        return p_cost, p_score, "PLANE"
    
    # Otherwise, the algorithm picks the cheapest/fastest mode based on score
    return (t_cost, t_score, "TRUCK") if t_score <= p_score else (p_cost, p_score, "PLANE")

# -------------------------------------------------------------------
# 4. THE ALGORITHM: CHEAPEST INSERTION
# -------------------------------------------------------------------
def insertion_tsp(nodes, roundtrip=True):
    # This algorithm is smarter than Nearest Neighbor. Instead of just picking 
    # the next city, it tries to fit each city into the existing loop 
    # where it causes the least amount of "extra" distance and cost.
    
    # 1. Starting the loop with the first two cities
    start = nodes[0]
    others = [n for n in nodes if n != start]
    
    best_init_neighbor = None
    min_init_score = float('inf')
    for candidate in others:
        d = float(D.loc[start, candidate])
        _, s, _ = get_metrics(d, regions_map[start], regions_map[candidate])
        if s < min_init_score:
            min_init_score, best_init_neighbor = s, candidate
            
    tour = [start, best_init_neighbor, start]
    unvisited = [n for n in nodes if n not in tour[:-1]]

    # 2. Main Loop: Adding cities one by one into the 'best' spot
    while unvisited:
        best_city, best_pos, min_delta = None, -1, float('inf')
        
        for x in unvisited:
            for i in range(len(tour) - 1):
                a, b = tour[i], tour[i+1]
                
                # We check the cost of adding city X between cities A and B
                _, s_ax, _ = get_metrics(float(D.loc[a, x]), regions_map[a], regions_map[x])
                _, s_xb, _ = get_metrics(float(D.loc[x, b]), regions_map[x], regions_map[b])
                _, s_ab, _ = get_metrics(float(D.loc[a, b]), regions_map[a], regions_map[b])
                
                # The 'Delta' is how much the total loop score increases
                delta = s_ax + s_xb - s_ab
                if delta < min_delta:
                    min_delta, best_city, best_pos = delta, x, i + 1
        
        tour.insert(best_pos, best_city)
        unvisited.remove(best_city)

    # 3. If the user doesn't want a roundtrip, we 'break' the loop at 
    # its most expensive point to create an open path.
    if not roundtrip:
        best_break_i, best_break_score = -1, float('inf')
        for i in range(len(tour) - 1):
            d = float(D.loc[tour[i], tour[i+1]])
            _, s, _ = get_metrics(d, regions_map[tour[i]], regions_map[tour[i+1]])
            if s < best_break_score:
                best_break_score, best_break_i = s, i
        
        cycle_nodes = tour[:-1]
        tour = cycle_nodes[best_break_i + 1:] + cycle_nodes[:best_break_i + 1]
    
    return tour

# -------------------------------------------------------------------
# 5. RUNNING THE CALCULATION
# -------------------------------------------------------------------
print("\n# ===== CIRCUIT NUMBER MAPPING =====")
for i, name in enumerate(names, start=1):
    print(f"# {i:2d}: {name}")
print("# ==================================\n")

n_input = input("How many circuits? (or 'all'): ").strip().lower()
if n_input == 'all':
    nodes = list(names)
else:
    try:
        n = int(n_input)
        nodes = [names[int(input(f"Circuit {i+1}: "))-1] for i in range(n)]
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        sys.exit()

rt_choice = (input("Roundtrip? y/n [y]: ").strip().lower() != "n")

# Solving the season path
res_path = insertion_tsp(nodes, roundtrip=rt_choice)

# -------------------------------------------------------------------
# 6. PRINTING THE FINAL REPORT
# -------------------------------------------------------------------
print("\n" + "="*60)
print("EXTENDED LOGISTICS REPORT (INSERTION HEURISTIC)")
print("="*60)
# We display exactly what parameters were used to get these results
print(f"  Optimization Priority: Time ({W_DIST*100:.0f}%) vs. Budget ({W_COST*100:.0f}%)")
print(f"  Normalizer: {COST_NORMALIZER}")

print(f"  Truck: Baseline Speed (100% distance)")
print(f"  Plane: High-Speed Mode ({P_SPEED_MULT*100:.0f}% perceived distance)")
print(f"         -> This represents a {(1-P_SPEED_MULT)*100:.0f}% reduction in travel time.")

print(f"\n  Financials:")
print(f"  - Truck: €{T_FIX} Fixed + €{T_VAR}/km")
print(f"  - Plane: €{P_FIX} Fixed + €{P_VAR}/km (non-linear scaling)")
print("-" * 60)

print("ROUTE DETAILS:")
total_d, total_c, tc_n, pc_n = 0, 0, 0, 0
for i in range(len(res_path)-1):
    d = float(D.loc[res_path[i], res_path[i+1]])
    cost, _, mode = get_metrics(d, regions_map[res_path[i]], regions_map[res_path[i+1]])
    print(f"  {res_path[i]} -> {res_path[i+1]} ({mode})")
    total_d += d
    total_c += cost
    if mode == "PLANE": pc_n += 1
    else: tc_n += 1

print("-" * 60)
print(f"TOTAL DISTANCE: {total_d:,.0f} km")
print(f"TOTAL COST:     € {total_c:,.2f}")
print(f"LOGISTICS STATS: {tc_n}x Truck, {pc_n}x Plane")
print("="*60)