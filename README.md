# weather-contract-calibration

Log a forecast-based probability for every daily high-temperature contract on Kalshi, next to the market's own price, and score both against what actually happened.

This is a rebuild of a system I designed and ran in spring 2026 that compared weather-model forecasts with Kalshi temperature contracts and traded the gaps. That version was retired after the season and its code was not kept. This one keeps the part that matters for learning: the prediction log and the scorecard. It does not trade and needs no Kalshi account.

**Attribution.** The concept, the data design and the scoring method are mine. The implementation was generated with Claude Code and reviewed by me; the commit history says so. If you are an interviewer, ask me to explain any file.

## What it does

Every hour (`run.sh`):

1. `scan.py` reads the open markets for seven U.S. cities from Kalshi's public API (`KXHIGHNY`, `KXHIGHCHI`, `KXHIGHMIA`, `KXHIGHAUS`, `KXHIGHDEN`, `KXHIGHLAX`, `KXHIGHPHIL`).
2. For each city it pulls the Open-Meteo **ensemble** forecast of the daily high: every member of GEFS (31) and ECMWF IFS (51), about 80 point forecasts per day.
3. `model.py` turns the members into a probability for each contract. A Gaussian with standard deviation `KERNEL_SD_F` (2.0 F to start) is placed on every member to stand in for the error between a model grid cell and the settlement station; the event probability is the average over members. Thresholds sit on the half-degree because Kalshi settles in whole degrees: ">76" pays on 77 and up, "75-76" on 75 or 76.
4. The record goes to `data/predictions.jsonl`: timestamp, contract, lead time, model probability, ensemble mean and spread, the market's bid, ask and mid, and the gap between model and market.
5. `settle.py` looks up every contract whose day has passed and records the YES/NO result in `data/outcomes.jsonl`.

`report.py` joins the two files and prints Brier scores for the model and for the market mid, a calibration table (what fraction of the "70 to 80 percent" predictions came true), and breakdowns by city and by lead time.

## Why it is built this way

- **Score the market too.** The question is not whether the model is good but whether it knows anything the market does not. Both get a Brier score on the same contracts.
- **Lead time is everything.** A same-day afternoon scan is not a forecast; the market has already seen most of the day's temperature. The report separates leads so the honest comparison (one to three days out) is visible.
- **The kernel width is a parameter, not a fact.** If the calibration table shows the model is overconfident, `KERNEL_SD_F` is too small. The point of logging is to find that out.
- **Station matters.** Each contract settles on one weather station. `config.py` lists the assumed station coordinates; a wrong station shows up as a bias in one city's calibration.
- **Standard library only.** `urllib`, `json`, `math`, `statistics`. Nothing to install.

## Run it

```
python3 scan.py              # one pass, all cities
python3 settle.py            # record results for finished days
python3 report.py --first    # score the earliest snapshot of each contract
python3 -m unittest discover -s tests
```

`launchd/com.example.weather-calibration.plist` is a template for running `run.sh` hourly on macOS; replace `/PATH/TO`.

## Data notes

Kalshi market data is read from the public endpoint `api.elections.kalshi.com/trade-api/v2` without authentication. Forecasts come from `ensemble-api.open-meteo.com`, which is free for non-commercial use. Requests are spaced a quarter second apart. The data files are not committed; they grow by about 80 lines per scan.
