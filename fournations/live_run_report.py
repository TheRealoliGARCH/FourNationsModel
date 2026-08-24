from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from .live_retrieval import Cell, RetrievalRun
from .snapshot_admission import FEATURES, NATIONS, YEARS, validate_panel

Fetcher = Callable[[str, int, str], float | None]


def retrieve_concurrently(fetcher: Fetcher, *, max_workers: int = 16) -> tuple[dict[Cell, float | None], dict[Cell, str]]:
    cells = [(n, y, f) for n in NATIONS for y in YEARS for f in FEATURES]
    panel: dict[Cell, float | None] = {}
    errors: dict[Cell, str] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(fetcher, n, y, f): (n, y, f) for n, y, f in cells}
        for future in as_completed(futures):
            cell = futures[future]
            try:
                value = future.result()
                if value is None:
                    raise ValueError("provider returned no value")
                panel[cell] = float(value)
            except Exception as exc:
                panel[cell] = None
                errors[cell] = f"{type(exc).__name__}: {exc}"
    return panel, errors


def report(fetcher: Fetcher, *, max_workers: int = 16) -> dict[str, object]:
    panel, errors = retrieve_concurrently(fetcher, max_workers=max_workers)
    admission = validate_panel(panel)
    return {
        "status": admission.status,
        "required_cells": 416,
        "retrieved_cells": sum(value is not None for value in panel.values()),
        "missing_cells": list(admission.missing),
        "errors": errors,
        "checksum": admission.checksum,
    }
