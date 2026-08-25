import pytest

from fournations.empirical_calibration import (
    NationEvidenceObservation,
    calibrate_nation,
    calibrate_nations,
    estimate_log_likelihood_components,
    estimate_prior_probability,
)
from fournations.information_revelation import InformationState


def observations():
    return (
        NationEvidenceObservation(1.0, 0.2, InformationState.REVEALED),
        NationEvidenceObservation(0.5, 0.1, InformationState.REVEALED),
        NationEvidenceObservation(-0.5, -0.2, InformationState.NON_REVEALED),
        NationEvidenceObservation(0.0, 0.0, InformationState.NON_REVEALED),
    )


def test_prior_estimate_uses_observed_revelation_frequency():
    assert estimate_prior_probability(observations()) == pytest.approx(0.5)


def test_likelihood_components_use_empirical_means():
    empirical, revelation = estimate_log_likelihood_components(observations())
    assert empirical == pytest.approx(0.25)
    assert revelation == pytest.approx(0.025)


def test_calibration_returns_joint_evaluator_contract():
    calibration = calibrate_nation(observations(), prior_probability=0.6)
    assert calibration.prior_probability == pytest.approx(0.6)
    assert calibration.empirical_log_likelihood == pytest.approx(0.25)


def test_multi_nation_calibration_preserves_external_priors():
    result = calibrate_nations(
        {"A": observations(), "B": observations()},
        priors={"A": 0.7},
    )
    assert result["A"].prior_probability == pytest.approx(0.7)
    assert result["B"].prior_probability == pytest.approx(0.5)


def test_empty_observations_are_rejected():
    with pytest.raises(ValueError):
        calibrate_nation(())
