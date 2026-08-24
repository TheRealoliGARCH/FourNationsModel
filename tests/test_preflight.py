from fournations.preflight import check_coverage, release_gate

def test_gate_requires_exact_key():
    r = check_coverage('x', 'USA', range(2012, 2025), range(2012, 2025), None)
    assert release_gate([r]) == 'blocked_unresolved_metadata'

def test_gate_requires_full_coverage():
    r = check_coverage('x', 'USA', range(2012, 2024), range(2012, 2025), 'A.X')
    assert release_gate([r]) == 'blocked_incomplete_coverage'

def test_gate_releases_only_complete_exact_results():
    r = check_coverage('x', 'USA', range(2012, 2025), range(2012, 2025), 'A.X')
    assert release_gate([r]) == 'ready_for_snapshot'
