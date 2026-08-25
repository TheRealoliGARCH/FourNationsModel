from math import log

import pytest

from fournations.cell_dispatcher import ProviderFetchers, dispatch
from fournations.live_providers import ProviderError


def monthly(year, value):
    return {f"{year}-{month:02d}": float(value) for month in range(1, 13)}


def quarterly(year, value):
    return {f"{year}-Q{quarter}": float(value) for quarter in range(1, 5)}


def make_fetchers():
    def annual(nation, series, year):
        return 100.0

    def bis_monthly(nation, series, year):
        return monthly(year, 120.0 if year == 2012 else 100.0)

    def bis_quarterly(nation, series, year):
        offsets = {"Q.CH.N.A.M.770.A": 1.0, "Q.CH.H.A.M.770.A": 2.0, "Q.CH.G.A.M.770.A": 3.0}
        return quarterly(year, offsets.get(series, 50.0))

    def oecd_monthly(nation, series, year):
        return monthly(year, 4.0)

    return ProviderFetchers(annual, annual, bis_monthly, bis_quarterly, oecd_monthly)


def test_imf_feature_dispatches_to_declared_indicator():
    assert dispatch(make_fetchers(), "USA", 2012, "inflation") == 100.0


def test_world_bank_gdp_is_log_transformed():
    assert dispatch(make_fetchers(), "IND", 2012, "log_gdp_usd") == log(100.0)


def test_reer_is_log_change_of_calendar_year_means():
    assert dispatch(make_fetchers(), "USA", 2012, "reer_log_change") == pytest.approx(log(120.0) - log(100.0))


def test_swiss_credit_sums_declared_components():
    assert dispatch(make_fetchers(), "CHE", 2012, "credit_gdp") == 6.0


def test_oecd_rate_is_calendar_year_mean():
    assert dispatch(make_fetchers(), "FRA", 2012, "long_term_rate") == 4.0


def test_incomplete_monthly_coverage_fails_closed():
    fetchers = make_fetchers()
    broken = ProviderFetchers(fetchers.imf, fetchers.world_bank, lambda n, s, y: {f"{y}-01": 1.0}, fetchers.bis_quarterly, fetchers.oecd_monthly)
    with pytest.raises(ProviderError):
        dispatch(broken, "USA", 2012, "reer_log_change")
