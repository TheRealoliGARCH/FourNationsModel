from __future__ import annotations

from typing import Callable

from .cell_dispatcher import ProviderFetchers, dispatch
from .concrete_sdmx_fetchers import ConcreteSDMXFetchers
from .live_providers import ProviderError
from .provider_bindings import BIS_CREDIT, BIS_REER, OECD_IRLT
from .sdmx_normalization import bis_csv_url, oecd_csv_url


def _observation_map(payload: dict[str, list[dict[str, object]]]) -> dict[str, float]:
    values: dict[str, float] = {}
    for row in payload["observations"]:
        period = row.get("period")
        value = row.get("value")
        if not isinstance(period, str) or value is None:
            raise ProviderError("malformed canonical observation")
        values[period] = float(value)
    return values


def make_live_cell_fetcher(
    *,
    imf: Callable[[str, str, int], float | None],
    world_bank: Callable[[str, str, int], float | None],
    sdmx: ConcreteSDMXFetchers,
) -> Callable[[str, int, str], float]:
    """Compose concrete provider transports into the canonical cell dispatcher."""

    def bis_monthly(nation: str, series: str, year: int) -> dict[str, float]:
        url = bis_csv_url("WS_EER", series, year, year)
        return _observation_map(sdmx.transport.get_csv_observations(url))

    def bis_quarterly(nation: str, series: str, year: int) -> dict[str, float]:
        url = bis_csv_url("WS_CREDIT_GAP", series, year, year)
        return _observation_map(sdmx.transport.get_csv_observations(url))

    def oecd_monthly(nation: str, series: str, year: int) -> dict[str, float]:
        url = oecd_csv_url("DSD_STES@DF_FINMARK", series, year, year)
        return _observation_map(sdmx.transport.get_csv_observations(url))

    fetchers = ProviderFetchers(
        imf=imf,
        world_bank=world_bank,
        bis_monthly=bis_monthly,
        bis_quarterly=bis_quarterly,
        oecd_monthly=oecd_monthly,
    )

    return lambda nation, year, feature: dispatch(fetchers, nation, year, feature)
