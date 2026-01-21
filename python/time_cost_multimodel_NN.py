import pandas as pd
import sys
import math
import os

# -------------------------------------------------------------------
# 1. SYSTEM SETUP
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

    # We let the user decide if they care more about speed (Time) or money (Cost)
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

    # Basic transport settings that we found from our research
    print("\n--- 3. TRANSPORT PARAMETERS ---")
    p_speed = get_val("Plane Time Factor (0.15 = 85% faster than road)", 0.15)
    p_fix = get_val("Plane Fixed Cost (Base fees)", 250000)
    p_var = get_val("Plane Variable Cost (Rate per km)", 80)
    t_fix = get_val("Truck Fixed Cost (Base fees)", 2000)
    t_var = get_val("Truck Variable Cost (Rate per km)", 3)

    return w_dist, w_cost, norm, p_speed, p_fix, p_var, t_fix, t_var

# Getting everything ready for the rest of the script
(W_DIST, W_COST, COST_NORMALIZER, 
 P_SPEED_MULT, P_FIX, P_VAR, 
 T_FIX, T_VAR) = interactive_setup()

T_SPEED_MULT = 1.0  
FILENAME = "distance_matrix_f1_extended.xlsx"
PATH = os.path.join(os.getcwd(), FILENAME)

# -------------------------------------------------------------------
# 2. LOADING DATA
# -------------------------------------------------------------------
try:
    # We load the Excel and make sure the "Label" is our main index
    raw_df = pd.read_excel(PATH).set_index("Label")
    regions_map = raw_df["Region"].to_dict()
    D = raw_df.drop(columns=["Region"])
    # Cleaning up any weird spaces in the circuit names
    D.index = D.index.astype(str).str.strip()
    D.columns = D.columns.astype(str).str.strip()
    names = list(D.index)
except Exception as e:
    print(f"\nERROR: Could not load file '{FILENAME}': {e}")
    sys.exit()

# -------------------------------------------------------------------
# 3. THE "BRAIN" (LOGISTICS LOGIC)
# -------------------------------------------------------------------
def get_metrics(dist, reg1, reg2):
    # TRUCK: Simple linear cost based on distance
    t_cost = T_FIX + (dist * T_VAR)
    t_score = (W_DIST * dist * T_SPEED_MULT) + (W_COST * (t_cost / COST_NORMALIZER))

    # PLANE: We use a Logarithm so longer flights get 'cheaper' per km.
    # We also added the "Fuel Ferry Paradox" here (dist ** 2.5). 
    # This makes ultra-long flights super expensive because of the extra fuel weight.
    log_c = math.log(dist + 1) * 500 * P_VAR
    fuel_penalty = 0.000001 * (dist ** 2.5) 
    p_cost = P_FIX + log_c + fuel_penalty
    
    # This score is what the algorithm uses to pick the best transport mode
    p_score = (W_DIST * dist * P_SPEED_MULT) + (W_COST * (p_cost / COST_NORMALIZER))
    
    # This is our 'Continent Guard' - if the regions don't match, we force a plane.
    if reg1 != reg2:
        return p_cost, p_score, "PLANE"
    
    # Otherwise, we just pick whichever mode has the better (lower) score
    return (t_cost, t_score, "TRUCK") if t_score <= p_score else (p_cost, p_score, "PLANE")

# -------------------------------------------------------------------
# 4. THE ALGORITHM (NEAREST NEIGHBOUR)
# -------------------------------------------------------------------
def nn_tsp(D, nodes, regions_map, roundtrip=True):
    # This algorithm is 'greedy' - it just keeps looking for the next 
    # closest race based on our strategic scores.
    unvisited = list(nodes[1:])
    path = [nodes[0]]
    modes_used = []
    total_dist, total_cost = 0.0, 0.0
    t_count, p_count = 0, 0
    cur = nodes[0]
    
    while unvisited:
        best_next, min_score = None, float('inf')
        for nxt in unvisited:
            d = float(D.loc[cur, nxt])
            # We call our logistics 'brain' for every possible next step
            c, s, m = get_metrics(d, regions_map[cur], regions_map[nxt])
            if s < min_score:
                min_score, best_next = s, nxt
                step_dist, step_cost, step_mode = d, c, m
        
        # Updating all our totals as we move through the season
        total_dist += step_dist
        total_cost += step_cost
        if step_mode == "PLANE": p_count += 1
        else: t_count += 1
        path.append(best_next)
        modes_used.append(step_mode)
        unvisited.remove(best_next)
        cur = best_next
        
    # If the user wants to end where they started (roundtrip)
    if roundtrip:
        d = float(D.loc[cur, nodes[0]])
        c, s, m = get_metrics(d, regions_map[cur], regions_map[nodes[0]])
        total_dist += d
        total_cost += c
        if m == "PLANE": p_count += 1
        else: t_count += 1
        path.append(nodes[0])
        modes_used.append(m)
        
    return path, modes_used, total_dist, total_cost, t_count, p_count

# -------------------------------------------------------------------
# 5. USER INTERFACE (PICKING RACES)
# -------------------------------------------------------------------
print("\n# ===== CIRCUIT SELECTION =====")
for i, name in enumerate(names, start=1):
    print(f"# {i:2d}: {name}")
print("# =============================\n")

# Letting the user pick all races or just a few specific ones
n_input = input("How many circuits? (or 'all'): ").strip().lower()
if n_input == 'all':
    nodes = list(names)
else:
    try:
        n = int(n_input)
        nodes = [names[int(input(f"Circuit {i+1}: "))-1] for i in range(n)]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit()

rt_choice = (input("Roundtrip? y/n [y]: ").strip().lower() != "n")

# Running the actual calculation
res_p, res_m, td, tc, tc_n, pc_n = nn_tsp(D, nodes, regions_map, rt_choice)

# -------------------------------------------------------------------
# 6. FINAL RESULTS 
# -------------------------------------------------------------------
print("\n" + "="*60)
print("EXTENDED LOGISTICS REPORT (NEAREST NEIGHBOUR)")
print("="*60)
print("SYSTEM PARAMETERS (Active for this run):")
print(f"  Optimization Priority: Time ({W_DIST*100:.0f}%) vs. Budget ({W_COST*100:.0f}%)")
print(f"  Normalizer: {COST_NORMALIZER} (Balances Euros and Kilometers)")

print(f"  Truck: Baseline Speed (100% perceived distance)")
print(f"  Plane: High-Speed Mode ({P_SPEED_MULT*100:.0f}% perceived distance)")
print(f"         -> This represents a {(1-P_SPEED_MULT)*100:.0f}% reduction in travel time.")

print(f"\n  Financials:")
print(f"  - Truck: €{T_FIX} Fixed + €{T_VAR}/km")
print(f"  - Plane: €{P_FIX} Fixed + €{P_VAR}/km (subject to non-linear scaling)")
print("-" * 60)

print("ROUTE DETAILS:")
for i in range(len(res_m)):
    print(f"  {res_p[i]} -> {res_p[i+1]} ({res_m[i]})")
    
print("-" * 60)
print(f"TOTAL DISTANCE: {td:,.0f} km")
print(f"TOTAL COST:     € {tc:,.2f}")
print(f"LOGISTICS STATS: {tc_n}x Truck, {pc_n}x Plane")
print("="*60)
