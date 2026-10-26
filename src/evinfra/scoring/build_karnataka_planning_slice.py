"""Build the Karnataka planning slice (R4-11): registered data to one proposed charger site.

One reproducible path, using the register datasets already in the repository:

1. Demand: observed battery-EV registrations of the served vehicle type (S35), grouped by
   registering office into district units (verified crosswalk, S30/S31).
2. Charger evidence: BEE listed charger rows (S18) and sites (S19) with OSM records (S11),
   each classed for e-4W compatibility (confirmed, confirmed not, unknown).
3. Unit screen: served registrations per BEE site with an e-4W confirmed or unknown row;
   the unit with the highest value (above a minimum count) is the slice unit.
4. Candidates: OSM fuel stations (S23) in the unit, near a city or town node (urban proxy),
   with no e-4W confirmed or unknown charger within the S33 1 km radius.
5. Selection: greedy by coverage gap under an illustrative public-cost budget, with the
   PM E-DRIVE cost split (S34) per site. Every site is a "model-selected candidate".

Every rule and value comes from configs/planning_slice_parameters.json, which states its
basis (clause, assumption or planner input). Nothing here is a validated recommendation:
no located demand exists inside a unit, no charger has an operating status, and capacity
(kWh/day) is not computed because the derating, hours and confidence parameters are not
frozen (checklist Part I).

Inputs (read, not changed): data/processed S11, S12, S18, S19, S23 (fuel, settlements),
S35; data/raw S06 and the Census 2011 district boundaries; S33 and S34 PDFs (hash check
only); configs/ka_rto_district_crosswalk.csv, configs/source_register.csv.

Outputs: outputs/reports/planning_slice/ (inputs.csv, unit_screen.csv, rto_served_bev.csv,
candidates.csv, proposal.csv, site_card.md, map.svg, summary.json). Tracked copies of the
reviewable files go to docs/submission/planning_slice/: written with --update-docs,
otherwise compared (exit 1 if they differ).

Uses only the standard library. Run from the repository root:
    python src/evinfra/scoring/build_karnataka_planning_slice.py [--force] [--update-docs]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

from evinfra.analysis import build_charger_inventory as bci
from evinfra.analysis import build_district_table as bdt
from evinfra.analysis import build_evidence_package as ep

ROOT = bdt.ROOT
PROC = bdt.OUT_DIR
RAW = bdt.RAW
PARAMS = ROOT / "configs" / "planning_slice_parameters.json"
OUT_DIR = ROOT / "outputs" / "reports" / "planning_slice"
DOCS_DIR = ROOT / "docs" / "submission" / "planning_slice"
DOCS_FILES = ("unit_screen.csv", "proposal.csv", "site_card.md", "map.svg", "summary.json")
BOUNDARIES = RAW / "district_boundaries" / bdt.BOUNDARIES.name

# (register ID, path, kind); kind "csv" or "geojson" gives a row/feature count.
INPUTS = [
    ("S35", PROC / "S35_ka_bev_rto_class_month.csv", "csv"),
    ("S30/S31", ep.CROSSWALK, "csv"),
    ("S18", PROC / "S18_karnataka_bee_pcs_rows.csv", "csv"),
    ("S19", PROC / "S19_karnataka_bee_pcs_sites.csv", "csv"),
    ("S11", PROC / "S11_karnataka_charger_inventory.csv", "csv"),
    ("S12", PROC / "S12_karnataka_district_charger_join.csv", "csv"),
    ("S23", PROC / "S23_osm_ka_fuel.geojson", "geojson"),
    ("S23", PROC / "S23_osm_ka_settlements.geojson", "geojson"),
    ("S06", RAW / bdt.S06.name, "csv"),
    ("S20", BOUNDARIES, "file"),
    ("S33", RAW / "S33_mop_evci_guidelines_2024-09-17.pdf", "file"),
    ("S34", RAW / "S34_mhi_pm_edrive_ev_pcs_operational_guidelines_2025-09-26.pdf", "file"),
    ("register", ep.REGISTER, "csv"),
    ("parameters", PARAMS, "file"),
]
TIER = "Model-selected candidate"
TIER_NOTE = "Chosen by the slice rules; land, parking, grid connection and ownership not checked"


class SliceError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_geojson(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)["features"]


def km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return bci.distance_m(lat1, lon1, lat2, lon2) / 1000


def check_inputs(register: list[dict[str, str]]) -> list[dict[str, str]]:
    """Hash every input; raw PDFs must match the hash recorded in the register."""
    reg = {r["dataset_id"]: r for r in register}
    out = []
    for rid, path, kind in INPUTS:
        if not path.exists():
            raise SliceError(f"Missing input {path}")
        digest = sha256(path)
        if rid in ("S33", "S34") and digest not in reg[rid]["sha256"]:
            raise SliceError(f"{path.name} hash differs from register {rid}")
        if kind == "csv":
            count = str(len(bdt.read_csv(path)))
        elif kind == "geojson":
            count = str(len(load_geojson(path)))
        else:
            count = ""
        out.append(
            {
                "register_id": rid,
                "path": path.relative_to(ROOT).as_posix(),
                "rows_or_features": count,
                "register_retrieved_or_built": reg[rid]["retrieved_at"] if rid in reg else "",
                "sha256": digest,
            }
        )
    return out


def e4w_state(charger_type: str, rules: dict) -> str:
    if charger_type in rules["confirmed"]:
        return "confirmed"
    if charger_type.startswith(rules["confirmed_not_prefix"]):
        return "confirmed_not"
    return "unknown"


def charger_points(s18: list[dict], s11: list[dict], rules: dict) -> list[dict]:
    """Located charger evidence with e-4W state; BEE rows and OSM records kept separate."""
    out = []
    for r in s18:
        if r["coordinate_status"] != "valid":
            continue
        out.append(
            {
                "id": r["source_row_id"],
                "lineage": "BEE",
                "site_id": r["site_id"],
                "lat": float(r["latitude"]),
                "lon": float(r["longitude"]),
                "lgd": r["lgd_district_code_by_point"],
                "e4w": e4w_state(r["charger_type"], rules),
                "kw": float(r["charger_rating_value"] or 0),
            }
        )
    for r in s11:
        out.append(
            {
                "id": r["inventory_id"],
                "lineage": "OSM",
                "site_id": "",
                "lat": float(r["latitude"]),
                "lon": float(r["longitude"]),
                "lgd": r["lgd_district_code"],
                "e4w": r["compat_motorcar"],
                "kw": 0.0,
            }
        )
    return out


def units(crosswalk: list[dict], s12: list[dict]) -> dict[str, dict]:
    names = {r["lgd_district_code"]: r["lgd_district_name"] for r in s12}
    out: dict[str, dict] = {}
    for r in crosswalk:
        if not ep.is_verified(r):
            raise SliceError(f"Crosswalk row {r['rto_code_vahan']} is not verified")
        code = r["lgd_district_code"]
        u = out.setdefault(
            code,
            {
                "codes": code.split(";"),
                "name": " + ".join(names.get(c, c) for c in code.split(";")),
                "rtos": [],
            },
        )
        u["rtos"].append(r["rto_code_vahan"])
    for u in out.values():
        u["rtos"].sort(key=lambda c: int(c[2:]))
    return out


def served_by_rto(s35: list[dict], year: int, classes: list[str]) -> tuple[dict, Counter]:
    """BEV registrations in the reference year: served classes by RTO, and all classes."""
    served: dict[str, Counter] = {}
    total: Counter = Counter()
    for r in s35:
        if not r["month_end_date"].startswith(str(year)):
            continue
        n = int(r["bev_registrations"])
        total[r["rto_code"]] += n
        if r["vehicle_class"] in classes:
            served.setdefault(r["rto_code"], Counter())[r["vehicle_class"]] += n
    return served, total


def screen_units(
    unit_map: dict, served: dict, total: Counter, chargers: list[dict], p: dict
) -> list[dict]:
    listed_sites: dict[str, set] = {}
    rows_by: dict[str, Counter] = {}
    osm_by: Counter = Counter()
    for c in chargers:
        if c["lineage"] == "BEE":
            rows_by.setdefault(c["lgd"], Counter())[c["e4w"]] += 1
            if c["e4w"] != "confirmed_not":
                listed_sites.setdefault(c["lgd"], set()).add(c["site_id"])
        else:
            osm_by[c["lgd"]] += 1
    minimum = p["unit_screen"]["min_served_bev_registrations"]
    out = []
    for key, u in unit_map.items():
        s = sum(sum(served.get(r, Counter()).values()) for r in u["rtos"])
        sites = sum(len(listed_sites.get(c, ())) for c in u["codes"])
        rows = Counter()
        for c in u["codes"]:
            rows.update(rows_by.get(c, Counter()))
        ratio = s / sites if sites else None
        out.append(
            {
                "unit_lgd_codes": key,
                "unit_name": u["name"],
                "rto_codes": " ".join(u["rtos"]),
                "served_bev_registrations": str(s),
                "all_bev_registrations": str(sum(total[r] for r in u["rtos"])),
                "bee_rows_e4w_confirmed": str(rows["confirmed"]),
                "bee_rows_e4w_unknown": str(rows["unknown"]),
                "bee_rows_e4w_confirmed_not": str(rows["confirmed_not"]),
                "bee_sites_e4w_listed": str(sites),
                "osm_records": str(sum(osm_by[c] for c in u["codes"])),
                "served_bev_per_listed_site": f"{ratio:.1f}" if ratio is not None else "",
                "screen_eligible": "yes" if s >= minimum and ratio is not None else "no",
                "_ratio": ratio if s >= minimum and ratio is not None else -1.0,
            }
        )
    out.sort(key=lambda r: (-r["_ratio"], -int(r["served_bev_registrations"]), r["unit_name"]))
    for i, r in enumerate(out, 1):
        r["screen_rank"] = str(i) if r["screen_eligible"] == "yes" else ""
        del r["_ratio"]
    return out


def brand_of(props: dict) -> str:
    return (props.get("brand") or props.get("operator") or "").strip()


def candidates(
    unit: dict,
    fuel: list[dict],
    settlements: list[dict],
    chargers: list[dict],
    census_to_lgd: dict,
    polygons: list[dict],
    p: dict,
) -> list[dict]:
    codes = set(unit["codes"])

    def in_unit(features: list[dict]) -> list[dict]:
        pts = [tuple(f["geometry"]["coordinates"]) for f in features]
        assigned = bdt.assign_points(pts, polygons)
        return [f for f, c in zip(features, assigned) if census_to_lgd.get(c or "") in codes]

    places = in_unit(
        [s for s in settlements if s["properties"].get("place") in p["urban_proxy"]["place_values"]]
    )
    blocking = [c for c in chargers if c["e4w"] != "confirmed_not"]
    psu = set(p["psu_omc_brands"]["value"])
    radius = p["duplication_radius_km"]["value"]
    urban_km = p["urban_proxy"]["radius_km"]
    out = []
    for f in in_unit(fuel):
        lon, lat = f["geometry"]["coordinates"]
        props = f["properties"]
        near_place = min(
            (
                (km(lat, lon, s["geometry"]["coordinates"][1], s["geometry"]["coordinates"][0]), s)
                for s in places
            ),
            key=lambda t: (t[0], t[1]["properties"]["@id"]),
            default=(math.inf, None),
        )
        nearest = min(
            ((km(lat, lon, c["lat"], c["lon"]), c) for c in blocking),
            key=lambda t: (t[0], t[1]["id"]),
        )
        brand = brand_of(props)
        if near_place[0] > urban_km:
            status = "rejected: outside urban proxy"
        elif nearest[0] <= radius:
            status = "rejected: e-4W confirmed/unknown charger within duplication radius"
        else:
            status = "eligible"
        place = near_place[1]["properties"] if near_place[1] else {}
        out.append(
            {
                "osm_id": props["@id"],
                "name": props.get("name", ""),
                "brand_or_operator": brand,
                "latitude": f"{lat:.6f}",
                "longitude": f"{lon:.6f}",
                "nearest_place": place.get("name", ""),
                "nearest_place_osm_id": place.get("@id", ""),
                "nearest_place_type": place.get("place", ""),
                "nearest_place_km": f"{near_place[0]:.2f}" if place else "",
                "nearest_e4w_charger_id": nearest[1]["id"],
                "nearest_e4w_charger_state": nearest[1]["e4w"],
                "nearest_e4w_charger_km": f"{nearest[0]:.3f}",
                "subsidy_category_modelled": "B" if brand.lower() in psu else "C",
                "status": status,
                "selection_order": "",
            }
        )
    out.sort(key=lambda r: (-float(r["nearest_e4w_charger_km"]), r["osm_id"]))
    return out


def cost_split(category: str, p: dict) -> dict[str, float]:
    cfg, share = p["configuration"], p["subsidy_categories"][category]
    up = cfg["upstream_benchmark_inr_lakh"] * cfg["count"]
    eq = cfg["evse_benchmark_inr_lakh"] * cfg["count"]
    subsidy = share["upstream_share"] * up + share["evse_share"] * eq
    other = p["other_public_funding_inr_lakh"]["value"]
    public = subsidy + other
    return {
        "total": round(up + eq, 4),
        "subsidy": round(subsidy, 4),
        "other_public": round(other, 4),
        "public": round(public, 4),
        "operator": round(up + eq - public, 4),
    }


def select(cands: list[dict], p: dict) -> list[dict]:
    """Greedy in objective order; skip sites that break spacing or exceed the budget."""
    budget = p["public_budget_inr_lakh"]["value"]
    spacing = p["selection"]["min_spacing_between_selected_km"]
    per_place = p["selection"]["max_sites_per_settlement"]
    chosen: list[dict] = []
    spent = 0.0
    for c in cands:
        if c["status"] != "eligible":
            continue
        cost = cost_split(c["subsidy_category_modelled"], p)["public"]
        lat, lon = float(c["latitude"]), float(c["longitude"])
        if any(km(lat, lon, float(s["latitude"]), float(s["longitude"])) < spacing for s in chosen):
            c["status"] = "eligible: not selected (spacing to a selected site)"
            continue
        if sum(s["nearest_place_osm_id"] == c["nearest_place_osm_id"] for s in chosen) >= per_place:
            c["status"] = "eligible: not selected (settlement already has a selected site)"
            continue
        if spent + cost > budget + 1e-9:
            c["status"] = "eligible: not selected (budget)"
            continue
        spent += cost
        c["status"] = "selected"
        c["selection_order"] = str(len(chosen) + 1)
        chosen.append(c)
    return chosen


def nearby(site: dict, chargers: list[dict], radius: float) -> dict:
    lat, lon = float(site["latitude"]), float(site["longitude"])
    near = [c for c in chargers if km(lat, lon, c["lat"], c["lon"]) <= radius]
    counts = Counter((c["lineage"], c["e4w"]) for c in near)
    return {
        "bee_rows_e4w_confirmed": counts[("BEE", "confirmed")],
        "bee_rows_e4w_unknown": counts[("BEE", "unknown")],
        "bee_rows_e4w_confirmed_not": counts[("BEE", "confirmed_not")],
        "osm_records": sum(v for (lin, _), v in counts.items() if lin == "OSM"),
        "bee_listed_kw_e4w_confirmed": round(
            sum(c["kw"] for c in near if c["lineage"] == "BEE" and c["e4w"] == "confirmed"), 1
        ),
    }


PROPOSAL_COLUMNS = [
    "site_id",
    "osm_id",
    "name",
    "latitude",
    "longitude",
    "tier_label",
    "vehicle_type",
    "configuration",
    "unit",
    "served_bev_registrations_in_unit",
    "nearest_place",
    "nearest_e4w_charger_km",
    "listed_e4w_chargers_within_radius",
    "capacity_kwh_day_low_central_high",
    "subsidy_category_modelled",
    "total_cost_inr_lakh",
    "pm_edrive_subsidy_modelled_inr_lakh",
    "other_public_inr_lakh",
    "public_cost_inr_lakh",
    "operator_share_inr_lakh",
    "reason",
    "evidence",
]


def proposal_rows(chosen, unit_row, chargers, p) -> list[dict]:
    cfg = p["configuration"]
    radius = p["nearby_radius_km"]["value"]
    out = []
    for c in chosen:
        cost = cost_split(c["subsidy_category_modelled"], p)
        nb = nearby(c, chargers, radius)
        out.append(
            {
                "site_id": f"KA-SLICE-{int(c['selection_order']):02d}",
                "osm_id": c["osm_id"],
                "name": c["name"],
                "latitude": c["latitude"],
                "longitude": c["longitude"],
                "tier_label": TIER,
                "vehicle_type": p["served_vehicle_type"]["value"],
                "configuration": f"{cfg['count']} x {cfg['connector']} {cfg['rated_kw']} kW",
                "unit": unit_row["unit_name"],
                "served_bev_registrations_in_unit": unit_row["served_bev_registrations"],
                "nearest_place": f"{c['nearest_place']} ({c['nearest_place_km']} km)",
                "nearest_e4w_charger_km": c["nearest_e4w_charger_km"],
                "listed_e4w_chargers_within_radius": (
                    f"{radius:g} km: BEE {nb['bee_rows_e4w_confirmed']} confirmed, "
                    f"{nb['bee_rows_e4w_unknown']} unknown; OSM {nb['osm_records']}"
                ),
                "capacity_kwh_day_low_central_high": "not computed (Part I parameters open)",
                "subsidy_category_modelled": c["subsidy_category_modelled"],
                "total_cost_inr_lakh": f"{cost['total']:.2f}",
                "pm_edrive_subsidy_modelled_inr_lakh": f"{cost['subsidy']:.3f}",
                "other_public_inr_lakh": f"{cost['other_public']:.2f}",
                "public_cost_inr_lakh": f"{cost['public']:.3f}",
                "operator_share_inr_lakh": f"{cost['operator']:.3f}",
                "reason": (
                    f"Rank {c['selection_order']} by coverage gap: nearest e-4W confirmed or "
                    f"unknown charger {c['nearest_e4w_charger_km']} km away; within "
                    f"{c['nearest_place_km']} km of {c['nearest_place']}"
                ),
                "evidence": "S35; S30/S31; S18/S19 (BEE, data till 26 Oct 2025); S11; S23; "
                "S33 cl. 11(1)(a); S34 s.6 Table 2, s.7 Tables 3-4",
            }
        )
    return out


def fusion_example(unit: dict, s18: list[dict], s19: list[dict], s11: list[dict]) -> dict | None:
    """First BEE site with an OSM record within 100 m (proximity only): in the unit if
    there is one, otherwise statewide (stated in the output)."""
    codes = set(unit["codes"])
    osm = {r["inventory_id"]: r for r in s11}
    matched = sorted(
        (s for s in s19 if s["osm_match_within_100m"] == "yes"),
        key=lambda r: (r["lgd_district_code_by_point"] not in codes, r["site_id"]),
    )
    for s in matched:
        o = osm[s["nearest_osm_inventory_id"]]
        rows = [r for r in s18 if r["site_id"] == s["site_id"]]
        return {
            "scope": "unit" if s["lgd_district_code_by_point"] in codes else "statewide",
            "bee_site": s["site_id"],
            "bee_site_lgd": s["lgd_district_code_by_point"],
            "bee_rows": [
                f"{r['source_row_id']} {r['cpo_name']} {r['charger_type']} {r['charger_rating']} kW"
                for r in rows
            ],
            "osm_record": o["inventory_id"],
            "osm_lineage": o["lineage_group"],
            "osm_name_operator": f"{o['name'] or '(no name)'} / {o['operator'] or '(none)'}",
            "distance_m": s["nearest_osm_distance_m"],
            "sites_matched_in_unit": sum(
                1
                for t in s19
                if t["lgd_district_code_by_point"] in codes and t["osm_match_within_100m"] == "yes"
            ),
            "sites_in_unit": sum(1 for t in s19 if t["lgd_district_code_by_point"] in codes),
            "sites_matched_statewide": len(matched),
        }
    return None


# ---------------------------------------------------------------- map


def svg_map(unit, polygons, census_codes, chargers, cands, chosen) -> str:
    polys = [p for p in polygons if p["census_code"] in census_codes]
    x0 = min(p["bbox"][0] for p in polys)
    y0 = min(p["bbox"][1] for p in polys)
    x1 = max(p["bbox"][2] for p in polys)
    y1 = max(p["bbox"][3] for p in polys)
    kx = math.cos(math.radians((y0 + y1) / 2))
    width = 760.0
    scale = width / ((x1 - x0) * kx)
    height = (y1 - y0) * scale
    pad, legend = 20, 120

    def pt(lon: float, lat: float) -> tuple[float, float]:
        return pad + (lon - x0) * kx * scale, pad + (y1 - lat) * scale

    def xy(lon: float, lat: float) -> str:
        x, y = pt(lon, lat)
        return f"{x:.1f},{y:.1f}"

    def inside(lon: float, lat: float) -> bool:
        return x0 <= lon <= x1 and y0 <= lat <= y1

    w, h = width + 2 * pad, height + 2 * pad + legend
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
            f'viewBox="0 0 {w:.0f} {h:.0f}" font-family="sans-serif" font-size="12">'
        ),
        f'<rect width="{w:.0f}" height="{h:.0f}" fill="#ffffff"/>',
    ]
    for p in polys:
        for ring in p["rings"]:
            pts = " ".join(xy(x, y) for x, y in ring)
            parts.append(f'<polygon points="{pts}" fill="#f2f2ee" stroke="#777" stroke-width="1"/>')
    style = {
        "confirmed_not": ("#9db7d5", 2.0),
        "unknown": ("#e0a040", 2.5),
        "confirmed": ("#2a7a3a", 3.0),
    }
    for state in ("confirmed_not", "unknown", "confirmed"):
        colour, r = style[state]
        for c in chargers:
            if c["e4w"] == state and inside(c["lon"], c["lat"]):
                x, y = pt(c["lon"], c["lat"])
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{colour}"/>')
    for c in cands:
        if c["status"] != "selected":
            fill = "#ffffff" if c["status"].startswith("rejected") else "#bbbbbb"
            x, y = pt(float(c["longitude"]), float(c["latitude"]))
            parts.append(
                f'<rect x="{x - 3:.1f}" y="{y - 3:.1f}" width="6" height="6" '
                f'fill="{fill}" stroke="#555" stroke-width="0.8"/>'
            )
    for c in chosen:
        x, y = pt(float(c["longitude"]), float(c["latitude"]))
        parts.append(
            f'<polygon points="{x:.1f},{y - 9:.1f} {x + 8:.1f},{y + 6:.1f} {x - 8:.1f},{y + 6:.1f}" '
            f'fill="#c0392b" stroke="#000" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x + 10:.1f}" y="{y + 4:.1f}" font-weight="bold">'
            f"S{c['selection_order']}</text>"
        )
    ly = height + 2 * pad + 8
    items = [
        ("circle", "#2a7a3a", "Listed charger, e-4W confirmed (BEE row or OSM)"),
        ("circle", "#e0a040", "Listed charger, e-4W unknown"),
        ("circle", "#9db7d5", "Listed charger, e-4W confirmed not (LEV)"),
        ("rect", "#bbbbbb", "Fuel station: eligible, not selected"),
        ("rect", "#ffffff", "Fuel station: rejected (urban proxy or 1 km rule)"),
        ("tri", "#c0392b", "Model-selected candidate (not field-verified)"),
    ]
    for i, (shape, colour, label) in enumerate(items):
        x, y = pad + (i % 2) * 380, ly + (i // 2) * 20
        if shape == "circle":
            parts.append(f'<circle cx="{x + 6}" cy="{y + 6}" r="4" fill="{colour}"/>')
        elif shape == "rect":
            parts.append(
                f'<rect x="{x + 2}" y="{y + 2}" width="8" height="8" fill="{colour}" '
                'stroke="#555" stroke-width="0.8"/>'
            )
        else:
            parts.append(
                f'<polygon points="{x + 6},{y} {x + 12},{y + 11} {x},{y + 11}" '
                f'fill="{colour}" stroke="#000" stroke-width="1"/>'
            )
        parts.append(f'<text x="{x + 18}" y="{y + 10}">{label}</text>')
    parts.append(
        f'<text x="{pad}" y="{ly + 74}" font-size="11" fill="#444">{unit["name"]} district '
        "unit (Census 2011 boundary, DataMeet). Data: BEE list (S15/S18), "
        "© OpenStreetMap contributors (S11, S23).</text>"
    )
    parts.append(
        f'<text x="{pad}" y="{ly + 90}" font-size="11" fill="#444">Illustrative planning slice; '
        "not a sanctioned or field-verified plan. No charger has an operating status.</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- report


def site_card(
    summary: dict,
    unit_row: dict,
    rto_rows: list[dict],
    prop: list[dict],
    fusion: dict | None,
    p: dict,
) -> str:
    top = prop[0]
    lines = [
        "# Planning slice site card (generated)",
        "",
        (
            "Generated by `src/evinfra/scoring/build_karnataka_planning_slice.py`. Do not edit by "
            "hand. Illustrative example of one budget-constrained run; not a recommendation to fund."
        ),
        "",
        f"## Proposed site {top['site_id']}",
        "",
        "| Field | Value |",
        "| --- | --- |",
    ]
    for key in PROPOSAL_COLUMNS:
        lines.append(f"| {key} | {top[key]} |")
    lines += [
        "",
        (
            f"All {len(prop)} selected sites are in `proposal.csv`; every one is a "
            f'"{TIER}" ({TIER_NOTE}).'
        ),
        "",
        "## Unit screen",
        "",
        (
            f"{unit_row['unit_name']} ranks 1 of {summary['units_screen_eligible']} eligible district "
            f"units: {unit_row['served_bev_registrations']} e-4W battery-EV registrations in "
            f"{p['reference_year']['value']} per {unit_row['bee_sites_e4w_listed']} BEE sites with an "
            f"e-4W confirmed or unknown row = {unit_row['served_bev_per_listed_site']}. "
            f"{ep.CAVEAT_OFFICE} This is a screening indicator, not a gap estimate."
        ),
        "",
        "## RTOs in the unit (observed registrations, registering office)",
        "",
        "| RTO | Office | Crosswalk status | e-4W BEV | All BEV |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rto_rows:
        lines.append(
            f"| {r['rto_code']} | {r['rto_name']} | {r['crosswalk_status']} | "
            f"{r['served_bev_registrations']} | {r['all_bev_registrations']} |"
        )
    lines += ["", "## Charger evidence fusion example (L-004)", ""]
    if fusion:
        lines += [
            f"- In this unit {fusion['sites_matched_in_unit']} of {fusion['sites_in_unit']} BEE "
            "sites have an OSM record within 100 m; statewide "
            f"{fusion['sites_matched_statewide']}. "
            + (
                "Example from this unit:"
                if fusion["scope"] == "unit"
                else f"Example from outside the unit (LGD {fusion['bee_site_lgd']}):"
            ),
            f"- BEE site {fusion['bee_site']} (lineage BEE): " + "; ".join(fusion["bee_rows"]),
            (
                f"- OSM record {fusion['osm_record']} (lineage {fusion['osm_lineage']}; "
                f"name/operator {fusion['osm_name_operator']}), {fusion['distance_m']} m away."
            ),
            (
                "- Two lineage groups by proximity (within 100 m). This is a proximity match, not a "
                "confirmed merge: the name/operator check (H-014) and the merged table (H-018) are "
                "not built."
            ),
        ]
    else:
        lines.append("- No BEE site has an OSM record within 100 m.")
    lines += [
        "",
        "## Missing fields and the fallback used (L-010)",
        "",
        "| Missing | Fallback in this slice |",
        "| --- | --- |",
        (
            "| Where vehicles are located inside the unit | None: spatial choice uses coverage gap "
            "only; registrations shown as unit totals |"
        ),
        (
            '| Charger operating status | All listed chargers treated as present; "unknown" '
            "compatibility blocks a candidate (conservative against duplication) |"
        ),
        (
            "| Capacity parameters (derating, hours, confidence scores) | Capacity not computed; "
            "listed chargers and rated kW reported instead |"
        ),
        (
            "| State-notified urban areas (S33 11(1)(a)) | OSM city/town nodes within "
            f"{p['urban_proxy']['radius_km']:g} km |"
        ),
        (
            "| Outlet ownership and nodal-agency eligibility (S34 s.2) | Category from OSM brand; "
            "eligible subsidy is modelled, not sanctioned |"
        ),
        "| Site-specific cost quote | BEE benchmark cost (S34 s.7); no range |",
        "| Land, parking, grid connection | Not checked; tier stays model-selected |",
        "| Verified Karnataka site-level plan | None; plan overlap not evaluated |",
        "| CEA DISCOM energy data | Not acquired; no consistency chart (L-008) |",
        "",
        "## Inputs",
        "",
        "See `inputs.csv` (register ID, row count, register date, SHA-256) and `summary.json`.",
        "",
    ]
    return "\n".join(lines)


def build(params_path: Path = PARAMS) -> tuple[dict[str, bytes], dict]:
    with open(params_path, encoding="utf-8") as f:
        p = json.load(f)
    register = bdt.read_csv(ep.REGISTER)
    inputs = check_inputs(register)
    s18 = bdt.read_csv(PROC / "S18_karnataka_bee_pcs_rows.csv")
    s19 = bdt.read_csv(PROC / "S19_karnataka_bee_pcs_sites.csv")
    s11 = bdt.read_csv(PROC / "S11_karnataka_charger_inventory.csv")
    s12 = bdt.read_csv(PROC / "S12_karnataka_district_charger_join.csv")
    s35 = bdt.read_csv(PROC / "S35_ka_bev_rto_class_month.csv")
    crosswalk = bdt.read_csv(ep.CROSSWALK)
    spine = [r for r in bdt.read_csv(RAW / bdt.S06.name) if r["state_code"] == bdt.STATE_CODE]
    census_to_lgd = {
        r["census_2011_district_code"]: r["district_code"]
        for r in spine
        if r["census_2011_district_code"] not in ("", "0", "None")
    }
    polygons = bdt.read_boundaries(BOUNDARIES, bdt.STATE_CODE)

    chargers = charger_points(s18, s11, p["bee_e4w_compatibility"])
    unit_map = units(crosswalk, s12)
    served, total = served_by_rto(
        s35, p["reference_year"]["value"], p["served_vehicle_type"]["vahan_classes"]
    )
    screen = screen_units(unit_map, served, total, chargers, p)
    unit_row = screen[0]
    if unit_row["screen_eligible"] != "yes":
        raise SliceError("No district unit passes the screen")
    unit = unit_map[unit_row["unit_lgd_codes"]]

    xw = {r["rto_code_vahan"]: r for r in crosswalk}
    rto_rows = [
        {
            "rto_code": r,
            "rto_name": xw[r]["rto_name_vahan"],
            "unit_lgd_codes": unit_row["unit_lgd_codes"],
            "unit_name": unit["name"],
            "crosswalk_status": xw[r]["status"],
            **{
                f"bev_{c}": str(served.get(r, Counter())[c])
                for c in p["served_vehicle_type"]["vahan_classes"]
            },
            "served_bev_registrations": str(sum(served.get(r, Counter()).values())),
            "all_bev_registrations": str(total[r]),
        }
        for r in unit["rtos"]
    ]
    fuel = load_geojson(PROC / "S23_osm_ka_fuel.geojson")
    settlements = load_geojson(PROC / "S23_osm_ka_settlements.geojson")
    cands = candidates(unit, fuel, settlements, chargers, census_to_lgd, polygons, p)
    chosen = select(cands, p)
    if not chosen:
        raise SliceError("No candidate selected")
    prop = proposal_rows(chosen, unit_row, chargers, p)
    fusion = fusion_example(unit, s18, s19, s11)
    census_codes = {c for c, lgd in census_to_lgd.items() if lgd in set(unit["codes"])}

    summary = {
        "parameters_sha256": sha256(params_path),
        "reference_year": p["reference_year"]["value"],
        "served_vehicle_type": p["served_vehicle_type"]["value"],
        "units_screened": len(screen),
        "units_screen_eligible": sum(r["screen_eligible"] == "yes" for r in screen),
        "slice_unit": unit_row["unit_name"],
        "slice_unit_rtos": unit["rtos"],
        "candidates_in_unit": len(cands),
        "candidates_by_status": dict(sorted(Counter(c["status"] for c in cands).items())),
        "selected_sites": len(chosen),
        "public_budget_inr_lakh": p["public_budget_inr_lakh"]["value"],
        "public_cost_selected_inr_lakh": round(
            sum(float(r["public_cost_inr_lakh"]) for r in prop), 3
        ),
        "located_charger_records": {
            "bee_rows": sum(c["lineage"] == "BEE" for c in chargers),
            "osm_records": sum(c["lineage"] == "OSM" for c in chargers),
        },
        "stage_status": {
            "1_charger_evidence": "partial: BEE rows and OSM records with e-4W state and "
            "proximity matches; no merged table or confidence scores",
            "2_demand_by_class_rto": "demonstrated: observed BEV registrations by RTO, class "
            "and month (S35), registering office",
            "3_cea_calibration": "method only: CEA data not acquired",
            "4_site_selection": "one example run demonstrated (one unit, e-4W, greedy, "
            "illustrative budget); equity mode and optimiser method only",
            "5_proposal_export": "one site card demonstrated; capacity range not computed",
            "6_validation": "method only",
        },
        "inputs": inputs,
    }
    outputs = {
        "inputs.csv": bdt.to_csv_bytes(list(inputs[0]), inputs),
        "unit_screen.csv": bdt.to_csv_bytes(list(screen[0]), screen),
        "rto_served_bev.csv": bdt.to_csv_bytes(list(rto_rows[0]), rto_rows),
        "candidates.csv": bdt.to_csv_bytes(list(cands[0]), cands),
        "proposal.csv": bdt.to_csv_bytes(PROPOSAL_COLUMNS, prop),
        "site_card.md": site_card(summary, unit_row, rto_rows, prop, fusion, p).encode("utf-8"),
        "map.svg": svg_map(unit, polygons, census_codes, chargers, cands, chosen).encode("utf-8"),
    }
    summary["outputs_sha256"] = {k: hashlib.sha256(v).hexdigest() for k, v in outputs.items()}
    outputs["summary.json"] = (json.dumps(summary, indent=2) + "\n").encode("utf-8")
    return outputs, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="replace outputs that differ")
    parser.add_argument(
        "--update-docs", action="store_true", help="write the tracked copies in docs/submission"
    )
    args = parser.parse_args(argv)
    outputs, summary = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    status = {k: bdt.write_if_unchanged(OUT_DIR / k, v, args.force) for k, v in outputs.items()}
    for name in DOCS_FILES:
        path = DOCS_DIR / name
        if args.update_docs:
            DOCS_DIR.mkdir(parents=True, exist_ok=True)
            path.write_bytes(outputs[name])
            status[f"docs/{name}"] = "written"
        else:
            # Newline-insensitive: git may check the tracked copy out with CRLF.
            same = path.exists() and path.read_bytes().replace(b"\r\n", b"\n") == outputs[name]
            status[f"docs/{name}"] = "same" if same else "differs"
    report = {k: v for k, v in summary.items() if k != "inputs"}
    json.dump({**report, "write_status": status}, sys.stdout, indent=2)
    print()
    return 1 if "differs" in status.values() else 0


if __name__ == "__main__":
    raise SystemExit(main())
