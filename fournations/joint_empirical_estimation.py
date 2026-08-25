from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from statistics import fmean
from typing import Iterable

from .information_revelation import InformationState
from .revelation_selection import RevelationParameters


_EPSILON = 1e-12


@dataclass(frozen=True)
class RevelationObservation:
    latent_value: float
    membership_probability: float
    option_value: float
    state: InformationState

    def __post_init__(self) -> None:
        values = (self.latent_value, self.membership_probability, self.option_value)
        if not all(isfinite(float(value)) for value in values):
            raise ValueError("observation covariates must be finite")
        if not 0.0 <= self.membership_probability <= 1.0:
            raise ValueError("membership_probability must lie in [0, 1]")


@dataclass(frozen=True)
class EstimationResult:
    parameters: RevelationParameters
    log_likelihood: float
    iterations: int


def _sigmoid(value: float) -> float:
    from math import exp
    if value >= 0.0:
        return 1.0 / (1.0 + exp(-value))
    transformed = exp(value)
    return transformed / (1.0 + transformed)


def revelation_log_likelihood(
    observations: Iterable[RevelationObservation],
    parameters: RevelationParameters,
) -> float:
    total = 0.0
    for observation in observations:
        score = (
            parameters.latent_weight * observation.latent_value
            + parameters.membership_weight * observation.membership_probability
            - parameters.option_value_weight * observation.option_value
        )
        probability = min(max(_sigmoid(score), _EPSILON), 1.0 - _EPSILON)
        total += log(probability if observation.state is InformationState.REVEALED else 1.0 - probability)
    return total


def fit_revelation_parameters(
    observations: Iterable[RevelationObservation],
    *,
    learning_rate: float = 0.1,
    iterations: int = 200,
) -> EstimationResult:
    data = tuple(observations)
    if not data:
        raise ValueError("at least one observation is required")
    if learning_rate <= 0.0 or not isfinite(learning_rate):
        raise ValueError("learning_rate must be finite and positive")
    if iterations < 1:
        raise ValueError("iterations must be positive")

    latent_weight = 0.0
    membership_weight = 0.0
    option_value_weight = 0.0
    for _ in range(iterations):
        latent_gradient = 0.0
        membership_gradient = 0.0
        option_gradient = 0.0
        for observation in data:
            score = (
                latent_weight * observation.latent_value
                + membership_weight * observation.membership_probability
                - option_value_weight * observation.option_value
            )
            probability = _sigmoid(score)
            target = 1.0 if observation.state is InformationState.REVEALED else 0.0
            residual = target - probability
            latent_gradient += residual * observation.latent_value
            membership_gradient += residual * observation.membership_probability
            option_gradient -= residual * observation.option_value
        scale = learning_rate / len(data)
        latent_weight += scale * latent_gradient
        membership_weight += scale * membership_gradient
        option_value_weight += scale * option_gradient

    parameters = RevelationParameters(
        latent_weight=latent_weight,
        membership_weight=membership_weight,
        option_value_weight=option_value_weight,
    )
    return EstimationResult(
        parameters=parameters,
        log_likelihood=revelation_log_likelihood(data, parameters),
        iterations=iterations,
    )


def empirical_revelation_rate(observations: Iterable[RevelationObservation]) -> float:
    data = tuple(observations)
    if not data:
        raise ValueError("at least one observation is required")
    return fmean(1.0 if observation.state is InformationState.REVEALED else 0.0 for observation in data)
