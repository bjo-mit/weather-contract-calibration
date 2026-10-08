"""Ensemble daily-high forecasts from Open-Meteo. Free, no key."""

from config import ENSEMBLE_MODELS, OPEN_METEO_ENSEMBLE
from http_util import get_json


def ensemble_highs(lat, lon, tz, days=4):
    """Return {date: [member highs in F]} for the next `days` days.

    Every ensemble member of every model in ENSEMBLE_MODELS is one sample.
    The control run (the column without a member number) is included too.
    """
    data = get_json(OPEN_METEO_ENSEMBLE, {
        "latitude": lat, "longitude": lon,
        "daily": "temperature_2m_max",
        "temperature_unit": "fahrenheit",
        "timezone": tz,
        "forecast_days": days,
        "models": ",".join(ENSEMBLE_MODELS),
    })
    daily = data["daily"]
    dates = daily["time"]
    out = {d: [] for d in dates}
    for key, values in daily.items():
        if not key.startswith("temperature_2m_max"):
            continue
        for d, v in zip(dates, values):
            if v is not None:
                out[d].append(float(v))
    return out
