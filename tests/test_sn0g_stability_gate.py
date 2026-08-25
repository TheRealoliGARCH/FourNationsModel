import pytest

from fournations.sn0g_stability_gate import (
    EpistemicState,
    epistemic_uncertainty,
    select_stable_equilibrium,
    sn0g_adjusted_instability,
)
from fournations.systemic_stability import StabilityWeights


def states():
    return {
        "A": EpistemicState(True, 0.8),
        "B": EpistemicState(False, 0.6, 0.4),
        "C": EpistemicState(True, 0.5),
    }


def equilibrium():
    return {
        "probabilities": {"A": 0.8, "B": 0.6, "C": 0.5},
        "deterrence": {"A": 0.0, "B": 0.1, "C": 0.0},
        "admissions": ("A", "B", "C"),
        "stable": True,
    }


def test_epistemic_uncertainty_preserves_known_unknown_distinction():
    assert epistemic_uncertainty(states()) == pytest.approx(0.4 / 3.0)


def test_adjusted_instability_adds_epistemic_component():
    score = sn0g_adjusted_instability(
        equilibrium()["probabilities"],
        equilibrium()["deterrence"],
        states(),
        epistemic_weight=2.0,
        weights=StabilityWeights(0.0, 0.0, 0.0),
    )
    assert score == pytest.approx(0.8 / 3.0)


def test_stability_gate_accepts_or_rejects_same_equilibrium_by_threshold():
    kwargs = {
        "epistemic_weight": 1.0,
        "weights": StabilityWeights(0.0, 0.0, 0.0),
    }
    accepted = select_stable_equilibrium(equilibrium(), states(), threshold=0.2, **kwargs)
    rejected = select_stable_equilibrium(equilibrium(), states(), threshold=0.1, **kwargs)
    assert accepted["systemically_stable"]
    assert not rejected["systemically_stable"]


def test_known_state_cannot_carry_unknown_uncertainty():
    with pytest.raises(ValueError):
        EpistemicState(True, 0.5, 0.1)


def test_probability_and_epistemic_keys_must_match():
    with pytest.raises(ValueError):
        sn0g_adjusted_instability(
            {"A": 0.5}, {}, {"B": EpistemicState(True, 0.5)}
        )
