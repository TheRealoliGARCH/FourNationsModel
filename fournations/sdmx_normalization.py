from __future__ import annotations

from typing import Any
from urllib.parse import quote

from .live_providers import ProviderError


def bis_csv_url(flow: str, key: str, start: int, end: int) -> str:
    return (
        f"https://stats.bis.org/api/v2/data/dataflow/BIS/{quote(flow, safe='')}/1.0/"
        f"{quote(key, safe='.')}/?startPeriod={start}&endPeriod={end}&format=csvfile"
    )


def oecd_csv_url(dataset: str, key: str, start: int, end: int) -> str:
    return (
        f"https://sdmx.oecd.org/public/rest/v1/data/OECD.SDD.STES,{quote(dataset, safe='')},/"
        f"{quote(key, safe='.+')}/?startPeriod={start}&endPeriod={end}&dimension_at_observation=AllDimensions"
    )


def normalize_csv_observations(text: str) -> dict[str, list[dict[str, object]]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ProviderError("empty SDMX CSV response")
    header = [field.strip() for field in lines[0].split(",")]
    try:
        period_i = header.index("TIME_PERIOD")
        value_i = header.index("OBS_VALUE")
    except ValueError as exc:
        raise ProviderError("SDMX CSV missing TIME_PERIOD or OBS_VALUE") from exc
    rows: list[dict[str, object]] = []
    for line in lines[1:]:
        fields = [field.strip() for field in line.split(",")]
        if len(fields) <= max(period_i, value_i):
            raise ProviderError("malformed SDMX CSV row")
        period, value = fields[period_i], fields[value_i]
        if not period or not value:
            continue
        rows.append({"period": period, "value": float(value)})
    return {"observations": rows}


def normalize_sdmx_json(payload: Any) -> dict[str, list[dict[str, object]]]:
    if isinstance(payload, dict) and isinstance(payload.get("observations"), list):
        return {"observations": payload["observations"]}
    raise ProviderError("unsupported SDMX JSON shape; explicit provider normalizer required")
