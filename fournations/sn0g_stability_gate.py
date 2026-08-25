from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from fournations.systemic_stability import StabilityWeights, systemic_instability


_EPSILON = 1e-12


@dataclass(frozen=True)
class EpistemicState:
    """Declared information status used to preserve known/unknown distinctions."""

    known: bool
    prior_probability: float
    unknown_uncertainty: float = 0.0

    def __post_init__(self) -> None:
        if not isfinite(self.prior_probability) or not 0.0 <= self.prior_probability <= 1.0:
            raise ValueError("prior_probability must lie in [0, 1]")
        if not isfinite(self.unknown_uncertainty) or not 0.0 <= self.unknown_uncertainty <= 1.0:
            raise ValueError("unknown_uncertainty must lie in [0, 1]")
        if self.known and self.unknown_uncertainty > _EPSILON:
            raise ValueError("known states must have zero unknown uncertainty")


def epistemic_uncertainty(states: Mapping[str, EpistemicState]) -> float:
    if not states:
        return 0.0
    return sum(state.unknown_uncertainty for state in states.values()) / len(states)


def sn0g_adjusted_instability(
    probabilities: Mapping[str, float],
    deterrence: Mapping[str, float],
    epistemic_states: Mapping[str, EpistemicState],
    *,
    epistemic_weight: float = 1.0,
    seats: int = 4,
    weights: StabilityWeights | None = None,
) -> float:
    if set(probabilities) != set(epistemic_states):
        raise ValueError("probabilities and epistemic_states must have identical keys")
    epistemic_weight = float(epistemic_weight)
    if not isfinite(epistemic_weight) or epistemic_weight < 0.0:
        raise ValueError("epistemic_weight must be finite and non-negative")
    base = systemic_instability(
        probabilities, deterrence, seats=seats, weights=weights
    )
    return base + epistemic_weight * epistemic_uncertainty(epistemic_states)


def select_stable_equilibrium(
    equilibrium: Mapping[str, object],
    epistemic_states: Mapping[str, EpistemicState],
    *,
    threshold: float,
    epistemic_weight: float = 1.0,
    seats: int = 4,
    weights: StabilityWeights | None = None,
) -> dict[str, object]:
    threshold = float(threshold)
    if not isfinite(threshold) or threshold < 0.0:
        raise ValueError("threshold must be finite and non-negative")
    probabilities = equilibrium.get("probabilities")
    deterrence = equilibrium.get("deterrence")
    admissions = equilibrium.get("admissions")
    if not isinstance(probabilities, Mapping) or not isinstance(deterrence, Mapping):
        raise ValueError("equilibrium must contain probability and deterrence mappings")
    if not isinstance(admissions, tuple):
        raise ValueError("equilibrium admissions must be a tuple")
    if len(admissions) > seats:
        raise ValueError("equilibrium violates the admission ceiling")
    score = sn0g_adjusted_instability(
        probabilities,
        deterrence,
        epistemic_states,
        epistemic_weight=epistemic_weight,
        seats=seats,
        weights=weights,
    )
    return {
        **equilibrium,
        "systemic_instability": score,
        "systemically_stable": score <= threshold + _EPSILON,
    }
