import pytest

from fournations.imf_worldbank_fetchers import IMFAdapter, make_imf_fetcher, make_world_bank_fetcher
from fournations.live_providers import ProviderError, WorldBankAdapter


class JsonClient:
    def __init__(self, payload):
        self.payload = payload
    def get_json(self, url):
        return self.payload


def test_imf_fetcher_reads_declared_annual_value():
    payload = {"values": {"NGDP_RPCH": {"USA": {"2013": 2.1}}}}
    fetch = make_imf_fetcher(IMFAdapter(JsonClient(payload)))
    assert fetch("USA", "NGDP_RPCH", 2013) == 2.1


def test_imf_fetcher_rejects_undeclared_series():
    fetch = make_imf_fetcher(IMFAdapter(JsonClient({"values": {}})))
    with pytest.raises(ProviderError):
        fetch("USA", "UNKNOWN", 2013)


def test_world_bank_fetcher_reads_requested_year():
    payload = [{}, [{"date": "2013", "value": 100.0}]]
    fetch = make_world_bank_fetcher(WorldBankAdapter(JsonClient(payload)))
    assert fetch("USA", "NY.GDP.MKTP.CD", 2013) == 100.0


def test_world_bank_fetcher_rejects_undeclared_series():
    fetch = make_world_bank_fetcher(WorldBankAdapter(JsonClient([{}, []])))
    with pytest.raises(ProviderError):
        fetch("USA", "UNKNOWN", 2013)
