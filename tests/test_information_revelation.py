from fournations.information_revelation import (
    InformationState,
    assess_option_value,
    classify_panel,
    public_information_coverage,
    revelation_state,
)


def test_revelation_state_distinguishes_observation_from_non_revelation():
    assert revelation_state(1.0) is InformationState.REVEALED
    assert revelation_state(None) is InformationState.NON_REVEALED


def test_classify_panel_preserves_cell_identity_and_observed_value():
    panel = {
        ("USA", 2013, "real_gdp_growth"): 2.0,
        ("CHE", 2013, "credit_gdp"): None,
    }
    classified = classify_panel(panel)
    assert classified[("USA", 2013, "real_gdp_growth")].state is InformationState.REVEALED
    assert classified[("CHE", 2013, "credit_gdp")].state is InformationState.NON_REVEALED
    assert classified[("CHE", 2013, "credit_gdp")].observed_value is None


def test_option_value_prefers_non_revelation_when_retention_is_more_valuable():
    assessment = assess_option_value(
        ("CHE", 2013, "credit_gdp"),
        reveal_value=3.0,
        retain_value=5.5,
    )
    assert assessment.option_value == 2.5
    assert assessment.preferred_state is InformationState.NON_REVEALED


def test_option_value_prefers_revelation_when_retention_has_no_positive_option_value():
    assessment = assess_option_value(
        ("USA", 2013, "real_gdp_growth"),
        reveal_value=5.0,
        retain_value=4.0,
    )
    assert assessment.option_value == -1.0
    assert assessment.preferred_state is InformationState.REVEALED


def test_public_information_coverage_is_distinct_from_snapshot_admission():
    panel = {
        ("USA", 2013, "a"): 1.0,
        ("USA", 2013, "b"): None,
        ("CHE", 2013, "a"): 2.0,
        ("CHE", 2013, "b"): None,
    }
    assert public_information_coverage(panel) == 0.5
