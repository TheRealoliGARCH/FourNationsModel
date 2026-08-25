import pytest

from fournations.membership import (
    MAX_MEMBERS,
    Candidate,
    admit,
    challenger_can_displace,
    membership_manifest,
)


def candidate(name, latent, revealed):
    return Candidate(name, latent, revealed)


def test_membership_is_capped_at_four():
    candidates = [candidate(f"N{i}", 10 - i, 10 - i) for i in range(6)]
    decision = admit(candidates)
    assert len(decision.admitted) == MAX_MEMBERS
    assert decision.admitted == ("N0", "N1", "N2", "N3")
    assert decision.excluded == ("N4", "N5")


def test_membership_uses_recognized_capability_not_latent_assertion():
    candidates = [
        candidate("latent_only", 100.0, 1.0),
        candidate("recognized", 5.0, 5.0),
    ]
    decision = admit(candidates, max_members=1)
    assert decision.admitted == ("recognized",)
    assert decision.excluded == ("latent_only",)


def test_challenger_must_exceed_incumbent_to_displace():
    incumbent = candidate("incumbent", 10.0, 7.0)
    assert challenger_can_displace(candidate("equal", 20.0, 7.0), incumbent) is False
    assert challenger_can_displace(candidate("better", 8.0, 7.1), incumbent) is True


def test_candidate_retains_recognition_gap():
    c = candidate("withheld", 9.0, 6.5)
    assert c.recognition_gap == 2.5


def test_membership_manifest_records_scarcity_boundary():
    manifest = membership_manifest(
        [candidate(f"N{i}", 10 - i, 10 - i) for i in range(5)]
    )
    assert manifest["max_members"] == 4
    assert manifest["candidate_count"] == 5
    assert len(manifest["admitted"]) == 4
    assert manifest["excluded"] == ["N4"]


def test_membership_cap_cannot_exceed_theoretical_bound():
    with pytest.raises(ValueError):
        admit([candidate("N", 1.0, 1.0)], max_members=5)
