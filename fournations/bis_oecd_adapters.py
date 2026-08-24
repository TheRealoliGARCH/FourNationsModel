from __future__ import annotations

from typing import Any

from .live_providers import ProviderError, SDMXAdapter, require_complete_months, require_complete_quarters
from .sdmx_observations import observations_from_json


def annual_from_monthly(payload: Any, year: int) -> float:
    return require_complete_months(observations_from_json(payload), year)


def annual_from_quarterly(payload: Any, year: int) -> float:
    return require_complete_quarters(observations_from_json(payload), year)


def swiss_credit_annual(component_payloads: tuple[Any, Any, Any], year: int) -> float:
    values = [annual_from_quarterly(payload, year) for payload in component_payloads]
    return sum(values)


def fetch_sdmx_annual(adapter: SDMXAdapter, url: str, year: int, frequency: str) -> float:
    payload = adapter.fetch(url)
    if frequency == "M":
        return annual_from_monthly(payload, year)
    if frequency == "Q":
        return annual_from_quarterly(payload, year)
    raise ProviderError(f"unsupported SDMX frequency {frequency}")
