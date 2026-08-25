from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Mapping

from .end_to_end import EndToEndResult, execute


def _panel_records(panel: Mapping[tuple[str, int, str], float | None]) -> list[dict[str, object]]:
    return [
        {
            "nation": nation,
            "year": year,
            "feature": feature,
            "value": value,
        }
        for (nation, year, feature), value in sorted(panel.items())
    ]


def report(result: EndToEndResult, *, experiment_id: str) -> dict[str, object]:
    admission = result.run.result
    return {
        "experiment_id": experiment_id,
        "retrieved_at": result.run.retrieved_at,
        "status": admission.status,
        "missing": [list(cell) for cell in admission.missing],
        "panel": _panel_records(result.run.panel),
        "snapshot_manifest": result.snapshot_manifest,
    }


def run(
    fetcher: Callable[[str, int, str], float | None],
    *,
    experiment_id: str,
    provider_keys: Mapping[str, str],
) -> dict[str, object]:
    result = execute(
        fetcher,
        experiment_id=experiment_id,
        provider_keys=provider_keys,
    )
    return report(result, experiment_id=experiment_id)


def write_report(path: str | Path, payload: Mapping[str, object]) -> None:
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
