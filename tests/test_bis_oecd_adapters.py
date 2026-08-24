import pytest

from fournations.bis_oecd_adapters import annual_from_monthly, annual_from_quarterly, swiss_credit_annual
from fournations.live_providers import ProviderError


def monthly(year):
    return {"observations": [{"period": f"{year}-{m:02d}", "value": m} for m in range(1, 13)]}


def quarterly(year, offset=0):
    return {"observations": [{"period": f"{year}-Q{q}", "value": q + offset} for q in range(1, 5)]}


def test_monthly_sdmx_requires_complete_calendar_year():
    assert annual_from_monthly(monthly(2012), 2012) == 6.5
    broken = monthly(2012)
    broken["observations"].pop()
    with pytest.raises(ProviderError):
        annual_from_monthly(broken, 2012)


def test_quarterly_sdmx_requires_complete_year():
    assert annual_from_quarterly(quarterly(2012), 2012) == 2.5


def test_swiss_credit_sums_component_annual_means():
    assert swiss_credit_annual((quarterly(2012, 0), quarterly(2012, 10), quarterly(2012, 20)), 2012) == 37.5
