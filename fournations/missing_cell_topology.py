from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping


def missing_records(panel: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    return [dict(record) for record in panel if record.get("value") is None]


def topology(panel: Iterable[Mapping[str, object]]) -> dict[str, object]:
    missing = missing_records(panel)
    by_feature = Counter(str(record["feature"]) for record in missing)
    by_nation = Counter(str(record["nation"]) for record in missing)
    by_nation_feature = Counter(
        f"{record['nation']}:{record['feature']}" for record in missing
    )
    return {
        "missing_cell_count": len(missing),
        "by_feature": dict(sorted(by_feature.items())),
        "by_nation": dict(sorted(by_nation.items())),
        "by_nation_feature": dict(sorted(by_nation_feature.items())),
        "missing_cells": missing,
    }
