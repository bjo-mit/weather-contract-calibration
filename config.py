"""Cities, forecast models and model parameters.

Each Kalshi daily high-temperature series settles on one weather station.
The coordinates below are the usual NWS stations for each city; Kalshi's
rules page (https://weather.com/kalshi) is the authority, and any
station mismatch shows up as a bias in the calibration report.
"""

CITIES = {
    "KXHIGHNY":   {"name": "New York (Central Park)",  "lat": 40.7789, "lon": -73.9692,  "tz": "America/New_York"},
    "KXHIGHCHI":  {"name": "Chicago (Midway)",         "lat": 41.7868, "lon": -87.7522,  "tz": "America/Chicago"},
    "KXHIGHMIA":  {"name": "Miami (MIA)",              "lat": 25.7959, "lon": -80.2870,  "tz": "America/New_York"},
    "KXHIGHAUS":  {"name": "Austin (Camp Mabry)",      "lat": 30.3208, "lon": -97.7604,  "tz": "America/Chicago"},
    "KXHIGHDEN":  {"name": "Denver (DEN)",             "lat": 39.8561, "lon": -104.6737, "tz": "America/Denver"},
    "KXHIGHLAX":  {"name": "Los Angeles (LAX)",        "lat": 33.9425, "lon": -118.4081, "tz": "America/Los_Angeles"},
    "KXHIGHPHIL": {"name": "Philadelphia (PHL)",       "lat": 39.8721, "lon": -75.2411,  "tz": "America/New_York"},
}

# Open-Meteo ensemble models. GEFS has 31 members, ECMWF IFS 51.
ENSEMBLE_MODELS = ["gfs025", "ecmwf_ifs025"]

# Standard deviation (degrees F) of the Gaussian kernel placed on each
# ensemble member. It stands in for the error between a model grid cell and
# the settlement station. 2.0 F is a starting guess; the calibration report
# is how you find out whether it is too wide or too narrow.
KERNEL_SD_F = 2.0

KALSHI_API = "https://api.elections.kalshi.com/trade-api/v2"
OPEN_METEO_ENSEMBLE = "https://ensemble-api.open-meteo.com/v1/ensemble"

DATA_DIR = "data"
PREDICTIONS_FILE = "predictions.jsonl"
OUTCOMES_FILE = "outcomes.jsonl"

# Polite spacing between HTTP requests, seconds.
REQUEST_PAUSE = 0.25
