from __future__ import annotations

from typing import Callable

from .live_providers import ProviderError, WorldBankAdapter
from .provider_bindings import IMF_WEO, WORLD_BANK
from .provider_transports import UrlTransport


class IMFAdapter:
    base_url = "https://www.imf.org/external/datamapper/api/v1"

    def __init__(self, transport: UrlTransport | None = None):
        self.transport = transport or UrlTransport()

    def annual_indicator(self, economy: str, indicator: str, year: int) -> float | None:
        payload = self.transport.get_json(f"{self.base_url}/{indicator}/{economy}")
        if not isinstance(payload, dict):
            raise ProviderError("unexpected IMF response")
        values = payload.get("values")
        if not isinstance(values, dict):
            raise ProviderError("missing IMF values")
        series = values.get(indicator)
        if not isinstance(series, dict):
            raise ProviderError("missing IMF indicator")
        economy_values = series.get(economy)
        if not isinstance(economy_values, dict):
            raise ProviderError("missing IMF economy")
        value = economy_values.get(str(year))
        return None if value is None else float(value)


def make_imf_fetcher(adapter: IMFAdapter) -> Callable[[str, str, int], float | None]:
    def fetch(economy: str, series: str, year: int) -> float | None:
        if series not in IMF_WEO.values():
            raise ProviderError(f"undeclared IMF series: {series}")
        return adapter.annual_indicator(economy, series, year)
    return fetch


def make_world_bank_fetcher(adapter: WorldBankAdapter) -> Callable[[str, str, int], float | None]:
    def fetch(economy: str, series: str, year: int) -> float | None:
        if series not in WORLD_BANK.values():
            raise ProviderError(f"undeclared World Bank series: {series}")
        return adapter.annual_indicator(economy, series, year, year).get(year)
    return fetch
