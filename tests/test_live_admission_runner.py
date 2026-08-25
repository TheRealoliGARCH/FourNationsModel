import json

from fournations.end_to_end import EndToEndResult
from fournations.live_admission_runner import report, write_report
from fournations.live_retrieval import RetrievalRun
from fournations.snapshot_admission import AdmissionResult


def _result(status, missing=(), manifest=None):
    run = RetrievalRun(
        result=AdmissionResult(status=status, missing=tuple(missing)),
        panel={"USA": {2013: {"gdp_growth": 2.0}}},
        retrieved_at="2026-08-25T00:00:00Z",
    )
    return EndToEndResult(run=run, snapshot_manifest=manifest)


def test_blocked_report_preserves_exact_missing_cells():
    payload = report(
        _result("blocked_incomplete_coverage", (("CHE", 2017, "credit_gdp"),)),
        experiment_id="host-nations-v2",
    )
    assert payload["status"] == "blocked_incomplete_coverage"
    assert payload["missing"] == [["CHE", 2017, "credit_gdp"]]
    assert payload["snapshot_manifest"] is None


def test_ready_report_preserves_manifest():
    manifest = {"shape": {"cells": 416}}
    payload = report(_result("ready_for_snapshot", manifest=manifest), experiment_id="host-nations-v2")
    assert payload["snapshot_manifest"] == manifest


def test_report_is_persisted_as_json(tmp_path):
    path = tmp_path / "admission.json"
    payload = {"status": "blocked_incomplete_coverage", "missing": []}
    write_report(path, payload)
    assert json.loads(path.read_text(encoding="utf-8")) == payload
