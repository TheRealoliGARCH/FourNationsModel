from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


NATIONS = ("USA", "CHE", "FRA", "IND")
YEARS = tuple(range(2012, 2025))


@dataclass(frozen=True)
class SeriesResolution:
    provider: str
    semantic_name: str
    nation: str
    exact_key: str | None
    periods: tuple[int, ...]


@dataclass(frozen=True)
class PreflightDecision:
    status: str
    unresolved: tuple[str, ...]
    incomplete: tuple[str, ...]


def evaluate(resolutions: Iterable[SeriesResolution]) -> PreflightDecision:
    rows = tuple(resolutions)
    unresolved = tuple(
        f"{r.provider}:{r.semantic_name}:{r.nation}"
        for r in rows if not r.exact_key
    )
    incomplete = tuple(
        f"{r.provider}:{r.semantic_name}:{r.nation}"
        for r in rows
        if r.exact_key and not set(YEARS).issubset(set(r.periods))
    )
    if unresolved:
        return PreflightDecision("blocked_unresolved_metadata", unresolved, incomplete)
    if incomplete:
        return PreflightDecision("blocked_incomplete_coverage", (), incomplete)
    return PreflightDecision("ready_for_snapshot", (), ())


def bis_reer_url(key: str) -> str:
    return f"https://stats.bis.org/api/v2/data/dataflow/BIS/WS_EER/1.0/{key}?startPeriod=2012-01&endPeriod=2024-12"


def oecd_irlt_url(key: str) -> str:
    return f"https://sdmx.oecd.org/public/rest/v1/data/{key}?startPeriod=2012&endPeriod=2024"
