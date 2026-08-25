from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite

from .information_revelation import InformationState


@dataclass(frozen=True)
class RevelationCovariates:
    latent_value: float
    membership_probability: float
    option_value: float
    feature_intercept: float = 0.0

    def __post_init__(self) -> None:
        values = (
            self.latent_value,
            self.membership_probability,
            self.option_value,
            self.feature_intercept,
        )
        if not all(isfinite(float(value)) for value in values):
            raise ValueError("revelation covariates must be finite")
        if not 0.0 <= self.membership_probability <= 1.0:
            raise ValueError("membership_probability must lie in [0, 1]")


@dataclass(frozen=True)
class RevelationParameters:
    latent_weight: float = 0.0
    membership_weight: float = 0.0
    option_value_weight: float = 1.0

    def __post_init__(self) -> None:
        if not all(
            isfinite(float(value))
            for value in (
                self.latent_weight,
                self.membership_weight,
                self.option_value_weight,
            )
        ):
            raise ValueError("revelation parameters must be finite")


def logistic(value: float) -> float:
    value = float(value)
    if value >= 0.0:
        return 1.0 / (1.0 + exp(-value))
    transformed = exp(value)
    return transformed / (1.0 + transformed)


def revelation_logit(
    covariates: RevelationCovariates,
    parameters: RevelationParameters,
) -> float:
    return (
        covariates.feature_intercept
        + parameters.latent_weight * covariates.latent_value
        + parameters.membership_weight * covariates.membership_probability
        - parameters.option_value_weight * covariates.option_value
    )


def revelation_probability(
    covariates: RevelationCovariates,
    parameters: RevelationParameters,
) -> float:
    return logistic(revelation_logit(covariates, parameters))


def preferred_information_state(
    covariates: RevelationCovariates,
    parameters: RevelationParameters,
    *,
    threshold: float = 0.5,
) -> InformationState:
    if not 0.0 < threshold < 1.0:
        raise ValueError("threshold must lie strictly between zero and one")
    probability = revelation_probability(covariates, parameters)
    return InformationState.REVEALED if probability >= threshold else InformationState.NON_REVEALED


def revelation_log_likelihood(
    state: InformationState,
    covariates: RevelationCovariates,
    parameters: RevelationParameters,
) -> float:
    probability = revelation_probability(covariates, parameters)
    if state is InformationState.REVEALED:
        from math import log
        return log(probability)
    from math import log
    return log(1.0 - probability)
