from __future__ import annotations

from typing import Any

from .live_providers import ProviderError


def observations_from_json(payload: Any) -> dict[str, float]:
    """Parse a deliberately narrow observation envelope into period/value pairs.

    The provider-specific adapter must normalize SDMX responses to either
    {"observations": [{"period": "YYYY-MM", "value": number}, ...]}
    or an equivalent mapping before calling this function.
    """
    if not isinstance(payload, dict):
        raise ProviderError("SDMX payload must be an object")
    rows = payload.get("observations")
    if not isinstance(rows, list):
        raise ProviderError("SDMX payload has no normalized observations list")
    out: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ProviderError("invalid SDMX observation row")
        period, value = row.get("period"), row.get("value")
        if not isinstance(period, str) or value is None:
            continue
        if period in out:
            raise ProviderError(f"duplicate observation for {period}")
        out[period] = float(value)
    return out
