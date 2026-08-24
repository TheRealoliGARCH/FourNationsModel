from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class HttpClient(Protocol):
    def get_json(self, url: str) -> object: ...


@dataclass(frozen=True)
class ProviderBinding:
    provider: str
    series: str
    economy: str
    frequency: str


class ProviderError(RuntimeError):
    pass


class WorldBankAdapter:
    base_url = "https://api.worldbank.org/v2/country"

    def __init__(self, client: HttpClient):
        self.client = client

    def annual_indicator(self, economy: str, indicator: str, start: int, end: int) -> dict[int, float]:
        url = f"{self.base_url}/{economy}/indicator/{indicator}?date={start}:{end}&format=json&per_page=100"
        payload = self.client.get_json(url)
        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
            raise ProviderError("unexpected World Bank response")
        values: dict[int, float] = {}
        for row in payload[1]:
            year, value = row.get("date"), row.get("value")
            if year is not None and value is not None:
                values[int(year)] = float(value)
        return values


class SDMXAdapter:
    def __init__(self, client: HttpClient, provider: str):
        self.client = client
        self.provider = provider

    def fetch(self, url: str) -> object:
        payload = self.client.get_json(url)
        if payload is None:
            raise ProviderError(f"empty {self.provider} response")
        return payload


def require_complete_months(monthly: dict[str, float], year: int) -> float:
    months = [monthly.get(f"{year}-{m:02d}") for m in range(1, 13)]
    if any(value is None for value in months):
        raise ProviderError(f"incomplete monthly coverage for {year}")
    return sum(float(value) for value in months) / 12.0


def require_complete_quarters(quarterly: dict[str, float], year: int) -> float:
    quarters = [quarterly.get(f"{year}-Q{q}") for q in range(1, 5)]
    if any(value is None for value in quarters):
        raise ProviderError(f"incomplete quarterly coverage for {year}")
    return sum(float(value) for value in quarters) / 4.0
