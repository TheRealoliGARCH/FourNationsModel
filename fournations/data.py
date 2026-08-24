from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

import pandas as pd


@dataclass(frozen=True)
class ObservationPanel:
    """Source-neutral empirical panel with provenance metadata."""

    frame: pd.DataFrame
    source: str
    retrieved_at: datetime
    series_ids: tuple[str, ...]

    def validate(self, required_columns: Sequence[str]) -> None:
        missing = [c for c in required_columns if c not in self.frame.columns]
        if missing:
            raise ValueError(f"missing required columns: {missing}")
        if self.frame.empty:
            raise ValueError("observation panel is empty")
        if self.frame.isna().all(axis=None):
            raise ValueError("observation panel contains no usable values")


def normalize_wide(
    frame: pd.DataFrame,
    *,
    date_column: str = "date",
    country_column: str = "country",
    value_columns: Sequence[str] = (),
    source: str,
    series_ids: Sequence[str],
    retrieved_at: datetime,
) -> ObservationPanel:
    """Normalize provider output without changing economic meaning."""
    required = [date_column, country_column, *value_columns]
    for column in required:
        if column not in frame.columns:
            raise ValueError(f"provider output lacks column {column!r}")
    result = frame.copy()
    result[date_column] = pd.to_datetime(result[date_column], utc=True)
    result = result.sort_values([country_column, date_column]).reset_index(drop=True)
    return ObservationPanel(
        frame=result,
        source=source,
        retrieved_at=retrieved_at,
        series_ids=tuple(series_ids),
    )


class DataSource:
    """Interface implemented by IMF/WB/BIS/OECD adapters."""

    name: str

    def fetch(self, series_ids: Sequence[str], **kwargs: object) -> ObservationPanel:
        raise NotImplementedError


class StaticDataSource(DataSource):
    """Deterministic adapter for tests and reproducible fixtures."""

    name = "static"

    def __init__(self, frame: pd.DataFrame, *, retrieved_at: datetime) -> None:
        self._frame = frame.copy()
        self._retrieved_at = retrieved_at

    def fetch(self, series_ids: Sequence[str], **kwargs: object) -> ObservationPanel:
        return ObservationPanel(
            frame=self._frame.copy(),
            source=self.name,
            retrieved_at=self._retrieved_at,
            series_ids=tuple(series_ids),
        )


class IMFDataSource(DataSource):
    name = "IMF"


class WorldBankDataSource(DataSource):
    name = "WorldBank"


class BISDataSource(DataSource):
    name = "BIS"


class OECDDataSource(DataSource):
    name = "OECD"
