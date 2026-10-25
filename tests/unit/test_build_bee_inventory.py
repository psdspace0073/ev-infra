"""Tests for evinfra.analysis.build_bee_inventory using small temporary fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_build_district_table import boundary, lgd, square, write_csv, write_shapefile_zip

from evinfra.analysis import build_bee_inventory as bbi
from evinfra.analysis import build_district_table as bdt
from evinfra.ingestion import extract_bee_pcs as ext

# Bagalkote (524 / census 556) covers lon 0..1, Ballari (528 / 565) covers lon 1..2,
# both lat 0..1. Vijayanagar (738) has no 2011 polygon.


def bee(rid, lat, lon, cpo="IOCL", state="Karnataka", district="Bagalkote", location="L1", **kw):
    r = dict.fromkeys(ext.COLUMNS, "")
    page, row_on_page = rid.split("-")[1:]
    r.update(
        source_row_id=rid,
        page=str(int(page[1:])),
        row_on_page=str(int(row_on_page[1:])),
        cpo_name=cpo,
        govt_private="Govt.",
        state=state,
        district=district,
        city_village="X",
        location=location,
        latitude=lat,
        longitude=lon,
        charger_type="CCS",
        charger_rating="30",
        connector_rating="30",
        no_of_connector="2",
    )
    r.update(kw)
    return r


def default_data() -> dict:
    return {
        "s16": [
            bee("S15-p0001-r01", "0.5", "0.6"),
            bee("S15-p0001-r02", "0.5", "0.6"),  # exact duplicate of r01
            bee("S15-p0001-r03", "0.5", "0.6", cpo="Tata Power", location="L2"),
            bee("S15-p0001-r04", "0.500100", "0.6", location="L3"),  # ~11 m north
            bee("S15-p0002-r01", "0.5", "1.5", district="Vijayanagara", location="L4"),
            bee("S15-p0002-r02", "0.7", "1.7", district="Bagalkote", location="L5"),
            bee("S15-p0002-r03", "0.3", "0.3", location="L6", latitude="0.3", longitude="0.3"),
            bee("S15-p0002-r04", "abc", "0.5", location="L7"),
            bee("S15-p0002-r05", "0.5", "5.0", location="L8"),
            bee("S15-p0002-r06", "0.5", "0.5", state="Kerala", location="Karnataka border"),
            bee("S15-p0003-r01", "0.2", "0.25", district="Nowhere", location="L9"),
            bee("S15-p0003-r02", "0.8", "0.85", location="L10", charger_rating="NA"),
        ],
        "s06": [
            lgd("Bagalkote", "524", "556"),
            lgd("Ballari", "528", "565"),
            lgd("Vijayanagar", "738", "0"),
            # Alias targets without fixture polygons.
            lgd("Ramanagara", "631", "0"),
            lgd("Chamarajanagara", "531", "0"),
            lgd("Davangere", "535", "0"),
        ],
        "boundaries": [
            (boundary("Bagalkot", "556"), [square(0, 0, 1, 1)]),
            (boundary("Bellary", "565"), [square(1, 0, 2, 1)]),
        ],
        "s11": [
            {"inventory_id": "KA-OSM-N1", "latitude": "0.5003", "longitude": "0.6"},  # ~33 m
            {"inventory_id": "KA-OSM-N2", "latitude": "0.1", "longitude": "1.9"},
        ],
    }


def install(tmp_path: Path, data: dict) -> tuple[Path, Path, Path]:
    raw = tmp_path / "raw"
    (raw / "district_boundaries").mkdir(parents=True)
    write_csv(raw / bdt.S06.name, data["s06"])
    write_shapefile_zip(raw / "district_boundaries" / bdt.BOUNDARIES.name, data["boundaries"])
    s16 = tmp_path / "s16.csv"
    write_csv(s16, data["s16"])
    s11 = tmp_path / "s11.csv"
    write_csv(s11, data["s11"])
    return s16, raw, s11


@pytest.fixture
def data() -> dict:
    return default_data()


def build(tmp_path, data):
    s16, raw, s11 = install(tmp_path, data)
    return bbi.build(s16, raw, s11)


def by_id(rows):
    return {r["source_row_id"]: r for r in rows}


def test_karnataka_filter_uses_state_field_only(tmp_path, data):
    rows, _, summary = build(tmp_path, data)
    assert "S15-p0002-r06" not in by_id(rows)
    assert summary["raw_rows_all_states"] == 12
    assert summary["karnataka_rows"] == 11
    assert summary["rows_mentioning_karnataka_in_location_but_other_state"] == 1


def test_source_fields_are_kept_as_printed(tmp_path, data):
    rows = by_id(build(tmp_path, data)[0])
    for col in bbi.SOURCE_FIELDS:
        assert rows["S15-p0002-r04"][col] == data["s16"][7][col]


def test_invalid_coordinates_are_flagged_not_dropped(tmp_path, data):
    rows, _, summary = build(tmp_path, data)
    r = by_id(rows)
    assert r["S15-p0002-r03"]["coordinate_status"] == "latitude_equals_longitude"
    assert r["S15-p0002-r04"]["coordinate_status"] == "not_numeric"
    assert r["S15-p0002-r05"]["coordinate_status"] == "outside_karnataka_polygons"
    assert r["S15-p0002-r05"]["site_id"] == ""
    assert summary["rows_with_valid_coordinates"] == 8
    assert len(rows) == 11


def test_exact_duplicates_are_counted_and_kept(tmp_path, data):
    rows, _, summary = build(tmp_path, data)
    r = by_id(rows)
    assert r["S15-p0001-r01"]["exact_duplicate_group_size"] == "2"
    assert r["S15-p0001-r02"]["exact_duplicate_group_size"] == "2"
    assert r["S15-p0001-r03"]["exact_duplicate_group_size"] == "1"
    assert summary["exact_duplicate_surplus_rows"] == 1


def test_station_keys_and_sites_count_different_units(tmp_path, data):
    rows, sites, summary = build(tmp_path, data)
    r = by_id(rows)
    assert r["S15-p0001-r01"]["station_key"] == r["S15-p0001-r02"]["station_key"]
    assert r["S15-p0001-r01"]["station_key"] != r["S15-p0001-r03"]["station_key"]
    assert r["S15-p0001-r01"]["site_id"] == r["S15-p0001-r03"]["site_id"]
    site = next(s for s in sites if s["site_id"] == r["S15-p0001-r01"]["site_id"])
    assert site["source_rows"] == "3"
    assert site["station_keys"] == "2"
    assert site["connectors"] == "6"
    assert site["cpo_names"] == "IOCL;Tata Power"
    assert summary["karnataka_connectors"] == 22


def test_nearby_sites_cluster_without_merging(tmp_path, data):
    rows, sites, summary = build(tmp_path, data)
    r = by_id(rows)
    a, b = r["S15-p0001-r01"]["site_id"], r["S15-p0001-r04"]["site_id"]
    assert a != b
    s = {x["site_id"]: x for x in sites}
    assert s[a]["nearby_sites_within_25m"] == "1"
    assert s[a]["site_cluster_25m"] == s[b]["site_cluster_25m"]
    assert summary["candidate_physical_sites"] == len(sites)
    assert summary["site_clusters_25m"] == len(sites) - 1


def test_district_assignment_and_checks(tmp_path, data):
    r = by_id(build(tmp_path, data)[0])
    assert r["S15-p0001-r01"]["district_check"] == "agree"
    assert r["S15-p0002-r01"]["lgd_district_code_stated"] == "738"  # alias Vijayanagara
    assert r["S15-p0002-r01"]["district_check"] == "agree_pre_split"
    assert r["S15-p0002-r02"]["district_check"] == "disagree"
    assert r["S15-p0002-r02"]["lgd_district_code_by_point"] == "528"
    assert r["S15-p0003-r01"]["district_check"] == "stated_district_unmatched"
    assert r["S15-p0002-r05"]["district_check"] == "not_assessable"


def test_missing_values_stay_missing(tmp_path, data):
    rows, _, summary = build(tmp_path, data)
    r = by_id(rows)
    assert r["S15-p0003-r02"]["charger_rating_value"] == ""
    assert r["S15-p0003-r02"]["charger_rating"] == "NA"
    assert {x["operational_status"] for x in rows} == {""}
    assert summary["rows_with_known_operating_status"] == 0
    assert summary["rows_confirmed_operational"] == 0
    assert summary["rows_with_numeric_charger_rating"] == 10


def test_osm_overlap_is_proximity_based(tmp_path, data):
    rows, sites, summary = build(tmp_path, data)
    site = next(s for s in sites if s["site_id"] == by_id(rows)["S15-p0001-r01"]["site_id"])
    assert site["nearest_osm_inventory_id"] == "KA-OSM-N1"
    assert site["osm_match_within_100m"] == "yes"
    assert summary["osm_records_with_bee_site_within_100m"] == 1
    assert summary["osm_records_without_bee_site_within_100m"] == 1


def test_unknown_alias_target_raises(tmp_path, data, monkeypatch):
    monkeypatch.setitem(bbi.DISTRICT_ALIASES, "bengaluru south", "999")
    with pytest.raises(bbi.BeeInventoryError, match="unknown LGD code"):
        build(tmp_path, data)


def test_duplicate_source_row_id_raises(tmp_path, data):
    data["s16"][1]["source_row_id"] = data["s16"][0]["source_row_id"]
    with pytest.raises(bbi.BeeInventoryError, match="Duplicate source_row_id"):
        build(tmp_path, data)


def test_missing_staging_column_raises(tmp_path, data):
    for r in data["s16"]:
        del r["no_of_connector"]
    with pytest.raises(bbi.BeeInventoryError, match="missing columns"):
        build(tmp_path, data)


def test_output_is_deterministic_and_independent_of_input_order(tmp_path, data):
    first = build(tmp_path / "a", data)
    data["s16"].reverse()
    second = build(tmp_path / "b", data)
    assert bdt.to_csv_bytes(bbi.ROW_COLUMNS, first[0]) == bdt.to_csv_bytes(
        bbi.ROW_COLUMNS, second[0]
    )
    assert bdt.to_csv_bytes(bbi.SITE_COLUMNS, first[1]) == bdt.to_csv_bytes(
        bbi.SITE_COLUMNS, second[1]
    )
    assert json.dumps(first[2], sort_keys=True) == json.dumps(second[2], sort_keys=True)


def test_dictionary_covers_every_column():
    d = bbi.dictionary_rows()
    assert [x["column"] for x in d if x["table"] == "S18"] == bbi.ROW_COLUMNS
    assert [x["column"] for x in d if x["table"] == "S19"] == bbi.SITE_COLUMNS
