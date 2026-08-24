import pytest

from fournations.live_providers import ProviderError, WorldBankAdapter, require_complete_months, require_complete_quarters


class FakeClient:
    def __init__(self, payload):
        self.payload = payload

    def get_json(self, url):
        return self.payload


def test_world_bank_adapter_extracts_nonmissing_values():
    adapter = WorldBankAdapter(FakeClient([{}, [{"date": "2012", "value": 3.5}, {"date": "2013", "value": None}]]))
    assert adapter.annual_indicator("USA", "NY.GDP.MKTP.CD", 2012, 2013) == {2012: 3.5}


def test_monthly_annualization_requires_all_twelve_months():
    monthly = {f"2012-{m:02d}": float(m) for m in range(1, 13)}
    assert require_complete_months(monthly, 2012) == 6.5
    del monthly["2012-12"]
    with pytest.raises(ProviderError):
        require_complete_months(monthly, 2012)


def test_quarterly_annualization_requires_all_four_quarters():
    quarterly = {f"2012-Q{q}": float(q) for q in range(1, 5)}
    assert require_complete_quarters(quarterly, 2012) == 2.5
    del quarterly["2012-Q4"]
    with pytest.raises(ProviderError):
        require_complete_quarters(quarterly, 2012)
