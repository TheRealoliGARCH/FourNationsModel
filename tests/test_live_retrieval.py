import pytest

from fournations.live_retrieval import certify, retrieve


def complete_fetcher(nation, year, feature):
    return float(year)


def test_complete_retrieval_certifies_snapshot():
    run = retrieve(complete_fetcher)
    assert run.result.status == "ready_for_snapshot"
    result = certify(run, {"gdp": "NY.GDP.MKTP.CD"})
    assert result["shape"]["cells"] == 416
    assert result["checksum_sha256"]


def test_provider_failure_is_localized_and_blocks_manifest():
    def fetcher(nation, year, feature):
        if (nation, year, feature) == ("CHE", 2017, "credit_gdp"):
            raise RuntimeError("provider failure")
        return 1.0

    run = retrieve(fetcher)
    assert run.result.status == "blocked_incomplete_coverage"
    assert run.result.missing == (("CHE", 2017, "credit_gdp"),)
    with pytest.raises(RuntimeError):
        certify(run, {})
