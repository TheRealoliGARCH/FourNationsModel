from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .joint_admission_likelihood import (
    JointEvidenceContribution,
    posterior_from_joint_evidence,
)


@dataclass(frozen=True)
class OriginIdentificationAssumptions:
    same_evidence: bool = True
    same_revelation_process: bool = True
    only_prior_differs: bool = True

    def __post_init__(self) -> None:
        if not (self.same_evidence and self.same_revelation_process and self.only_prior_differs):
            raise ValueError(
                "origin counterfactual requires matched evidence, revelation process, and prior-only treatment"
            )


@dataclass(frozen=True)
class OriginCounterfactualResult:
    factual_posterior: float
    counterfactual_posterior: float
    origin_effect: float
    assumptions: OriginIdentificationAssumptions


def _validate_probability(value: float, name: str) -> float:
    value = float(value)
    if not isfinite(value) or not 0.0 < value < 1.0:
        raise ValueError(f"{name} must lie strictly between zero and one")
    return value


def estimate_origin_effect(
    factual_prior: float,
    neutral_counterfactual_prior: float,
    contribution: JointEvidenceContribution,
    assumptions: OriginIdentificationAssumptions | None = None,
) -> OriginCounterfactualResult:
    factual_prior = _validate_probability(factual_prior, "factual_prior")
    neutral_counterfactual_prior = _validate_probability(
        neutral_counterfactual_prior,
        "neutral_counterfactual_prior",
    )
    assumptions = assumptions or OriginIdentificationAssumptions()
    factual = posterior_from_joint_evidence(factual_prior, contribution)
    counterfactual = posterior_from_joint_evidence(
        neutral_counterfactual_prior,
        contribution,
    )
    return OriginCounterfactualResult(
        factual_posterior=factual,
        counterfactual_posterior=counterfactual,
        origin_effect=factual - counterfactual,
        assumptions=assumptions,
    )


def prior_sensitivity_bounds(
    lower_prior: float,
    upper_prior: float,
    contribution: JointEvidenceContribution,
) -> tuple[float, float]:
    lower = _validate_probability(lower_prior, "lower_prior")
    upper = _validate_probability(upper_prior, "upper_prior")
    if lower > upper:
        raise ValueError("lower_prior must not exceed upper_prior")
    return (
        posterior_from_joint_evidence(lower, contribution),
        posterior_from_joint_evidence(upper, contribution),
    )
