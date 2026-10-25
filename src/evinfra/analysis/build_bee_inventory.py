"""Build S18 (Karnataka BEE charger rows) and S19 (candidate physical sites + OSM overlap).

Inputs (read-only):
    S16  data/interim/S16_bee_pcs_rows_all_states.csv (staging extraction of the S15 BEE PDF)
    S06  LGD district codes (stated district name -> LGD code; 2011 code -> LGD code)
    S11  data/processed/S11_karnataka_charger_inventory.csv (OSM baseline)
    Census 2011 district boundaries (datameet shapefile, point-in-polygon checks)

Units. One S15 row is one charger entry (charger type, ratings and a connector count)
at a location. Rows are never merged. Derived keys:
    station_key  identical (CPO name, location text, latitude, longitude): one possible
                 grouping of rows into "stations" (the source does not define the unit);
    site_id      identical (latitude, longitude) among rows with valid coordinates: a
                 candidate physical site, which may hold several CPOs' stations;
    site_cluster_25m  single-linkage groups of sites within 25 m: a lower-bound view of
                 physical places (one complex can carry many charge points).
Exact duplicate rows (all 12 source fields equal) and nearby sites (distinct
coordinates within 25 m) are flagged and counted, never removed or merged.

Validation. Karnataka rows are selected on the explicit State field only. Coordinates
are kept as printed; a row has valid coordinates only if both parse as numbers, latitude
differs from longitude, and the point lies inside a Karnataka Census 2011 district
polygon. Invalid points are flagged with a reason and kept. Districts come from the
stated District field (mapped to LGD with an explicit alias table) and, separately,
from the point's polygon; disagreements are flagged, not corrected.

Not in the source and therefore always missing: operating status, opening hours,
public-access confirmation. Charger and connector ratings are copied as printed; the
source does not state their unit.

Uses only the standard library. Run from the repository root:
    python src/evinfra/analysis/build_bee_inventory.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from evinfra.analysis import build_charger_inventory as bci
from evinfra.analysis import build_district_table as bdt

ROOT = bdt.ROOT
RAW = bdt.RAW
S16 = ROOT / "data" / "interim" / "S16_bee_pcs_rows_all_states.csv"
S11 = bci.OUT_INVENTORY
OUT_DIR = bdt.OUT_DIR
OUT_ROWS = OUT_DIR / "S18_karnataka_bee_pcs_rows.csv"
OUT_SITES = OUT_DIR / "S19_karnataka_bee_pcs_sites.csv"
OUT_SUMMARY = OUT_DIR / "S18_S19_summary.json"
OUT_DICT = OUT_DIR / "S18_S19_dictionary.csv"

STATE_NAME = "karnataka"
NEARBY_SITE_M = 25.0
OSM_MATCH_M = 100.0
SOURCE_FIELDS = [
    "cpo_name",
    "govt_private",
    "state",
    "district",
    "city_village",
    "location",
    "latitude",
    "longitude",
    "charger_type",
    "charger_rating",
    "connector_rating",
    "no_of_connector",
]
# Stated district names in S15 that differ from S06 LGD names (case-insensitive).
DISTRICT_ALIASES = {
    "bengaluru south": "631",  # Ramanagara in S06; renamed Bengaluru South (S07 uses it)
    "chamarajanagar": "531",  # S06: Chamarajanagara
    "davanagere": "535",  # S06: Davangere
    "vijayanagara": "738",  # S06: Vijayanagar
}

ROW_COLUMNS = [
    "source_row_id",
    "page",
    "row_on_page",
    *SOURCE_FIELDS,
    "coordinate_status",
    "census_2011_district_code_by_point",
    "lgd_district_code_by_point",
    "lgd_district_code_stated",
    "lgd_district_name_stated",
    "district_check",
    "exact_duplicate_group_size",
    "station_key",
    "site_id",
    "charger_rating_value",
    "connector_count",
    "operational_status",
]
SITE_COLUMNS = [
    "site_id",
    "latitude",
    "longitude",
    "source_rows",
    "connectors",
    "station_keys",
    "cpo_names",
    "lgd_district_code_stated",
    "lgd_district_code_by_point",
    "max_charger_rating_value",
    "nearby_sites_within_25m",
    "site_cluster_25m",
    "nearest_osm_inventory_id",
    "nearest_osm_distance_m",
    "osm_match_within_100m",
]


class BeeInventoryError(ValueError):
    """Raised when inputs are malformed or fail a consistency check."""


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def build(s16: Path = S16, raw: Path = RAW, s11: Path = S11) -> tuple[list[dict], list[dict], dict]:
    staging = bdt.read_csv(s16)
    missing = [c for c in ["source_row_id", *SOURCE_FIELDS] if staging and c not in staging[0]]
    if missing:
        raise BeeInventoryError(f"S16 is missing columns: {missing}")
    ids = [r["source_row_id"] for r in staging]
    if len(ids) != len(set(ids)):
        raise BeeInventoryError("Duplicate source_row_id in S16")

    rows = [dict(r) for r in staging if r["state"].strip().lower() == STATE_NAME]
    summary: dict = {
        "raw_rows_all_states": len(staging),
        "karnataka_rows": len(rows),
        "rows_mentioning_karnataka_in_location_but_other_state": sum(
            1
            for r in staging
            if r["state"].strip().lower() != STATE_NAME and "karnataka" in r["location"].lower()
        ),
    }
    if not rows:
        raise BeeInventoryError("No Karnataka rows in S16")

    spine = [r for r in bdt.read_csv(raw / bdt.S06.name) if r["state_code"] == bdt.STATE_CODE]
    lgd_by_name = {r["district_name"].strip().lower(): r for r in spine}
    lgd_by_code = {r["district_code"]: r for r in spine}
    census_to_lgd = {
        r["census_2011_district_code"]: r["district_code"]
        for r in spine
        if r["census_2011_district_code"] not in ("", "0", "None")
    }
    for name, code in DISTRICT_ALIASES.items():
        if code not in lgd_by_code:
            raise BeeInventoryError(f"Alias {name!r} points to unknown LGD code {code}")

    # Coordinates: parse, then point-in-polygon once per distinct coordinate pair.
    polygons = bdt.read_boundaries(
        raw / "district_boundaries" / bdt.BOUNDARIES.name, bdt.STATE_CODE
    )
    parsed = {}
    for r in rows:
        lat, lon = parse_float(r["latitude"]), parse_float(r["longitude"])
        if lat is None or lon is None:
            status = "not_numeric"
        elif lat == lon:
            status = "latitude_equals_longitude"
        else:
            status = "check_polygon"
        parsed[r["source_row_id"]] = (lat, lon, status)
    candidates = sorted(
        {
            (r["latitude"], r["longitude"])
            for r in rows
            if parsed[r["source_row_id"]][2] == "check_polygon"
        }
    )
    assigned = bdt.assign_points([(float(lon), float(lat)) for lat, lon in candidates], polygons)
    polygon_of = dict(zip(candidates, assigned))

    exact = Counter(tuple(r[f] for f in SOURCE_FIELDS) for r in rows)
    station_keys: dict[tuple, str] = {}
    site_ids: dict[tuple, str] = {}
    for r in sorted(rows, key=lambda x: x["source_row_id"]):
        lat, lon, status = parsed[r["source_row_id"]]
        c2011 = ""
        if status == "check_polygon":
            c2011 = polygon_of[(r["latitude"], r["longitude"])] or ""
            status = "valid" if c2011 else "outside_karnataka_polygons"
        r["coordinate_status"] = status
        r["census_2011_district_code_by_point"] = c2011
        r["lgd_district_code_by_point"] = census_to_lgd.get(c2011, "")

        stated = r["district"].strip().lower()
        code = DISTRICT_ALIASES.get(stated) or (
            lgd_by_name[stated]["district_code"] if stated in lgd_by_name else ""
        )
        r["lgd_district_code_stated"] = code
        r["lgd_district_name_stated"] = lgd_by_code[code]["district_name"] if code else ""
        if not code:
            r["district_check"] = "stated_district_unmatched"
        elif not r["lgd_district_code_by_point"]:
            r["district_check"] = "not_assessable"
        elif code == r["lgd_district_code_by_point"]:
            r["district_check"] = "agree"
        elif code == "738" and r["lgd_district_code_by_point"] == bdt.BALLARI_LGD:
            r["district_check"] = "agree_pre_split"  # 2011 Ballari polygon includes Vijayanagar
        else:
            r["district_check"] = "disagree"

        r["exact_duplicate_group_size"] = str(exact[tuple(r[f] for f in SOURCE_FIELDS)])
        skey = (r["cpo_name"], r["location"], r["latitude"], r["longitude"])
        station_keys.setdefault(skey, f"KA-BEE-ST{len(station_keys) + 1:05d}")
        r["station_key"] = station_keys[skey]
        if status == "valid":
            site = (r["latitude"], r["longitude"])
            site_ids.setdefault(site, f"KA-BEE-S{len(site_ids) + 1:05d}")
            r["site_id"] = site_ids[site]
        else:
            r["site_id"] = ""
        rating = parse_float(r["charger_rating"])
        r["charger_rating_value"] = "" if rating is None else r["charger_rating"]
        r["connector_count"] = r["no_of_connector"] if r["no_of_connector"].isdigit() else ""
        r["operational_status"] = ""
    rows.sort(key=lambda x: x["source_row_id"])

    # Sites.
    by_site: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if r["site_id"]:
            by_site[r["site_id"]].append(r)
    osm = bdt.read_csv(s11)
    osm_points = [(o["inventory_id"], float(o["latitude"]), float(o["longitude"])) for o in osm]
    sites = []
    for sid in sorted(by_site):
        group = by_site[sid]
        lat, lon = float(group[0]["latitude"]), float(group[0]["longitude"])
        stated = sorted({g["lgd_district_code_stated"] for g in group})
        ratings = [float(g["charger_rating_value"]) for g in group if g["charger_rating_value"]]
        nearest = min(
            ((bci.distance_m(lat, lon, olat, olon), oid) for oid, olat, olon in osm_points),
            default=None,
        )
        sites.append(
            {
                "site_id": sid,
                "latitude": group[0]["latitude"],
                "longitude": group[0]["longitude"],
                "source_rows": str(len(group)),
                "connectors": str(sum(int(g["connector_count"] or 0) for g in group)),
                "station_keys": str(len({g["station_key"] for g in group})),
                "cpo_names": ";".join(sorted({g["cpo_name"] for g in group})),
                "lgd_district_code_stated": ";".join(stated),
                "lgd_district_code_by_point": group[0]["lgd_district_code_by_point"],
                "max_charger_rating_value": f"{max(ratings):g}" if ratings else "",
                "nearby_sites_within_25m": "0",
                "nearest_osm_inventory_id": nearest[1] if nearest else "",
                "nearest_osm_distance_m": f"{nearest[0]:.1f}" if nearest else "",
                "osm_match_within_100m": "yes" if nearest and nearest[0] <= OSM_MATCH_M else "no",
                "_lat": lat,
                "_lon": lon,
            }
        )
    # Nearby distinct sites: sort by latitude and only compare within the radius band.
    order = sorted(sites, key=lambda s: s["_lat"])
    band = NEARBY_SITE_M / 111_000 * 1.01
    parent = {s["site_id"]: s["site_id"] for s in sites}

    def root(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    nearby_pairs = 0
    for i, a in enumerate(order):
        for b in order[i + 1 :]:
            if b["_lat"] - a["_lat"] > band:
                break
            if bci.distance_m(a["_lat"], a["_lon"], b["_lat"], b["_lon"]) <= NEARBY_SITE_M:
                nearby_pairs += 1
                for s in (a, b):
                    s["nearby_sites_within_25m"] = str(int(s["nearby_sites_within_25m"]) + 1)
                ra, rb = sorted((root(a["site_id"]), root(b["site_id"])))
                parent[rb] = ra
    for s in sites:
        # Single-linkage cluster at 25 m, named after its lowest site_id (deterministic).
        s["site_cluster_25m"] = root(s["site_id"]).replace("KA-BEE-S", "KA-BEE-C")
        del s["_lat"], s["_lon"]

    # OSM side of the comparison: each OSM record against the nearest BEE site.
    site_points = [(float(s["latitude"]), float(s["longitude"])) for s in sites]
    osm_matched = sum(
        1
        for _, olat, olon in osm_points
        if any(bci.distance_m(olat, olon, la, lo) <= OSM_MATCH_M for la, lo in site_points)
    )

    status_counts = Counter(r["coordinate_status"] for r in rows)
    summary.update(
        {
            "karnataka_connectors": sum(int(r["connector_count"] or 0) for r in rows),
            "coordinate_status": dict(sorted(status_counts.items())),
            "rows_with_valid_coordinates": status_counts["valid"],
            "station_keys": len(station_keys),
            "candidate_physical_sites": len(sites),
            "exact_duplicate_groups": sum(1 for c in exact.values() if c > 1),
            "rows_in_exact_duplicate_groups": sum(c for c in exact.values() if c > 1),
            "exact_duplicate_surplus_rows": sum(c - 1 for c in exact.values() if c > 1),
            "nearby_site_pairs_within_25m": nearby_pairs,
            "site_clusters_25m": len({s["site_cluster_25m"] for s in sites}),
            "rows_with_known_operating_status": 0,
            "rows_confirmed_operational": 0,
            "rows_with_numeric_charger_rating": sum(1 for r in rows if r["charger_rating_value"]),
            "rows_with_stated_district_matched_to_lgd": sum(
                1 for r in rows if r["lgd_district_code_stated"]
            ),
            "rows_with_point_district": sum(1 for r in rows if r["lgd_district_code_by_point"]),
            "district_check": dict(sorted(Counter(r["district_check"] for r in rows).items())),
            "govt_private": dict(sorted(Counter(r["govt_private"] for r in rows).items())),
            "osm_records": len(osm_points),
            "osm_records_with_bee_site_within_100m": osm_matched,
            "osm_records_without_bee_site_within_100m": len(osm_points) - osm_matched,
            "bee_sites_with_osm_record_within_100m": sum(
                1 for s in sites if s["osm_match_within_100m"] == "yes"
            ),
        }
    )
    if sum(int(s["source_rows"]) for s in sites) != status_counts["valid"]:
        raise BeeInventoryError("Site row counts do not sum to rows with valid coordinates")
    return rows, sites, summary


def dictionary_rows() -> list[dict[str, str]]:
    d = {
        "source_row_id": "S15-p<page>-r<row>: page and row of the table row in the S15 PDF",
        "page": "S15 PDF page",
        "row_on_page": "Table row on that page (header row counted)",
        "coordinate_status": "valid / not_numeric / latitude_equals_longitude / "
        "outside_karnataka_polygons. Coordinates are never corrected",
        "census_2011_district_code_by_point": "Census 2011 polygon containing the point (valid only)",
        "lgd_district_code_by_point": "LGD code of that polygon via S06; 2011 Ballari polygon = 528",
        "lgd_district_code_stated": "LGD code of the stated District field (S06 names + aliases)",
        "lgd_district_name_stated": "S06 name for lgd_district_code_stated",
        "district_check": "agree / agree_pre_split (stated Vijayanagara, point in 2011 Ballari) / "
        "disagree / not_assessable / stated_district_unmatched",
        "exact_duplicate_group_size": "Rows in S15 Karnataka with all 12 source fields identical "
        "(1 = unique). Kept: may be identical chargers at one station",
        "station_key": "ID per identical (CPO, location, latitude, longitude) as printed",
        "site_id": "ID per identical (latitude, longitude), valid coordinates only",
        "charger_rating_value": "Charger Rating if numeric; unit not stated in source",
        "connector_count": "No. of Connector if an integer",
        "operational_status": "Always missing: the source has no status field",
        "latitude": "As printed in S15 (S18) / site coordinate (S19)",
        "longitude": "As printed in S15 (S18) / site coordinate (S19)",
        "source_rows": "S18 rows at this site",
        "connectors": "Sum of connector_count at this site",
        "station_keys": "Distinct station_key values at this site",
        "cpo_names": "Distinct CPO names at this site",
        "max_charger_rating_value": "Largest numeric charger rating at this site; unit not stated",
        "nearby_sites_within_25m": f"Other sites within {NEARBY_SITE_M:.0f} m (possible same place)",
        "site_cluster_25m": f"Single-linkage cluster of sites within {NEARBY_SITE_M:.0f} m; a lower-bound "
        "grouping for physical places, not a confirmed merge",
        "nearest_osm_inventory_id": "Nearest S11 OSM record",
        "nearest_osm_distance_m": "Distance to it, metres",
        "osm_match_within_100m": f"yes if nearest OSM record is within {OSM_MATCH_M:.0f} m "
        "(proximity only, not a confirmed identity match)",
    }
    out = []
    for col in ROW_COLUMNS:
        desc = d.get(col, "Source field as printed in S15 (only PDF word-wrap line breaks joined)")
        out.append({"table": "S18", "column": col, "description": desc})
    for col in SITE_COLUMNS:
        desc = d.get(col)
        if desc is None:
            desc = {
                "lgd_district_code_stated": "Distinct stated LGD codes of the site's rows",
                "lgd_district_code_by_point": "LGD code by point-in-polygon",
            }[col]
        out.append({"table": "S19", "column": col, "description": desc})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true", help="replace outputs whose content differs"
    )
    args = parser.parse_args(argv)

    rows, sites, summary = build()
    summary["inputs_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (S16, S11)
    }
    outputs = {
        OUT_ROWS: bdt.to_csv_bytes(ROW_COLUMNS, rows),
        OUT_SITES: bdt.to_csv_bytes(SITE_COLUMNS, sites),
        OUT_DICT: bdt.to_csv_bytes(["table", "column", "description"], dictionary_rows()),
        OUT_SUMMARY: (json.dumps(summary, indent=2) + "\n").encode("utf-8"),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {}
    for path, data in outputs.items():
        report[path.name] = {
            "status": bdt.write_if_unchanged(path, data, args.force),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    json.dump({**summary, "outputs": report}, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
