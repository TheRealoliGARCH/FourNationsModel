from __future__ import annotations

import csv
from pathlib import Path
from typing import Mapping

from fournations.admission_robustness import (
    admission_flip_pairs,
    invariant_admissions,
    robustness_score,
)
from fournations.scenario_generation import (
    PerturbationGrid,
    ScenarioParameters,
    generate_scenarios,
)


def scaled_posteriors(
    baseline: Mapping[str, float],
    parameters: ScenarioParameters,
) -> dict[str, float]:
    scale = (
        parameters.prior_multiplier
        * parameters.empirical_multiplier
        * parameters.revelation_multiplier
    )
    return {
        nation: min(max(float(posterior) * scale, 0.0), 1.0)
        for nation, posterior in baseline.items()
    }


def run_experiment(
    baseline: Mapping[str, float],
    grid: PerturbationGrid,
    *,
    seats: int = 4,
) -> dict[str, object]:
    scenarios = generate_scenarios(
        grid,
        lambda parameters: scaled_posteriors(baseline, parameters),
    )
    return {
        "scenarios": scenarios,
        "invariant_admissions": invariant_admissions(scenarios, seats=seats),
        "flip_pairs": admission_flip_pairs(scenarios, seats=seats),
        "robustness_score": robustness_score(scenarios, seats=seats),
    }


def write_scenario_results(result: Mapping[str, object], path: str | Path, *, seats: int = 4) -> None:
    from fournations.admission_robustness import admitted_nations

    scenarios = result["scenarios"]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("scenario", "admitted_nations"))
        for scenario in scenarios:
            writer.writerow((
                scenario.name,
                ";".join(admitted_nations(scenario.posteriors, seats)),
            ))


def main() -> None:
    baseline = {"A": 0.90, "B": 0.80, "C": 0.70, "D": 0.60, "E": 0.50}
    grid = PerturbationGrid(
        prior_multipliers=(0.9, 1.0, 1.1),
        empirical_multipliers=(0.9, 1.0, 1.1),
        revelation_multipliers=(0.9, 1.0, 1.1),
    )
    result = run_experiment(baseline, grid)
    write_scenario_results(result, "results/admission_stability_scenarios.csv")
    print("invariant_admissions=", result["invariant_admissions"])
    print("flip_pairs=", result["flip_pairs"])
    print("robustness_score=", result["robustness_score"])


if __name__ == "__main__":
    main()
