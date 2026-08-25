from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .cell_dispatcher import ProviderFetchers, dispatch
from .live_providers import ProviderError, WorldBankAdapter
from .provider_bindings import BIS_CREDIT, BIS_REER, OECD_IRLT

JsonGetter = Callable[[str], object]
MonthlyGetter = Callable[[str, str, int], dict[str, float]]
QuarterlyGetter = Callable[[str, str, int], dict[str, float]]


@dataclass(frozen=True)
class LiveProviderConfig:
    imf_url: Callable[[str, str, int], str]
    bis_monthly: MonthlyGetter
    bis_quarterly: QuarterlyGetter
    oecd_monthly: MonthlyGetter


def _imf_annual(get_json: JsonGetter, url_builder: Callable[[str, str, int], str]):
    def fetch(nation: str, series: str, year: int) -> float | None:
        payload = get_json(url_builder(nation, series, year))
        if not isinstance(payload, dict):
            raise ProviderError("unexpected IMF response")
        values = payload.get("values", payload)
        if not isinstance(values, dict):
            raise ProviderError("IMF response has no values mapping")
        raw = values.get(str(year))
        return None if raw is None else float(raw)
    return fetch


def _world_bank_annual(get_json: JsonGetter):
    adapter = WorldBankAdapter(type("Client", (), {"get_json": staticmethod(get_json)})())

    def fetch(nation: str, series: str, year: int) -> float | None:
        values = adapter.annual_indicator(nation, series, year, year)
        return values.get(year)
    return fetch


def make_live_fetcher(get_json: JsonGetter, config: LiveProviderConfig) -> Callable[[str, int, str], float]:
    fetchers = ProviderFetchers(
        imf=_imf_annual(get_json, config.imf_url),
        world_bank=_world_bank_annual(get_json),
        bis_monthly=config.bis_monthly,
        bis_quarterly=config.bis_quarterly,
        oecd_monthly=config.oecd_monthly,
    )

    def fetch(nation: str, year: int, feature: str) -> float:
        return dispatch(fetchers, nation, year, feature)

    return fetch


def declared_series() -> dict[str, object]:
    return {"bis_reer": dict(BIS_REER), "bis_credit": dict(BIS_CREDIT), "oecd_irlt": dict(OECD_IRLT)}
