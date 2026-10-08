#!/usr/bin/env python3
"""Look up results for markets whose target date has passed and record them.

    python3 settle.py
"""

import datetime as dt

import kalshi
import store
from config import OUTCOMES_FILE


def settle():
    done = store.outcomes()
    today = dt.date.today()
    pending = {}
    for r in store.predictions():
        if r["ticker"] in done or r["ticker"] in pending:
            continue
        if dt.date.fromisoformat(r["target_date"]) < today:
            pending[r["ticker"]] = r
    n = 0
    for ticker in sorted(pending):
        try:
            result = kalshi.market_result(ticker)
        except Exception as e:
            print(f"{ticker}: lookup failed: {e}")
            continue
        if result is None:
            continue
        store.append(OUTCOMES_FILE, {
            "ticker": ticker,
            "series": pending[ticker]["series"],
            "target_date": pending[ticker]["target_date"],
            "result": result,
            "y": 1 if result == "yes" else 0,
            "settled_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        })
        n += 1
    print(f"settled {n} markets; {len(pending) - n} still pending")


if __name__ == "__main__":
    settle()
