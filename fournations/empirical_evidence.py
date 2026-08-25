from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .information_revelation import Cell, InformationState, revelation_state


@dataclass(frozen=True)
class EmpiricalEvidence:
    cell: Cell
    value: float | None
    revelation_state: InformationState
    provider: str | None
    retrieved_at: str | None

    def __post_init__(self) -> None:
        if revelation_state(self.value) is not self.revelation_state:
            raise ValueError("value and revelation_state must agree")


@dataclass(frozen=True)
class EvidenceBatch:
    records: tuple[EmpiricalEvidence, ...]

    @property
    def revealed_count(self) -> int:
        return sum(record.revelation_state is InformationState.REVEALED for record in self.records)

    @property
    def non_revealed_count(self) -> int:
        return len(self.records) - self.revealed_count

    @property
    def coverage(self) -> float:
        return self.revealed_count / len(self.records) if self.records else 0.0


def adapt_panel(
    panel: Mapping[Cell, float | None],
    *,
    providers: Mapping[Cell, str] | None = None,
    retrieved_at: str | None = None,
) -> EvidenceBatch:
    providers = providers or {}
    return EvidenceBatch(
        records=tuple(
            EmpiricalEvidence(
                cell=cell,
                value=value,
                revelation_state=revelation_state(value),
                provider=providers.get(cell),
                retrieved_at=retrieved_at,
            )
            for cell, value in sorted(panel.items())
        )
    )


def evidence_by_nation(batch: EvidenceBatch) -> Mapping[str, tuple[EmpiricalEvidence, ...]]:
    grouped: dict[str, list[EmpiricalEvidence]] = {}
    for record in batch.records:
        grouped.setdefault(record.cell[0], []).append(record)
    return {nation: tuple(records) for nation, records in sorted(grouped.items())}


def revealed_values(records: Iterable[EmpiricalEvidence]) -> tuple[float, ...]:
    return tuple(record.value for record in records if record.revelation_state is InformationState.REVEALED)
