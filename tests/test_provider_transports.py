import pytest

from fournations.live_providers import ProviderError
from fournations.provider_transports import Response, UrlTransport


class FakeResponse:
    def __init__(self, status, body, content_type="application/json"):
        self.status = status
        self._body = body
        self.headers = {"Content-Type": content_type}

    def read(self):
        return self._body

    def getcode(self):
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def opener_for(response):
    def opener(request, timeout):
        return response
    return opener


def test_json_transport_decodes_successful_response():
    transport = UrlTransport(opener_for(FakeResponse(200, b'{"x": 1}')))
    assert transport.get_json("https://example.invalid") == {"x": 1}


def test_non_200_response_fails_closed():
    transport = UrlTransport(opener_for(FakeResponse(503, b"down")))
    with pytest.raises(ProviderError):
        transport.get_json("https://example.invalid")


def test_csv_transport_normalizes_observations():
    body = b"TIME_PERIOD,OBS_VALUE\n2012-01,1.5\n"
    transport = UrlTransport(opener_for(FakeResponse(200, body, "text/csv")))
    assert transport.get_csv_observations("https://example.invalid") == {
        "observations": [{"period": "2012-01", "value": 1.5}]
    }


def test_invalid_json_fails_closed():
    transport = UrlTransport(opener_for(FakeResponse(200, b"not-json")))
    with pytest.raises(ProviderError):
        transport.get_json("https://example.invalid")
