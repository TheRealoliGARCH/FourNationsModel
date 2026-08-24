from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Mapping, Sequence
import numpy as np
from .empirical import Observation

@dataclass(frozen=True)
class FeatureSpec:
    name: str
    series_id: str
    transform: Callable[[float], float] = lambda x: x

@dataclass(frozen=True)
class NationState:
    economy: str
    period: str
    values: tuple[float, ...]
    feature_names: tuple[str, ...]

    def vector(self) -> np.ndarray:
        return np.asarray(self.values, dtype=float)

@dataclass(frozen=True)
class Generator:
    economies: tuple[str, ...]
    period: str
    state_matrix: np.ndarray
    feature_names: tuple[str, ...]

    def flattened(self) -> np.ndarray:
        return self.state_matrix.reshape(-1)

class PanelConstructionError(ValueError): pass

def build_states(observations: Iterable[Observation], economies: Sequence[str], period: str, features: Sequence[FeatureSpec]) -> tuple[NationState, ...]:
    index: dict[tuple[str,str], Observation] = {}
    for o in observations:
        if o.period == period:
            index[(o.economy.upper(), o.series_id)] = o
    states=[]
    for economy in economies:
        values=[]
        for f in features:
            key=(economy.upper(), f.series_id)
            if key not in index:
                raise PanelConstructionError(f"missing {f.series_id} for {economy} at {period}")
            values.append(float(f.transform(index[key].value)))
        states.append(NationState(economy.upper(), period, tuple(values), tuple(f.name for f in features)))
    return tuple(states)

def build_generator(states: Sequence[NationState]) -> Generator:
    if len(states) != 4:
        raise PanelConstructionError("Four Nations Model requires exactly four nation states")
    period=states[0].period; names=states[0].feature_names
    if any(s.period != period or s.feature_names != names for s in states):
        raise PanelConstructionError("states must share period and feature schema")
    economies=tuple(s.economy for s in states)
    if len(set(economies)) != 4: raise PanelConstructionError("economies must be distinct")
    return Generator(economies, period, np.vstack([s.vector() for s in states]), names)

def candidate_generators(base: Generator, perturbations: Mapping[str, Sequence[float]]) -> tuple[Generator, ...]:
    grids=[tuple(perturbations.get(name, (0.0,))) for name in base.feature_names]
    candidates=[]
    for delta in product(*grids):
        shift=np.asarray(delta,dtype=float)
        candidates.append(Generator(base.economies, base.period, base.state_matrix + shift, base.feature_names))
    return tuple(candidates)

def pairwise_distance_statistic(generator: Generator, norm: int | float = 2) -> np.ndarray:
    x=generator.state_matrix
    return np.asarray([np.linalg.norm(x[i]-x[j], ord=norm) for i in range(4) for j in range(i+1,4)])

def rank_signature(generator: Generator) -> np.ndarray:
    return np.vstack([np.argsort(np.argsort(generator.state_matrix[:,j])) for j in range(generator.state_matrix.shape[1])]).T
