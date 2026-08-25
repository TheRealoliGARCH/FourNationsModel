from __future__ import annotations

from typing import Callable

from .bis_oecd_adapters import annual_from_monthly, annual_from_quarterly, swiss_credit_annual
from .provider_bindings import BIS_CREDIT, BIS_REER, OECD_IRLT
from .provider_transports import UrlTransport
from .sdmx_normalization import bis_csv_url, oecd_csv_url


class ConcreteSDMXFetchers:
    """Concrete BIS/OECD fetchers preserving declared series and transformations."""

    def __init__(self, transport: UrlTransport | None = None):
        self.transport = transport or UrlTransport()

    def bis_reer(self, nation: str, year: int) -> tuple[float, float]:
        current_url = bis_csv_url("WS_EER", BIS_REER[nation], year, year)
        previous_url = bis_csv_url("WS_EER", BIS_REER[nation], year - 1, year - 1)
        current_payload = self.transport.get_csv_observations(current_url)
        previous_payload = self.transport.get_csv_observations(previous_url)
        current = annual_from_monthly(current_payload, year)
        previous = annual_from_monthly(previous_payload, year - 1)
        return current, previous

    def bis_credit(self, nation: str, year: int) -> float:
        series = BIS_CREDIT[nation]
        payloads = tuple(
            self.transport.get_csv_observations(bis_csv_url("WS_CREDIT_GAP", key, year, year))
            for key in series
        )
        if nation == "CHE":
            return swiss_credit_annual(payloads, year)
        return annual_from_quarterly(payloads[0], year)

    def oecd_irlt(self, nation: str, year: int) -> float:
        url = oecd_csv_url("DSD_STES@DF_FINMARK", OECD_IRLT[nation], year, year)
        return annual_from_monthly(self.transport.get_csv_observations(url), year)


def make_bis_reer_getter(fetchers: ConcreteSDMXFetchers) -> Callable[[str, int], tuple[float, float]]:
    return fetchers.bis_reer


def make_bis_credit_getter(fetchers: ConcreteSDMXFetchers) -> Callable[[str, int], float]:
    return fetchers.bis_credit


def make_oecd_irlt_getter(fetchers: ConcreteSDMXFetchers) -> Callable[[str, int], float]:
    return fetchers.oecd_irlt
