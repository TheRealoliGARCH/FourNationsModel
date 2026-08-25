from pathlib import Path

from fournations.admission_stability_experiment import run_experiment, write_scenario_results
from fournations.calibrated_admission_evaluator import NationCalibration
from fournations.scenario_generation import PerturbationGrid


def calibrations():
    return {
        "A": NationCalibration(0.60, 1.0, 0.1),
        "B": NationCalibration(0.55, 0.8, 0.1),
        "C": NationCalibration(0.50, 0.6, 0.0),
        "D": NationCalibration(0.45, 0.4, 0.0),
        "E": NationCalibration(0.40, 0.2, -0.1),
    }


def grid():
    return PerturbationGrid(
        prior_multipliers=(0.9, 1.0),
        empirical_multipliers=(0.9, 1.0),
        revelation_multipliers=(0.9, 1.0),
    )


def test_experiment_runs_full_factorial_grid():
    result = run_experiment(calibrations(), grid())
    assert len(result["scenarios"]) == 8
    assert result["invariant_admissions"] == ("A", "B", "C", "D")
    assert result["robustness_score"] == 1.0


def test_experiment_reports_no_flips_when_rank_order_is_preserved():
    result = run_experiment(calibrations(), grid())
    assert result["flip_pairs"] == ()


def test_results_writer_creates_reproducible_csv(tmp_path: Path):
    result = run_experiment(calibrations(), grid())
    output = tmp_path / "results.csv"
    write_scenario_results(result, output)
    text = output.read_text(encoding="utf-8")
    assert text.startswith("scenario,admitted_nations")
    assert text.count("prior=") == 8
