from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Mapping


@dataclass(frozen=True)
class AdmissionScenario:
    name: str
    posteriors: Mapping[str, float]

    def __post_init__(self) -> None:
        if not self.posteriors:
            raise ValueError("scenario must contain at least one posterior")
        if any(not 0.0 <= float(value) <= 1.0 for value in self.posteriors.values()):
            raise ValueError("posteriors must lie in [0, 1]")


def admitted_nations(posteriors: Mapping[str, float], seats: int = 4) -> tuple[str, ...]:
    if seats < 1:
        raise ValueError("seats must be positive")
    return tuple(
        nation
        for nation, _ in sorted(posteriors.items(), key=lambda item: (-float(item[1]), item[0]))[:seats]
    )


def scenario_admissions(
    scenarios: Iterable[AdmissionScenario],
    *,
    seats: int = 4,
) -> Mapping[str, tuple[str, ...]]:
    return {
        scenario.name: admitted_nations(scenario.posteriors, seats)
        for scenario in scenarios
    }


def invariant_admissions(
    scenarios: Iterable[AdmissionScenario],
    *,
    seats: int = 4,
) -> tuple[str, ...]:
    admissions = tuple(scenario_admissions(scenarios, seats=seats).values())
    if not admissions:
        raise ValueError("at least one scenario is required")
    common = set(admissions[0])
    for admitted in admissions[1:]:
        common.intersection_update(admitted)
    return tuple(sorted(common))


def admission_flip_pairs(
    scenarios: Iterable[AdmissionScenario],
    *,
    seats: int = 4,
) -> tuple[tuple[str, str], ...]:
    admissions = scenario_admissions(scenarios, seats=seats)
    return tuple(
        (left, right)
        for left, right in combinations(sorted(admissions), 2)
        if admissions[left] != admissions[right]
    )


def robustness_score(
    scenarios: Iterable[AdmissionScenario],
    *,
    seats: int = 4,
) -> float:
    scenarios = tuple(scenarios)
    if not scenarios:
        raise ValueError("at least one scenario is required")
    invariant = invariant_admissions(scenarios, seats=seats)
    return len(invariant) / min(seats, len(scenarios[0].posteriors))
