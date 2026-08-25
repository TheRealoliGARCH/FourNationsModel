import pytest

from fournations.joint_admission_likelihood import JointEvidenceContribution
from fournations.origin_counterfactual import (
    OriginIdentificationAssumptions,
    estimate_origin_effect,
    prior_sensitivity_bounds,
)


def contribution():
    return JointEvidenceContribution(
        empirical_log_likelihood=0.4,
        revelation_log_likelihood=-0.1,
    )


def test_origin_effect_compares_matched_factual_and_counterfactual_worlds():
    result = estimate_origin_effect(0.7, 0.5, contribution())
    assert result.factual_posterior > result.counterfactual_posterior
    assert result.origin_effect > 0.0
    assert result.assumptions.same_evidence
    assert result.assumptions.same_revelation_process


def test_equal_priors_produce_zero_origin_effect():
    result = estimate_origin_effect(0.5, 0.5, contribution())
    assert result.origin_effect == pytest.approx(0.0)


def test_matched_identification_assumptions_are_enforced():
    with pytest.raises(ValueError):
        OriginIdentificationAssumptions(same_evidence=False)
    with pytest.raises(ValueError):
        OriginIdentificationAssumptions(same_revelation_process=False)
    with pytest.raises(ValueError):
        OriginIdentificationAssumptions(only_prior_differs=False)


def test_prior_sensitivity_bounds_preserve_posterior_order():
    lower, upper = prior_sensitivity_bounds(0.3, 0.7, contribution())
    assert lower < upper


def test_invalid_prior_bounds_are_rejected():
    with pytest.raises(ValueError):
        prior_sensitivity_bounds(0.8, 0.2, contribution())
