from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


_DECISION_TOLERANCE = 1e-12


@dataclass(frozen=True)
class ParticipationDecision:
    admission_probability_without_revelation: float
    admission_probability_with_revelation: float
    admission_value: float
    revelation_cost: float
    option_value_loss: float

    def __post_init__(self) -> None:
        for name in (
            "admission_probability_without_revelation",
            "admission_probability_with_revelation",
        ):
            value = float(getattr(self, name))
            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must lie in [0, 1]")
        for name in ("admission_value", "revelation_cost", "option_value_loss"):
            value = float(getattr(self, name))
            if not isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and non-negative")

    @property
    def admission_gain(self) -> float:
        return (
            self.admission_probability_with_revelation
            - self.admission_probability_without_revelation
        )

    @property
    def revelation_benefit(self) -> float:
        return self.admission_gain * self.admission_value

    @property
    def revelation_burden(self) -> float:
        return self.revelation_cost + self.option_value_loss

    @property
    def participation_margin(self) -> float:
        return self.revelation_benefit - self.revelation_burden

    @property
    def should_reveal(self) -> bool:
        return self.participation_margin >= -_DECISION_TOLERANCE


def minimum_admission_gain(
    admission_value: float,
    revelation_cost: float,
    option_value_loss: float,
) -> float:
    admission_value = float(admission_value)
    revelation_cost = float(revelation_cost)
    option_value_loss = float(option_value_loss)
    if not isfinite(admission_value) or admission_value <= 0.0:
        raise ValueError("admission_value must be finite and positive")
    if any(
        not isfinite(value) or value < 0.0
        for value in (revelation_cost, option_value_loss)
    ):
        raise ValueError("cost and option loss must be finite and non-negative")
    return (revelation_cost + option_value_loss) / admission_value


def admission_threshold(decision: ParticipationDecision) -> float:
    return minimum_admission_gain(
        decision.admission_value,
        decision.revelation_cost,
        decision.option_value_loss,
    )
