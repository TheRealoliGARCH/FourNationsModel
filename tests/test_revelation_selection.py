import pytest

from fournations.information_revelation import InformationState
from fournations.revelation_selection import (
    RevelationCovariates,
    RevelationParameters,
    preferred_information_state,
    revelation_log_likelihood,
    revelation_probability,
)


def covariates(*, latent=0.0, membership=0.5, option=0.0, intercept=0.0):
    return RevelationCovariates(
        latent_value=latent,
        membership_probability=membership,
        option_value=option,
        feature_intercept=intercept,
    )


def test_positive_option_value_reduces_revelation_probability():
    parameters = RevelationParameters(option_value_weight=1.0)
    low = revelation_probability(covariates(option=0.0), parameters)
    high = revelation_probability(covariates(option=2.0), parameters)
    assert high < low


def test_membership_probability_can_raise_revelation_when_weight_is_positive():
    parameters = RevelationParameters(membership_weight=2.0, option_value_weight=0.0)
    low = revelation_probability(covariates(membership=0.1), parameters)
    high = revelation_probability(covariates(membership=0.9), parameters)
    assert high > low


def test_latent_value_can_raise_revelation_when_weight_is_positive():
    parameters = RevelationParameters(latent_weight=1.0, option_value_weight=0.0)
    assert revelation_probability(covariates(latent=2.0), parameters) > revelation_probability(
        covariates(latent=-2.0), parameters
    )


def test_preferred_information_state_uses_probability_threshold():
    parameters = RevelationParameters(option_value_weight=1.0)
    assert preferred_information_state(covariates(option=-2.0), parameters) is InformationState.REVEALED
    assert preferred_information_state(covariates(option=2.0), parameters) is InformationState.NON_REVEALED


def test_log_likelihood_is_finite_for_both_information_states():
    parameters = RevelationParameters()
    x = covariates()
    assert revelation_log_likelihood(InformationState.REVEALED, x, parameters) < 0.0
    assert revelation_log_likelihood(InformationState.NON_REVEALED, x, parameters) < 0.0


def test_invalid_membership_probability_is_rejected():
    with pytest.raises(ValueError):
        covariates(membership=1.1)


def test_invalid_threshold_is_rejected():
    with pytest.raises(ValueError):
        preferred_information_state(covariates(), RevelationParameters(), threshold=1.0)
