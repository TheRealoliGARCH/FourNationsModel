import pytest
from fournations.feature_aggregation import swiss_nonfinancial_credit_gdp, annual_mean

def test_swiss_credit_is_component_sum():
    assert swiss_nonfinancial_credit_gdp({"N": 120.0, "H": 80.0, "G": 20.0}) == 220.0

def test_swiss_credit_fails_closed_on_missing_component():
    with pytest.raises(ValueError):
        swiss_nonfinancial_credit_gdp({"N": 120.0, "H": 80.0})

def test_annual_mean_requires_all_months():
    monthly = {f"2012-{m:02d}": float(m) for m in range(1, 13)}
    assert annual_mean(monthly, 2012) == 6.5
    monthly.pop("2012-12")
    with pytest.raises(ValueError):
        annual_mean(monthly, 2012)
