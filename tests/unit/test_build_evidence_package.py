"""Tests for the Round 1 evidence package builder and its audit."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from evinfra.analysis import build_evidence_package as ep

REGISTER_TEXT = {
    "S01": "",
    "S03": "Karnataka 6,097",
    "S06": "",
    "S10": "",
    "S11": "",
    "S15": "",
    "S16": "",
    "S17": "Karnataka 6,096 EVCS installed (751 fast, 5,345 slow)",
    "S18": "",
    "S19": "",
    "S20": "",
    "S24": "",
    "S25": "Sep 2026 181,753; Dec 2025 130,313",
    "S26": "",
    "S27": "",
    "S28": "",
}


def month(date, bev, total):
    return {"month_end_date": date, "bev": str(bev), "all_fuel_total": str(total)}


def charger(lat, lon, district):
    return {"latitude": lat, "longitude": lon, "lgd_district_code_by_point": district}


@pytest.fixture
def data():
    return {
        "s26": {
            "karnataka_source_rows": 100,
            "rtos": 2,
            "months": 2,
            "first_month": "2025-12-31",
            "last_month": "2026-09-30",
            "s01_cross_check": {
                "2025": {
                    "s26_bev": 932,
                    "s01_bev": 1000,
                    "difference": -68,
                    "difference_pct": -6.8,
                },
                "2026": {"s26_bev": 10, "s01_bev": 20, "note": "not comparable"},
            },
        },
        "s28": {
            "annual_state_bev": {"2025": 932, "2026": 10},
            "annual_year_complete": {"2025": True, "2026": False},
            "rto_months_without_rows": 1,
            "rto_months_without_rows_by_rto": {"KA2": 1},
            "s24_vs_s27_consistency": {
                "rto_months_compared": 3,
                "equal_totals": 3,
                "differences": [],
            },
        },
        "monthly": {
            "2025-12-31": month("2025-12-31", 900, 130751),
            "2026-09-30": month("2026-09-30", 10, 184194),
        },
        "annual": [
            {"year": "2025", "rto_code": "KA1", "rto_name": "One RTO", "share_of_state_bev": "0.6"},
            {"year": "2025", "rto_code": "KA2", "rto_name": "Two RTO", "share_of_state_bev": "0.4"},
        ],
        "s18": {
            "karnataka_rows": 3,
            "karnataka_connectors": 4,
            "rows_with_valid_coordinates": 3,
            "candidate_physical_sites": 2,
            "rows_with_known_operating_status": 0,
            "osm_records": 1,
            "osm_records_with_bee_site_within_100m": 0,
            "rows_with_point_district": 3,
            "district_check": {"disagree": 0},
        },
        "s18_rows": [
            charger("12.1", "77.1", "525"),
            charger("12.1", "77.1", "525"),
            charger("15.0", "75.0", "528"),
        ],
        "s19_sites": [charger("12.1", "77.1", "525"), charger("15.0", "75.0", "528")],
        "s12": [
            {
                "lgd_district_code": "525",
                "lgd_district_name": "Bengaluru Urban",
                "osm_mapped_charging_records": "1",
                "ev_registrations_district": "",
            },
            {
                "lgd_district_code": "528",
                "lgd_district_name": "Ballari",
                "osm_mapped_charging_records": "0",
                "ev_registrations_district": "",
            },
        ],
        "crosswalk": [{"status": "unresolved"}, {"status": "unresolved"}],
        "register": [{"dataset_id": k, "notes": v} for k, v in REGISTER_TEXT.items()],
    }


def by_metric(claims, metric):
    return [c for c in claims if c["metric"] == metric]


def test_clean_build_passes_audit(data):
    claims, ctx = ep.build_claims(data, None)
    assert ep.audit(claims, data, ctx) == []
    assert ctx["verified_rtos"] == 0
    assert {c["status"] for c in claims} <= ep.STATUSES


def test_district_demand_is_not_computable_without_verified_crosswalk(data):
    claims, ctx = ep.build_claims(data, None)
    district_demand = [
        c for c in claims if c["geography_level"] == "district" and c["topic"] in {"demand", "gap"}
    ]
    assert district_demand and all(c["status"] == "not_computable" for c in district_demand)
    assert all(r["ev_registrations"] == "" for r in ctx["supply"])
    district_demand[0]["status"] = "verified_reproducible"
    assert any("without verified crosswalk" in e for e in ep.audit(claims, data, ctx))


def test_district_supply_counts_by_point(data):
    _, ctx = ep.build_claims(data, None)
    supply = {r["lgd_district_code"]: r for r in ctx["supply"]}
    assert supply["525"]["bee_rows_by_point"] == "2"
    assert supply["525"]["bee_candidate_sites_by_point"] == "1"
    assert supply["528"]["bee_rows_by_point"] == "1"


def test_supply_sum_mismatch_fails(data):
    data["s18"]["rows_with_point_district"] = 4
    claims, ctx = ep.build_claims(data, None)
    assert any("district supply sums" in e for e in ep.audit(claims, data, ctx))


def test_bev_gap_and_all_fuel_gap_are_separate(data):
    claims, ctx = ep.build_claims(data, None)
    bev = [c for c in by_metric(claims, "bev_new_registrations") if "-68" in c["claim"]]
    fuel = [c for c in by_metric(claims, "all_fuel_new_registrations") if "+2,441" in c["claim"]]
    assert len(bev) == 1 and bev[0]["claim"].startswith("Battery-EV")
    assert bev[0]["status"] == "unresolved" and "S01" in bev[0]["register_ids"]
    assert len(fuel) == 1 and fuel[0]["claim"].startswith("All-fuel")
    assert "+1.34%" in fuel[0]["claim"] and "S25" in fuel[0]["register_ids"]
    assert "-68" not in fuel[0]["claim"] and "2,441" not in bev[0]["claim"]
    fuel[0]["metric"] = "bev_new_registrations"
    assert any("metric not stated" in e for e in ep.audit(claims, data, ctx))


def test_superseded_figure_is_rejected_elsewhere(data):
    claims, ctx = ep.build_claims(data, None)
    claims[0]["claim"] += " Stage 3 found 6,113 records."
    assert any("superseded figure" in e for e in ep.audit(claims, data, ctx))


def test_official_value_must_be_in_register(data):
    data["register"] = [
        {"dataset_id": r["dataset_id"], "notes": r["notes"].replace("181,753", "")}
        for r in data["register"]
    ]
    claims, ctx = ep.build_claims(data, None)
    assert any("181,753" in e for e in ep.audit(claims, data, ctx))


def test_unknown_register_id_fails(data):
    claims, ctx = ep.build_claims(data, None)
    claims[0]["register_ids"] = "S99"
    assert any("S99" in e for e in ep.audit(claims, data, ctx))


def test_district_registrations_in_s12_fail(data):
    data["s12"][0]["ev_registrations_district"] = "123"
    claims, ctx = ep.build_claims(data, None)
    assert any("S12 has district EV" in e for e in ep.audit(claims, data, ctx))


def test_stage3_comparison(tmp_path: Path, data):
    path = tmp_path / "stage3.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["latitude", "longitude"])
        w.writeheader()
        w.writerows([{"latitude": "12.1", "longitude": "77.1"}, {"latitude": "", "longitude": ""}])
    result = ep.compare_stage3(data["s18_rows"], path)
    assert result["rows"] == 2
    assert result["rows_without_coordinates"] == 1
    assert result["s18_rows_unmatched"] == 2
    assert result["stage3_rows_not_in_s18"] == 0
    claims, ctx = ep.build_claims(data, result)
    superseded = [c for c in claims if c["status"] == "superseded"]
    assert len(superseded) == 1 and ep.audit(claims, data, ctx) == []
    assert ep.compare_stage3(data["s18_rows"], tmp_path / "missing.csv") is None
