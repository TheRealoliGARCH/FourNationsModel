import pytest

from fournations.information_revelation import InformationState
from fournations.joint_empirical_estimation import (
    RevelationObservation,
    empirical_revelation_rate,
    fit_revelation_parameters,
    revelation_log_likelihood,
)


def observation(latent, membership, option, revealed):
    return RevelationObservation(
        latent_value=latent,
        membership_probability=membership,
        option_value=option,
        state=InformationState.REVEALED if revealed else InformationState.NON_REVEALED,
    )


def sample():
    return (
        observation(2.0, 0.9, 0.0, True),
        observation(1.0, 0.8, 0.1, True),
        observation(-1.0, 0.2, 1.0, False),
        observation(-2.0, 0.1, 2.0, False),
    )


def test_empirical_revelation_rate_is_observed_frequency():
    assert empirical_revelation_rate(sample()) == 0.5


def test_fitting_improves_over_zero_parameter_baseline():
    data = sample()
    baseline = revelation_log_likelihood(data, fit_revelation_parameters(data, iterations=1).parameters)
    fitted = fit_revelation_parameters(data, iterations=200)
    assert fitted.log_likelihood >= baseline
    assert fitted.iterations == 200


def test_fitted_parameters_are_finite():
    result = fit_revelation_parameters(sample())
    assert result.parameters.latent_weight > 0.0
    assert result.parameters.option_value_weight > 0.0


def test_empty_data_is_rejected():
    with pytest.raises(ValueError):
        fit_revelation_parameters(())


def test_invalid_membership_probability_is_rejected():
    with pytest.raises(ValueError):
        observation(0.0, 1.1, 0.0, True)
