"""Build S23: Karnataka OSM GeoJSON layers and boundary files from the S21 extract.

Inputs (read-only, data/raw/):
    S21  OSM France Karnataka extract: .osm.pbf (all layers) and .poly (cut polygon)
    S22  Overpass responses, if present: used ONLY as independent count cross-checks

Outputs (data/processed/):
    S23_osm_ka_<layer>.geojson                     one FeatureCollection per layer
    S23_karnataka_boundary_osm_admin.geojson       OSM admin relation, ONE Feature
    S23_karnataka_extract_polygon_osmfr.geojson    S21 .poly polygon, ONE Feature
    S23_summary.json                               counts, coverage, cross-checks, hashes

Layers (tag filters mirror src/queries/osm_ka_<layer>.overpassql):
    roads_major     ways: highway motorway|trunk|primary|secondary|tertiary (+ _link) -> LineString
    power_lines     ways: power line|minor_line|cable -> LineString
    settlements     place city|town|village|hamlet|suburb|neighbourhood|quarter -> Point
    amenities       amenity=* except parking/fuel/charging_station types -> Point
    parking         amenity parking|motorcycle_parking -> Point
    fuel            amenity=fuel -> Point
    charging_stations  amenity=charging_station -> Point (cross-check with S10)
    power_points    power plant|substation|generator|transformer|switch|compensator|converter -> Point
Point layers take nodes, ways and relations; ways and relations become a Point at the
centre of their bounding box (property "@geometry": "center", as Overpass "out center").

Rules: properties are the OSM tags plus "@id", "@type". Nothing is simplified, merged
or dropped. The extract keeps whole ways/relations that cross the state border, so each
feature is tested against the OSM admin boundary at its representative point (Point, or
the middle vertex of a line) and flagged "@outside_admin_boundary" when outside. Ways
with nodes missing from the extract keep their available vertices and are counted.

Uses only the standard library. Run from the repository root (about 1 minute):
    python src/evinfra/analysis/build_osm_karnataka_layers.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from itertools import pairwise
from pathlib import Path

from evinfra.analysis import build_district_table as bdt
from evinfra.ingestion import osm_pbf
from evinfra.ingestion.osm_pbf import LayerSpec

ROOT = bdt.ROOT
RAW = bdt.RAW
OUT_DIR = bdt.OUT_DIR
PBF_GLOB = "S21_osmfr_karnataka_*.osm.pbf"
POLY_GLOB = "S21_osmfr_karnataka_*.poly"
S22_GLOB = "S22_osm_ka_*_overpass_*.json"
OUT_ADMIN = "S23_karnataka_boundary_osm_admin.geojson"
OUT_POLY = "S23_karnataka_extract_polygon_osmfr.geojson"
OUT_SUMMARY = "S23_summary.json"

MAJOR_ROAD = re.compile(r"^(motorway|trunk|primary|secondary|tertiary)(_link)?$")
SETTLEMENT = {"city", "town", "village", "hamlet", "suburb", "neighbourhood", "quarter"}
PARKING = {"parking", "motorcycle_parking"}
AMENITY_EXCLUDED = PARKING | {"parking_space", "parking_entrance", "fuel", "charging_station"}
POWER_POINT = {
    "plant",
    "substation",
    "generator",
    "transformer",
    "switch",
    "compensator",
    "converter",
}
POWER_LINE = {"line", "minor_line", "cable"}


def is_boundary(t):
    return (
        t.get("boundary") == "administrative"
        and t.get("admin_level") == "4"
        and t.get("ISO3166-2") == "IN-KA"
    )


SPECS = [
    LayerSpec(
        "roads_major",
        lambda t: bool(MAJOR_ROAD.match(t.get("highway", ""))),
        node=False,
        relation=False,
    ),
    LayerSpec("power_lines", lambda t: t.get("power") in POWER_LINE, node=False, relation=False),
    LayerSpec("settlements", lambda t: t.get("place") in SETTLEMENT),
    LayerSpec("amenities", lambda t: "amenity" in t and t["amenity"] not in AMENITY_EXCLUDED),
    LayerSpec("parking", lambda t: t.get("amenity") in PARKING),
    LayerSpec("fuel", lambda t: t.get("amenity") == "fuel"),
    LayerSpec("charging_stations", lambda t: t.get("amenity") == "charging_station"),
    LayerSpec("power_points", lambda t: t.get("power") in POWER_POINT),
    LayerSpec("boundary", is_boundary, node=False, way=False),
]
LINE_LAYERS = {"roads_major", "power_lines"}


class LayerError(ValueError):
    """Raised when inputs are malformed or geometry cannot be built."""


# ---------------------------------------------------------------- polygons


def parse_poly(text: str) -> list[list[tuple[float, float]]]:
    """Osmosis .poly -> list of rings [(lon, lat), ...]. Holes ('!' sections) are rejected."""
    lines = [ln.strip() for ln in text.splitlines()]
    rings, current = [], None
    for ln in lines[1:]:  # line 0 is the polygon name
        if not ln:
            continue
        if ln == "END":
            if current is None:
                break
            rings.append(current)
            current = None
        elif current is None:
            if ln.startswith("!"):
                raise LayerError("Polygon holes in .poly are not supported")
            current = []
        else:
            lon, lat = (float(v) for v in ln.split()[:2])
            current.append((lon, lat))
    if current is not None or not rings:
        raise LayerError("Malformed .poly file")
    for r in rings:
        if r[0] != r[-1]:
            r.append(r[0])
    return rings


class BandedPolygon:
    """Even-odd point-in-polygon with edges bucketed by latitude band (fast for many points)."""

    def __init__(self, rings, band: float = 0.02):
        self.band = band
        self.buckets: dict[int, list[tuple[float, float, float, float]]] = {}
        for ring in rings:
            for (x1, y1), (x2, y2) in pairwise(ring):
                if y1 == y2:
                    continue
                for b in range(int(min(y1, y2) // band), int(max(y1, y2) // band) + 1):
                    self.buckets.setdefault(b, []).append((x1, y1, x2, y2))

    def contains(self, x: float, y: float) -> bool:
        inside = False
        for x1, y1, x2, y2 in self.buckets.get(int(y // self.band), ()):
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                inside = not inside
        return inside


def signed_area(ring) -> float:
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in pairwise(ring)) / 2


def oriented(ring, ccw: bool):
    return ring if (signed_area(ring) > 0) == ccw else ring[::-1]


def assemble_rings(segments: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    """Join way geometries end-to-end into closed rings."""
    todo = [list(s) for s in segments if len(s) >= 2]
    rings = []
    while todo:
        ring = todo.pop(0)
        while ring[0] != ring[-1]:
            for k, seg in enumerate(todo):
                if seg[0] == ring[-1]:
                    ring.extend(seg[1:])
                elif seg[-1] == ring[-1]:
                    ring.extend(seg[-2::-1])
                else:
                    continue
                todo.pop(k)
                break
            else:
                raise LayerError(f"Ring does not close (open end at {ring[-1]})")
        if len(ring) < 4:
            raise LayerError("Degenerate ring")
        rings.append(ring)
    return rings


def relation_multipolygon(rel: dict) -> list:
    outer, inner = [], []
    for m in rel.get("members", []):
        if m.get("type") != "way" or not m.get("geometry"):
            continue
        if any(p is None for p in m["geometry"]):
            raise LayerError(f"Boundary member way {m.get('ref')} has missing nodes")
        coords = [(p["lon"], p["lat"]) for p in m["geometry"]]
        (inner if m.get("role") == "inner" else outer).append(coords)
    if not outer:
        raise LayerError("Relation has no outer member geometry")
    polygons = [[oriented(r, True)] for r in assemble_rings(outer)]
    for hole in assemble_rings(inner) if inner else []:
        x, y = hole[0]
        host = next((p for p in polygons if BandedPolygon([p[0]]).contains(x, y)), None)
        if host is None:
            raise LayerError("Inner ring is not inside any outer ring")
        host.append(oriented(hole, False))
    return [[[list(pt) for pt in ring] for ring in poly] for poly in polygons]


# ---------------------------------------------------------------- features


def bbox_centre(points: list[dict]) -> dict | None:
    pts = [p for p in points if p]
    if not pts:
        return None
    lats, lons = [p["lat"] for p in pts], [p["lon"] for p in pts]
    return {
        "lat": round((min(lats) + max(lats)) / 2, 7),
        "lon": round((min(lons) + max(lons)) / 2, 7),
    }


def element_points(e: dict) -> list[dict]:
    if e["type"] == "way":
        return e.get("geometry", [])
    if e["type"] == "relation":
        pts = []
        for m in e.get("members", []):
            if m["type"] == "way":
                pts += m.get("geometry", [])
            elif "lat" in m:
                pts.append({"lat": m["lat"], "lon": m["lon"]})
        return pts
    return [{"lat": e["lat"], "lon": e["lon"]}]


def feature(e: dict, line: bool) -> tuple[dict | None, int]:
    """Return (feature or None if no coordinates at all, number of missing vertices)."""
    props = {"@id": f"{e['type']}/{e['id']}", "@type": e["type"], **e.get("tags", {})}
    if e["type"] == "node":
        return {
            "type": "Feature",
            "properties": props,
            "geometry": {"type": "Point", "coordinates": [e["lon"], e["lat"]]},
        }, 0
    pts = element_points(e)
    missing = sum(1 for p in pts if p is None)
    if line:
        coords = [[p["lon"], p["lat"]] for p in pts if p]
        if len(coords) < 2:
            return None, missing
        return {
            "type": "Feature",
            "properties": props,
            "geometry": {"type": "LineString", "coordinates": coords},
        }, missing
    c = bbox_centre(pts)
    if c is None:
        return None, missing
    props["@geometry"] = "center"
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {"type": "Point", "coordinates": [c["lon"], c["lat"]]},
    }, missing


def representative(geom: dict) -> list[float]:
    if geom["type"] == "Point":
        return geom["coordinates"]
    coords = geom["coordinates"]
    return coords[len(coords) // 2]


def newest(paths) -> Path:
    paths = sorted(paths)
    if not paths:
        raise LayerError("No input files found")
    return paths[-1]


def overpass_counts(raw: Path) -> dict[str, dict]:
    """Element counts of the newest S22 response per layer (cross-check only)."""
    by_layer: dict[str, list[Path]] = {}
    for p in raw.glob(S22_GLOB):
        if p.name.endswith(".manifest.json"):
            continue
        layer = p.name.removeprefix("S22_osm_ka_").rsplit("_overpass_", 1)[0]
        by_layer.setdefault(layer, []).append(p)
    out = {}
    for layer, paths in sorted(by_layer.items()):
        p = newest(paths)
        data = json.loads(p.read_text(encoding="utf-8"))
        out[layer] = {
            "file": p.name,
            "osm_base_timestamp": data.get("osm3s", {}).get("timestamp_osm_base"),
            "elements": len(data["elements"]),
            "has_geometry": any(
                "geometry" in e or "members" in e or "center" in e or "lat" in e
                for e in data["elements"]
            ),
        }
    return out


# ---------------------------------------------------------------- build


def build(raw: Path = RAW) -> tuple[dict[str, dict], dict]:
    pbf = newest(raw.glob(PBF_GLOB))
    poly_path = newest(raw.glob(POLY_GLOB))
    extract_rings = parse_poly(poly_path.read_text(encoding="utf-8"))
    extract_poly = BandedPolygon(extract_rings)

    elements, read_report = osm_pbf.select(pbf, SPECS)
    summary: dict = {
        "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (pbf, poly_path)},
        "pbf_read": read_report,
        "layers": {},
    }

    rels = elements.pop("boundary")
    if len(rels) != 1:
        raise LayerError(f"Expected 1 Karnataka admin relation in the PBF, found {len(rels)}")
    rel = rels[0]
    admin_coords = relation_multipolygon(rel)
    admin = BandedPolygon([ring for poly in admin_coords for ring in poly])
    outer_pts = [pt for poly in admin_coords for pt in poly[0]]
    outputs: dict[str, dict] = {
        OUT_ADMIN: {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "@id": f"relation/{rel['id']}",
                        "@type": "relation",
                        **rel["tags"],
                    },
                    "geometry": {"type": "MultiPolygon", "coordinates": admin_coords},
                }
            ],
        },
        OUT_POLY: {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Karnataka extract polygon (OSM France)",
                        "source": poly_path.name,
                    },
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [
                            [[list(p) for p in oriented(r, True)]] for r in extract_rings
                        ],
                    },
                }
            ],
        },
    }
    summary["boundary"] = {
        "relation": f"relation/{rel['id']}",
        "name": rel["tags"].get("name"),
        "polygons": len(admin_coords),
        "inner_rings": sum(len(p) - 1 for p in admin_coords),
        "outer_vertices": len(outer_pts),
        "outer_vertices_outside_extract_polygon": sum(
            1 for x, y in outer_pts if not extract_poly.contains(x, y)
        ),
        "extract_polygon_vertices": sum(len(r) for r in extract_rings),
    }

    for spec in SPECS:
        if spec.name == "boundary":
            continue
        line = spec.name in LINE_LAYERS
        feats, dropped, partial, outside = [], [], 0, 0
        for e in sorted(elements[spec.name], key=lambda x: (x["type"], x["id"])):
            f, missing = feature(e, line)
            if f is None:
                dropped.append(f"{e['type']}/{e['id']}")
                continue
            partial += 1 if missing else 0
            x, y = representative(f["geometry"])
            if not admin.contains(x, y):
                f["properties"]["@outside_admin_boundary"] = "yes"
                outside += 1
            feats.append(f)
        outputs[f"S23_osm_ka_{spec.name}.geojson"] = {
            "type": "FeatureCollection",
            "features": feats,
        }
        summary["layers"][spec.name] = {
            "features": len(feats),
            "inside_admin_boundary": len(feats) - outside,
            "outside_admin_boundary": outside,
            "osm_types": dict(sorted(Counter(f["properties"]["@type"] for f in feats).items())),
            "geometry_types": dict(sorted(Counter(f["geometry"]["type"] for f in feats).items())),
            "features_with_missing_vertices": partial,
            "elements_without_any_coordinates": dropped,
        }
    summary["overpass_cross_check"] = overpass_counts(raw)
    return outputs, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true", help="replace outputs whose content differs"
    )
    args = parser.parse_args(argv)

    outputs, summary = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # The summary records only content facts (bytes, hashes), so it is itself reproducible;
    # write statuses go to stdout only.
    status, summary["outputs"] = {}, {}
    for name, obj in outputs.items():
        data = (json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        status[name] = bdt.write_if_unchanged(OUT_DIR / name, data, args.force)
        summary["outputs"][name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    summary_bytes = (json.dumps(summary, indent=2) + "\n").encode("utf-8")
    status[OUT_SUMMARY] = bdt.write_if_unchanged(OUT_DIR / OUT_SUMMARY, summary_bytes, args.force)
    json.dump({**summary, "write_status": status}, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
