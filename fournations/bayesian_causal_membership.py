from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from .membership import Candidate, MAX_MEMBERS


@dataclass(frozen=True)
class MembershipPrior:
    nation: str
    probability: float
    origin_treatment: bool = False

    def __post_init__(self) -> None:
        if not 0.0 < self.probability < 1.0:
            raise ValueError("prior probability must lie strictly between zero and one")


@dataclass(frozen=True)
class CausalEvidence:
    nation: str
    likelihood_if_member: float
    likelihood_if_not_member: float

    def __post_init__(self) -> None:
        if self.likelihood_if_member <= 0.0 or self.likelihood_if_not_member <= 0.0:
            raise ValueError("likelihoods must be positive")


@dataclass(frozen=True)
class PosteriorMembership:
    nation: str
    prior: float
    posterior: float
    likelihood_ratio: float
    origin_treatment: bool


def bayes_update(prior: float, likelihood_if_member: float, likelihood_if_not_member: float) -> float:
    numerator = likelihood_if_member * prior
    denominator = numerator + likelihood_if_not_member * (1.0 - prior)
    if denominator <= 0.0 or not isfinite(denominator):
        raise ValueError("Bayes denominator must be finite and positive")
    return numerator / denominator


def update_membership(prior: MembershipPrior, evidence: CausalEvidence) -> PosteriorMembership:
    if prior.nation != evidence.nation:
        raise ValueError("prior and evidence must refer to the same nation")
    posterior = bayes_update(
        prior.probability,
        evidence.likelihood_if_member,
        evidence.likelihood_if_not_member,
    )
    return PosteriorMembership(
        nation=prior.nation,
        prior=prior.probability,
        posterior=posterior,
        likelihood_ratio=evidence.likelihood_if_member / evidence.likelihood_if_not_member,
        origin_treatment=prior.origin_treatment,
    )


def causal_effect(
    factual: PosteriorMembership,
    counterfactual: PosteriorMembership,
) -> float:
    if factual.nation != counterfactual.nation:
        raise ValueError("counterfactual comparison requires the same nation")
    return factual.posterior - counterfactual.posterior


def rank_posteriors(
    posteriors: Mapping[str, PosteriorMembership],
    candidates: Mapping[str, Candidate],
    *,
    max_members: int = MAX_MEMBERS,
) -> tuple[str, ...]:
    if max_members < 1 or max_members > MAX_MEMBERS:
        raise ValueError(f"max_members must lie in [1, {MAX_MEMBERS}]")
    if set(posteriors) != set(candidates):
        raise ValueError("posterior and candidate sets must match")
    return tuple(
        nation
        for nation, _ in sorted(
            posteriors.items(),
            key=lambda item: (-item[1].posterior, -candidates[item[0]].revealed_capability, item[0]),
        )[:max_members]
    )


def prior_sensitivity(
    nation: str,
    priors: tuple[float, ...],
    evidence: CausalEvidence,
    *,
    origin_treatment: bool = False,
) -> tuple[PosteriorMembership, ...]:
    return tuple(
        update_membership(
            MembershipPrior(nation, probability, origin_treatment=origin_treatment),
            evidence,
        )
        for probability in priors
    )
