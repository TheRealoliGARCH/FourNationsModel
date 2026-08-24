from fournations.provider_bindings import NATIONS, bindings, require_declared_binding


def test_every_nation_has_all_nation_specific_external_features():
    rows = bindings()
    for nation in NATIONS:
        for feature in ("credit_gdp", "reer_log_change", "long_term_rate"):
            row = require_declared_binding(feature, nation)
            assert row.series


def test_swiss_credit_is_explicit_component_aggregation():
    row = require_declared_binding("credit_gdp", "CHE")
    assert row.series == ("Q.CH.N.A.M.770.A", "Q.CH.H.A.M.770.A", "Q.CH.G.A.M.770.A")


def test_common_macro_features_are_bound_once():
    rows = bindings()
    assert len([r for r in rows if r.feature == "real_gdp_growth"]) == 1
    assert len([r for r in rows if r.feature == "log_gdp_usd"]) == 1
