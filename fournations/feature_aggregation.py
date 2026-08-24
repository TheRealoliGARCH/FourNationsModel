from __future__ import annotations

from collections.abc import Mapping


def aggregate_percent_of_gdp(components: Mapping[str, float], required: tuple[str, ...]) -> float:
    missing = tuple(name for name in required if name not in components)
    if missing:
        raise ValueError(f"missing aggregate components: {', '.join(missing)}")
    return sum(float(components[name]) for name in required)


def swiss_nonfinancial_credit_gdp(components: Mapping[str, float]) -> float:
    """Aggregate BIS Swiss N, H and G borrower sectors into total non-financial-sector credit/GDP."""
    return aggregate_percent_of_gdp(components, ("N", "H", "G"))


def annual_mean(monthly: Mapping[str, float], year: int) -> float:
    keys = tuple(f"{year}-{month:02d}" for month in range(1, 13))
    missing = tuple(key for key in keys if key not in monthly)
    if missing:
        raise ValueError(f"incomplete calendar year {year}: {', '.join(missing)}")
    return sum(float(monthly[key]) for key in keys) / 12.0
