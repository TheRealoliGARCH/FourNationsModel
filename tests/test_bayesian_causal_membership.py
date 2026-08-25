import pytest

from fournations.bayesian_causal_membership import (
    CausalEvidence,
    MembershipPrior,
    causal_effect,
    prior_sensitivity,
    rank_posteriors,
    update_membership,
)
from fournations.membership import Candidate


def test_evidence_updates_prior_upward_when_likelihood_ratio_exceeds_one():
    posterior = update_membership(
        MembershipPrior("IND", 0.6, origin_treatment=True),
        CausalEvidence("IND", likelihood_if_member=0.8, likelihood_if_not_member=0.2),
    )
    assert posterior.posterior > posterior.prior
    assert posterior.likelihood_ratio == 4.0
    assert posterior.origin_treatment is True


def test_counterfactual_prior_generates_causal_difference():
    evidence = CausalEvidence("IND", 0.7, 0.3)
    factual = update_membership(MembershipPrior("IND", 0.7, origin_treatment=True), evidence)
    counterfactual = update_membership(MembershipPrior("IND", 0.5), evidence)
    assert causal_effect(factual, counterfactual) > 0.0


def test_origin_treatment_is_not_automatic_membership():
    posterior = update_membership(
        MembershipPrior("IND", 0.55, origin_treatment=True),
        CausalEvidence("IND", 0.1, 0.9),
    )
    assert posterior.posterior < 0.55


def test_ranking_remains_capped_at_four():
    names = ("A", "B", "C", "D", "E")
    posteriors = {
        name: update_membership(
            MembershipPrior(name, 0.5),
            CausalEvidence(name, 0.5 + index / 20, 0.5),
        )
        for index, name in enumerate(names)
    }
    candidates = {name: Candidate(name, 1.0, 1.0) for name in names}
    assert rank_posteriors(posteriors, candidates) == ("E", "D", "C", "B")


def test_prior_sensitivity_preserves_order_under_fixed_evidence():
    evidence = CausalEvidence("IND", 0.6, 0.4)
    results = prior_sensitivity("IND", (0.3, 0.5, 0.7), evidence, origin_treatment=True)
    assert [result.posterior for result in results] == sorted(result.posterior for result in results)


def test_mismatched_counterfactuals_are_rejected():
    a = update_membership(MembershipPrior("A", 0.5), CausalEvidence("A", 0.6, 0.4))
    b = update_membership(MembershipPrior("B", 0.5), CausalEvidence("B", 0.6, 0.4))
    with pytest.raises(ValueError):
        causal_effect(a, b)
