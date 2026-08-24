from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping

@dataclass(frozen=True)
class CoverageResult:
    feature: str
    nation: str
    observed_years: tuple[int, ...]
    missing_years: tuple[int, ...]
    exact_key: str | None

    @property
    def complete(self) -> bool:
        return not self.missing_years and self.exact_key is not None


def check_coverage(feature: str, nation: str, years: Iterable[int], expected: Iterable[int], exact_key: str | None) -> CoverageResult:
    expected_set = tuple(sorted(set(expected)))
    observed_set = set(years)
    missing = tuple(y for y in expected_set if y not in observed_set)
    return CoverageResult(feature, nation, tuple(sorted(observed_set)), missing, exact_key)


def release_gate(results: Iterable[CoverageResult]) -> str:
    results = tuple(results)
    if not results:
        return "blocked_no_results"
    if any(r.exact_key is None for r in results):
        return "blocked_unresolved_metadata"
    if any(r.missing_years for r in results):
        return "blocked_incomplete_coverage"
    return "ready_for_snapshot"
