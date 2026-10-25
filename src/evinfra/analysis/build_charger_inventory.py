"""Build S11 (Karnataka charger inventory) and S12 (S09 district table + charger columns).

Inputs (read-only, from data/raw/ and data/processed/):
    S02  OSM Karnataka charging stations (overpass-turbo GeoJSON, 24 Oct 2026)
    S10  OSM Karnataka charging stations (Overpass API JSON with element metadata)
    S06  LGD district codes (Census 2011 code -> current LGD district)
    S09  Derived Karnataka district indicator table
    Census 2011 district boundaries (datameet shapefile, used to assign points)

Inventory rules:
    - One record per OSM element (type/id). S02 and S10 are the same lineage group
      (OSM), so a shared element is one record listing both source IDs.
    - Tags and coordinates come from S10 when present (it carries version and edit
      date); otherwise from S02. Whether the two tag sets match is recorded.
    - Possible duplicates (same name or operator within 50 m) are flagged, never merged.
    - Compatibility is three-state per OSM vehicle tag: confirmed / confirmed_not /
      unknown. Nothing is inferred from operator, brand or name.
    - Operating status, rated power and public status are not inferred.

District join: points are assigned to Census 2011 polygons and mapped to LGD codes via
S06. Vijayanagar (LGD 738) has no 2011 polygon, so its charger columns stay missing and
Ballari (528) covers the pre-split area, as in S09. EV registrations, DISCOM and grid
columns are present but left missing: no source at district level exists in the repo.

Uses only the standard library. Run from the repository root:
    python src/evinfra/analysis/build_charger_inventory.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

from evinfra.analysis import build_district_table as bdt

RAW = bdt.RAW
OUT_DIR = bdt.OUT_DIR
S02 = bdt.S02
S10_GLOB = "S10_osm_karnataka_charging_stations_overpass_*.json"
S09 = bdt.OUT_TABLE
OUT_INVENTORY = OUT_DIR / "S11_karnataka_charger_inventory.csv"
OUT_JOIN = OUT_DIR / "S12_karnataka_district_charger_join.csv"
OUT_DICT = OUT_DIR / "S11_S12_dictionary.csv"

DUPLICATE_RADIUS_M = 50.0
PUBLIC_ACCESS = {"yes", "permissive", "public"}
RESTRICTED_ACCESS = {"private", "customers", "no", "permit", "destination", "delivery"}
COMPAT_TAGS = ("motorcar", "motorcycle", "scooter", "bicycle")
CONFIRMED = {"yes", "designated"}

INVENTORY_COLUMNS = [
    "inventory_id",
    "lineage_group",
    "source_ids",
    "source_record_id",
    "osm_element_type",
    "latitude",
    "longitude",
    "coordinate_basis",
    "osm_version",
    "osm_last_edited",
    "s02_s10_tags_identical",
    "name",
    "operator",
    "brand",
    "access_tag",
    "access_class",
    "fee",
    "capacity_tag",
    "socket_tags",
    "output_tags",
    "battery_swapping_tag",
    "check_date",
    *[f"compat_{t}" for t in COMPAT_TAGS],
    "operational_status",
    "possible_duplicate_of",
    "census_2011_district_code",
    "lgd_district_code",
    "lgd_district_name",
    "district_assignment_note",
]

JOIN_EXTRA_COLUMNS = [
    "inv_osm_records",
    "inv_osm_access_public_tagged",
    "inv_osm_access_restricted_tagged",
    "inv_osm_access_unknown",
    "inv_osm_compat_motorcar_confirmed",
    "inv_osm_compat_motorcycle_confirmed",
    "inv_osm_battery_swapping_tagged",
    "ev_registrations_district",
    "discom_names",
    "grid_spare_capacity",
]


class InventoryError(ValueError):
    """Raised when inputs are malformed or fail a consistency check."""


# ---------------------------------------------------------------- readers


def find_s10(raw: Path) -> Path:
    files = sorted(p for p in raw.glob(S10_GLOB) if not p.name.endswith(".manifest.json"))
    if not files:
        raise InventoryError(f"No S10 file matching {S10_GLOB} in {raw}")
    return files[-1]


def read_s02(path: Path) -> dict[str, dict]:
    records = {}
    for f in json.loads(path.read_text(encoding="utf-8"))["features"]:
        key = f["properties"]["@id"]
        tags = {k: v for k, v in f["properties"].items() if not k.startswith("@")}
        lon, lat = f["geometry"]["coordinates"][:2]
        records[key] = {"tags": tags, "lat": lat, "lon": lon, "type": key.split("/")[0]}
    return records


def read_s10(path: Path) -> dict[str, dict]:
    records = {}
    for e in json.loads(path.read_text(encoding="utf-8"))["elements"]:
        key = f"{e['type']}/{e['id']}"
        point = e if "lat" in e else e.get("center")
        if point is None:
            raise InventoryError(f"S10 element {key} has no coordinates or centre")
        records[key] = {
            "tags": dict(e.get("tags", {})),
            "lat": point["lat"],
            "lon": point["lon"],
            "type": e["type"],
            "version": str(e.get("version", "")),
            "timestamp": e.get("timestamp", ""),
        }
    return records


# ---------------------------------------------------------------- helpers


def comparable_tags(tags: dict[str, str]) -> dict[str, str]:
    """Drop the multipolygon 'type' tag, which overpass-turbo and Overpass treat differently."""
    return {k: v for k, v in tags.items() if k != "type"}


def access_class(value: str) -> str:
    v = value.strip().lower()
    if v in PUBLIC_ACCESS:
        return "public_tagged"
    if v in RESTRICTED_ACCESS:
        return "restricted_tagged"
    return "unknown"


def compat_state(value: str | None) -> str:
    if value is None or not value.strip():
        return "unknown"
    v = value.strip().lower()
    if v in CONFIRMED:
        return "confirmed"
    if v == "no":
        return "confirmed_not"
    return "unknown"


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371008.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def tag_list(tags: dict[str, str], match) -> str:
    return ";".join(f"{k}={v}" for k, v in sorted(tags.items()) if match(k))


# ---------------------------------------------------------------- build


def build(raw: Path = RAW, s09: Path = S09) -> tuple[list[dict], list[str], list[dict], dict]:
    report: dict = {}
    s10_path = find_s10(raw)
    s02 = read_s02(raw / S02.name)
    s10 = read_s10(s10_path)
    report["s02_records"] = len(s02)
    report["s10_records"] = len(s10)
    report["s10_file"] = s10_path.name

    spine = [r for r in bdt.read_csv(raw / bdt.S06.name) if r["state_code"] == bdt.STATE_CODE]
    census_to_lgd = {}
    for r in spine:
        code = r["census_2011_district_code"]
        if code not in ("", "0", "None"):
            if code in census_to_lgd:
                raise InventoryError(f"Census 2011 code {code} maps to several LGD districts")
            census_to_lgd[code] = (r["district_code"], r["district_name"])

    polygons = bdt.read_boundaries(
        raw / "district_boundaries" / bdt.BOUNDARIES.name, bdt.STATE_CODE
    )

    keys = sorted(s02.keys() | s10.keys(), key=lambda k: (k.split("/")[0], int(k.split("/")[1])))
    assigned = bdt.assign_points(
        [((s10.get(k) or s02[k])["lon"], (s10.get(k) or s02[k])["lat"]) for k in keys], polygons
    )

    records = []
    for key, c2011 in zip(keys, assigned):
        rec = s10.get(key) or s02[key]
        tags = rec["tags"]
        sources = [sid for sid, src in (("S02", s02), ("S10", s10)) if key in src]
        identical = ""
        if len(sources) == 2:
            same = comparable_tags(s02[key]["tags"]) == comparable_tags(s10[key]["tags"])
            identical = "yes" if same else "no"
        lgd, lgd_name, note = "", "", ""
        if c2011 is None:
            note = "outside Karnataka Census 2011 district polygons (quarantined)"
        else:
            lgd, lgd_name = census_to_lgd[c2011]
            if lgd == bdt.BALLARI_LGD:
                note = "2011 Ballari polygon; may lie in present-day Vijayanagar (LGD 738)"
        etype = rec["type"]
        records.append(
            {
                "inventory_id": f"KA-OSM-{etype[0].upper()}{key.split('/')[1]}",
                "lineage_group": "OSM",
                "source_ids": ";".join(sources),
                "source_record_id": key,
                "osm_element_type": etype,
                "latitude": f"{rec['lat']:.7f}",
                "longitude": f"{rec['lon']:.7f}",
                "coordinate_basis": "node position" if etype == "node" else f"{etype} centre",
                "osm_version": rec.get("version", ""),
                "osm_last_edited": rec.get("timestamp", ""),
                "s02_s10_tags_identical": identical,
                "name": tags.get("name", ""),
                "operator": tags.get("operator", ""),
                "brand": tags.get("brand", ""),
                "access_tag": tags.get("access", ""),
                "access_class": access_class(tags.get("access", "")),
                "fee": tags.get("fee", ""),
                "capacity_tag": tags.get("capacity", ""),
                "socket_tags": tag_list(tags, lambda k: k.startswith("socket:")),
                "output_tags": tag_list(tags, lambda k: k.endswith(":output") or k == "output"),
                "battery_swapping_tag": tags.get(
                    "charging_station:battery_swapping", tags.get("battery_swapping", "")
                ),
                "check_date": tags.get("check_date", ""),
                **{f"compat_{t}": compat_state(tags.get(t)) for t in COMPAT_TAGS},
                "operational_status": "",
                "possible_duplicate_of": "",
                "census_2011_district_code": c2011 or "",
                "lgd_district_code": lgd,
                "lgd_district_name": lgd_name,
                "district_assignment_note": note,
                "_lat": rec["lat"],
                "_lon": rec["lon"],
            }
        )

    pairs = 0
    for i, a in enumerate(records):
        for b in records[i + 1 :]:
            same_label = any(
                a[f] and a[f].strip().lower() == b[f].strip().lower() for f in ("name", "operator")
            )
            if same_label and distance_m(a["_lat"], a["_lon"], b["_lat"], b["_lon"]) <= (
                DUPLICATE_RADIUS_M
            ):
                pairs += 1
                for x, y in ((a, b), (b, a)):
                    ids = [v for v in x["possible_duplicate_of"].split(";") if v]
                    x["possible_duplicate_of"] = ";".join(ids + [y["inventory_id"]])
    for r in records:
        del r["_lat"], r["_lon"]

    report["inventory_records"] = len(records)
    report["records_in_both_sources"] = sum(1 for r in records if r["source_ids"] == "S02;S10")
    report["records_tags_differ"] = sum(1 for r in records if r["s02_s10_tags_identical"] == "no")
    report["records_quarantined"] = sum(1 for r in records if not r["census_2011_district_code"])
    report["possible_duplicate_pairs"] = pairs

    # District join: S09 columns + charger columns.
    s09_rows = bdt.read_csv(s09)
    s09_columns = list(s09_rows[0])
    by_lgd: dict[str, list[dict]] = {}
    for r in records:
        if r["lgd_district_code"]:
            by_lgd.setdefault(r["lgd_district_code"], []).append(r)
    join_rows = []
    for row in s09_rows:
        out = dict(row)
        for col in JOIN_EXTRA_COLUMNS:
            out[col] = ""
        if row["census_2011_district_code"]:
            recs = by_lgd.get(row["lgd_district_code"], [])
            out["inv_osm_records"] = str(len(recs))
            for cls in ("public_tagged", "restricted_tagged", "unknown"):
                out[f"inv_osm_access_{cls}"] = str(sum(1 for r in recs if r["access_class"] == cls))
            for t in ("motorcar", "motorcycle"):
                out[f"inv_osm_compat_{t}_confirmed"] = str(
                    sum(1 for r in recs if r[f"compat_{t}"] == "confirmed")
                )
            out["inv_osm_battery_swapping_tagged"] = str(
                sum(1 for r in recs if r["battery_swapping_tag"].lower() == "yes")
            )
            if out["inv_osm_records"] != row["osm_mapped_charging_records"]:
                raise InventoryError(
                    f"District {row['lgd_district_code']}: inventory count {out['inv_osm_records']}"
                    f" != S09 osm_mapped_charging_records {row['osm_mapped_charging_records']}"
                )
        join_rows.append(out)

    assigned_total = sum(int(r["inv_osm_records"] or 0) for r in join_rows)
    if assigned_total != len(records) - report["records_quarantined"]:
        raise InventoryError("District charger counts do not sum to the assigned inventory records")
    report["join_rows"] = len(join_rows)
    report["join_assigned_records"] = assigned_total
    return records, s09_columns + JOIN_EXTRA_COLUMNS, join_rows, report


def dictionary_rows() -> list[dict[str, str]]:
    def row(table: str, column: str, description: str) -> dict[str, str]:
        return {"table": table, "column": column, "description": description}

    inv = {
        "inventory_id": "Stable ID: KA-OSM-<N|W|R><OSM element id>",
        "lineage_group": "Independent evidence lineage. S02 and S10 are both OSM, so one lineage",
        "source_ids": "Register IDs of the files that contain this element",
        "source_record_id": "OSM element type/id",
        "osm_element_type": "node, way or relation",
        "latitude": "WGS84 degrees (S10 if present, else S02)",
        "longitude": "WGS84 degrees (S10 if present, else S02)",
        "coordinate_basis": "Node position, or Overpass centre of a way/relation",
        "osm_version": "OSM element version (S10 only)",
        "osm_last_edited": "Last edit timestamp of the OSM element (S10 only); not a survey date",
        "s02_s10_tags_identical": "yes/no when in both files (ignoring the multipolygon 'type' tag)",
        "name": "OSM name tag, as mapped",
        "operator": "OSM operator tag, as mapped",
        "brand": "OSM brand tag, as mapped",
        "access_tag": "OSM access tag, as mapped (blank = not tagged)",
        "access_class": "public_tagged / restricted_tagged / unknown, from access_tag only",
        "fee": "OSM fee tag",
        "capacity_tag": "OSM capacity tag (vehicles at once, as mapped); not rated power",
        "socket_tags": "All socket:* tags, key=value;...",
        "output_tags": "All *:output tags, key=value;... (rated output as mapped)",
        "battery_swapping_tag": "charging_station:battery_swapping or battery_swapping tag",
        "check_date": "OSM check_date tag (last mapper check), if any",
        "operational_status": "Always missing: OSM mapping does not show whether a charger works",
        "possible_duplicate_of": f"inventory_ids with the same name or operator within "
        f"{DUPLICATE_RADIUS_M:.0f} m; flagged only, never merged",
        "census_2011_district_code": "Census 2011 district polygon containing the point",
        "lgd_district_code": "Current LGD district via S06 (2011 code -> LGD)",
        "lgd_district_name": "Current LGD district name (S06)",
        "district_assignment_note": "Boundary caveats and quarantine reason",
    }
    rows = [row("S11", c, inv[c]) for c in INVENTORY_COLUMNS if c in inv]
    rows += [
        row(
            "S11",
            f"compat_{t}",
            f"Three-state from OSM {t} tag: confirmed (yes/designated), "
            "confirmed_not (no), unknown (missing/other)",
        )
        for t in COMPAT_TAGS
    ]
    order = {c: i for i, c in enumerate(INVENTORY_COLUMNS)}
    rows.sort(key=lambda r: order[r["column"]])
    join = {
        "inv_osm_records": "S11 records assigned to this district; equals S09 "
        "osm_mapped_charging_records (checked). Mapped records, not installed or working chargers",
        "inv_osm_access_public_tagged": "S11 records with access_class public_tagged",
        "inv_osm_access_restricted_tagged": "S11 records with access_class restricted_tagged",
        "inv_osm_access_unknown": "S11 records with access_class unknown",
        "inv_osm_compat_motorcar_confirmed": "S11 records with compat_motorcar confirmed",
        "inv_osm_compat_motorcycle_confirmed": "S11 records with compat_motorcycle confirmed",
        "inv_osm_battery_swapping_tagged": "S11 records with battery swapping tagged yes",
        "ev_registrations_district": "MISSING by design: S01 VAHAN has statewide totals only; "
        "no district or RTO registrations in the repo",
        "discom_names": "MISSING by design: no verified DISCOM-to-district list in the repo",
        "grid_spare_capacity": "MISSING by design: no substation or spare-capacity source",
    }
    rows.append(row("S12", "(S09 columns)", "All S09 columns unchanged; see the S09 dictionary"))
    rows += [row("S12", c, join[c]) for c in JOIN_EXTRA_COLUMNS]
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true", help="replace outputs whose content differs"
    )
    args = parser.parse_args(argv)

    records, join_columns, join_rows, report = build()
    outputs = {
        OUT_INVENTORY: bdt.to_csv_bytes(INVENTORY_COLUMNS, records),
        OUT_JOIN: bdt.to_csv_bytes(join_columns, join_rows),
        OUT_DICT: bdt.to_csv_bytes(["table", "column", "description"], dictionary_rows()),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path, data in outputs.items():
        report[path.name] = {
            "status": bdt.write_if_unchanged(path, data, args.force),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    json.dump(report, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
