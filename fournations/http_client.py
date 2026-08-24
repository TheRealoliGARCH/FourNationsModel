from __future__ import annotations

import json
from urllib.request import Request, urlopen


class UrllibJsonClient:
    """Minimal stdlib-only HTTP client for provider adapters."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def get_json(self, url: str) -> object:
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "FourNationsModel/1.0"})
        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))
