from solar_suitability.scoring import aspect_south_score, normalize_values, score_records, weighted_score


def test_normalize_values_handles_direction_and_missing_values():
    assert normalize_values([10, 20, None], higher_is_better=True) == [0.0, 1.0, 0.0]
    assert normalize_values([10, 20], higher_is_better=False) == [1.0, 0.0]


def test_weighted_score_normalizes_by_weight_sum():
    score = weighted_score({"a": 1.0, "b": 0.0}, {"a": 2.0, "b": 2.0})

    assert score == 0.5


def test_exclusion_precedence_sets_score_to_zero():
    rows = score_records(
        [{"pv_resource": 1.0, "protected_area": True}, {"pv_resource": 0.5, "protected_area": False}],
        {"pv_resource": 1.0},
        exclusion_flags=["protected_area"],
    )

    assert rows[0]["excluded"] is True
    assert rows[0]["suitability_score"] == 0.0
    assert rows[1]["suitability_score"] == 0.5


def test_aspect_south_score_prefers_180_degrees():
    assert aspect_south_score(180) == 1.0
    assert aspect_south_score(0) == 0.0
    assert aspect_south_score(90) == 0.5
