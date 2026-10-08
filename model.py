"""Turn ensemble members into a probability for one Kalshi market.

Each member is a point forecast of the daily high. Place a Gaussian with
standard deviation KERNEL_SD_F on each member (grid-to-station error), then
average the probability that the event occurs. Settlement is in whole degrees,
so the thresholds sit on the half-degree.
"""

import math
import statistics

from config import KERNEL_SD_F


def _phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def prob_event(members, strike_type, floor, cap, sd=KERNEL_SD_F):
    """P(market pays YES) under the smoothed ensemble."""
    if not members:
        return None
    total = 0.0
    for x in members:
        if strike_type == "greater":          # high > floor  <=> high >= floor + 1
            p = 1.0 - _phi((floor + 0.5 - x) / sd)
        elif strike_type == "less":           # high < cap    <=> high <= cap - 1
            p = _phi((cap - 0.5 - x) / sd)
        elif strike_type == "between":        # floor <= high <= cap
            p = _phi((cap + 0.5 - x) / sd) - _phi((floor - 0.5 - x) / sd)
        else:
            raise ValueError(strike_type)
        total += p
    return total / len(members)


def summary(members):
    if not members:
        return {"n": 0, "mean": None, "sd": None}
    return {
        "n": len(members),
        "mean": round(statistics.fmean(members), 2),
        "sd": round(statistics.pstdev(members), 2) if len(members) > 1 else 0.0,
    }
