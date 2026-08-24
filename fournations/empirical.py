from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol
import json

@dataclass(frozen=True)
class Observation:
    source: str
    provider: str
    series_id: str
    economy: str
    period: str
    value: float
    unit: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DatasetSnapshot:
    provider: str
    request: Mapping[str, Any]
    retrieved_at: str
    observations: tuple[Observation, ...]
    checksum: str

class ProviderAdapter(Protocol):
    provider: str
    def fetch(self, request: Mapping[str, Any]) -> Iterable[Observation]: ...

def canonical_payload(observations: Iterable[Observation]) -> bytes:
    rows = [{"source":o.source,"provider":o.provider,"series_id":o.series_id,"economy":o.economy,"period":o.period,"value":o.value,"unit":o.unit,"metadata":dict(o.metadata)} for o in observations]
    return json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()

def snapshot(provider: str, request: Mapping[str, Any], observations: Iterable[Observation]) -> DatasetSnapshot:
    rows = tuple(observations)
    return DatasetSnapshot(provider, dict(request), datetime.now(timezone.utc).isoformat(), rows, sha256(canonical_payload(rows)).hexdigest())

def write_snapshot(dataset: DatasetSnapshot, directory: str | Path) -> Path:
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{dataset.provider.lower()}-{dataset.checksum[:16]}.json"
    payload = {"provider":dataset.provider,"request":dict(dataset.request),"retrieved_at":dataset.retrieved_at,"checksum":dataset.checksum,"observations":[o.__dict__ for o in dataset.observations]}
    path.write_text(json.dumps(payload, sort_keys=True, default=str), encoding="utf-8")
    return path

@dataclass
class Registry:
    adapters: dict[str, ProviderAdapter] = field(default_factory=dict)
    def register(self, adapter: ProviderAdapter) -> None: self.adapters[adapter.provider.upper()] = adapter
    def fetch(self, provider: str, request: Mapping[str, Any]) -> DatasetSnapshot:
        key = provider.upper()
        if key not in self.adapters: raise KeyError(f"provider {provider!r} is not registered")
        adapter = self.adapters[key]
        return snapshot(adapter.provider, request, adapter.fetch(request))

@dataclass(frozen=True)
class FunctionalAdapter:
    provider: str
    loader: Callable[[Mapping[str, Any]], Iterable[Observation]]
    def fetch(self, request: Mapping[str, Any]) -> Iterable[Observation]: return self.loader(request)

def normalize(observations: Iterable[Observation], *, unit_map: Mapping[str, str] | None = None) -> tuple[Observation, ...]:
    unit_map = unit_map or {}; out=[]
    for o in observations:
        out.append(Observation(o.source.strip(),o.provider.upper().strip(),o.series_id.strip(),o.economy.strip().upper(),o.period.strip(),float(o.value),unit_map.get(o.unit or "",o.unit),dict(o.metadata)))
    return tuple(sorted(out,key=lambda x:(x.provider,x.series_id,x.economy,x.period)))
