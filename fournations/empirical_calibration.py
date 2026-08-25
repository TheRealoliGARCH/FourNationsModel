from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from statistics import fmean
from typing import Iterable, Mapping

from .calibrated_admission_evaluator import NationCalibration
from .information_revelation import InformationState


_EPSILON = 1e-12


@dataclass(frozen=True)
class NationEvidenceObservation:
    empirical_score: float
    revelation_score: float
    state: InformationState

    def __post_init__(self) -> None:
        if not isfinite(float(self.empirical_score)):
            raise ValueError("empirical_score must be finite")
        if not isfinite(float(self.revelation_score)):
            raise ValueError("revelation_score must be finite")


def _logit(probability: float) -> float:
    probability = min(max(float(probability), _EPSILON), 1.0 - _EPSILON)
    return log(probability / (1.0 - probability))


def estimate_prior_probability(observations: Iterable[NationEvidenceObservation]) -> float:
    data = tuple(observations)
    if not data:
        raise ValueError("at least one observation is required")
    revealed = fmean(
        1.0 if observation.state is InformationState.REVEALED else 0.0
        for observation in data
    )
    return min(max(revealed, _EPSILON), 1.0 - _EPSILON)


def estimate_log_likelihood_components(
    observations: Iterable[NationEvidenceObservation],
) -> tuple[float, float]:
    data = tuple(observations)
    if not data:
        raise ValueError("at least one observation is required")
    empirical = fmean(observation.empirical_score for observation in data)
    revelation = fmean(
        observation.revelation_score for observation in data)
    return empirical, revelation


def calibrate_nation(
    observations: Iterable[NationEvidenceObservation],
    *,
    prior_probability: float | None = None,
) -> NationCalibration:
    data = tuple(observations)
    empirical, revelation = estimate_log_likelihood_components(data)
    prior = estimate_prior_probability(data) if prior_probability is None else float(prior_probability)
    if not 0.0 < prior < 1.0:
        raise ValueError("prior_probability must lie strictly between zero and one")
    return NationCalibration(
        prior_probability=prior,
        empirical_log_likelihood=empirical,
        revelation_log_likelihood=revelation,
    )


def calibrate_nations(
    evidence: Mapping[str, Iterable[NationEvidenceObservation]],
    *,
    priors: Mapping[str, float] | None = None,
) -> dict[str, NationCalibration]:
    if not evidence:
        raise ValueError("at least one nation is required")
    priors = priors or {}
    return {
        nation: calibrate_nation(
            observations,
            prior_probability=priors.get(nation),
        )
        for nation, observations in evidence.items()
    }
