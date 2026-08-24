import pytest

from fournations.live_providers import ProviderError
from fournations.sdmx_normalization import bis_csv_url, normalize_csv_observations, oecd_csv_url


def test_bis_url_contains_flow_key_and_periods():
    url = bis_csv_url("WS_EER", "M.R.B.US", 2012, 2024)
    assert "WS_EER" in url and "M.R.B.US" in url
    assert "startPeriod=2012" in url and "endPeriod=2024" in url


def test_oecd_url_contains_dataset_key_and_periods():
    url = oecd_csv_url("DSD_STES@DF_FINMARK", "USA.M.IRLT.PA.....", 2012, 2024)
    assert "DF_FINMARK" in url and "USA.M.IRLT.PA" in url


def test_csv_normalization_returns_canonical_observation_envelope():
    payload = "TIME_PERIOD,OBS_VALUE\n2012-01,1.5\n2012-02,2.5\n"
    assert normalize_csv_observations(payload) == {"observations": [
        {"period": "2012-01", "value": 1.5},
        {"period": "2012-02", "value": 2.5},
    ]}


def test_csv_missing_required_columns_fails_closed():
    with pytest.raises(ProviderError):
        normalize_csv_observations("DATE,VALUE\n2012-01,1.0\n")
