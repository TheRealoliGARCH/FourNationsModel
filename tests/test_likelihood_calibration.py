import pytest

from fournations.empirical_evidence import EmpiricalEvidence
from fournations.information_revelation import InformationState
from fournations.likelihood_calibration import (
    calibrate_feature,
    calibrate_from_evidence,
    evidence_likelihood_ratio,
    likelihood_ratio,
)


def record(nation, value, feature="growth"):
    return EmpiricalEvidence(
        cell=(nation, 2017, feature),
        value=value,
        revelation_state=(InformationState.REVEALED if value is not None else InformationState.NON_REVEALED),
        provider="test",
        retrieved_at=None,
    )


def test_calibration_uses_member_and_non_member_samples():
    calibration = calibrate_feature("growth", (4.0, 6.0), (0.0, 2.0))
    assert calibration.member_mean == 5.0
    assert calibration.non_member_mean == 1.0
    assert calibration.pooled_scale > 0.0


def test_member_like_value_has_likelihood_ratio_above_one():
    calibration = calibrate_feature("growth", (4.0, 6.0), (0.0, 2.0))
    assert likelihood_ratio(5.0, calibration) > 1.0
    assert likelihood_ratio(1.0, calibration) < 1.0


def test_non_revealed_records_do_not_enter_calibration():
    calibration = calibrate_from_evidence(
        "growth",
        (record("A", 4.0), record("B", None)),
        (record("C", 0.0), record("D", None)),
    )
    assert calibration.member_mean == 4.0
    assert calibration.non_member_mean == 0.0


def test_batch_evidence_combines_feature_level_log_likelihoods():
    calibration = calibrate_feature("growth", (4.0, 6.0), (0.0, 2.0))
    ratio = evidence_likelihood_ratio((record("A", 5.0), record("B", 5.0)), calibration)
    assert ratio > 1.0


def test_empty_calibration_group_is_rejected():
    with pytest.raises(ValueError):
        calibrate_feature("growth", (), (1.0,))


def test_non_finite_values_are_rejected():
    with pytest.raises(ValueError):
        calibrate_feature("growth", (1.0, float("inf")), (0.0,))
