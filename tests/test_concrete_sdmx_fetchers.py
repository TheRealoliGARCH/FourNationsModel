from fournations.concrete_sdmx_fetchers import ConcreteSDMXFetchers


def monthly(year, value):
    return {"observations": [{"period": f"{year}-{m:02d}", "value": value} for m in range(1, 13)]}


def quarterly(year, value):
    return {"observations": [{"period": f"{year}-Q{q}", "value": value} for q in range(1, 5)]}


class FakeTransport:
    def __init__(self, responses):
        self.responses = responses
        self.urls = []

    def get_csv_observations(self, url):
        self.urls.append(url)
        return self.responses.pop(0)


def test_bis_reer_fetches_two_calendar_years():
    transport = FakeTransport([monthly(2012, 110), monthly(2013, 120)])
    fetchers = ConcreteSDMXFetchers(transport)
    assert fetchers.bis_reer("USA", 2013) == (120.0, 110.0)
    assert "startPeriod=2012" in transport.urls[0]
    assert "endPeriod=2013" in transport.urls[0]


def test_swiss_credit_fetches_declared_three_components():
    transport = FakeTransport([quarterly(2018, 1), quarterly(2018, 2), quarterly(2018, 3)])
    fetchers = ConcreteSDMXFetchers(transport)
    assert fetchers.bis_credit("CHE", 2018) == 6.0
    assert len(transport.urls) == 3


def test_oecd_irlt_uses_declared_monthly_series():
    transport = FakeTransport([monthly(2020, 2.5)])
    fetchers = ConcreteSDMXFetchers(transport)
    assert fetchers.oecd_irlt("IND", 2020) == 2.5
    assert "2020" in transport.urls[0]
