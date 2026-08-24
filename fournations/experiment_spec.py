from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NationAnchor:
    nation: str
    role: str
    basis: str


FIRST_EXPERIMENT_ANCHORS = (
    NationAnchor("USA", "institution_host", "IMF and World Bank headquarters"),
    NationAnchor("CHE", "institution_host", "BIS headquarters"),
    NationAnchor("FRA", "institution_host", "OECD headquarters"),
    NationAnchor("IND", "author_origin", "author is from Kolkata, India"),
)


def first_experiment_nations() -> tuple[str, str, str, str]:
    nations = tuple(anchor.nation for anchor in FIRST_EXPERIMENT_ANCHORS)
    if len(nations) != 4 or len(set(nations)) != 4:
        raise ValueError("first experiment must contain exactly four distinct nations")
    return nations
