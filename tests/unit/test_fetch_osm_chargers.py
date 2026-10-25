"""Tests for the response checks in evinfra.ingestion.fetch_osm_chargers (no network)."""

from __future__ import annotations

import json

import pytest

from evinfra.ingestion import fetch_osm_chargers as fetch


def payload(**data) -> bytes:
    return json.dumps(data).encode("utf-8")


def test_summarise_counts_element_types():
    body = payload(
        osm3s={"timestamp_osm_base": "2026-10-25T13:53:21Z"},
        elements=[{"type": "node"}, {"type": "node"}, {"type": "way"}],
    )
    assert fetch.summarise(body) == {
        "osm_base_timestamp": "2026-10-25T13:53:21Z",
        "element_count": 3,
        "element_types": {"node": 2, "way": 1},
    }


def test_summarise_rejects_remark():
    with pytest.raises(ValueError, match="remark"):
        fetch.summarise(payload(remark="runtime error: timeout", elements=[{"type": "node"}]))


def test_summarise_rejects_empty_result():
    with pytest.raises(ValueError, match="no elements"):
        fetch.summarise(payload(elements=[]))


def test_query_targets_karnataka_charging_stations():
    query = fetch.QUERY.read_text(encoding="utf-8")
    assert '"ISO3166-2"="IN-KA"' in query
    assert '["amenity"="charging_station"]' in query
