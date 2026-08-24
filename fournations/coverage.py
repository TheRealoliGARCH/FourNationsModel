from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class CoverageRecord:
    feature: str
    provider: str
    economies: tuple[str, ...]
    periods: tuple[int, ...]
    complete: bool
    key: str | None = None
    unit: str | None = None


def common_periods(records: Iterable[CoverageRecord]) -> tuple[int, ...]:
    records = tuple(records)
    if not records:
        return ()
    common = set(records[0].periods)
    for record in records[1:]:
        common &= set(record.periods)
    return tuple(sorted(common))


def gate(records: Iterable[CoverageRecord], required_start: int, required_end: int) -> str:
    records = tuple(records)
    required = tuple(range(required_start, required_end + 1))
    if any(not r.complete for r in records):
        return "blocked_pending_complete_coverage"
    if common_periods(records) != required:
        return "blocked_pending_complete_coverage"
    return "ready_for_snapshot"
