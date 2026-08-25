from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Mapping

from .admission_robustness import AdmissionScenario


@dataclass(frozen=True)
class PerturbationGrid:
    prior_multipliers: tuple[float, ...]
    empirical_multipliers: tuple[float, ...]
    revelation_multipliers: tuple[float, ...]

    def __post_init__(self) -> None:
        groups = (
            self.prior_multipliers,
            self.empirical_multipliers,
            self.revelation_multipliers,
        )
        if any(not group for group in groups):
            raise ValueError("each perturbation dimension must be non-empty")
        if any(value < 0.0 for group in groups for value in group):
            raise ValueError("perturbation multipliers must be non-negative")

    def points(self) -> tuple[tuple[float, float, float], ...]:
        return tuple(product(
            self.prior_multipliers,
            self.empirical_multipliers,
            self.revelation_multipliers,
        ))


@dataclass(frozen=True)
class ScenarioParameters:
    prior_multiplier: float
    empirical_multiplier: float
    revelation_multiplier: float

    @property
    def name(self) -> str:
        return (
            f"prior={self.prior_multiplier:g}|"
            f"empirical={self.empirical_multiplier:g}|"
            f"revelation={self.revelation_multiplier:g}"
        )


def generate_parameters(grid: PerturbationGrid) -> tuple[ScenarioParameters, ...]:
    return tuple(ScenarioParameters(*point) for point in grid.points())


def generate_scenarios(
    grid: PerturbationGrid,
    evaluator: Callable[[ScenarioParameters], Mapping[str, float]],
) -> tuple[AdmissionScenario, ...]:
    scenarios = []
    for parameters in generate_parameters(grid):
        posteriors = evaluator(parameters)
        scenarios.append(AdmissionScenario(parameters.name, dict(posteriors)))
    return tuple(scenarios)


def stability_region(
    scenarios: Iterable[AdmissionScenario],
    admitted: Iterable[str],
    *,
    seats: int = 4,
) -> tuple[str, ...]:
    target = tuple(sorted(admitted))
    if len(target) > seats:
        raise ValueError("target admission set cannot exceed available seats")
    from .admission_robustness import admitted_nations
    return tuple(
        scenario.name
        for scenario in scenarios
        if tuple(sorted(admitted_nations(scenario.posteriors, seats))) == target
    )
