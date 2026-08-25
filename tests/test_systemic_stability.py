import pytest

from fournations.systemic_stability import (
    StabilityWeights,
    admission_pressure,
    competitive_instability,
    is_systemically_stable,
    systemic_instability,
)


def probabilities():
    return {"A": 0.90, "B": 0.80, "C": 0.70, "D": 0.60, "E": 0.59}


def test_admission_pressure_measures_top_four_boundary_challenge():
    assert admission_pressure(probabilities()) == pytest.approx(0.0)


def test_competitive_instability_increases_with_tighter_probability_clustering():
    clustered = competitive_instability({"A": 0.51, "B": 0.50, "C": 0.49})
    separated = competitive_instability({"A": 0.90, "B": 0.50, "C": 0.10})
    assert clustered > separated


def test_systemic_function_combines_distinct_stability_components():
    score = systemic_instability(
        probabilities(),
        {"E": 0.10},
        weights=StabilityWeights(2.0, 3.0, 0.0),
    )
    assert score == pytest.approx(0.30)


def test_stability_threshold_is_enforced():
    kwargs = {"weights": StabilityWeights(0.0, 1.0, 0.0)}
    assert is_systemically_stable(probabilities(), {"E": 0.10}, threshold=0.10, **kwargs)
    assert not is_systemically_stable(probabilities(), {"E": 0.10}, threshold=0.09, **kwargs)


def test_invalid_seat_count_is_rejected():
    with pytest.raises(ValueError):
        admission_pressure(probabilities(), seats=5)
