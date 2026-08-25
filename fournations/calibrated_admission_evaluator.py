from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from typing import Mapping

from .joint_admission_likelihood import JointEvidenceContribution
from .scenario_generation import ScenarioParameters


@dataclass(frozen=True)
class NationCalibration:
    prior_probability: float
    empirical_log_likelihood: float
    revelation_log_likelihood: float

    def __post_init__(self) -> None:
        if not 0.0 < float(self.prior_probability) < 1.0:
            raise ValueError("prior_probability must lie strictly between zero and one")


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        return 1.0 / (1.0 + exp(-value))
    transformed = exp(value)
    return transformed / (1.0 + transformed)


def evaluate_calibrated_posteriors(
    calibrations: Mapping[str, NationCalibration],
    parameters: ScenarioParameters,
) -> dict[str, float]:
    posteriors: dict[str, float] = {}
    for nation, calibration in calibrations.items():
        prior = calibration.prior_probability * parameters.prior_multiplier
        prior = min(max(prior, 1e-12), 1.0 - 1e-12)
        contribution = JointEvidenceContribution(
            empirical_log_likelihood=(
                calibration.empirical_log_likelihood * parameters.empirical_multiplier
            ),
            revelation_log_likelihood=(
                calibration.revelation_log_likelihood * parameters.revelation_multiplier
            ),
        )
        log_odds = log(prior / (1.0 - prior)) + contribution.total_log_likelihood
        posteriors[nation] = _sigmoid(log_odds)
    return posteriors
