from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping

from .snapshot_admission import AdmissionResult, FEATURES, NATIONS, YEARS, manifest, validate_panel

Cell = tuple[str, int, str]
Fetcher = Callable[[str, int, str], float | None]
Checkpoint = Callable[[Mapping[Cell, float | None]], None]


@dataclass(frozen=True)
class RetrievalRun:
    result: AdmissionResult
    panel: Mapping[Cell, float | None]
    retrieved_at: str


def retrieve(
    fetcher: Fetcher,
    *,
    max_workers: int = 16,
    checkpoint: Checkpoint | None = None,
) -> RetrievalRun:
    cells = [(nation, year, feature) for nation in NATIONS for year in YEARS for feature in FEATURES]
    panel: dict[Cell, float | None] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetcher, *cell): cell for cell in cells}
        for future in as_completed(futures):
            cell = futures[future]
            try:
                panel[cell] = future.result()
            except Exception:
                panel[cell] = None
            if checkpoint is not None:
                checkpoint(dict(panel))

    result = validate_panel(panel)
    retrieved_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return RetrievalRun(result=result, panel=panel, retrieved_at=retrieved_at)


def certify(run: RetrievalRun, provider_keys: Mapping[str, str]) -> dict:
    return manifest(
        "host-nations-v2",
        run.result,
        provider_keys=provider_keys,
        retrieved_at=run.retrieved_at,
    )
