import pytest

from fournations.scenario_generation import (
    PerturbationGrid,
    ScenarioParameters,
    generate_parameters,
    generate_scenarios,
    stability_region,
)


def grid():
    return PerturbationGrid(
        prior_multipliers=(0.8, 1.0),
        empirical_multipliers=(1.0, 1.2),
        revelation_multipliers=(0.9, 1.1),
    )


def evaluator(parameters):
    return {
        "A": 0.90,
        "B": 0.80,
        "C": 0.70,
        "D": 0.60 + 0.01 * parameters.empirical_multiplier,
        "E": 0.50,
    }


def test_grid_generates_full_factorial_parameter_coverage():
    parameters = generate_parameters(grid())
    assert len(parameters) == 8
    assert parameters[0] == ScenarioParameters(0.8, 1.0, 0.9)
    assert parameters[-1] == ScenarioParameters(1.0, 1.2, 1.1)


def test_generated_scenarios_are_deterministic_and_named():
    scenarios = generate_scenarios(grid(), evaluator)
    assert len(scenarios) == 8
    assert scenarios[0].name == "prior=0.8|empirical=1|revelation=0.9"
    assert scenarios[0].posteriors["A"] == 0.90


def test_stability_region_returns_scenarios_with_target_top_four():
    scenarios = generate_scenarios(grid(), evaluator)
    region = stability_region(scenarios, ("A", "B", "C", "D"))
    assert len(region) == 8


def test_stability_region_can_be_empty():
    scenarios = generate_scenarios(grid(), evaluator)
    assert stability_region(scenarios, ("A", "B", "C", "E")) == ()


def test_empty_grid_dimension_is_rejected():
    with pytest.raises(ValueError):
        PerturbationGrid((), (1.0,), (1.0,))


def test_negative_multiplier_is_rejected():
    with pytest.raises(ValueError):
        PerturbationGrid((-0.1,), (1.0,), (1.0,))
