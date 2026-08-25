from pathlib import Path

import pytest

from empirical.run_admission_stability_experiment import (
    run_experiment,
    scaled_posteriors,
    write_scenario_results,
)
from fournations.scenario_generation import PerturbationGrid, ScenarioParameters


def baseline():
    return {"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.6, "E": 0.5}


def grid():
    return PerturbationGrid(
        prior_multipliers=(0.9, 1.0),
        empirical_multipliers=(0.9, 1.0),
        revelation_multipliers=(0.9, 1.0),
    )


def test_scaled_posteriors_apply_explicit_combined_multiplier():
    parameters = ScenarioParameters(1.0, 1.1, 1.0)
    scaled = scaled_posteriors(baseline(), parameters)
    assert scaled["A"] == pytest.approx(0.99)
    assert scaled["E"] == pytest.approx(0.55)


def test_experiment_runs_full_factorial_grid():
    result = run_experiment(baseline(), grid())
    assert len(result["scenarios"]) == 8
    assert result["invariant_admissions"] == ("A", "B", "C", "D")
    assert result["robustness_score"] == 1.0


def test_experiment_reports_no_flips_when_rank_order_is_preserved():
    result = run_experiment(baseline(), grid())
    assert result["flip_pairs"] == ()


def test_results_writer_creates_reproducible_csv(tmp_path: Path):
    result = run_experiment(baseline(), grid())
    output = tmp_path / "results.csv"
    write_scenario_results(result, output)
    text = output.read_text(encoding="utf-8")
    assert text.startswith("scenario,admitted_nations")
    assert text.count("prior=") == 8
