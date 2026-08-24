from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class InstitutionalHost:
    institution: str
    nation: str

HOSTS = (
    InstitutionalHost("IMF", "USA"),
    InstitutionalHost("WORLD_BANK", "USA"),
    InstitutionalHost("BIS", "CHE"),
    InstitutionalHost("OECD", "FRA"),
)

@dataclass(frozen=True)
class HostExperimentSpec:
    hosts: tuple[InstitutionalHost, ...] = HOSTS
    fourth_nation: str | None = None

    def nations(self) -> tuple[str, ...]:
        ordered: list[str] = []
        for host in self.hosts:
            if host.nation not in ordered:
                ordered.append(host.nation)
        if self.fourth_nation is not None and self.fourth_nation not in ordered:
            ordered.append(self.fourth_nation)
        return tuple(ordered)

    def validate(self) -> None:
        nations = self.nations()
        if len(nations) != 4:
            raise ValueError(f"institutional hosts yield {len(nations)} distinct nations {nations}; provide fourth_nation")

def host_multiplicity() -> Mapping[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {}
    for host in HOSTS:
        out.setdefault(host.nation, []).append(host.institution)
    return {nation: tuple(institutions) for nation, institutions in out.items()}
