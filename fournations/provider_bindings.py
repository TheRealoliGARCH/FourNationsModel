from __future__ import annotations

from dataclasses import dataclass


NATIONS = ("USA", "CHE", "FRA", "IND")

IMF_WEO = {
    "real_gdp_growth": "NGDP_RPCH",
    "inflation": "PCPIPCH",
    "current_account_gdp": "BCA_NGDPD",
    "government_debt_gdp": "GGXWDG_NGDP",
}

WORLD_BANK = {"log_gdp_usd": "NY.GDP.MKTP.CD"}

BIS_REER = {
    "USA": "M.R.B.US",
    "CHE": "M.R.B.CH",
    "FRA": "M.R.B.FR",
    "IND": "M.R.B.IN",
}

BIS_CREDIT = {
    "USA": ("Q.US.C.A.M.770.A",),
    "CHE": ("Q.CH.N.A.M.770.A", "Q.CH.H.A.M.770.A", "Q.CH.G.A.M.770.A"),
    "FRA": ("Q.FR.C.A.M.770.A",),
    "IND": ("Q.IN.C.A.M.770.A",),
}

OECD_IRLT = {nation: f"{nation}.M.IRLT.PA....." for nation in NATIONS}


@dataclass(frozen=True)
class Binding:
    provider: str
    feature: str
    nation: str | None
    series: tuple[str, ...]
    frequency: str
    annual_rule: str


def bindings() -> tuple[Binding, ...]:
    rows = []
    for feature, series in IMF_WEO.items():
        rows.append(Binding("IMF", feature, None, (series,), "A", "identity"))
    rows.append(Binding("World Bank", "log_gdp_usd", None, (WORLD_BANK["log_gdp_usd"],), "A", "log"))
    for nation in NATIONS:
        rows.append(Binding("BIS", "credit_gdp", nation, BIS_CREDIT[nation], "Q", "annual_mean; CHE=sum_components_then_annual_mean"))
        rows.append(Binding("BIS", "reer_log_change", nation, (BIS_REER[nation],), "M", "calendar_year_mean_then_log_change"))
        rows.append(Binding("OECD", "long_term_rate", nation, (OECD_IRLT[nation],), "M", "calendar_year_mean"))
    return tuple(rows)


def require_declared_binding(feature: str, nation: str | None) -> Binding:
    matches = [row for row in bindings() if row.feature == feature and row.nation == nation]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one binding for {feature}/{nation}")
    return matches[0]
