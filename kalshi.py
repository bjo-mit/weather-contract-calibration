"""Read-only access to Kalshi's public market data. No account is needed."""

import datetime as dt
import re

from config import KALSHI_API
from http_util import get_json

_TICKER_RE = re.compile(r"^(?P<series>[A-Z]+)-(?P<yy>\d\d)(?P<mon>[A-Z]{3})(?P<dd>\d\d)-(?P<kind>[TB])(?P<strike>[\d.]+)$")
_MONTHS = {m: i for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}


def parse_ticker(ticker):
    """'KXHIGHNY-26OCT09-T76' -> (series, date, kind, strike). Returns None if the shape is unexpected."""
    m = _TICKER_RE.match(ticker)
    if not m:
        return None
    date = dt.date(2000 + int(m["yy"]), _MONTHS[m["mon"]], int(m["dd"]))
    return m["series"], date, m["kind"], float(m["strike"])


def open_markets(series_ticker, limit=200):
    """All open markets in a series, with the fields this project uses."""
    data = get_json(f"{KALSHI_API}/markets", {"series_ticker": series_ticker, "status": "open", "limit": limit})
    out = []
    for m in data.get("markets", []):
        parsed = parse_ticker(m["ticker"])
        if not parsed:
            continue
        _, date, _, _ = parsed
        out.append({
            "ticker": m["ticker"],
            "series": series_ticker,
            "target_date": date.isoformat(),
            "strike_type": m.get("strike_type"),       # greater | less | between
            "floor": m.get("floor_strike"),
            "cap": m.get("cap_strike"),
            "yes_bid": _dollars(m.get("yes_bid_dollars")),
            "yes_ask": _dollars(m.get("yes_ask_dollars")),
            "last": _dollars(m.get("last_price_dollars")),
            "close_time": m.get("close_time"),
        })
    return out


def market_result(ticker):
    """'yes', 'no' or None if the market has not settled."""
    data = get_json(f"{KALSHI_API}/markets/{ticker}")
    r = (data.get("market") or {}).get("result") or ""
    return r if r in ("yes", "no") else None


def _dollars(s):
    try:
        return float(s) if s is not None else None
    except (TypeError, ValueError):
        return None


def event_probability(strike_type, floor, cap, high_f):
    """Did a settled high temperature make this market pay YES? 1 or 0.

    Kalshi settles in whole degrees F. '>76' pays on 77 and up; '<69' on 68 and
    down; '75-76' on 75 or 76.
    """
    t = round(high_f)
    if strike_type == "greater":
        return 1 if t > floor else 0
    if strike_type == "less":
        return 1 if t < cap else 0
    if strike_type == "between":
        return 1 if floor <= t <= cap else 0
    raise ValueError(strike_type)
