from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log
from statistics import fmean, pstdev
from typing import Iterable

from .empirical_evidence import EmpiricalEvidence


_EPSILON = 1e-12


@dataclass(frozen=True)
class FeatureCalibration:
    feature: str
    member_mean: float
    non_member_mean: float
    pooled_scale: float

    def __post_init__(self) -> None:
        if not self.pooled_scale > 0.0 or not isfinite(self.pooled_scale):
            raise ValueError("pooled_scale must be finite and positive")


def _scale(values: tuple[float, ...]) -> float:
    if len(values) < 2:
        return 1.0
    return max(pstdev(values), _EPSILON)


def calibrate_feature(
    feature: str,
    member_values: Iterable[float],
    non_member_values: Iterable[float],
) -> FeatureCalibration:
    member = tuple(float(value) for value in member_values)
    non_member = tuple(float(value) for value in non_member_values)
    if not member or not non_member:
        raise ValueError("both member and non-member samples are required")
    if not all(isfinite(value) for value in member + non_member):
        raise ValueError("calibration values must be finite")
    scale = max((_scale(member) + _scale(non_member)) / 2.0, _EPSILON)
    return FeatureCalibration(
        feature=feature,
        member_mean=fmean(member),
        non_member_mean=fmean(non_member),
        pooled_scale=scale,
    )


def log_likelihood_ratio(value: float, calibration: FeatureCalibration) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError("evidence value must be finite")
    member_distance = ((value - calibration.member_mean) / calibration.pooled_scale) ** 2
    non_member_distance = ((value - calibration.non_member_mean) / calibration.pooled_scale) ** 2
    return 0.5 * (non_member_distance - member_distance)


def likelihood_ratio(value: float, calibration: FeatureCalibration) -> float:
    return exp(log_likelihood_ratio(value, calibration))


def calibrate_from_evidence(
    feature: str,
    member_records: Iterable[EmpiricalEvidence],
    non_member_records: Iterable[EmpiricalEvidence],
) -> FeatureCalibration:
    member_values = [
        record.value
        for record in member_records
        if record.cell[2] == feature and record.value is not None
    ]
    non_member_values = [
        record.value
        for record in non_member_records
        if record.cell[2] == feature and record.value is not None
    ]
    return calibrate_feature(feature, member_values, non_member_values)


def evidence_log_likelihood(records: Iterable[EmpiricalEvidence], calibration: FeatureCalibration) -> float:
    return sum(
        log_likelihood_ratio(record.value, calibration)
        for record in records
        if record.cell[2] == calibration.feature and record.value is not None
    )


def evidence_likelihood_ratio(records: Iterable[EmpiricalEvidence], calibration: FeatureCalibration) -> float:
    return exp(evidence_log_likelihood(records, calibration))
