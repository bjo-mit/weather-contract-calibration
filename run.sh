#!/bin/bash
# One scheduled pass: log predictions, then record any newly settled results.
cd "$(dirname "$0")" || exit 1
python3 scan.py
python3 settle.py
