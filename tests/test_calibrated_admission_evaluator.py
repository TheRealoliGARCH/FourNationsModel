import pytest

from fournations.admission_stability_experiment import run_experiment
from fournations.calibrated_admission_evaluator import (
    NationCalibration,
    evaluate_calibrated_posteriors,
)
from fournations.scenario_generation import PerturbationGrid, ScenarioParameters


def calibrations():
    return {
        "A": NationCalibration(0.60, 1.0, 0.1),
        "B": NationCalibration(0.55, 0.8, 0.1),
        "C": NationCalibration(0.50, 0.6, 0.0),
        "D": NationCalibration(0.45, 0.4, 0.0),
        "E": NationCalibration(0.40, 0.2, -0.1),
    }


def test_baseline_parameters_produce_probabilities():
    posteriors = evaluate_calibrated_posteriors(
        calibrations(), ScenarioParameters(1.0, 1.0, 1.0)
    )
    assert all(0.0 < value < 1.0 for value in posteriors.values())
    assert posteriors["A"] > posteriors["E"]


def test_empirical_multiplier_changes_empirical_component():
    low = evaluate_calibrated_posteriors(
        calibrations(), ScenarioParameters(1.0, 0.5, 1.0)
    )
    high = evaluate_calibrated_posteriors(
        calibrations(), ScenarioParameters(1.0, 1.5, 1.0)
    )
    assert high["A"] > low["A"]


def test_runner_uses_calibrated_nation_inputs():
    grid = PerturbationGrid((1.0,), (1.0,), (1.0,))
    result = run_experiment(calibrations(), grid)
    scenario = result["scenarios"][0]
    assert scenario.posteriors == pytest.approx(
        evaluate_calibrated_posteriors(calibrations(), ScenarioParameters(1.0, 1.0, 1.0))
    )


def test_invalid_prior_is_rejected():
    with pytest.raises(ValueError):
        NationCalibration(1.0, 0.0, 0.0)
