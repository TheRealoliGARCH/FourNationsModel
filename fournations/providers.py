from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .empirical import FunctionalAdapter, Observation, Registry

PROVIDERS = ("IMF", "WORLD_BANK", "BIS", "OECD")

@dataclass(frozen=True)
class ProviderRequest:
    series_id: str
    economies: tuple[str, ...] = ()
    start: str | None = None
    end: str | None = None
    options: Mapping[str, str] | None = None

def empty_registry() -> Registry:
    registry = Registry()
    for provider in PROVIDERS:
        registry.register(FunctionalAdapter(provider, lambda request, p=provider: ()))
    return registry

def rows(provider: str, raw: Iterable[Mapping[str, object]]) -> tuple[Observation, ...]:
    return tuple(Observation(
        source=str(r.get("source", provider)), provider=provider,
        series_id=str(r["series_id"]), economy=str(r["economy"]),
        period=str(r["period"]), value=float(r["value"]),
        unit=None if r.get("unit") is None else str(r["unit"]),
        metadata=dict(r.get("metadata", {})),
    ) for r in raw)
