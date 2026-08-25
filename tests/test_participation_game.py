import pytest

from fournations.participation_game import (
    ParticipationDecision,
    admission_threshold,
    minimum_admission_gain,
)


def test_low_admission_gain_can_make_revelation_irrational():
    decision = ParticipationDecision(
        admission_probability_without_revelation=0.01,
        admission_probability_with_revelation=0.02,
        admission_value=100.0,
        revelation_cost=2.0,
        option_value_loss=1.0,
    )
    assert decision.revelation_benefit == pytest.approx(1.0)
    assert decision.revelation_burden == pytest.approx(3.0)
    assert decision.participation_margin == pytest.approx(-2.0)
    assert not decision.should_reveal


def test_boundary_candidate_reveals_when_admission_gain_covers_burden():
    decision = ParticipationDecision(
        admission_probability_without_revelation=0.40,
        admission_probability_with_revelation=0.50,
        admission_value=100.0,
        revelation_cost=6.0,
        option_value_loss=4.0,
    )
    assert decision.participation_margin == pytest.approx(0.0)
    assert decision.should_reveal


def test_threshold_recovers_required_probability_gain():
    assert minimum_admission_gain(100.0, 6.0, 4.0) == pytest.approx(0.1)


def test_threshold_uses_decision_parameters():
    decision = ParticipationDecision(0.2, 0.3, 100.0, 6.0, 4.0)
    assert admission_threshold(decision) == pytest.approx(0.1)


def test_invalid_probability_is_rejected():
    with pytest.raises(ValueError):
        ParticipationDecision(0.0, 1.1, 100.0, 0.0, 0.0)


def test_non_positive_admission_value_is_rejected_for_threshold():
    with pytest.raises(ValueError):
        minimum_admission_gain(0.0, 1.0, 1.0)
