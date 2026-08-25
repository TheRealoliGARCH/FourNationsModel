from fournations.concrete_sdmx_fetchers import ConcreteSDMXFetchers
from fournations.live_cell_fetcher import make_live_cell_fetcher
from fournations.provider_transports import Response


class Transport:
    def __init__(self):
        self.urls = []
    def get_csv_observations(self, url):
        self.urls.append(url)
        if "DF_FINMARK" in url or "WS_EER" in url:
            return {"observations": [{"period": f"2012-{m:02d}", "value": 1.0} for m in range(1, 13)]}
        return {"observations": [{"period": f"2012-Q{q}", "value": 1.0} for q in range(1, 5)]}


def test_composed_fetcher_routes_bis_reer():
    fetcher = make_live_cell_fetcher(
        imf=lambda n, s, y: 1.0,
        world_bank=lambda n, s, y: 100.0,
        sdmx=ConcreteSDMXFetchers(Transport()),
    )
    assert fetcher("USA", 2012, "reer_log_change") == 0.0


def test_composed_fetcher_routes_oecd_irlt():
    fetcher = make_live_cell_fetcher(
        imf=lambda n, s, y: 1.0,
        world_bank=lambda n, s, y: 100.0,
        sdmx=ConcreteSDMXFetchers(Transport()),
    )
    assert fetcher("USA", 2012, "long_term_rate") == 1.0
