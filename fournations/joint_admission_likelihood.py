from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Iterable

from .empirical_evidence import EmpiricalEvidence
from .information_revelation import InformationState
from .likelihood_calibration import FeatureCalibration, evidence_log_likelihood
from .revelation_selection import (
    RevelationCovariates,
    RevelationParameters,
    revelation_log_likelihood,
)


@dataclass(frozen=True)
class JointEvidenceContribution:
    empirical_log_likelihood: float
    revelation_log_likelihood: float

    @property
    def total_log_likelihood(self) -> float:
        return self.empirical_log_likelihood + self.revelation_log_likelihood


def joint_log_likelihood(
    records: Iterable[EmpiricalEvidence],
    calibration: FeatureCalibration,
    covariates: RevelationCovariates,
    parameters: RevelationParameters,
) -> JointEvidenceContribution:
    records = tuple(records)
    matching = tuple(record for record in records if record.cell[2] == calibration.feature)
    empirical = evidence_log_likelihood(matching, calibration)
    revelation = sum(
        revelation_log_likelihood(record.revelation_state, covariates, parameters)
        for record in matching
    )
    return JointEvidenceContribution(empirical, revelation)


def joint_likelihood_ratio(
    records: Iterable[EmpiricalEvidence],
    calibration: FeatureCalibration,
    covariates: RevelationCovariates,
    parameters: RevelationParameters,
) -> float:
    contribution = joint_log_likelihood(records, calibration, covariates, parameters)
    if not isfinite(contribution.total_log_likelihood):
        raise ValueError("joint log likelihood must be finite")
    return exp(contribution.total_log_likelihood)


def joint_log_odds_update(
    prior_probability: float,
    contribution: JointEvidenceContribution,
) -> float:
    prior_probability = float(prior_probability)
    if not 0.0 < prior_probability < 1.0:
        raise ValueError("prior_probability must lie strictly between zero and one")
    if not isfinite(contribution.total_log_likelihood):
        raise ValueError("joint log likelihood must be finite")
    from math import log
    return log(prior_probability / (1.0 - prior_probability)) + contribution.total_log_likelihood


def posterior_from_joint_evidence(
    prior_probability: float,
    contribution: JointEvidenceContribution,
) -> float:
    log_odds = joint_log_odds_update(prior_probability, contribution)
    if log_odds >= 0.0:
        return 1.0 / (1.0 + exp(-log_odds))
    transformed = exp(log_odds)
    return transformed / (1.0 + transformed)
