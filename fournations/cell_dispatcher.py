from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Callable

from .feature_aggregation import swiss_nonfinancial_credit_gdp
from .live_providers import ProviderError
from .provider_bindings import BIS_CREDIT, BIS_REER, IMF_WEO, OECD_IRLT, WORLD_BANK, require_declared_binding

AnnualFetcher = Callable[[str, str, int], float | None]
MonthlyFetcher = Callable[[str, str, int], dict[str, float]]
QuarterlyFetcher = Callable[[str, str, int], dict[str, float]]


@dataclass(frozen=True)
class ProviderFetchers:
    imf: AnnualFetcher
    world_bank: AnnualFetcher
    bis_monthly: MonthlyFetcher
    bis_quarterly: QuarterlyFetcher
    oecd_monthly: MonthlyFetcher


def _require(value: float | None, label: str) -> float:
    if value is None:
        raise ProviderError(f"missing provider observation: {label}")
    return float(value)


def _annual_mean(monthly: dict[str, float], year: int) -> float:
    keys = [f"{year}-{month:02d}" for month in range(1, 13)]
    missing = [key for key in keys if key not in monthly]
    if missing:
        raise ProviderError(f"incomplete monthly coverage for {year}: {', '.join(missing)}")
    return sum(float(monthly[key]) for key in keys) / 12.0


def _quarterly_mean(quarterly: dict[str, float], year: int) -> float:
    keys = [f"{year}-Q{quarter}" for quarter in range(1, 5)]
    missing = [key for key in keys if key not in quarterly]
    if missing:
        raise ProviderError(f"incomplete quarterly coverage for {year}: {', '.join(missing)}")
    return sum(float(quarterly[key]) for key in keys) / 4.0


def dispatch(fetchers: ProviderFetchers, nation: str, year: int, feature: str) -> float:
    require_declared_binding(feature, None if feature in (*IMF_WEO, "log_gdp_usd") else nation)

    if feature in IMF_WEO:
        return _require(fetchers.imf(nation, IMF_WEO[feature], year), f"IMF/{nation}/{feature}/{year}")

    if feature == "log_gdp_usd":
        value = _require(fetchers.world_bank(nation, WORLD_BANK[feature], year), f"WorldBank/{nation}/{feature}/{year}")
        if value <= 0.0:
            raise ProviderError(f"nonpositive GDP for log transform: {nation}/{year}")
        return log(value)

    if feature == "reer_log_change":
        current = _annual_mean(fetchers.bis_monthly(nation, BIS_REER[nation], year), year)
        previous = _annual_mean(fetchers.bis_monthly(nation, BIS_REER[nation], year - 1), year - 1)
        if current <= 0.0 or previous <= 0.0:
            raise ProviderError(f"nonpositive REER for log change: {nation}/{year}")
        return log(current) - log(previous)

    if feature == "credit_gdp":
        component_values = [_quarterly_mean(fetchers.bis_quarterly(nation, key, year), year) for key in BIS_CREDIT[nation]]
        if nation == "CHE":
            return swiss_nonfinancial_credit_gdp(dict(zip(("N", "H", "G"), component_values)))
        return component_values[0]

    if feature == "long_term_rate":
        return _annual_mean(fetchers.oecd_monthly(nation, OECD_IRLT[nation], year), year)

    raise ProviderError(f"unsupported feature: {feature}")
