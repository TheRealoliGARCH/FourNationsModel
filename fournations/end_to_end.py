from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from .live_retrieval import RetrievalRun, retrieve
from .provider_bindings import bindings
from .snapshot_admission import manifest

CellFetcher = Callable[[str, int, str], float | None]


@dataclass(frozen=True)
class EndToEndResult:
    run: RetrievalRun
    snapshot_manifest: Mapping[str, object] | None


def execute(
    fetcher: CellFetcher,
    *,
    experiment_id: str,
    provider_keys: Mapping[str, str],
    retrieved_at: str | None = None,
) -> EndToEndResult:
    run = retrieve(fetcher)
    if run.result.status != "ready_for_snapshot":
        return EndToEndResult(run, None)
    return EndToEndResult(
        run,
        manifest(
            experiment_id,
            run.result,
            provider_keys=provider_keys,
            retrieved_at=retrieved_at or run.retrieved_at,
        ),
    )


def bound_provider_keys() -> dict[str, str]:
    keys: dict[str, str] = {}
    for binding in bindings():
        scope = binding.nation or "ALL"
        keys[f"{binding.feature}:{scope}"] = ",".join(binding.series)
    return keys
