from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
from typing import Iterator

import mpmath as mp


@dataclass(frozen=True)
class PrecisionPolicy:
    """Numerical policy for identification decisions.

    `digits` controls arbitrary-precision verification. `abs_tol` and `rel_tol`
    are explicit decision tolerances; they are deliberately not hidden inside
    an algorithm so that sensitivity to tolerance can be audited.
    """

    digits: int = 80
    abs_tol: float = 1e-12
    rel_tol: float = 1e-10
    residual_tol: float = 1e-12
    uniqueness_tol: float = 1e-12
    condition_limit: float = 1e12

    def validate(self) -> None:
        if self.digits < 32:
            raise ValueError("digits must be >= 32 for high-precision verification")
        for name in ("abs_tol", "rel_tol", "residual_tol", "uniqueness_tol"):
            value = getattr(self, name)
            if not (value > 0):
                raise ValueError(f"{name} must be positive")
        if self.condition_limit <= 1:
            raise ValueError("condition_limit must exceed 1")

    @contextmanager
    def workdps(self) -> Iterator[None]:
        self.validate()
        with mp.workdps(self.digits):
            yield

    def close(self, a: float, b: float) -> bool:
        scale = max(1.0, abs(a), abs(b))
        return abs(a - b) <= self.abs_tol + self.rel_tol * scale
