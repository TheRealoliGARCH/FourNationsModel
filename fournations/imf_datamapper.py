from __future__ import annotations

from .live_providers import HttpClient, ProviderError

BASE = "https://www.imf.org/external/datamapper/api/v1"


class IMFDataMapperAdapter:
    def __init__(self, client: HttpClient):
        self.client = client

    def annual_series(self, indicator: str, economy: str, start: int, end: int) -> dict[int, float]:
        payload = self.client.get_json(f"{BASE}/{indicator}/{economy}")
        if not isinstance(payload, dict):
            raise ProviderError("unexpected IMF DataMapper response")
        block = payload.get("values", {}).get(indicator, {}).get(economy, {})
        if not isinstance(block, dict):
            raise ProviderError(f"missing IMF series {indicator}/{economy}")
        values = {}
        for year in range(start, end + 1):
            value = block.get(str(year))
            if value is not None:
                values[year] = float(value)
        return values
