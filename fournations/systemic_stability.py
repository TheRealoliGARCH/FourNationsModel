from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping


_EPSILON = 1e-12


@dataclass(frozen=True)
class StabilityWeights:
    admission_pressure: float = 1.0
    deterrence_burden: float = 1.0
    competitive_instability: float = 1.0

    def __post_init__(self) -> None:
        for name in (
            "admission_pressure",
            "deterrence_burden",
            "competitive_instability",
        ):
            value = float(getattr(self, name))
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")


def admission_pressure(
    probabilities: Mapping[str, float],
    *,
    seats: int = 4,
) -> float:
    if seats <= 0 or seats > 4:
        raise ValueError("seats must lie in [1, 4]")
    if not probabilities:
        return 0.0
    values = sorted((float(value) for value in probabilities.values()), reverse=True)
    if len(values) <= seats:
        return 0.0
    boundary = values[seats - 1]
    challenger = values[seats]
    return max(challenger - boundary, 0.0)


def deterrence_burden(deterrence: Mapping[str, float]) -> float:
    total = 0.0
    for value in deterrence.values():
        value = float(value)
        if not isfinite(value) or value < 0.0:
            raise ValueError("deterrence values must be finite and non-negative")
        total += value
    return total


def competitive_instability(
    probabilities: Mapping[str, float]) -> float:
    values = tuple(float(value) for value in probabilities.values())
    if len(values) < 2:
        return 0.0
    if any(not isfinite(value) or not 0.0 <= value <= 1.0 for value in values):
        raise ValueError("probabilities must lie in [0, 1]")
    return sum(
        1.0 - abs(left - right)
        for index, left in enumerate(values)
        for right in values[index + 1 :]
    ) / (len(values) * (len(values) - 1) / 2)


def systemic_instability(
    probabilities: Mapping[str, float],
    deterrence: Mapping[str, float],
    *,
    seats: int = 4,
    weights: StabilityWeights | None = None,
) -> float:
    weights = weights or StabilityWeights()
    pressure = admission_pressure(probabilities, seats=seats)
    burden = deterrence_burden(deterrence)
    competition = competitive_instability(probabilities)
    return (
        weights.admission_pressure * pressure
        + weights.deterrence_burden * burden
        + weights.competitive_instability * competition
    )


def is_systemically_stable(
    probabilities: Mapping[str, float],
    deterrence: Mapping[str, float],
    *,
    threshold: float,
    seats: int = 4,
    weights: StabilityWeights | None = None,
) -> bool:
    threshold = float(threshold)
    if not isfinite(threshold) or threshold < 0.0:
        raise ValueError("threshold must be finite and non-negative")
    return systemic_instability(
        probabilities, deterrence, seats=seats, weights=weights
    ) <= threshold + _EPSILON
