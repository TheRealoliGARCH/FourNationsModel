from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np

from .isg_bci import CausalConstraint, IdentificationResult, RelationalStatistic, identify
from .precision import PrecisionPolicy


@dataclass(frozen=True)
class ToleranceLevel:
    residual_tol: float
    digits: int


@dataclass(frozen=True)
class ToleranceCertificate:
    levels: tuple[ToleranceLevel, ...]
    results: tuple[IdentificationResult, ...]
    stable: bool
    classification_path: tuple[str, ...]
    accepted_count_path: tuple[int, ...]
    boundary_indices: tuple[int, ...]
    certificate_status: str

    @property
    def final(self) -> IdentificationResult:
        return self.results[-1]


def geometric_ladder(
    initial_tolerance: float = 1e-8,
    *,
    levels: int = 5,
    shrink: float = 0.1,
    initial_digits: int = 50,
    digits_step: int = 25,
) -> tuple[ToleranceLevel, ...]:
    if initial_tolerance <= 0 or not 0 < shrink < 1 or levels < 2:
        raise ValueError("invalid tolerance ladder")
    return tuple(
        ToleranceLevel(
            residual_tol=initial_tolerance * shrink**k,
            digits=initial_digits + digits_step * k,
        )
        for k in range(levels)
    )


def audit_tolerance(
    observations: np.ndarray,
    candidates: Iterable[np.ndarray],
    relational: RelationalStatistic,
    causal_constraints: Sequence[CausalConstraint] = (),
    *,
    ladder: Sequence[ToleranceLevel] | None = None,
    condition_limit: float = 1e12,
) -> ToleranceCertificate:
    """Audit identification stability across progressively scarce tolerances.

    Candidates are materialized once so every rung sees the identical search
    space. Stability requires the identification classification and accepted
    support cardinality to remain unchanged over the complete ladder.
    """
    materialized = tuple(np.asarray(c, dtype=float) for c in candidates)
    ladder = tuple(ladder or geometric_ladder())
    if len(ladder) < 2:
        raise ValueError("at least two tolerance levels are required")

    results: list[IdentificationResult] = []
    for level in ladder:
        policy = PrecisionPolicy(
            digits=level.digits,
            residual_tol=level.residual_tol,
            condition_limit=condition_limit,
        )
        results.append(
            identify(
                observations,
                materialized,
                relational,
                causal_constraints,
                policy=policy,
            )
        )

    classifications = tuple(r.status.split(":", 1)[0] for r in results)
    counts = tuple(len(r.accepted) for r in results)
    stable = len(set(classifications)) == 1 and len(set(counts)) == 1

    # Boundary cases are candidates accepted at the loosest level but rejected
    # at the tightest level. They are the observations consuming tolerance.
    loosest = set(range(len(materialized)))
    residuals = [relational.residual(c) for c in materialized]
    loose_tol = ladder[0].residual_tol
    tight_tol = ladder[-1].residual_tol
    boundary = tuple(
        i for i, residual in enumerate(residuals)
        if tight_tol < residual <= loose_tol and i in loosest
    )

    ill = any("ill_conditioned" in r.status for r in results)
    certificate_status = (
        "certified" if stable and not ill else
        "unstable_tolerance_path" if not stable else
        "ill_conditioned"
    )

    return ToleranceCertificate(
        levels=ladder,
        results=tuple(results),
        stable=stable,
        classification_path=classifications,
        accepted_count_path=counts,
        boundary_indices=boundary,
        certificate_status=certificate_status,
    )
