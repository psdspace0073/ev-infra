"""Tests for the Karnataka planning slice (R4-11)."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter

import pytest

from evinfra.scoring import build_karnataka_planning_slice as ps

with open(ps.PARAMS, encoding="utf-8") as f:
    P = json.load(f)


def cand(osm_id, lat, lon, gap_km, place="p1", category="C", status="eligible"):
    return {
        "osm_id": osm_id,
        "latitude": f"{lat:.6f}",
        "longitude": f"{lon:.6f}",
        "nearest_place_osm_id": place,
        "nearest_e4w_charger_km": f"{gap_km:.3f}",
        "subsidy_category_modelled": category,
        "status": status,
        "selection_order": "",
    }


def test_e4w_state_three_states():
    rules = P["bee_e4w_compatibility"]
    assert ps.e4w_state("CCS-II", rules) == "confirmed"
    assert ps.e4w_state("LEV AC Charge point", rules) == "confirmed_not"
    assert ps.e4w_state("Bharat AC-001", rules) == "unknown"


def test_cost_split_counts_each_amount_once():
    c = ps.cost_split("C", P)
    assert c["total"] == pytest.approx(13.29)
    assert c["subsidy"] == pytest.approx(0.8 * 6.04)
    b = ps.cost_split("B", P)
    assert b["subsidy"] == pytest.approx(0.8 * 6.04 + 0.7 * 7.25)
    for split in (b, c):
        assert split["public"] == pytest.approx(split["subsidy"] + split["other_public"])
        assert split["operator"] == pytest.approx(split["total"] - split["public"])


def test_select_respects_budget_spacing_and_settlement_limit():
    params = json.loads(json.dumps(P))
    params["public_budget_inr_lakh"]["value"] = 10.0  # two category C sites (4.832 each)
    cands = [
        cand("a", 12.0, 76.0, 9.0, place="p1"),
        cand("b", 12.0, 76.005, 8.0, place="p2"),  # ~0.54 km from a: spacing
        cand("c", 12.1, 76.0, 7.0, place="p1"),  # same settlement as a
        cand("d", 12.2, 76.0, 6.0, place="p3", status="rejected: outside urban proxy"),
        cand("e", 12.3, 76.0, 5.0, place="p4"),
        cand("f", 12.4, 76.0, 4.0, place="p5"),  # over budget
    ]
    chosen = ps.select(cands, params)
    assert [c["osm_id"] for c in chosen] == ["a", "e"]
    status = {c["osm_id"]: c["status"] for c in cands}
    assert status["b"].endswith("(spacing to a selected site)")
    assert status["c"].endswith("(settlement already has a selected site)")
    assert status["d"] == "rejected: outside urban proxy"
    assert status["f"].endswith("(budget)")


@pytest.fixture(scope="module")
def built():
    if not all(path.exists() for _, path, _ in ps.INPUTS):
        pytest.skip("slice inputs not present")
    return ps.build()


def rows(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


def test_build_is_deterministic_and_matches_tracked_outputs(built):
    outputs, _ = built
    again, _ = ps.build()
    assert outputs == again
    for name, data in outputs.items():
        path = ps.OUT_DIR / name
        if path.exists():
            assert path.read_bytes().replace(b"\r\n", b"\n") == data, name


def test_selected_sites_meet_stated_constraints(built):
    outputs, summary = built
    cands = rows(outputs["candidates.csv"])
    selected = [c for c in cands if c["status"] == "selected"]
    assert len(selected) == summary["selected_sites"] > 0
    radius = P["duplication_radius_km"]["value"]
    urban = P["urban_proxy"]["radius_km"]
    for c in selected:
        assert float(c["nearest_e4w_charger_km"]) > radius
        assert float(c["nearest_place_km"]) <= urban
    assert Counter(c["nearest_place_osm_id"] for c in selected).most_common(1)[0][1] == 1
    proposal = rows(outputs["proposal.csv"])
    assert {p["tier_label"] for p in proposal} == {ps.TIER}
    public = sum(float(p["public_cost_inr_lakh"]) for p in proposal)
    assert public <= P["public_budget_inr_lakh"]["value"]
    for p in proposal:
        assert p["capacity_kwh_day_low_central_high"].startswith("not computed")


def test_unit_screen_uses_verified_units_and_minimum(built):
    outputs, summary = built
    screen = rows(outputs["unit_screen.csv"])
    assert len(screen) == 29
    minimum = P["unit_screen"]["min_served_bev_registrations"]
    for r in screen:
        eligible = int(r["served_bev_registrations"]) >= minimum
        assert (r["screen_eligible"] == "yes") == eligible
    assert screen[0]["unit_name"] == summary["slice_unit"]
    ratios = [float(r["served_bev_per_listed_site"]) for r in screen if r["screen_rank"]]
    assert ratios == sorted(ratios, reverse=True)


def test_site_card_states_caveats(built):
    outputs, _ = built
    card = outputs["site_card.md"].decode("utf-8")
    assert "not owner residence" in card
    assert "not a confirmed merge" in card
    assert "modelled, not sanctioned" in card
