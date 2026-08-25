from __future__ import annotations

from typing import Any, Mapping

from fournations.endogenous_deterrence_equilibrium import (
    EndogenousDeterrenceGame,
    candidate_probabilities,
    optimal_deterrence,
    revelation_best_responses,
    top_admissions,
)
from fournations.sn0g_stability_gate import EpistemicState, select_stable_equilibrium
from fournations.systemic_stability import StabilityWeights


def solve_stability_constrained_equilibrium(
    game: EndogenousDeterrenceGame,
    epistemic_states: Mapping[str, EpistemicState],
    *,
    threshold: float,
    epistemic_weight: float = 1.0,
    stability_weights: StabilityWeights | None = None,
    max_iterations: int = 100,
) -> dict[str, Any]:
    """Return a strategic fixed point together with its SNoG stability verdict."""
    revelations = {name: False for name in game.candidates}

    if set(epistemic_states) != set(game.candidates):
        raise ValueError("epistemic states must match game candidates")

    for _ in range(max_iterations):
        deterrence = optimal_deterrence(game, revelations)
        next_revelations = revelation_best_responses(game, deterrence)
        if next_revelations == revelations:
            probabilities = candidate_probabilities(game, revelations, deterrence)
            admissions = top_admissions(probabilities, game.max_admissions)
            equilibrium = {
                "revelations": revelations,
                "deterrence": deterrence,
                "probabilities": probabilities,
                "admissions": admissions,
                "strategic_fixed_point": True,
            }
            selected = select_stable_equilibrium(
                equilibrium,
                epistemic_states,
                threshold=threshold,
                epistemic_weight=epistemic_weight,
                seats=game.max_admissions,
                weights=stability_weights,
            )
            stable = bool(selected["systemically_stable"])
            return {
                **selected,
                "systemically_admissible": stable,
                "stability_score": selected["systemic_instability"],
                "rejection_reason": None if stable else "stability_gate",
            }
        revelations = next_revelations

    return {
        "revelations": revelations,
        "deterrence": {},
        "probabilities": {},
        "admissions": (),
        "strategic_fixed_point": False,
        "systemically_admissible": False,
        "stability_score": None,
        "rejection_reason": "no_fixed_point",
    }
