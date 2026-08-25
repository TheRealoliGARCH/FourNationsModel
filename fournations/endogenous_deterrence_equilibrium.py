from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping


_EPSILON = 1e-12


@dataclass(frozen=True)
class CandidateStrategy:
    baseline_probability: float
    revelation_increment: float
    admission_value: float
    revelation_cost: float
    option_value_loss: float

    def __post_init__(self) -> None:
        for name in ("baseline_probability", "revelation_increment"):
            value = float(getattr(self, name))
            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1]")
        for name in ("admission_value", "revelation_cost", "option_value_loss"):
            value = float(getattr(self, name))
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")


@dataclass(frozen=True)
class EndogenousDeterrenceGame:
    candidates: Mapping[str, CandidateStrategy]
    deterrence_capacity: float
    deterrence_cost_per_unit: float
    incumbent_displacement_loss: float
    max_admissions: int = 4

    def __post_init__(self) -> None:
        if not self.candidates:
            raise ValueError("at least one candidate is required")
        if self.max_admissions <= 0 or self.max_admissions > 4:
            raise ValueError("max_admissions must lie in [1, 4]")
        for name in (
            "deterrence_capacity",
            "deterrence_cost_per_unit",
            "incumbent_displacement_loss",
        ):
            value = float(getattr(self, name))
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")


def candidate_probabilities(
    game: EndogenousDeterrenceGame,
    revelations: Mapping[str, bool],
    deterrence: Mapping[str, float],
) -> dict[str, float]:
    probabilities: dict[str, float] = {}
    for name, strategy in game.candidates.items():
        revealed = bool(revelations.get(name, False))
        deterrence_effect = max(float(deterrence.get(name, 0.0)), 0.0)
        value = strategy.baseline_probability
        if revealed:
            value += strategy.revelation_increment
        probabilities[name] = min(max(value - deterrence_effect, 0.0), 1.0)
    return probabilities


def top_admissions(probabilities: Mapping[str, float], seats: int = 4) -> tuple[str, ...]:
    return tuple(
        name
        for name, _ in sorted(probabilities.items(), key=lambda item: (-item[1], item[0]))[:seats]
    )


def optimal_deterrence(
    game: EndogenousDeterrenceGame,
    revelations: Mapping[str, bool],
) -> dict[str, float]:
    probabilities = candidate_probabilities(game, revelations, {})
    ranked = sorted(probabilities, key=lambda name: (-probabilities[name], name))
    threats = ranked[: game.max_admissions]
    remaining = game.deterrence_capacity
    allocation = {name: 0.0 for name in game.candidates}
    for name in reversed(threats):
        if remaining <= _EPSILON:
            break
        strategy = game.candidates[name]
        if not revelations.get(name, False):
            continue
        marginal_benefit = game.incumbent_displacement_loss
        if marginal_benefit + _EPSILON < game.deterrence_cost_per_unit:
            continue
        reduction = min(strategy.revelation_increment, remaining)
        allocation[name] = reduction
        remaining -= reduction
    return allocation


def revelation_best_responses(
    game: EndogenousDeterrenceGame,
    deterrence: Mapping[str, float],
) -> dict[str, bool]:
    decisions: dict[str, bool] = {}
    for name, strategy in game.candidates.items():
        marginal_probability = max(strategy.revelation_increment - float(deterrence.get(name, 0.0)), 0.0)
        benefit = marginal_probability * strategy.admission_value
        burden = strategy.revelation_cost + strategy.option_value_loss
        decisions[name] = benefit + _EPSILON >= burden
    return decisions


def solve_equilibrium(
    game: EndogenousDeterrenceGame,
    *,
    max_iterations: int = 100,
) -> dict[str, object]:
    revelations = {name: False for name in game.candidates}
    for _ in range(max_iterations):
        deterrence = optimal_deterrence(game, revelations)
        next_revelations = revelation_best_responses(game, deterrence)
        if next_revelations == revelations:
            probabilities = candidate_probabilities(game, revelations, deterrence)
            admissions = top_admissions(probabilities, game.max_admissions)
            return {
                "revelations": revelations,
                "deterrence": deterrence,
                "probabilities": probabilities,
                "admissions": admissions,
                "stable": True,
            }
        revelations = next_revelations
    probabilities = candidate_probabilities(game, revelations, optimal_deterrence(game, revelations))
    return {
        "revelations": revelations,
        "deterrence": optimal_deterrence(game, revelations),
        "probabilities": probabilities,
        "admissions": top_admissions(probabilities, game.max_admissions),
        "stable": False,
    }
