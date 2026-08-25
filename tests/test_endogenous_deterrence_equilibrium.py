import pytest

from fournations.endogenous_deterrence_equilibrium import (
    CandidateStrategy,
    EndogenousDeterrenceGame,
    candidate_probabilities,
    solve_equilibrium,
    top_admissions,
)


def game():
    return EndogenousDeterrenceGame(
        candidates={
            "A": CandidateStrategy(0.70, 0.00, 100.0, 10.0, 0.0),
            "B": CandidateStrategy(0.60, 0.00, 100.0, 10.0, 0.0),
            "C": CandidateStrategy(0.50, 0.00, 100.0, 10.0, 0.0),
            "D": CandidateStrategy(0.40, 0.00, 100.0, 10.0, 0.0),
            "E": CandidateStrategy(0.30, 0.30, 100.0, 5.0, 5.0),
        },
        deterrence_capacity=0.20,
        deterrence_cost_per_unit=50.0,
        incumbent_displacement_loss=100.0,
    )


def test_probability_map_is_endogenous_to_revelation_and_deterrence():
    probabilities = candidate_probabilities(
        game(), {"E": True}, {"E": 0.10}
    )
    assert probabilities["E"] == pytest.approx(0.50)


def test_top_admissions_enforce_sn0g_scarcity_ceiling():
    admissions = top_admissions({"A": 0.9, "B": 0.8, "C": 0.7, "D": 0.6, "E": 0.5})
    assert admissions == ("A", "B", "C", "D")
    assert len(admissions) <= 4


def test_equilibrium_returns_revelation_deterrence_and_admissions():
    result = solve_equilibrium(game())
    assert set(result) == {"revelations", "deterrence", "probabilities", "admissions", "stable"}
    assert len(result["admissions"]) <= 4


def test_capacity_and_scarcity_constraints_are_validated():
    with pytest.raises(ValueError):
        EndogenousDeterrenceGame({}, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError):
        EndogenousDeterrenceGame(
            {"A": CandidateStrategy(0.5, 0.1, 1.0, 0.0, 0.0)},
            0.0, 0.0, 0.0, max_admissions=5,
        )
