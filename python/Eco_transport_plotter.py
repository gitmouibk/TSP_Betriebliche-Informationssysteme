import folium
from folium.plugins import PolyLineTextPath


class TransportTSPPlotter:
    """
    Visualizes a TSP route based on transport-aware optimization
    on a real-world map using OpenStreetMap (Folium).
    """

    MODE_COLORS = {
        "ship": "green",
        "truck": "orange",
        "plane": "red"
    }

    def __init__(self, circuit_metadata: dict):
        """
        Parameters
        ----------
        circuit_metadata : dict
            Metadata dictionary containing coordinates for each circuit.
        """
        self.meta = circuit_metadata

    def plot_route(self, route, output_file="TI_transport_tsp_route.html"):
        """
        Plot the given route on an interactive world map.

        Parameters
        ----------
        route : list[str]
            Ordered list of circuit names (roundtrip included).
        output_file : str
            Output HTML file name.
        """

        # Extract coordinates in route order
        coords = [self.meta[c]["coords"] for c in route]

        # Center map roughly at average location
        avg_lat = sum(c[0] for c in coords) / len(coords)
        avg_lon = sum(c[1] for c in coords) / len(coords)

        m = folium.Map(location=(avg_lat, avg_lon), zoom_start=2)

        line = folium.PolyLine(coords, weight=3, color="red").add_to(m)

        # Direction arrow (centered on route)
        PolyLineTextPath(
            line,
            "▶",
            repeat=False,
            center=True,
            offset=0,
            attributes={
                "fill": "red",
                "font-size": "18px",
                "font-weight": "bold"
            }
        ).add_to(m)

        # Add markers
        for i, c in enumerate(route[:-1], start=1):
            lat, lon = self.meta[c]["coords"]

            color = "green" if i == 1 else "blue"

            folium.Marker(
                location=(lat, lon),
                popup=f"{i}. {c}",
                tooltip=c,
                icon=folium.Icon(color=color, icon="flag"),
            ).add_to(m)

        m.save(output_file)

    def plot_route_with_modes(self, route, edges, output_file="TI_transport_tsp_route.html"):
        coords = {c: self.meta[c]["coords"] for c in route}

        avg_lat = sum(lat for lat, _ in coords.values()) / len(coords)
        avg_lon = sum(lon for _, lon in coords.values()) / len(coords)

        m = folium.Map(location=(avg_lat, avg_lon), zoom_start=2)

        # Draw colored edges
        for a, b, mode in edges:
            line = folium.PolyLine(
                locations=[coords[a], coords[b]],
                color=self.MODE_COLORS[mode],
                weight=4,
                tooltip=f"{a} → {b} ({mode})"
            ).add_to(m)

            # Direction arrow (centered on edge)
            PolyLineTextPath(
                line,
                "▶",
                repeat=False,
                center=True,
                offset=0,
                attributes={
                    "fill": self.MODE_COLORS[mode],
                    "font-size": "18px",
                    "font-weight": "bold"
                }
            ).add_to(m)

        # Markers
        for i, c in enumerate(route[:-1], start=1):
            lat, lon = coords[c]
            color = "green" if i == 1 else "blue"

            folium.Marker(
                location=(lat, lon),
                popup=f"{i}. {c}",
                icon=folium.Icon(color=color)
            ).add_to(m)

        m.save(output_file)