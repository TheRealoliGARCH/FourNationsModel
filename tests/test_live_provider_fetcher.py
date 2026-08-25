import math

from fournations.live_provider_fetcher import LiveProviderConfig, make_live_fetcher


def test_live_fetcher_composes_imf_world_bank_and_dispatcher():
    def get_json(url):
        if "imf" in url:
            return {"values": {"2012": 3.5}}
        return [{}, [{"date": "2012", "value": 100.0}]]

    monthly = {f"2012-{m:02d}": 100.0 for m in range(1, 13)}
    monthly.update({f"2011-{m:02d}": 90.0 for m in range(1, 13)})
    quarterly = {f"2012-Q{q}": 10.0 for q in range(1, 5)}

    config = LiveProviderConfig(
        imf_url=lambda nation, series, year: f"https://imf.invalid/{nation}/{series}/{year}",
        bis_monthly=lambda nation, series, year: {k: v for k, v in monthly.items() if k.startswith(str(year))},
        bis_quarterly=lambda nation, series, year: quarterly,
        oecd_monthly=lambda nation, series, year: {k: v for k, v in monthly.items() if k.startswith(str(year))},
    )
    fetch = make_live_fetcher(get_json, config)

    assert fetch("USA", 2012, "real_gdp_growth") == 3.5
    assert fetch("USA", 2012, "log_gdp_usd") == math.log(100.0)
    assert fetch("USA", 2012, "reer_log_change") == math.log(100.0) - math.log(90.0)
    assert fetch("USA", 2012, "credit_gdp") == 10.0
    assert fetch("USA", 2012, "long_term_rate") == 100.0


def test_swiss_credit_is_composed_from_three_components():
    def get_json(url):
        return {"values": {"2012": 1.0}}

    config = LiveProviderConfig(
        imf_url=lambda *args: "https://imf.invalid",
        bis_monthly=lambda *args: {f"2012-{m:02d}": 1.0 for m in range(1, 13)},
        bis_quarterly=lambda nation, series, year: {f"2012-Q{q}": {"Q.CH.N.A.M.770.A": 1.0, "Q.CH.H.A.M.770.A": 2.0, "Q.CH.G.A.M.770.A": 3.0}[series] for q in range(1, 5)},
        oecd_monthly=lambda *args: {f"2012-{m:02d}": 1.0 for m in range(1, 13)},
    )
    assert make_live_fetcher(get_json, config)("CHE", 2012, "credit_gdp") == 6.0
