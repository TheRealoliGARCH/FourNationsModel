import pytest

from fournations.revelation_deterrence_game import (
    CandidateIncumbentGame,
    pure_strategy_equilibrium,
)


def test_incumbents_deter_when_expected_seat_loss_exceeds_cost():
    game = CandidateIncumbentGame(
        probability_without_revelation=0.10,
        probability_with_revelation=0.70,
        admission_value=100.0,
        revelation_cost=5.0,
        option_value_loss=5.0,
        deterrence_effect=0.30,
        incumbent_loss_if_admitted=100.0,
        deterrence_cost=20.0,
    )
    assert game.incumbent_deterrence_benefit == pytest.approx(30.0)
    assert game.incumbents_should_deter


def test_deterrence_can_reverse_candidate_revelation_incentive():
    game = CandidateIncumbentGame(
        probability_without_revelation=0.10,
        probability_with_revelation=0.30,
        admission_value=100.0,
        revelation_cost=8.0,
        option_value_loss=7.0,
        deterrence_effect=0.20,
        incumbent_loss_if_admitted=100.0,
        deterrence_cost=10.0,
    )
    assert game.candidate_should_reveal(deter=False)
    assert not game.candidate_should_reveal(deter=True)
    assert pure_strategy_equilibrium(game) == (False, True)


def test_candidate_can_reveal_despite_deterrence():
    game = CandidateIncumbentGame(
        probability_without_revelation=0.10,
        probability_with_revelation=0.90,
        admission_value=100.0,
        revelation_cost=10.0,
        option_value_loss=10.0,
        deterrence_effect=0.20,
        incumbent_loss_if_admitted=100.0,
        deterrence_cost=10.0,
    )
    assert pure_strategy_equilibrium(game) == (True, True)


def test_no_deterrence_and_no_revelation_equilibrium():
    game = CandidateIncumbentGame(
        probability_without_revelation=0.10,
        probability_with_revelation=0.15,
        admission_value=100.0,
        revelation_cost=10.0,
        option_value_loss=10.0,
        deterrence_effect=0.02,
        incumbent_loss_if_admitted=100.0,
        deterrence_cost=10.0,
    )
    assert pure_strategy_equilibrium(game) == (False, False)


def test_invalid_deterrence_effect_is_rejected():
    with pytest.raises(ValueError):
        CandidateIncumbentGame(0.1, 0.2, 1.0, 0.0, 0.0, 1.1, 1.0, 0.0)
