from fournations.snapshot_admission import FEATURES, NATIONS, YEARS, manifest, validate_panel


def full_panel():
    return {(n, y, f): 1.0 for n in NATIONS for y in YEARS for f in FEATURES}


def test_complete_panel_has_416_cells_and_checksum():
    result = validate_panel(full_panel())
    assert result.status == "ready_for_snapshot"
    assert result.checksum is not None


def test_missing_cell_blocks_admission():
    panel = full_panel()
    panel[("CHE", 2017, "credit_gdp")] = None
    result = validate_panel(panel)
    assert result.status == "blocked_incomplete_coverage"
    assert result.missing == (("CHE", 2017, "credit_gdp"),)


def test_manifest_refuses_unadmitted_panel():
    result = validate_panel({})
    try:
        manifest("host-nations-v2", result, provider_keys={}, retrieved_at="2026-08-25T00:00:00Z")
    except RuntimeError:
        pass
    else:
        raise AssertionError("manifest must reject incomplete panel")
