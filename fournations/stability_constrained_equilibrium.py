from __future__ import annotations

from typing import Any

from fournations.endogenous_deterrence_equilibrium import (
    EndogenousDeterrenceGame,
    candidate_probabilities,
    optimal_deterrence,
    revelation_best_responses,
    top_admissions,
)
from fournations.sn0g_epistemic_stability import (
    EpistemicState,
    StabilityGate,
    evaluate_equilibrium_stability,
)


def solve_stability_constrained_equilibrium(
    game: EndogenousDeterrenceGame,
    epistemic_state: EpistemicState,
    gate: StabilityGate,
    *,
    max_iterations: int = 100,
) -> dict[str, Any]:
    """Return a fixed point only when it also passes the SNoG stability gate."""
    revelations = {name: False for name in game.candidates}

    for _ in range(max_iterations):
        deterrence = optimal_deterrence(game, revelations)
        next_revelations = revelation_best_responses(game, deterrence)
        if next_revelations == revelations:
            probabilities = candidate_probabilities(game, revelations, deterrence)
            admissions = top_admissions(probabilities, game.max_admissions)
            stability = evaluate_equilibrium_stability(
                probabilities,
                deterrence,
                epistemic_state=epistemic_state,
                gate=gate,
                seats=game.max_admissions,
            )
            return {
                "revelations": revelations,
                "deterrence": deterrence,
                "probabilities": probabilities,
                "admissions": admissions,
                "strategic_fixed_point": True,
                "systemically_admissible": stability.is_stable,
                "stability_score": stability.score,
                "rejection_reason": None if stability.is_stable else "stability_gate",
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
