"""Append-only JSONL files for predictions and outcomes."""

import json
import os

from config import DATA_DIR, OUTCOMES_FILE, PREDICTIONS_FILE


def _path(name):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, name)


def append(name, record):
    with open(_path(name), "a") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")


def read(name):
    p = _path(name)
    if not os.path.exists(p):
        return []
    with open(p) as f:
        return [json.loads(line) for line in f if line.strip()]


def predictions():
    return read(PREDICTIONS_FILE)


def outcomes():
    return {r["ticker"]: r for r in read(OUTCOMES_FILE)}
