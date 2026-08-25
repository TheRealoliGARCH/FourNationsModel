from fournations.missing_cell_topology import topology


def test_topology_counts_missing_cells_by_feature_and_nation():
    panel = [
        {"nation": "USA", "year": 2013, "feature": "credit_gdp", "value": None},
        {"nation": "USA", "year": 2014, "feature": "credit_gdp", "value": None},
        {"nation": "CHE", "year": 2013, "feature": "inflation", "value": None},
        {"nation": "CHE", "year": 2014, "feature": "inflation", "value": 1.0},
    ]
    result = topology(panel)
    assert result["missing_cell_count"] == 3
    assert result["by_feature"] == {"credit_gdp": 2, "inflation": 1}
    assert result["by_nation"] == {"CHE": 1, "USA": 2}
    assert result["by_nation_feature"] == {"CHE:inflation": 1, "USA:credit_gdp": 2}


def test_topology_preserves_exact_missing_identity():
    panel = [{"nation": "IND", "year": 2020, "feature": "long_term_rate", "value": None}]
    result = topology(panel)
    assert result["missing_cells"] == panel
