from fournations.end_to_end import execute
from fournations.snapshot_admission import FEATURES


def fetcher(nation, year, feature):
    return float(year + len(nation) + len(feature))


def failing_fetcher(nation, year, feature):
    if (nation, year, feature) == ("CHE", 2017, "credit_gdp"):
        raise RuntimeError("provider unavailable")
    return fetcher(nation, year, feature)


def test_complete_execution_emits_manifest():
    result = execute(
        fetcher,
        experiment_id="host-nations-v2",
        provider_keys={f: f for f in FEATURES},
        retrieved_at="2026-08-25T00:00:00Z",
        max_workers=4,
    )
    assert result.run.admission.status == "ready_for_snapshot"
    assert result.snapshot_manifest is not None
    assert result.snapshot_manifest["shape"]["cells"] == 416


def test_failed_cell_emits_no_manifest():
    result = execute(
        failing_fetcher,
        experiment_id="host-nations-v2",
        provider_keys={},
        retrieved_at="2026-08-25T00:00:00Z",
        max_workers=4,
    )
    assert result.run.admission.status == "blocked_incomplete_coverage"
    assert result.snapshot_manifest is None
    assert ("CHE", 2017, "credit_gdp") in result.run.admission.missing
