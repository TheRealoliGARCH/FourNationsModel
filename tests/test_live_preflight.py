from fournations.live_preflight import NATIONS, YEARS, SeriesResolution, evaluate

def rows(key=True, periods=YEARS):
    return [SeriesResolution('BIS','reer',n,'k' if key else None,tuple(periods)) for n in NATIONS]

def test_unresolved_metadata_blocks_release():
    result = evaluate(rows(key=False))
    assert result.status == 'blocked_unresolved_metadata'

def test_incomplete_coverage_blocks_release():
    result = evaluate(rows(periods=YEARS[:-1]))
    assert result.status == 'blocked_incomplete_coverage'

def test_complete_exact_coverage_releases():
    result = evaluate(rows())
    assert result.status == 'ready_for_snapshot'
