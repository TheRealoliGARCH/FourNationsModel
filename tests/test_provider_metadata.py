from fournations.provider_metadata import SeriesRecord, resolve_unique, coverage

PERIODS = tuple(str(y) for y in range(2012, 2025))

def record(key, economy, semantic, periods=PERIODS):
    return SeriesRecord("BIS", key, economy, semantic, periods, {})

def test_unique_provider_record_resolves_exactly():
    r = resolve_unique([record("Q.IN.C.A.M.770.A", "IN", "credit_gdp")], provider="BIS", economy="IN", semantic="credit_gdp")
    assert r.status == "resolved"
    assert r.key == "Q.IN.C.A.M.770.A"
    assert coverage(r, PERIODS) == "complete"

def test_missing_record_remains_unresolved():
    r = resolve_unique([], provider="BIS", economy="CH", semantic="credit_gdp")
    assert r.status == "unresolved"

def test_multiple_records_are_not_silently_selected():
    rows = [record("Q.CH.N.A.M.770.A", "CH", "credit_gdp"), record("Q.CH.H.A.M.770.A", "CH", "credit_gdp")]
    r = resolve_unique(rows, provider="BIS", economy="CH", semantic="credit_gdp")
    assert r.status == "ambiguous"
