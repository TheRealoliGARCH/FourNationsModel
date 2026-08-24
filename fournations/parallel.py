from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class JobResult:
    index: int
    ok: bool
    value: object | None
    error: str | None


def run_parallel(
    jobs: Sequence[T],
    worker: Callable[[T], R],
    *,
    max_workers: int | None = None,
) -> list[JobResult]:
    """Run independent identification jobs with process-level fault isolation."""
    results: list[JobResult] = [JobResult(i, False, None, "not completed") for i in range(len(jobs))]
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        future_map = {pool.submit(worker, job): i for i, job in enumerate(jobs)}
        for future in as_completed(future_map):
            index = future_map[future]
            try:
                results[index] = JobResult(index, True, future.result(), None)
            except Exception as exc:  # one failed worker must not erase completed jobs
                results[index] = JobResult(index, False, None, f"{type(exc).__name__}: {exc}")
    return results


class DistributedRunner:
    """Scheduler-neutral interface for outer-node distribution.

    A cluster backend can implement `map` (Ray, Dask, Slurm launcher, Kubernetes
    jobs, etc.). The mathematical worker contract remains unchanged.
    """

    def map(self, worker: Callable[[T], R], jobs: Iterable[T]) -> list[R]:
        raise NotImplementedError
