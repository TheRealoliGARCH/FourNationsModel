import pytest

from fournations.empirical_evidence import (
    EmpiricalEvidence,
    adapt_panel,
    evidence_by_nation,
    revealed_values,
)
from fournations.information_revelation import InformationState


def test_adapter_preserves_cell_identity_value_and_provenance():
    cell = ("IND", 2017, "real_gdp_growth")
    batch = adapt_panel(
        {cell: 6.8},
        providers={cell: "world_bank"},
        retrieved_at="2026-08-25T12:00:00Z",
    )
    record = batch.records[0]
    assert record.cell == cell
    assert record.value == 6.8
    assert record.revelation_state is InformationState.REVEALED
    assert record.provider == "world_bank"
    assert record.retrieved_at == "2026-08-25T12:00:00Z"


def test_non_revelation_is_preserved_without_numeric_imputation():
    batch = adapt_panel({("CHE", 2017, "credit_gdp"): None})
    record = batch.records[0]
    assert record.value is None
    assert record.revelation_state is InformationState.NON_REVEALED
    assert revealed_values(batch.records) == ()


def test_evidence_batch_reports_public_information_coverage():
    batch = adapt_panel(
        {
            ("IND", 2017, "a"): 1.0,
            ("IND", 2017, "b"): None,
            ("USA", 2017, "a"): 2.0,
            ("USA", 2017, "b"): None,
        }
    )
    assert batch.revealed_count == 2
    assert batch.non_revealed_count == 2
    assert batch.coverage == 0.5


def test_evidence_can_be_grouped_by_nation_deterministically():
    batch = adapt_panel(
        {
            ("USA", 2017, "a"): 2.0,
            ("IND", 2017, "a"): 1.0,
            ("IND", 2017, "b"): None,
        }
    )
    grouped = evidence_by_nation(batch)
    assert tuple(grouped) == ("IND", "USA")
    assert len(grouped["IND"]) == 2


def test_inconsistent_value_and_revelation_state_is_rejected():
    with pytest.raises(ValueError):
        EmpiricalEvidence(
            cell=("IND", 2017, "a"),
            value=None,
            revelation_state=InformationState.REVEALED,
            provider=None,
            retrieved_at=None,
        )
