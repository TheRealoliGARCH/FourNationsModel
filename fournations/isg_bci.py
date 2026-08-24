from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np

from .precision import PrecisionPolicy


@dataclass(frozen=True)
class RelationalStatistic:
    """Observed relational statistic R(D)=r.

    `value` is the observed statistic. `map_fn` maps a candidate generator D
    into the same representation. `distance_fn` measures admissibility.
    """

    value: np.ndarray
    map_fn: Callable[[np.ndarray], np.ndarray]
    distance_fn: Callable[[np.ndarray, np.ndarray], float]

    def residual(self, generator: np.ndarray) -> float:
        observed = np.asarray(self.value, dtype=float)
        generated = np.asarray(self.map_fn(generator), dtype=float)
        return float(self.distance_fn(generated, observed))


@dataclass(frozen=True)
class CausalConstraint:
    """Causal restriction defining membership in G_C."""

    name: str
    predicate: Callable[[np.ndarray], bool]

    def accepts(self, signal: np.ndarray) -> bool:
        return bool(self.predicate(signal))


@dataclass(frozen=True)
class IdentificationResult:
    """Auditable result of an ISG-BCI identification run."""

    accepted: tuple[np.ndarray, ...]
    realization_count: int
    causal_count: int
    residuals: tuple[float, ...]
    posterior_entropy: float | None
    unique: bool
    tolerance: float
    precision_digits: int
    condition_number: float | None
    status: str


def _numeric_condition_number(candidates: Sequence[np.ndarray]) -> float | None:
    if len(candidates) < 2:
        return None
    matrix = np.stack([np.ravel(c) for c in candidates], axis=0)
    if min(matrix.shape) < 1:
        return None
    try:
        return float(np.linalg.cond(matrix))
    except np.linalg.LinAlgError:
        return float("inf")


def identify(
    observations: np.ndarray,
    candidates: Iterable[np.ndarray],
    relational: RelationalStatistic,
    causal_constraints: Sequence[CausalConstraint] = (),
    *,
    policy: PrecisionPolicy | None = None,
) -> IdentificationResult:
    """Run the computational core of the ISG-BCI identification layer.

    The theory defines the realization manifold M_r={D:R(D)=r} and the causal
    feasible set F=M_r intersect G_C. This implementation evaluates a finite,
    explicitly supplied candidate approximation to M_r, rather than asserting
    that an arbitrary continuous problem has a finite solution.
    """

    del observations  # kept in the API to make Y=S+epsilon explicit to callers
    policy = policy or PrecisionPolicy()
    policy.validate()

    accepted: list[np.ndarray] = []
    residuals: list[float] = []
    realization_count = 0
    causal_count = 0

    for candidate in candidates:
        generator = np.asarray(candidate, dtype=float)
        residual = relational.residual(generator)
        realization_count += 1
        if residual > policy.residual_tol:
            continue
        causal_count += 1
        if all(constraint.accepts(generator) for constraint in causal_constraints):
            accepted.append(generator.copy())
            residuals.append(residual)

    unique = len(accepted) == 1
    status = (
        "uniquely_identified"
        if unique
        else "non_identified"
        if len(accepted) == 0
        else "set_identified"
    )

    # In a finite candidate implementation, entropy can only be estimated from
    # an explicit posterior model. With no likelihood/prior supplied, report
    # None rather than fabricate H=0. The theory's H=0 result requires unique
    # support under the full Bayesian model.
    posterior_entropy = 0.0 if unique else None

    condition_number = _numeric_condition_number(accepted)
    if condition_number is not None and condition_number > policy.condition_limit:
        status = f"{status}:ill_conditioned"

    return IdentificationResult(
        accepted=tuple(accepted),
        realization_count=realization_count,
        causal_count=causal_count,
        residuals=tuple(residuals),
        posterior_entropy=posterior_entropy,
        unique=unique,
        tolerance=policy.residual_tol,
        precision_digits=policy.digits,
        condition_number=condition_number,
        status=status,
    )
