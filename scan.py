#!/usr/bin/env python3
"""One pass: for every open daily-high market in each city, log the model
probability next to the market price. Run it on a schedule (hourly is plenty).

    python3 scan.py            # all cities
    python3 scan.py KXHIGHNY   # one series
"""

import datetime as dt
import sys

import kalshi
import forecast
import model
import store
from config import CITIES, PREDICTIONS_FILE


def scan(series_list):
    now = dt.datetime.now(dt.timezone.utc)
    n = 0
    for series in series_list:
        city = CITIES[series]
        try:
            markets = kalshi.open_markets(series)
        except Exception as e:  # keep going for the other cities
            print(f"{series}: market fetch failed: {e}", file=sys.stderr)
            continue
        if not markets:
            continue
        try:
            highs = forecast.ensemble_highs(city["lat"], city["lon"], city["tz"])
        except Exception as e:
            print(f"{series}: forecast fetch failed: {e}", file=sys.stderr)
            continue
        for m in markets:
            members = highs.get(m["target_date"])
            if not members:
                continue
            p = model.prob_event(members, m["strike_type"], m["floor"], m["cap"])
            s = model.summary(members)
            bid, ask = m["yes_bid"], m["yes_ask"]
            mid = round((bid + ask) / 2, 4) if bid is not None and ask is not None else None
            target_midday = dt.datetime.fromisoformat(m["target_date"]).replace(hour=12, tzinfo=dt.timezone.utc)
            store.append(PREDICTIONS_FILE, {
                "ts": now.isoformat(timespec="seconds"),
                "ticker": m["ticker"],
                "series": series,
                "target_date": m["target_date"],
                "lead_hours": round((target_midday - now).total_seconds() / 3600, 1),
                "strike_type": m["strike_type"],
                "floor": m["floor"],
                "cap": m["cap"],
                "p_model": round(p, 4),
                "members": s["n"],
                "ens_mean": s["mean"],
                "ens_sd": s["sd"],
                "yes_bid": bid,
                "yes_ask": ask,
                "mid": mid,
                "edge": round(p - mid, 4) if mid is not None else None,
            })
            n += 1
    print(f"{now.isoformat(timespec='seconds')} logged {n} predictions")


if __name__ == "__main__":
    args = sys.argv[1:]
    scan(args if args else list(CITIES))
