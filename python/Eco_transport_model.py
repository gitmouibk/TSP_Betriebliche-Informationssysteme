# Eco_transport_model.py

class TransportModel:
# Defines simplified logistical rules for transporting
# Formula 1 equipment between circuits.

# It determines which transport modes are allowed between two circuits
# and computes weighted transport costs based on distance.

    # Relative cost / emission factors
    FACTORS = {
        "truck": 1.0,
        "ship": 0.6,
        "plane": 3.0
    }

    def __init__(self, metadata: dict, max_truck_distance=1500, factors=None):
        """
        Parameters:
        metadata (dict):
            Circuit metadata containing continent and coastal information.
        max_truck_distance (float):
            Maximum distance (km) for truck transport.
        """
        self.meta = metadata
        self.max_truck_distance = max_truck_distance

        # Transport weighting factors (eco model)
        self.FACTORS = factors or {
            "truck": 1.0,
            "ship": 0.6,
            "plane": 3.0
        }

    def allowed_modes(self, a: str, b: str, distance: float):
        """
        Determine allowed transport modes between two circuits.
        """
        modes = []

        A = self.meta[a]
        B = self.meta[b]

        # Truck: same continent + short distance
        if (
            A["continent"] == B["continent"]
            and distance <= self.max_truck_distance
        ):
            modes.append("truck")

        # Ship: different continents + both coastal
        if (
            A["continent"] != B["continent"]
            and A["coastal"]
            and B["coastal"]
        ):
            modes.append("ship")

        # Plane is always allowed
        modes.append("plane")

        return modes

    def transport_cost(self, a: str, b: str, distance: float):
        """
        Compute the minimal transport cost between two circuits.
        """
        modes = self.allowed_modes(a, b, distance)
        return min(distance * self.FACTORS[m] for m in modes)

    def transport_cost_with_mode(self, a, b, distance):
        modes = self.allowed_modes(a, b, distance)

        best_mode = min(modes, key=lambda m: distance * self.FACTORS[m])
        best_cost = distance * self.FACTORS[best_mode]

        return best_cost, best_mode

    def build_cost_matrix(self, distance_matrix):
        """
        Build a transport-weighted cost matrix from a pure distance matrix.
        And returns Matrix of geographic distances in kilometers.
        """

        cost = distance_matrix.astype(float).copy()

        for i in distance_matrix.index:
            for j in distance_matrix.columns:
                if i == j:
                    cost.loc[i, j] = 0.0
                else:
                    d = float(distance_matrix.at[i, j])
                    cost.loc[i, j] = self.transport_cost(i, j, d)

        return cost


def interactive_eco_setup():
    """
    Interactive configuration of eco transport factors.
    """
    print("\n" + "=" * 60)
    print("ECO LOGISTICS MODEL SETUP")
    print("Press ENTER to keep default values")
    print("=" * 60)

    def ask(prompt, default):
        val = input(f"{prompt} [{default}]: ").strip()
        try:
            return float(val) if val else default
        except ValueError:
            print("Invalid input, using default.")
            return default

    print("\n--- TRANSPORT WEIGHTING FACTORS ---")
    truck = ask("Truck factor (baseline)", 1.0)
    ship = ask("Ship factor (lower = greener)", 0.6)
    plane = ask("Plane factor (higher = worse)", 3.0)

    print("\n--- MODEL ASSUMPTIONS ---")
    print("• Truck: same continent and limited distance")
    print("• Intercontinental transport allowed only between coastal circuits")
    print("• Plane: always allowed")

    return {
        "truck": truck,
        "ship": ship,
        "plane": plane
    }