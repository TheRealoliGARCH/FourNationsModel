from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping

from .snapshot_admission import AdmissionResult, FEATURES, NATIONS, YEARS, manifest, validate_panel

Cell = tuple[str, int, str]
Fetcher = Callable[[str, int, str], float | None]


@dataclass(frozen=True)
class RetrievalRun:
    result: AdmissionResult
    panel: Mapping[Cell, float | None]
    retrieved_at: str


def retrieve(fetcher: Fetcher) -> RetrievalRun:
    panel: dict[Cell, float | None] = {}
    for nation in NATIONS:
        for year in YEARS:
            for feature in FEATURES:
                try:
                    panel[(nation, year, feature)] = fetcher(nation, year, feature)
                except Exception:
                    panel[(nation, year, feature)] = None
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
