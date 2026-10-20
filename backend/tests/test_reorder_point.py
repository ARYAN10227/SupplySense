"""Unit tests for the statistical reorder-point formula."""

import math

from services.reorder_point_calculator import DEFAULT_Z, _statistical_reorder_point


def test_no_demand_means_no_reorder_point():
    result = _statistical_reorder_point(avg_daily=0, std_daily=3, lead_time_days=5)
    assert result["reorder_point"] == 0
    assert result["safety_stock"] == 0


def test_reorder_point_is_lead_time_demand_plus_safety_stock():
    avg, std, lead = 10.0, 4.0, 9
    result = _statistical_reorder_point(avg, std, lead, z_score=1.65)
    expected_safety = 1.65 * std * math.sqrt(lead)  # 19.8
    assert result["lead_time_demand"] == 90.0
    assert result["safety_stock"] == round(expected_safety)
    assert result["reorder_point"] == round(90 + expected_safety)


def test_zero_variability_needs_no_safety_stock():
    result = _statistical_reorder_point(avg_daily=5, std_daily=0, lead_time_days=4)
    assert result["safety_stock"] == 0
    assert result["reorder_point"] == 20


def test_higher_service_level_raises_reorder_point():
    low = _statistical_reorder_point(8, 3, 7, z_score=1.28)
    high = _statistical_reorder_point(8, 3, 7, z_score=2.33)
    assert high["reorder_point"] > low["reorder_point"]


def test_default_z_matches_95_percent_service_level():
    assert abs(DEFAULT_Z - 1.645) < 0.01
