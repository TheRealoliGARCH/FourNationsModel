from pathlib import Path

import scripts.run_live_admission as entry


def test_entrypoint_writes_runner_payload(monkeypatch, tmp_path):
    calls = {}

    monkeypatch.setattr(entry, "run", lambda fetcher, **kwargs: calls.setdefault("payload", {"status": "blocked_incomplete_coverage", "missing": []}))
    monkeypatch.setattr(entry, "write_report", lambda path, payload: Path(path).write_text("ok", encoding="utf-8"))
    monkeypatch.setattr("sys.argv", ["run_live_admission.py", "--output", str(tmp_path / "report.json")])

    entry.main()
    assert calls["payload"]["status"] == "blocked_incomplete_coverage"
    assert (tmp_path / "report.json").read_text(encoding="utf-8") == "ok"
