from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class SeriesRecord:
    provider: str
    key: str
    economy: str
    semantic: str
    periods: tuple[str, ...]
    metadata: Mapping[str, str]


@dataclass(frozen=True)
class Resolution:
    provider: str
    economy: str
    semantic: str
    key: str | None
    status: str
    periods: tuple[str, ...]


def enumerate_matches(records: Iterable[SeriesRecord], *, provider: str, economy: str, semantic: str) -> tuple[SeriesRecord, ...]:
    return tuple(
        r for r in records
        if r.provider.upper() == provider.upper()
        and r.economy.upper() == economy.upper()
        and r.semantic == semantic
    )


def resolve_unique(records: Iterable[SeriesRecord], *, provider: str, economy: str, semantic: str) -> Resolution:
    matches = enumerate_matches(records, provider=provider, economy=economy, semantic=semantic)
    if not matches:
        return Resolution(provider, economy, semantic, None, "unresolved", ())
    if len(matches) > 1:
        return Resolution(provider, economy, semantic, None, "ambiguous", ())
    record = matches[0]
    return Resolution(provider, economy, semantic, record.key, "resolved", record.periods)


def coverage(resolution: Resolution, required_periods: Iterable[str]) -> str:
    required = set(required_periods)
    if resolution.status != "resolved":
        return resolution.status
    return "complete" if required <= set(resolution.periods) else "incomplete"
