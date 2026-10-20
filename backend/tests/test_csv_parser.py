"""Tests for CSV column detection and parsing (heuristic path, AI disabled)."""

from unittest.mock import patch

from utils.csv_parser import _heuristic_map_columns, parse_csv


def test_heuristic_maps_common_column_names():
    mapping = _heuristic_map_columns(["Product Name", "Sale Date", "Qty", "MRP (₹)", "Expiry"])
    assert mapping == {
        "name": "Product Name",
        "date": "Sale Date",
        "quantity": "Qty",
        "price": "MRP (₹)",
        "expiry_date": "Expiry",
    }


def test_heuristic_ignores_unknown_columns():
    assert _heuristic_map_columns(["foo", "bar"]) == {}


@patch("utils.csv_parser._ai_map_columns", return_value=None)
def test_parse_csv_falls_back_to_heuristics(_mock_ai):
    csv = (
        "product_name,date,quantity,price,category\n"
        "Paracetamol 500mg,2026-04-01,12,2.5,Medicine\n"
        "ORS Sachet,2026-04-01,8,20,Medicine\n"
    ).encode()
    products, detected = parse_csv(csv, "sales.csv")
    assert {p.name for p in products} == {"Paracetamol 500mg", "ORS Sachet"}
    assert "product_name" in detected and "quantity" in detected


@patch("utils.csv_parser._ai_map_columns", return_value=None)
def test_parse_csv_skips_blank_names(_mock_ai):
    csv = b"product_name,quantity\nParacetamol,5\n,3\n"
    products, _ = parse_csv(csv, "sales.csv")
    assert [p.name for p in products] == ["Paracetamol"]


@patch("utils.csv_parser._ai_map_columns", return_value=None)
def test_empty_file_returns_nothing(_mock_ai):
    assert parse_csv(b"product_name,quantity\n", "empty.csv") == ([], [])
