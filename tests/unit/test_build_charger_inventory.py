"""Tests for evinfra.analysis.build_charger_inventory using small temporary fixtures."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from test_build_district_table import boundary, lgd, square, write_csv, write_shapefile_zip

from evinfra.analysis import build_charger_inventory as bci
from evinfra.analysis import build_district_table as bdt

# Bagalkote (524 / 556) covers x 0..1, Ballari (528 / 565) covers x 1..2,
# Vijayanagar (738) has no 2011 polygon. Coordinates are lon/lat degrees.


def s02_feature(key, lon, lat, **tags):
    return {
        "type": "Feature",
        "properties": {"@id": key, "amenity": "charging_station", **tags},
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "id": key,
    }


def s10_element(key, lon, lat, version=1, **tags):
    etype, eid = key.split("/")
    e = {"type": etype, "id": int(eid), "version": version, "timestamp": "2025-01-01T00:00:00Z"}
    point = {"lat": lat, "lon": lon}
    if etype == "node":
        e.update(point)
    else:
        e["center"] = point
    e["tags"] = {"amenity": "charging_station", **tags}
    return e


def s09_row(code, name, c2011, osm):
    return {
        "lgd_district_code": code,
        "lgd_district_name": name,
        "census_2011_district_code": c2011,
        "osm_mapped_charging_records": osm,
    }


def default_data() -> dict:
    return {
        "s02": [
            s02_feature("node/1", 0.5, 0.5, name="A", access="yes", motorcar="yes"),
            s02_feature("node/2", 0.5002, 0.5, name="A", motorcycle="no"),
            s02_feature("way/3", 1.5, 0.5, operator="Op", access="private"),
            s02_feature("node/4", 0.2, 0.2, name="Old only"),
        ],
        "s10": [
            s10_element("node/1", 0.5, 0.5, name="A", access="yes", motorcar="yes"),
            s10_element("node/2", 0.5002, 0.5, name="A", motorcycle="no"),
            s10_element("way/3", 1.5, 0.5, operator="Op", access="private"),
            s10_element("node/5", 1.2, 0.8, name="New only", **{"socket:type2": "2"}),
        ],
        "s06": [
            lgd("Bagalkote", "524", "556"),
            lgd("Ballari", "528", "565"),
            lgd("Vijayanagar", "738", "0"),
        ],
        "boundaries": [
            (boundary("Bagalkot", "556"), [square(0, 0, 1, 1)]),
            (boundary("Bellary", "565"), [square(1, 0, 2, 1)]),
        ],
        "s09": [
            s09_row("524", "Bagalkote", "556", "3"),
            s09_row("528", "Ballari", "565", "2"),
            s09_row("738", "Vijayanagar", "", ""),
        ],
    }


def install(tmp_path: Path, data: dict) -> tuple[Path, Path]:
    raw = tmp_path / "raw"
    (raw / "district_boundaries").mkdir(parents=True)
    (raw / bdt.S02.name).write_text(json.dumps({"features": data["s02"]}), encoding="utf-8")
    s10 = raw / "S10_osm_karnataka_charging_stations_overpass_2026-10-25.json"
    s10.write_text(json.dumps({"elements": data["s10"]}), encoding="utf-8")
    (raw / (s10.name + ".manifest.json")).write_text("{}", encoding="utf-8")
    write_csv(raw / bdt.S06.name, data["s06"])
    write_shapefile_zip(raw / "district_boundaries" / bdt.BOUNDARIES.name, data["boundaries"])
    s09 = tmp_path / "s09.csv"
    write_csv(s09, data["s09"])
    return raw, s09


@pytest.fixture
def data() -> dict:
    return default_data()


def build(tmp_path, data):
    raw, s09 = install(tmp_path, data)
    return bci.build(raw, s09)


def by_id(records):
    return {r["source_record_id"]: r for r in records}


def test_one_record_per_osm_element_with_lineage(tmp_path, data):
    records, _, _, report = build(tmp_path, data)
    recs = by_id(records)
    assert sorted(recs) == ["node/1", "node/2", "node/4", "node/5", "way/3"]
    assert recs["node/1"]["source_ids"] == "S02;S10"
    assert recs["node/4"]["source_ids"] == "S02"
    assert recs["node/5"]["source_ids"] == "S10"
    assert {r["lineage_group"] for r in records} == {"OSM"}
    assert recs["node/1"]["s02_s10_tags_identical"] == "yes"
    assert recs["node/4"]["s02_s10_tags_identical"] == ""
    assert report["records_in_both_sources"] == 3


def test_s10_metadata_and_centre_coordinates(tmp_path, data):
    records, _, _, _ = build(tmp_path, data)
    recs = by_id(records)
    assert recs["way/3"]["coordinate_basis"] == "way centre"
    assert recs["way/3"]["osm_version"] == "1"
    assert recs["node/4"]["osm_version"] == ""
    assert recs["node/5"]["socket_tags"] == "socket:type2=2"


def test_tag_difference_between_sources_is_recorded(tmp_path, data):
    data["s10"][0]["tags"]["access"] = "private"
    records, _, _, report = build(tmp_path, data)
    rec = by_id(records)["node/1"]
    assert rec["s02_s10_tags_identical"] == "no"
    assert rec["access_tag"] == "private"  # S10 wins
    assert report["records_tags_differ"] == 1


def test_access_and_compatibility_are_not_inferred(tmp_path, data):
    recs = by_id(build(tmp_path, data)[0])
    assert recs["node/1"]["access_class"] == "public_tagged"
    assert recs["way/3"]["access_class"] == "restricted_tagged"
    assert recs["node/5"]["access_class"] == "unknown"
    assert recs["node/1"]["compat_motorcar"] == "confirmed"
    assert recs["node/2"]["compat_motorcycle"] == "confirmed_not"
    assert recs["node/5"]["compat_motorcar"] == "unknown"
    assert {r["operational_status"] for r in recs.values()} == {""}


def test_possible_duplicates_are_flagged_not_merged(tmp_path, data):
    records, _, _, report = build(tmp_path, data)
    recs = by_id(records)
    assert len(records) == 5
    assert recs["node/1"]["possible_duplicate_of"] == recs["node/2"]["inventory_id"]
    assert recs["node/2"]["possible_duplicate_of"] == recs["node/1"]["inventory_id"]
    assert recs["way/3"]["possible_duplicate_of"] == ""
    assert report["possible_duplicate_pairs"] == 1


def test_distant_same_name_is_not_a_duplicate(tmp_path, data):
    data["s10"][1]["lon"] = 0.6  # about 11 km away
    data["s02"][1]["geometry"]["coordinates"][0] = 0.6
    recs = by_id(build(tmp_path, data)[0])
    assert recs["node/1"]["possible_duplicate_of"] == ""


def test_district_assignment_and_ballari_note(tmp_path, data):
    recs = by_id(build(tmp_path, data)[0])
    assert recs["node/1"]["lgd_district_code"] == "524"
    assert recs["way/3"]["lgd_district_code"] == "528"
    assert "Vijayanagar" in recs["way/3"]["district_assignment_note"]


def test_point_outside_polygons_is_quarantined(tmp_path, data):
    data["s10"][3]["lon"] = 5.0
    data["s09"][1]["osm_mapped_charging_records"] = "1"
    records, _, _, report = build(tmp_path, data)
    rec = by_id(records)["node/5"]
    assert rec["lgd_district_code"] == ""
    assert "quarantined" in rec["district_assignment_note"]
    assert report["records_quarantined"] == 1


def test_join_keeps_s09_and_leaves_demand_and_grid_missing(tmp_path, data):
    _, columns, rows, _ = build(tmp_path, data)
    assert columns[:4] == list(data["s09"][0])
    j = {r["lgd_district_code"]: r for r in rows}
    assert j["524"]["inv_osm_records"] == "3"
    assert j["528"]["inv_osm_records"] == "2"
    assert j["524"]["inv_osm_access_public_tagged"] == "1"
    assert j["738"]["inv_osm_records"] == ""
    for r in rows:
        assert r["ev_registrations_district"] == ""
        assert r["discom_names"] == ""
        assert r["grid_spare_capacity"] == ""


def test_count_mismatch_with_s09_raises(tmp_path, data):
    data["s09"][0]["osm_mapped_charging_records"] = "99"
    with pytest.raises(bci.InventoryError, match="S09"):
        build(tmp_path, data)


def test_missing_s10_raises(tmp_path, data):
    raw, s09 = install(tmp_path, data)
    for p in raw.glob("S10_*"):
        p.unlink()
    with pytest.raises(bci.InventoryError, match="No S10"):
        bci.build(raw, s09)


def test_dictionary_covers_every_inventory_and_join_column():
    rows = bci.dictionary_rows()
    s11 = [r["column"] for r in rows if r["table"] == "S11"]
    s12 = [r["column"] for r in rows if r["table"] == "S12" and r["column"] != "(S09 columns)"]
    assert s11 == bci.INVENTORY_COLUMNS
    assert s12 == bci.JOIN_EXTRA_COLUMNS


def test_output_is_deterministic(tmp_path, data):
    first = build(tmp_path / "a", data)
    data["s10"].reverse()
    data["s02"].reverse()
    second = build(tmp_path / "b", data)
    assert bdt.to_csv_bytes(bci.INVENTORY_COLUMNS, first[0]) == bdt.to_csv_bytes(
        bci.INVENTORY_COLUMNS, second[0]
    )


def test_inventory_csv_round_trips(tmp_path, data):
    records = build(tmp_path, data)[0]
    path = tmp_path / "inv.csv"
    path.write_bytes(bdt.to_csv_bytes(bci.INVENTORY_COLUMNS, records))
    with open(path, encoding="utf-8", newline="") as f:
        assert list(csv.DictReader(f)) == records
