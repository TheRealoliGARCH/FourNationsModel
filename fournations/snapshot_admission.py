from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Mapping, Sequence


NATIONS = ("USA", "CHE", "FRA", "IND")
YEARS = tuple(range(2012, 2025))
FEATURES = (
    "real_gdp_growth",
    "inflation",
    "current_account_gdp",
    "government_debt_gdp",
    "log_gdp_usd",
    "credit_gdp",
    "reer_log_change",
    "long_term_rate",
)


@dataclass(frozen=True)
class AdmissionResult:
    status: str
    missing: tuple[tuple[str, int, str], ...]
    checksum: str | None = None


def required_cells() -> tuple[tuple[str, int, str], ...]:
    return tuple((nation, year, feature) for nation in NATIONS for year in YEARS for feature in FEATURES)


def validate_panel(panel: Mapping[tuple[str, int, str], float | None]) -> AdmissionResult:
    missing = tuple(cell for cell in required_cells() if cell not in panel or panel[cell] is None)
    if missing:
        return AdmissionResult("blocked_incomplete_coverage", missing)
    payload = [(n, y, f, float(panel[(n, y, f)])) for n, y, f in required_cells()]
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return AdmissionResult("ready_for_snapshot", (), sha256(encoded).hexdigest())


def manifest(experiment_id: str, result: AdmissionResult, *, provider_keys: Mapping[str, str], retrieved_at: str) -> dict:
    if result.status != "ready_for_snapshot" or result.checksum is None:
        raise RuntimeError("cannot create manifest before complete snapshot admission")
    return {
        "experiment_id": experiment_id,
        "shape": {"nations": 4, "years": 13, "features": 8, "cells": 416},
        "checksum_sha256": result.checksum,
        "provider_keys": dict(sorted(provider_keys.items())),
        "retrieved_at": retrieved_at,
    }
