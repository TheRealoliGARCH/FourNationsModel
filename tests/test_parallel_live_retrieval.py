from fournations.live_retrieval import retrieve


def test_retrieve_checkpoints_completed_cells(monkeypatch):
    import fournations.live_retrieval as module

    monkeypatch.setattr(module, "NATIONS", ("USA",))
    monkeypatch.setattr(module, "YEARS", (2013,))
    monkeypatch.setattr(module, "FEATURES", ("a", "b"))

    checkpoints = []
    run = retrieve(lambda nation, year, feature: 1.0, max_workers=2, checkpoint=checkpoints.append)

    assert len(run.panel) == 2
    assert len(checkpoints) == 2
    assert len(checkpoints[0]) == 1
    assert len(checkpoints[1]) == 2


def test_retrieve_records_failed_future_as_missing(monkeypatch):
    import fournations.live_retrieval as module

    monkeypatch.setattr(module, "NATIONS", ("USA",))
    monkeypatch.setattr(module, "YEARS", (2013,))
    monkeypatch.setattr(module, "FEATURES", ("ok", "bad"))

    def fetcher(nation, year, feature):
        if feature == "bad":
            raise TimeoutError("bounded timeout")
        return 1.0

    run = retrieve(fetcher, max_workers=2)
    assert run.panel[("USA", 2013, "ok")] == 1.0
    assert run.panel[("USA", 2013, "bad")] is None
