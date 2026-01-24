# Eco_transport_data.py
# Static metadata describing logistical properties of selected F1 circuits.
# This dataset assigns each circuit to a continent and specifies whether
# the circuit can be reasonably accessed by sea transport.

CIRCUIT_METADATA = {

    # =================
    # EUROPE
    # =================
    "Autodromo Enzo e Dino Ferrari": {
        "continent": "Europe",
        "coastal": False,
        "coords": (44.3439, 11.7167)
    },
    "Circuit de Monaco": {
        "continent": "Europe",
        "coastal": True,
        "coords": (43.7347, 7.4206)
    },
    "Circuit de Barcelona-Catalunya": {
        "continent": "Europe",
        "coastal": True,
        "coords": (41.5700, 2.2611)
    },
    "Red Bull Ring": {
        "continent": "Europe",
        "coastal": False,
        "coords": (47.2197, 14.7647)
    },
    "Silverstone Circuit": {
        "continent": "Europe",
        "coastal": False,
        "coords": (52.0786, -1.0169)
    },
    "Circuit de Spa-Francorchamps": {
        "continent": "Europe",
        "coastal": False,
        "coords": (50.4372, 5.9714)
    },
    "Hungaroring": {
        "continent": "Europe",
        "coastal": False,
        "coords": (47.5789, 19.2486)
    },
    "Circuit Park Zandvoort": {
        "continent": "Europe",
        "coastal": True,
        "coords": (52.3889, 4.5409)
    },
    "Autodromo Nazionale Monza": {
        "continent": "Europe",
        "coastal": False,
        "coords": (45.6156, 9.2811)
    },

    # =================
    # ASIA
    # =================
    "Shanghai International Circuit": {
        "continent": "Asia",
        "coastal": True,
        "coords": (31.3389, 121.2197)
    },
    "Suzuka International Racing Course": {
        "continent": "Asia",
        "coastal": False,
        "coords": (34.8431, 136.5419)
    },
    "Bahrain International Circuit": {
        "continent": "Asia",
        "coastal": True,
        "coords": (26.0325, 50.5106)
    },
    "Jeddah Corniche Circuit": {
        "continent": "Asia",
        "coastal": True,
        "coords": (21.6319, 39.1044)
    },
    "Marina Bay Street Circuit": {
        "continent": "Asia",
        "coastal": True,
        "coords": (1.2914, 103.8644)
    },
    "Losail International Circuit": {
        "continent": "Asia",
        "coastal": True,
        "coords": (25.4900, 51.4542)
    },
    "Yas Marina Circuit": {
        "continent": "Asia",
        "coastal": True,
        "coords": (24.4672, 54.6031)
    },

    # Azerbaijan is inland as Caspian Sea can't reasonably be considered coastal for our purposes
    "Baku City Circuit": {
        "continent": "Asia",
        "coastal": False,
        "coords": (40.3725, 49.8533)
    },

    # =================
    # NORTH AMERICA
    # =================
    "Miami International Autodrome": {
        "continent": "North America",
        "coastal": True,
        "coords": (25.9581, -80.2389)
    },
    "Circuit Gilles-Villeneuve": {
        "continent": "North America",
        "coastal": True,
        "coords": (45.5006, -73.5228)
    },
    "Circuit of The Americas (COTA)": {
        "continent": "North America",
        "coastal": False,
        "coords": (30.1328, -97.6411)
    },
    "Autódromo Hermanos Rodríguez": {
        "continent": "North America",
        "coastal": False,
        "coords": (19.4042, -99.0907)
    },
    "Las Vegas Strip Circuit": {
        "continent": "North America",
        "coastal": False,
        "coords": (36.1147, -115.1728)
    },

    # =================
    # SOUTH AMERICA
    # =================
    "Interlagos (Autódromo José Carlos Pace)": {
        "continent": "South America",
        "coastal": True,
        "coords": (-23.7036, -46.6997)
    },

    # =================
    # OCEANIA
    # =================
    "Albert Park Circuit": {
        "continent": "Oceania",
        "coastal": True,
        "coords": (-37.8497, 144.9680)
    }
}