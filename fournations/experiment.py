from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence
import numpy as np
from .empirical import DatasetSnapshot, Observation
from .generator import FeatureSpec, build_generator, build_states, candidate_generators, pairwise_distance_statistic
from .isg_bci import CausalConstraint, RelationalStatistic, identify
from .tolerance import ToleranceCertificate, audit_tolerance

@dataclass(frozen=True)
class PilotSpec:
    economies: tuple[str,str,str,str]
    period: str
    features: tuple[FeatureSpec,...]
    perturbations: Mapping[str,Sequence[float]]

@dataclass(frozen=True)
class EmpiricalExperiment:
    spec: PilotSpec
    snapshot_checksum: str
    candidate_count: int
    identification_status: str
    tolerance: ToleranceCertificate

def run_pilot(snapshot: DatasetSnapshot, spec: PilotSpec, *, constraints: Sequence[CausalConstraint]=()) -> EmpiricalExperiment:
    observations=tuple(snapshot.observations)
    states=build_states(observations,spec.economies,spec.period,spec.features)
    base=build_generator(states)
    candidates=candidate_generators(base,spec.perturbations)
    observed=pairwise_distance_statistic(base)
    relational=RelationalStatistic(
        value=observed,
        map_fn=lambda x: pairwise_distance_statistic(type(base)(base.economies,base.period,np.asarray(x).reshape(base.state_matrix.shape),base.feature_names)),
        distance_fn=lambda a,b: float(np.linalg.norm(a-b)),
    )
    arrays=tuple(c.flattened() for c in candidates)
    first=identify(base.flattened(),arrays,relational,constraints)
    certificate=audit_tolerance(base.flattened(),arrays,relational,constraints)
    return EmpiricalExperiment(spec,snapshot.checksum,len(arrays),first.status,certificate)
