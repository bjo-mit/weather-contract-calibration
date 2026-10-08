#!/usr/bin/env python3
"""Score the model against the market on settled contracts.

    python3 report.py              # all settled predictions
    python3 report.py --first      # only the first snapshot of each market
    python3 report.py --last       # only the last snapshot before close

Brier score: mean (p - y)^2; lower is better; 0.25 is a coin flip at p=0.5.
"""

import sys
from collections import defaultdict

import store


def brier(pairs):
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs) if pairs else None


def select(preds, mode):
    if mode == "all":
        return preds
    by_ticker = {}
    for r in preds:
        cur = by_ticker.get(r["ticker"])
        if cur is None or (mode == "first" and r["ts"] < cur["ts"]) or (mode == "last" and r["ts"] > cur["ts"]):
            by_ticker[r["ticker"]] = r
    return list(by_ticker.values())


def main(mode):
    outcomes = store.outcomes()
    preds = [r for r in store.predictions() if r["ticker"] in outcomes]
    preds = select(preds, mode)
    if not preds:
        print("no settled predictions yet")
        return
    model_pairs = [(r["p_model"], outcomes[r["ticker"]]["y"]) for r in preds]
    market_pairs = [(r["mid"], outcomes[r["ticker"]]["y"]) for r in preds if r["mid"] is not None]
    print(f"settled predictions: {len(preds)} ({mode} snapshot); with a market quote: {len(market_pairs)}")
    print(f"Brier  model: {brier(model_pairs):.4f}   market mid: {brier(market_pairs) if market_pairs else float('nan'):.4f}")

    print("\nCalibration (model probability bucket -> observed frequency):")
    buckets = defaultdict(list)
    for p, y in model_pairs:
        buckets[min(int(p * 10), 9)].append(y)
    for b in sorted(buckets):
        ys = buckets[b]
        print(f"  {b/10:.1f}-{(b+1)/10:.1f}: n={len(ys):4d}  observed={sum(ys)/len(ys):.2f}")

    print("\nBy city:")
    by_city = defaultdict(list)
    for r in preds:
        by_city[r["series"]].append((r["p_model"], outcomes[r["ticker"]]["y"]))
    for s in sorted(by_city):
        print(f"  {s:11s} n={len(by_city[s]):4d}  Brier={brier(by_city[s]):.4f}")

    print("\nBy lead time:")
    by_lead = defaultdict(list)
    for r in preds:
        h = r["lead_hours"]
        band = "same day, after noon" if h < 0 else "<12h" if h < 12 else "12-36h" if h < 36 else "36-60h" if h < 60 else "60h+"
        by_lead[band].append((r["p_model"], outcomes[r["ticker"]]["y"]))
    for band in ("same day, after noon", "<12h", "12-36h", "36-60h", "60h+"):
        if by_lead[band]:
            print(f"  {band:20s} n={len(by_lead[band]):4d}  Brier={brier(by_lead[band]):.4f}")

    edges = [(r["edge"], r["p_model"], outcomes[r["ticker"]]["y"]) for r in preds if r["edge"] is not None]
    if edges:
        big = [(p, y) for e, p, y in edges if abs(e) >= 0.15]
        print(f"\nWhere model and market disagreed by 15 points or more: n={len(big)}, model Brier={brier(big) if big else float('nan'):.4f}")


if __name__ == "__main__":
    mode = "all"
    if "--first" in sys.argv:
        mode = "first"
    if "--last" in sys.argv:
        mode = "last"
    main(mode)
