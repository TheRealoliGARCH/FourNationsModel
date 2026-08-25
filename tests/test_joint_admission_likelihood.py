import math
import pytest

from fournations.empirical_evidence import EmpiricalEvidence
from fournations.information_revelation import InformationState
from fournations.joint_admission_likelihood import (
    joint_log_likelihood,
    joint_log_odds_update,
    posterior_from_joint_evidence,
)
from fournations.likelihood_calibration import calibrate_feature
from fournations.revelation_selection import RevelationCovariates, RevelationParameters


def record(value):
    return EmpiricalEvidence(
        cell=("IND", 2017, "growth"),
        value=value,
        revelation_state=(InformationState.REVEALED if value is not None else InformationState.NON_REVEALED),
        provider="test",
        retrieved_at=None,
    )


def setup_model():
    calibration = calibrate_feature("growth", (4.0, 6.0), (0.0, 2.0))
    covariates = RevelationCovariates(0.0, 0.5, 0.0)
    parameters = RevelationParameters(option_value_weight=0.0)
    return calibration, covariates, parameters


def test_joint_likelihood_contains_empirical_and_revelation_terms():
    calibration, covariates, parameters = setup_model()
    contribution = joint_log_likelihood((record(5.0),), calibration, covariates, parameters)
    assert contribution.empirical_log_likelihood > 0.0
    assert contribution.revelation_log_likelihood < 0.0
    assert contribution.total_log_likelihood == pytest.approx(
        contribution.empirical_log_likelihood + contribution.revelation_log_likelihood
    )


def test_non_revelation_contributes_selection_but_not_numeric_evidence():
    calibration, covariates, parameters = setup_model()
    contribution = joint_log_likelihood((record(None),), calibration, covariates, parameters)
    assert contribution.empirical_log_likelihood == 0.0
    assert contribution.revelation_log_likelihood < 0.0


def test_joint_log_odds_updates_prior():
    calibration, covariates, parameters = setup_model()
    contribution = joint_log_likelihood((record(5.0),), calibration, covariates, parameters)
    updated = joint_log_odds_update(0.5, contribution)
    assert updated == pytest.approx(contribution.total_log_likelihood)


def test_joint_posterior_is_a_probability():
    calibration, covariates, parameters = setup_model()
    contribution = joint_log_likelihood((record(5.0), record(None)), calibration, covariates, parameters)
    posterior = posterior_from_joint_evidence(0.5, contribution)
    assert 0.0 < posterior < 1.0


def test_invalid_prior_is_rejected():
    calibration, covariates, parameters = setup_model()
    contribution = joint_log_likelihood((record(5.0),), calibration, covariates, parameters)
    with pytest.raises(ValueError):
        joint_log_odds_update(1.0, contribution)
