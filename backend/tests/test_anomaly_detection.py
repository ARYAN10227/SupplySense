"""Unit tests for the Z-score anomaly detection engine."""

from services.anomaly_service import (
    _classify_anomalies,
    _compute_z_scores,
    _detect_patterns,
)


def test_z_scores_need_matching_lengths_and_three_points():
    assert _compute_z_scores([1, 2], [1, 2]) == []
    assert _compute_z_scores([1, 2, 3], [1, 2]) == []


def test_z_scores_empty_when_residuals_are_constant():
    # Every week is off by exactly 5 → zero variance → no z-scores
    assert _compute_z_scores([15, 25, 35], [10, 20, 30]) == []


def test_z_scores_are_standardised_residuals():
    results = _compute_z_scores([10, 10, 10, 40], [10, 10, 10, 10])
    assert len(results) == 4
    assert results[3]["residual"] == 30
    # The outlier is the only point above the mean
    assert results[3]["z_score"] > 0
    assert all(r["z_score"] < 0 for r in results[:3])
    assert abs(sum(r["z_score"] for r in results)) < 0.05


def test_spike_and_drop_are_classified_by_threshold():
    z = [
        {"index": 0, "z_score": 2.5, "actual": 50, "predicted": 20, "residual": 30},
        {"index": 1, "z_score": -2.3, "actual": 2, "predicted": 20, "residual": -18},
        {"index": 2, "z_score": 1.9, "actual": 30, "predicted": 20, "residual": 10},
    ]
    anomalies = _classify_anomalies(z, threshold=2.0)
    assert [(a["index"], a["type"]) for a in anomalies] == [(0, "spike"), (1, "drop")]


def test_single_large_spike_is_detected_end_to_end():
    actuals = [20, 21, 19, 20, 22, 20, 21, 19, 20, 80]
    predicted = [20] * 10
    anomalies = _classify_anomalies(_compute_z_scores(actuals, predicted))
    assert len(anomalies) == 1
    assert anomalies[0]["index"] == 9
    assert anomalies[0]["type"] == "spike"


def test_three_consecutive_same_direction_weeks_form_a_pattern():
    z = [{"index": i, "z_score": v} for i, v in enumerate([0.1, 0.8, 0.9, 1.1, -0.2])]
    patterns = _detect_patterns(z, consecutive_weeks=3)
    assert len(patterns) == 1
    assert patterns[0]["direction"] == "spike"
    assert (patterns[0]["start_index"], patterns[0]["end_index"]) == (1, 3)


def test_mixed_direction_weeks_are_not_a_pattern():
    z = [{"index": i, "z_score": v} for i, v in enumerate([0.9, -0.9, 0.9, -0.9])]
    assert _detect_patterns(z) == []
