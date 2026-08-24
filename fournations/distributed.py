from __future__ import annotations
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, Generic, Iterable, Sequence, TypeVar

T = TypeVar('T'); R = TypeVar('R')

@dataclass(frozen=True)
class Shard(Generic[T]):
    shard_id: int
    candidates: tuple[T, ...]

@dataclass(frozen=True)
class ShardResult(Generic[R]):
    shard_id: int
    status: str
    values: tuple[R, ...] = ()
    error: str | None = None

@dataclass(frozen=True)
class DistributedResult(Generic[R]):
    shards: tuple[ShardResult[R], ...]
    complete: bool
    def values(self) -> tuple[R, ...]:
        return tuple(v for shard in self.shards if shard.status == 'completed' for v in shard.values)
    def failures(self) -> tuple[ShardResult[R], ...]:
        return tuple(s for s in self.shards if s.status == 'failed')

def partition(candidates: Sequence[T], shard_size: int) -> tuple[Shard[T], ...]:
    if shard_size < 1: raise ValueError('shard_size must be positive')
    return tuple(Shard(i, tuple(candidates[i*shard_size:(i+1)*shard_size])) for i in range((len(candidates)+shard_size-1)//shard_size))

def _evaluate(shard: Shard[T], fn: Callable[[T], R]) -> ShardResult[R]:
    try:
        return ShardResult(shard.shard_id, 'completed', tuple(fn(x) for x in shard.candidates))
    except Exception as exc:
        return ShardResult(shard.shard_id, 'failed', error=f'{type(exc).__name__}: {exc}')

def execute(candidates: Sequence[T], fn: Callable[[T], R], *, shard_size: int = 128, workers: int | None = None) -> DistributedResult[R]:
    shards = partition(candidates, shard_size)
    results: list[ShardResult[R]] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_evaluate, shard, fn) for shard in shards]
        for future in as_completed(futures):
            results.append(future.result())
    ordered = tuple(sorted(results, key=lambda x: x.shard_id))
    return DistributedResult(ordered, all(x.status == 'completed' for x in ordered))

def merge_strict(result: DistributedResult[R]) -> tuple[R, ...]:
    if not result.complete:
        failed = ', '.join(str(x.shard_id) for x in result.failures())
        raise RuntimeError(f'incomplete distributed evaluation; failed shards: {failed}')
    return result.values()
