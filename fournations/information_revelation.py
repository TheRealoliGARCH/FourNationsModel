from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


Cell = tuple[str, int, str]


class InformationState(str, Enum):
    REVEALED = "revealed"
    NON_REVEALED = "non_revealed"


@dataclass(frozen=True)
class RevelationDecision:
    cell: Cell
    state: InformationState
    observed_value: float | None


@dataclass(frozen=True)
class OptionValueAssessment:
    cell: Cell
    reveal_value: float
    retain_value: float

    @property
    def option_value(self) -> float:
        return self.retain_value - self.reveal_value

    @property
    def preferred_state(self) -> InformationState:
        return (
            InformationState.NON_REVEALED
            if self.option_value > 0.0
            else InformationState.REVEALED
        )


def revelation_state(value: float | None) -> InformationState:
    return InformationState.REVEALED if value is not None else InformationState.NON_REVEALED


def classify_panel(panel: Mapping[Cell, float | None]) -> dict[Cell, RevelationDecision]:
    return {
        cell: RevelationDecision(
            cell=cell,
            state=revelation_state(value),
            observed_value=value,
        )
        for cell, value in panel.items()
    }


def assess_option_value(
    cell: Cell,
    *,
    reveal_value: float,
    retain_value: float,
) -> OptionValueAssessment:
    return OptionValueAssessment(
        cell=cell,
        reveal_value=float(reveal_value),
        retain_value=float(retain_value),
    )


def public_information_coverage(panel: Mapping[Cell, float | None]) -> float:
    if not panel:
        return 0.0
    return sum(value is not None for value in panel.values()) / len(panel)
