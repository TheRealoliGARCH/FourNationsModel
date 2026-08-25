from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .bayesian_causal_membership import CausalEvidence, MembershipPrior, PosteriorMembership, update_membership
from .membership import Candidate, MAX_MEMBERS


@dataclass(frozen=True)
class SequentialEvidence:
    nation: str
    observations: tuple[CausalEvidence, ...]


@dataclass(frozen=True)
class AdmissionState:
    posteriors: Mapping[str, PosteriorMembership]
    admitted: tuple[str, ...]
    capacity: int


def sequential_update(prior: MembershipPrior, evidence: Iterable[CausalEvidence]) -> PosteriorMembership:
    current = prior
    posterior: PosteriorMembership | None = None
    for observation in evidence:
        posterior = update_membership(current, observation)
        current = MembershipPrior(prior.nation, posterior.posterior, origin_treatment=prior.origin_treatment)
    if posterior is None:
        posterior = PosteriorMembership(prior.nation, prior.probability, prior.probability, 1.0, prior.origin_treatment)
    return posterior


def admit_posteriors(posteriors: Mapping[str, PosteriorMembership], candidates: Mapping[str, Candidate], *, capacity: int = MAX_MEMBERS) -> AdmissionState:
    if capacity < 1 or capacity > MAX_MEMBERS:
        raise ValueError(f"capacity must lie in [1, {MAX_MEMBERS}]")
    if set(posteriors) != set(candidates):
        raise ValueError("posterior and candidate sets must match")
    admitted = tuple(nation for nation, _ in sorted(posteriors.items(), key=lambda item: (-item[1].posterior, -candidates[item[0]].revealed_capability, item[0]))[:capacity])
    return AdmissionState(posteriors, admitted, capacity)


def counterfactual_origin_effect(factual_prior: MembershipPrior, counterfactual_prior: MembershipPrior, evidence: Iterable[CausalEvidence]) -> float:
    observations = tuple(evidence)
    factual = sequential_update(factual_prior, observations)
    counterfactual = sequential_update(counterfactual_prior, observations)
    return factual.posterior - counterfactual.posterior
