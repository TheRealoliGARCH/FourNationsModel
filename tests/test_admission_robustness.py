import pytest

from fournations.admission_robustness import (
    AdmissionScenario,
    admission_flip_pairs,
    admitted_nations,
    invariant_admissions,
    robustness_score,
    scenario_admissions,
)


def scenarios():
    return (
        AdmissionScenario("baseline", {"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.6, "E": 0.5}),
        AdmissionScenario("prior_low", {"A": 0.85, "B": 0.8, "C": 0.7, "D": 0.55, "E": 0.65}),
        AdmissionScenario("selection_high", {"A": 0.88, "B": 0.79, "C": 0.71, "D": 0.58, "E": 0.62}),
    )


def test_admission_is_deterministic_with_name_tie_breaking():
    admitted = admitted_nations({"B": 0.5, "A": 0.5, "C": 0.4}, seats=2)
    assert admitted == ("A", "B")


def test_scenario_admissions_preserve_all_scenarios():
    admissions = scenario_admissions(scenarios())
    assert tuple(admissions) == ("baseline", "prior_low", "selection_high")
    assert admissions["baseline"] == ("A", "B", "C", "D")


def test_invariant_admissions_identify_stable_seats():
    assert invariant_admissions(scenarios()) == ("A", "B", "C")


def test_flip_pairs_identify_ranking_changes():
    flips = admission_flip_pairs(scenarios())
    assert flips == (("baseline", "prior_low"), ("baseline", "selection_high"))


def test_robustness_score_is_fraction_of_invariant_seats():
    assert robustness_score(scenarios()) == pytest.approx(0.75)


def test_empty_scenario_collection_is_rejected():
    with pytest.raises(ValueError):
        invariant_admissions(())
