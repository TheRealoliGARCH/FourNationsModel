from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

MAX_MEMBERS = 4


@dataclass(frozen=True)
class Candidate:
    nation: str
    latent_capability: float
    revealed_capability: float

    @property
    def recognition_gap(self) -> float:
        return self.latent_capability - self.revealed_capability


@dataclass(frozen=True)
class MembershipDecision:
    admitted: tuple[str, ...]
    excluded: tuple[str, ...]
    cutoff_score: float | None


def recognition_score(candidate: Candidate) -> float:
    """Membership is earned on recognized, not merely asserted, capability."""
    return float(candidate.revealed_capability)


def admit(candidates: Iterable[Candidate], *, max_members: int = MAX_MEMBERS) -> MembershipDecision:
    if max_members < 1 or max_members > MAX_MEMBERS:
        raise ValueError(f"max_members must lie in [1, {MAX_MEMBERS}]")

    ranked = sorted(candidates, key=lambda c: (-recognition_score(c), c.nation))
    admitted_candidates = ranked[:max_members]
    excluded_candidates = ranked[max_members:]
    cutoff = recognition_score(admitted_candidates[-1]) if admitted_candidates else None
    return MembershipDecision(
        admitted=tuple(c.nation for c in admitted_candidates),
        excluded=tuple(c.nation for c in excluded_candidates),
        cutoff_score=cutoff,
    )


def challenger_can_displace(
    challenger: Candidate,
    incumbent: Candidate,
) -> bool:
    return recognition_score(challenger) > recognition_score(incumbent)


def membership_manifest(
    candidates: Iterable[Candidate],
    *,
    max_members: int = MAX_MEMBERS,
) -> Mapping[str, object]:
    candidates = tuple(candidates)
    decision = admit(candidates, max_members=max_members)
    return {
        "max_members": max_members,
        "candidate_count": len(candidates),
        "admitted": list(decision.admitted),
        "excluded": list(decision.excluded),
        "cutoff_score": decision.cutoff_score,
    }
