"""Tiny JSON-over-HTTP helper. Standard library only."""

import json
import time
import urllib.parse
import urllib.request

from config import REQUEST_PAUSE

_last_call = 0.0


def get_json(url, params=None, timeout=30):
    """GET a URL and parse the JSON body. Waits REQUEST_PAUSE between calls."""
    global _last_call
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    wait = REQUEST_PAUSE - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": "weather-contract-calibration/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read()
    _last_call = time.monotonic()
    return json.loads(body)
