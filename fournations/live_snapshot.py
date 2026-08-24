from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping

from .snapshot_admission import AdmissionResult, manifest, validate_panel

Cell = tuple[str, int, str]
FetchCell = Callable[[str, int, str], float | None]

@dataclass(frozen=True)
class LiveSnapshotRun:
    admission: AdmissionResult
    panel: Mapping[Cell, float | None]
    manifest: dict | None


def run_live_snapshot(*, experiment_id: str, fetch_cell: FetchCell, provider_keys: Mapping[str, str], retrieved_at: str | None = None) -> LiveSnapshotRun:
    from .snapshot_admission import required_cells
    panel = {cell: fetch_cell(*cell) for cell in required_cells()}
    admission = validate_panel(panel)
    if admission.status != "ready_for_snapshot":
        return LiveSnapshotRun(admission, panel, None)
    timestamp = retrieved_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return LiveSnapshotRun(
        admission,
        panel,
        manifest(experiment_id, admission, provider_keys=provider_keys, retrieved_at=timestamp),
    )
