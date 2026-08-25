from fournations.endogenous_deterrence_equilibrium import (
    CandidateStrategy,
    EndogenousDeterrenceGame,
)
from fournations.sn0g_epistemic_stability import EpistemicState, StabilityGate
from fournations.systemic_stability import StabilityWeights
from fournations.stability_constrained_equilibrium import (
    solve_stability_constrained_equilibrium,
)


def game():
    return EndogenousDeterrenceGame(
        candidates={
            "A": CandidateStrategy(0.9, 0.0, 100.0, 1.0, 0.0),
            "B": CandidateStrategy(0.8, 0.0, 100.0, 1.0, 0.0),
            "C": CandidateStrategy(0.7, 0.0, 100.0, 1.0, 0.0),
            "D": CandidateStrategy(0.6, 0.0, 100.0, 1.0, 0.0),
        },
        deterrence_capacity=0.0,
        deterrence_cost_per_unit=0.0,
        incumbent_displacement_loss=0.0,
    )


def test_stable_fixed_point_is_admissible():
    result = solve_stability_constrained_equilibrium(
        game(),
        EpistemicState(unknown_uncertainty=0.0),
        StabilityGate(
            threshold=1.0,
            epistemic_weight=0.0,
            stability_weights=StabilityWeights(0.0, 0.0, 0.0),
        ),
    )
    assert result["strategic_fixed_point"]
    assert result["systemically_admissible"]
    assert result["rejection_reason"] is None
    assert len(result["admissions"]) <= 4


def test_unstable_fixed_point_is_rejected():
    result = solve_stability_constrained_equilibrium(
        game(),
        EpistemicState(unknown_uncertainty=1.0),
        StabilityGate(
            threshold=0.5,
            epistemic_weight=1.0,
            stability_weights=StabilityWeights(0.0, 0.0, 0.0),
        ),
    )
    assert result["strategic_fixed_point"]
    assert not result["systemically_admissible"]
    assert result["rejection_reason"] == "stability_gate"


def test_no_fixed_point_is_not_admissible():
    result = solve_stability_constrained_equilibrium(
        game(),
        EpistemicState(unknown_uncertainty=0.0),
        StabilityGate(
            threshold=1.0,
            epistemic_weight=0.0,
            stability_weights=StabilityWeights(0.0, 0.0, 0.0),
        ),
        max_iterations=0,
    )
    assert not result["strategic_fixed_point"]
    assert not result["systemically_admissible"]
    assert result["rejection_reason"] == "no_fixed_point"
