from fournations.live_snapshot import run_live_snapshot
from fournations.snapshot_admission import required_cells


def test_runner_certifies_complete_panel():
    run = run_live_snapshot(
        experiment_id="host-nations-v2",
        fetch_cell=lambda n, y, f: 1.0,
        provider_keys={"demo": "test"},
        retrieved_at="2026-08-25T00:00:00Z",
    )
    assert run.admission.status == "ready_for_snapshot"
    assert run.manifest is not None
    assert run.manifest["shape"]["cells"] == 416


def test_runner_preserves_failed_cell_locations():
    failed = required_cells()[10]
    run = run_live_snapshot(
        experiment_id="host-nations-v2",
        fetch_cell=lambda n, y, f: None if (n, y, f) == failed else 1.0,
        provider_keys={},
        retrieved_at="2026-08-25T00:00:00Z",
    )
    assert run.admission.status == "blocked_incomplete_coverage"
    assert run.manifest is None
    assert run.admission.missing == (failed,)
