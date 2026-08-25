from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


_EPSILON = 1e-12


@dataclass(frozen=True)
class CandidateIncumbentGame:
    probability_without_revelation: float
    probability_with_revelation: float
    admission_value: float
    revelation_cost: float
    option_value_loss: float
    deterrence_effect: float
    incumbent_loss_if_admitted: float
    deterrence_cost: float

    def __post_init__(self) -> None:
        for name in (
            "probability_without_revelation",
            "probability_with_revelation",
            "deterrence_effect",
        ):
            value = float(getattr(self, name))
            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1]")
        for name in (
            "admission_value",
            "revelation_cost",
            "option_value_loss",
            "incumbent_loss_if_admitted",
            "deterrence_cost",
        ):
            value = float(getattr(self, name))
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")

    @property
    def candidate_probability_without_deterrence(self) -> float:
        return self.probability_with_revelation

    @property
    def candidate_probability_with_deterrence(self) -> float:
        return max(0.0, self.probability_with_revelation - self.deterrence_effect)

    @property
    def incumbent_deterrence_benefit(self) -> float:
        probability_reduction = (
            self.candidate_probability_without_deterrence
            - self.candidate_probability_with_deterrence
        )
        return probability_reduction * self.incumbent_loss_if_admitted

    @property
    def incumbents_should_deter(self) -> bool:
        return self.incumbent_deterrence_benefit + _EPSILON >= self.deterrence_cost

    def candidate_revelation_margin(self, *, deter: bool) -> float:
        admission_probability = (
            self.candidate_probability_with_deterrence
            if deter
            else self.candidate_probability_without_deterrence
        )
        benefit = (
            admission_probability - self.probability_without_revelation
        ) * self.admission_value
        burden = self.revelation_cost + self.option_value_loss
        return benefit - burden

    def candidate_should_reveal(self, *, deter: bool) -> bool:
        return self.candidate_revelation_margin(deter=deter) >= -_EPSILON


def pure_strategy_equilibrium(game: CandidateIncumbentGame) -> tuple[bool, bool]:
    """Return (reveal, deter) when mutual best responses form a pure equilibrium."""
    candidate_if_deter = game.candidate_should_reveal(deter=True)
    candidate_if_no_deter = game.candidate_should_reveal(deter=False)
    incumbent_deter = game.incumbents_should_deter

    if incumbent_deter and candidate_if_deter:
        return True, True
    if not incumbent_deter and candidate_if_no_deter:
        return True, False
    if not incumbent_deter and not candidate_if_no_deter:
        return False, False
    return False, True
