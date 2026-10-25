"""Tests for the staging logic in evinfra.ingestion.extract_bee_pcs (no PDF needed)."""

from __future__ import annotations

import pytest

from evinfra.ingestion import extract_bee_pcs as ext

HEADER = [
    "CPO Name",
    "Govt/Private",
    "State",
    "District",
    "City/Village",
    "Location",
    "Latitude",
    "Longitude",
    "Types of Chargers Installed/\nConnector",
    "Charger\nRating",
    "Connector\nRating",
    "No. of\nConnector",
]


def row(cpo="IOCL", state="Karnataka", location="MG Road", lat="12.9", lon="77.6"):
    return [cpo, "Govt.", state, "Mysuru", "Mysuru", location, lat, lon, "CCS", "30", "30", "1"]


def test_header_rows_are_dropped_and_counted():
    rows, report = ext.normalise_rows([[HEADER, row()], [HEADER, row()]])
    assert len(rows) == 2
    assert report["header_rows"] == 2


def test_source_row_ids_follow_page_and_row_position():
    rows, _ = ext.normalise_rows([[HEADER, row(), row()], [row()]])
    assert [r["source_row_id"] for r in rows] == ["S15-p0001-r02", "S15-p0001-r03", "S15-p0002-r01"]
    assert rows[2]["page"] == "2" and rows[2]["row_on_page"] == "1"


def test_wrapped_cell_text_is_joined_and_otherwise_unchanged():
    rows, _ = ext.normalise_rows([[row(location="Near Bus Stand,\nHubballi  Road", lat="12.90")]])
    assert rows[0]["location"] == "Near Bus Stand, Hubballi  Road"
    assert rows[0]["latitude"] == "12.90"


def test_no_rows_are_filtered_by_state():
    rows, _ = ext.normalise_rows([[row(state="Kerala"), row(state="KARNATAKA")]])
    assert [r["state"] for r in rows] == ["Kerala", "KARNATAKA"]


def test_identical_rows_are_all_kept():
    rows, _ = ext.normalise_rows([[row(), row(), row()]])
    assert len(rows) == 3


def test_blank_rows_are_counted_and_none_cells_become_empty():
    blank = [None] * 12
    partial = row()
    partial[1] = None
    rows, report = ext.normalise_rows([[blank, partial]])
    assert report["blank_rows"] == 1
    assert rows[0]["govt_private"] == ""


def test_wrong_cell_count_raises():
    with pytest.raises(ext.ExtractionError, match="11 cells"):
        ext.normalise_rows([[row()[:11]]])


def test_staging_columns_cover_every_source_field():
    assert len(ext.FIELDS) == len(ext.SOURCE_HEADER) == 12
    assert ext.COLUMNS[:3] == ["source_row_id", "page", "row_on_page"]
