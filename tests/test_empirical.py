from fournations.empirical import FunctionalAdapter, Observation, Registry, normalize


def test_snapshot_is_deterministic_for_same_observations():
    registry = Registry()
    registry.register(FunctionalAdapter("IMF", lambda request: [Observation("IMF", "IMF", "X", "USA", "2025", 1.0, "pct")]))
    a = registry.fetch("IMF", {"series": "X"})
    b = registry.fetch("IMF", {"series": "X"})
    assert a.checksum == b.checksum
    assert len(a.observations) == 1


def test_normalization_orders_panel():
    data = normalize([
        Observation("WB", "wb", "gdp", "usa", "2024", 2.0),
        Observation("WB", "wb", "gdp", "jpn", "2024", 1.0),
    ])
    assert [x.economy for x in data] == ["JPN", "USA"]
