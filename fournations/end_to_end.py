from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .feature_bindings import FEATURE_BINDINGS
from .live_retrieval import RetrievalRun, retrieve_live
from .snapshot_admission import manifest

CellFetcher = Callable[[str, int, str], float]


@dataclass(frozen=True)
class EndToEndResult:
    run: RetrievalRun
    snapshot_manifest: Mapping[str, object] | None


def execute(fetcher: CellFetcher, *, experiment_id: str, provider_keys: Mapping[str, str], retrieved_at: str, max_workers: int = 16) -> EndToEndResult:
    run = retrieve_live(fetcher, max_workers=max_workers)
    if run.admission.status != "ready_for_snapshot":
        return EndToEndResult(run, None)
    return EndToEndResult(
        run,
        manifest(
            experiment_id,
            run.admission,
            provider_keys=provider_keys,
            retrieved_at=retrieved_at,
        ),
    )


def bound_provider_keys() -> dict[str, str]:
    keys: dict[str, str] = {}
    for feature, binding in FEATURE_BINDINGS.items():
        keys[feature] = str(binding)
    return keys
