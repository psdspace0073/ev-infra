"""Build S09: a derived Karnataka district-level indicator table.

Inputs (read-only, from data/raw/):
    S02  OSM Karnataka charging stations (GeoJSON points)
    S04  Census 2011 A-1 table: villages, towns, households, population, area
    S06  LGD district codes with Census 2011 district codes (join spine)
    S07  NFHS district indicators (2015-16, 2019-21, 2023-24)
    S08  Mission Antyodaya 2020 district infrastructure
    Census 2011 district boundaries (datameet shapefile, used only to assign S02 points)

S01 (VAHAN) is state-level only (calendar-year totals, no district or RTO field),
so it is deliberately not joined.

Join rules:
    - Spine: the 31 current Karnataka districts in S06 (state_code 29).
    - S07, S08: joined on LGD district code.
    - S04 and the 2011 boundaries: joined on Census 2011 district code via S06.
    - Vijayanagar (LGD 738) has no Census 2011 code. Census 2011 values and
      2011-boundary charger counts are left missing for it, and Ballari's values
      cover the pre-split area. Nothing is allocated between the two.

Uses only the standard library. Run from the repository root:
    python src/evinfra/analysis/build_district_table.py [--force]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"
OUT_TABLE = OUT_DIR / "S09_karnataka_district_indicators.csv"
OUT_DICT = OUT_DIR / "S09_karnataka_district_indicators_dictionary.csv"

S02 = RAW / "S02_osm_karnataka_charging_stations.geojson"
S04 = RAW / "S04_census_2011_district_population_area.xlsx.xlsx"
S06 = RAW / "S06_idp_district_lgd_codes.csv"
S07 = RAW / "S07_idp_nfhs_district_indicators.csv"
S08 = RAW / "S08_idp_mission_antyodaya_district_infrastructure_2020.csv"
BOUNDARIES = RAW / "district_boundaries" / "datameet maps master Districts-Census_2011.zip"

STATE_CODE = "29"
VIJAYANAGAR_LGD = "738"
BALLARI_LGD = "528"
BENGALURU_SOUTH_LGD = "631"

NFHS_ROUNDS = {"2015-16": "2015_16", "2019-21": "2019_21", "2023-24": "2023_24"}
NFHS_INDICATORS = {
    "population_under_15": "% of household population",
    "population_60plus": "% of household population",
    "sex_ratio_total": "females per 1,000 males",
    "population_electricity": "% of household population",
    "women_literate": "% of women age 15-49",
    "households_bank_account": "% of households",
    "women_ever_used_internet": "% of women age 15-49",
    "men_ever_used_internet": "% of men age 15-49",
}

MA_COLUMNS = [
    "villages_surveyed",
    "tot_pop",
    "all_weather_road",
    "cc_road_full",
    "cc_road_partial",
    "cc_road_not",
    "pub_trans_bus",
    "pub_trans_no",
    "railway",
]

CENSUS_FIELDS = {
    "K": "population",
    "J": "households",
    "N": "area_sqkm",
    "O": "density_per_sqkm",
}
CENSUS_ROW_TYPES = ("total", "rural", "urban")

# Source tokens that mean "no value"; they are written out as blank cells.
MISSING_TOKENS = {"", "None", "NA"}


class DistrictTableError(ValueError):
    """Raised when inputs are malformed or fail a join or consistency check."""


def clean(value: str | None) -> str:
    return "" if value is None or value.strip() in MISSING_TOKENS else value


def parse_int(value: str, what: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise DistrictTableError(f"{what}: expected an integer, got {value!r}") from None


# ---------------------------------------------------------------- readers


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_xlsx_rows(path: Path) -> list[dict[str, str]]:
    """Return the first worksheet as a list of {column letter: cell text}."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as z:
        shared = [
            "".join(t.text or "" for t in si.iter(f"{{{ns['m']}}}t"))
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)
        ]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.iter(f"{{{ns['m']}}}row"):
        values = {}
        for cell in row.findall("m:c", ns):
            v = cell.find("m:v", ns)
            if v is None:
                continue
            col = re.match(r"[A-Z]+", cell.get("r")).group()
            values[col] = shared[int(v.text)] if cell.get("t") == "s" else v.text
        rows.append(values)
    return rows


def read_boundaries(path: Path, state_code: str) -> list[dict]:
    """Read Census 2011 district polygons for one state from a zipped shapefile."""
    with zipfile.ZipFile(path) as z:
        dbf = z.read("2011_Dist.dbf")
        shp = z.read("2011_Dist.shp")
        shx = z.read("2011_Dist.shx")

    n_records, header_len, record_len = struct.unpack("<IHH", dbf[4:12])
    fields = []
    for i in range(32, header_len - 1, 32):
        name = dbf[i : i + 11].split(b"\0")[0].decode()
        fields.append((name, dbf[i + 16]))
    attrs = []
    for k in range(n_records):
        rec = dbf[header_len + k * record_len : header_len + (k + 1) * record_len]
        pos, row = 1, {}
        for name, length in fields:
            row[name] = rec[pos : pos + length].decode("latin-1").strip()
            pos += length
        attrs.append(row)

    polygons = []
    for k, row in enumerate(attrs):
        if row["ST_CEN_CD"] != state_code:
            continue
        offset = struct.unpack(">i", shx[100 + 8 * k : 104 + 8 * k])[0] * 2
        content = offset + 8
        shape_type = struct.unpack("<i", shp[content : content + 4])[0]
        if shape_type != 5:
            raise ValueError(f"Unexpected shape type {shape_type} for {row['DISTRICT']}")
        bbox = struct.unpack("<4d", shp[content + 4 : content + 36])
        n_parts, n_points = struct.unpack("<2i", shp[content + 36 : content + 44])
        parts = list(struct.unpack(f"<{n_parts}i", shp[content + 44 : content + 44 + 4 * n_parts]))
        start = content + 44 + 4 * n_parts
        pts = struct.unpack(f"<{2 * n_points}d", shp[start : start + 16 * n_points])
        coords = list(zip(pts[0::2], pts[1::2]))
        rings = [coords[a:b] for a, b in zip(parts, parts[1:] + [n_points])]
        polygons.append(
            {
                "census_code": str(int(row["censuscode"])),
                "name": row["DISTRICT"],
                "bbox": bbox,
                "rings": rings,
            }
        )
    return polygons


# ---------------------------------------------------------------- geometry


def point_in_rings(x: float, y: float, rings: list[list[tuple[float, float]]]) -> bool:
    """Even-odd ray casting over all rings, so holes are excluded."""
    inside = False
    for ring in rings:
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i]
            x2, y2 = ring[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                inside = not inside
    return inside


def assign_points(points: list[tuple[float, float]], polygons: list[dict]) -> list[str | None]:
    result = []
    for x, y in points:
        hits = [
            p["census_code"]
            for p in polygons
            if p["bbox"][0] <= x <= p["bbox"][2]
            and p["bbox"][1] <= y <= p["bbox"][3]
            and point_in_rings(x, y, p["rings"])
        ]
        if len(hits) > 1:
            raise ValueError(f"Point ({x}, {y}) falls in several districts: {hits}")
        result.append(hits[0] if hits else None)
    return result


# ---------------------------------------------------------------- build


def build() -> tuple[list[str], list[dict[str, str]], dict]:
    report: dict = {}

    spine = [r for r in read_csv(S06) if r["state_code"] == STATE_CODE]
    codes = [r["district_code"] for r in spine]
    if len(codes) != len(set(codes)):
        raise ValueError("Duplicate LGD district codes in S06 spine")
    report["spine_districts"] = len(spine)

    # Census 2011 (S04): district-level Total and Rural/Urban rows, keyed by census code.
    census: dict[str, dict[str, str]] = {}
    for row in read_xlsx_rows(S04):
        if row.get("A") != STATE_CODE or row.get("D") != "DISTRICT" or row.get("C") != "00000":
            continue
        code = str(int(row["B"]))
        tru = row.get("F", "").strip().lower()
        if tru not in CENSUS_ROW_TYPES:
            raise DistrictTableError(
                f"Census 2011 district {code}: unexpected Total/Rural/Urban value {row.get('F')!r}"
            )
        entry = census.setdefault(code, {"name": row["E"].strip()})
        if f"{tru}_population" in entry:
            raise ValueError(f"Duplicate Census 2011 {tru} row for district {code}")
        for col, field in CENSUS_FIELDS.items():
            entry[f"{tru}_{field}"] = row.get(col, "")
        if tru == "total":
            entry["villages_inhabited"] = row.get("G", "")
            entry["towns"] = row.get("I", "")
    for code, entry in census.items():
        missing = [t for t in CENSUS_ROW_TYPES if f"{t}_population" not in entry]
        if missing:
            raise DistrictTableError(
                f"Census 2011 district {code} ({entry['name']}) has no "
                f"{'/'.join(t.title() for t in missing)} row in S04"
            )
    report["census_2011_district_rows"] = len(census)

    # NFHS (S07): keyed by (LGD code, round).
    nfhs: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv(S07):
        if row["state_code"] != STATE_CODE:
            continue
        key = (row["district_code"], row["year"])
        if key in nfhs:
            raise ValueError(f"Duplicate NFHS row {key}")
        nfhs[key] = row
    report["nfhs_karnataka_rows"] = len(nfhs)

    # Mission Antyodaya (S08): keyed by LGD code.
    ma: dict[str, dict[str, str]] = {}
    for row in read_csv(S08):
        if row["state_code"] != STATE_CODE:
            continue
        if row["district_code"] in ma:
            raise ValueError(f"Duplicate Mission Antyodaya row {row['district_code']}")
        ma[row["district_code"]] = row
    report["mission_antyodaya_karnataka_rows"] = len(ma)

    # OSM chargers (S02): assign each mapped point to a Census 2011 district polygon.
    polygons = read_boundaries(BOUNDARIES, STATE_CODE)
    boundary_names = {p["census_code"]: p["name"] for p in polygons}
    features = json.loads(S02.read_text(encoding="utf-8"))["features"]
    points = [tuple(f["geometry"]["coordinates"][:2]) for f in features]
    assigned = assign_points(points, polygons)
    osm_counts: dict[str, int] = {}
    for code in assigned:
        if code is not None:
            osm_counts[code] = osm_counts.get(code, 0) + 1
    report["boundary_polygons"] = len(polygons)
    report["osm_features"] = len(features)
    report["osm_assigned"] = sum(1 for c in assigned if c is not None)
    report["osm_unassigned"] = sum(1 for c in assigned if c is None)

    columns = [
        "lgd_district_code",
        "lgd_district_name",
        "census_2011_district_code",
        "boundary_note",
        "census_2011_name",
        "census_2011_population_total",
        "census_2011_population_rural",
        "census_2011_population_urban",
        "census_2011_households_total",
        "census_2011_area_sqkm",
        "census_2011_density_per_sqkm",
        "census_2011_villages_inhabited",
        "census_2011_towns",
        "boundary_2011_name",
        "osm_mapped_charging_records",
    ]
    columns += [f"ma2020_{c}" for c in MA_COLUMNS] + [
        "ma2020_all_weather_road_share",
        "ma2020_district_name",
    ]
    for label in NFHS_ROUNDS.values():
        columns += [f"nfhs_{label}_{ind}" for ind in NFHS_INDICATORS]
    columns.append("nfhs_district_name")

    rows = []
    for d in sorted(spine, key=lambda r: int(r["district_code"])):
        lgd = d["district_code"]
        c2011 = d["census_2011_district_code"]
        c2011 = "" if c2011 in ("", "0", "None") else c2011
        out = {col: "" for col in columns}
        out["lgd_district_code"] = lgd
        out["lgd_district_name"] = d["district_name"]
        out["census_2011_district_code"] = c2011
        out["boundary_note"] = boundary_note(lgd)

        if c2011:
            c = census.get(c2011)
            if c is None:
                raise ValueError(f"No Census 2011 row for code {c2011} ({d['district_name']})")
            out["census_2011_name"] = c["name"]
            out["census_2011_population_total"] = c.get("total_population", "")
            out["census_2011_population_rural"] = c.get("rural_population", "")
            out["census_2011_population_urban"] = c.get("urban_population", "")
            out["census_2011_households_total"] = c.get("total_households", "")
            out["census_2011_area_sqkm"] = c.get("total_area_sqkm", "")
            out["census_2011_density_per_sqkm"] = c.get("total_density_per_sqkm", "")
            out["census_2011_villages_inhabited"] = c.get("villages_inhabited", "")
            out["census_2011_towns"] = c.get("towns", "")
            if c2011 not in boundary_names:
                raise ValueError(f"No 2011 boundary polygon for code {c2011}")
            out["boundary_2011_name"] = boundary_names[c2011]
            out["osm_mapped_charging_records"] = str(osm_counts.get(c2011, 0))

        m = ma.get(lgd)
        if m is not None:
            for col in MA_COLUMNS:
                out[f"ma2020_{col}"] = clean(m[col])
            surveyed = ma_number(m, "villages_surveyed", lgd)
            if surveyed is None:
                raise DistrictTableError(
                    f"Mission Antyodaya villages_surveyed is blank for district {lgd} "
                    f"({m['district_name']}); it is required as the denominator"
                )
            all_weather = ma_number(m, "all_weather_road", lgd)
            if surveyed > 0 and all_weather is not None:
                out["ma2020_all_weather_road_share"] = f"{all_weather / surveyed:.4f}"
            out["ma2020_district_name"] = m["district_name"]

        for year, label in NFHS_ROUNDS.items():
            n = nfhs.get((lgd, year))
            if n is None:
                continue
            for ind in NFHS_INDICATORS:
                out[f"nfhs_{label}_{ind}"] = clean(n[ind])
            out["nfhs_district_name"] = n["district_name"]
        rows.append(out)

    validate(rows, columns, census, ma, nfhs, report)
    return columns, rows, report


def ma_number(row: dict[str, str], col: str, lgd: str) -> float | None:
    """Return a Mission Antyodaya count as a number, None if missing, or raise if malformed."""
    value = clean(row[col])
    if value == "":
        return None
    try:
        number = float(value)
    except ValueError:
        raise DistrictTableError(
            f"Mission Antyodaya {col} for district {lgd} is not numeric: {row[col]!r}"
        ) from None
    if number < 0:
        raise DistrictTableError(f"Mission Antyodaya {col} for district {lgd} is negative: {value}")
    return number


def boundary_note(lgd: str) -> str:
    if lgd == VIJAYANAGAR_LGD:
        return (
            "Created from Ballari after 2011; no Census 2011 code. Census 2011 values and "
            "2011-boundary OSM counts left missing (counted under Ballari). No NFHS or "
            "Mission Antyodaya row. Nothing allocated."
        )
    if lgd == BALLARI_LGD:
        return (
            "Census 2011 values and 2011-boundary OSM counts cover pre-split Ballari, "
            "including present-day Vijayanagar. NFHS and Mission Antyodaya rows "
            "presumably also cover the combined area."
        )
    if lgd == BENGALURU_SOUTH_LGD:
        return "Formerly Ramanagara; Census 2011, S06 and S08 use the name Ramanagara."
    return ""


def validate(rows, columns, census, ma, nfhs, report) -> None:
    keys = [r["lgd_district_code"] for r in rows]
    duplicates = sorted({k for k in keys if keys.count(k) > 1})
    if duplicates:
        raise DistrictTableError(f"Duplicate district keys in output: {duplicates}")
    if len(rows) != report["spine_districts"]:
        raise DistrictTableError(
            f"Output has {len(rows)} rows but the S06 spine has {report['spine_districts']}"
        )

    c2011_codes = {r["census_2011_district_code"] for r in rows if r["census_2011_district_code"]}
    if c2011_codes != set(census):
        raise DistrictTableError(
            f"Census 2011 codes do not match: spine-only {c2011_codes - set(census)}, "
            f"census-only {set(census) - c2011_codes}"
        )
    unmatched_ma = set(ma) - set(keys)
    unmatched_nfhs = {k for k, _ in nfhs} - set(keys)
    if unmatched_ma:
        raise DistrictTableError(f"Mission Antyodaya codes not in spine: {unmatched_ma}")
    if unmatched_nfhs:
        raise DistrictTableError(f"NFHS codes not in spine: {unmatched_nfhs}")

    pop_total = 0
    for r in rows:
        if not r["census_2011_district_code"]:
            continue
        label = f"Census 2011 {r['census_2011_name']} ({r['census_2011_district_code']})"
        total = parse_int(r["census_2011_population_total"], f"{label} total population")
        rural = parse_int(r["census_2011_population_rural"], f"{label} rural population")
        urban = parse_int(r["census_2011_population_urban"], f"{label} urban population")
        if rural + urban != total:
            raise DistrictTableError(
                f"{label}: rural + urban != total ({rural} + {urban} != {total})"
            )
        pop_total += total
    report["census_2011_population_sum"] = pop_total

    report["osm_records_in_table"] = sum(
        int(r["osm_mapped_charging_records"]) for r in rows if r["osm_mapped_charging_records"]
    )
    report["missing_cells"] = {
        col: sum(1 for r in rows if r[col] == "")
        for col in columns
        if any(r[col] == "" for r in rows)
    }


def dictionary_rows() -> list[dict[str, str]]:
    def entry(column, source, source_column, unit, period, definition):
        return {
            "column": column,
            "source": source,
            "source_column": source_column,
            "unit": unit,
            "period": period,
            "definition": definition,
        }

    rows = [
        entry(
            "lgd_district_code",
            "S06",
            "district_code",
            "code",
            "LGD snapshot",
            "Current LGD district code; join key",
        ),
        entry(
            "lgd_district_name",
            "S06",
            "district_name",
            "text",
            "LGD snapshot",
            "District name as listed in S06",
        ),
        entry(
            "census_2011_district_code",
            "S06",
            "census_2011_district_code",
            "code",
            "2011",
            "Census 2011 district code; blank where S06 gives 0",
        ),
        entry(
            "boundary_note",
            "derived",
            "",
            "text",
            "",
            "Documented boundary or naming mismatch for this district",
        ),
        entry(
            "census_2011_name",
            "S04",
            "Name (col E)",
            "text",
            "2011",
            "District name in the Census 2011 A-1 table",
        ),
        entry(
            "census_2011_population_total",
            "S04",
            "Population Persons (col K), Total row",
            "persons",
            "2011",
            "Census 2011 population, total",
        ),
        entry(
            "census_2011_population_rural",
            "S04",
            "Population Persons (col K), Rural row",
            "persons",
            "2011",
            "Census 2011 population, rural",
        ),
        entry(
            "census_2011_population_urban",
            "S04",
            "Population Persons (col K), Urban row",
            "persons",
            "2011",
            "Census 2011 population, urban",
        ),
        entry(
            "census_2011_households_total",
            "S04",
            "Number of households (col J), Total row",
            "households",
            "2011",
            "Census 2011 households",
        ),
        entry(
            "census_2011_area_sqkm",
            "S04",
            "Area (col N), Total row",
            "sq km",
            "2011",
            "Census 2011 district area",
        ),
        entry(
            "census_2011_density_per_sqkm",
            "S04",
            "Population per sq km (col O), Total row",
            "persons per sq km",
            "2011",
            "As published in S04, not recomputed",
        ),
        entry(
            "census_2011_villages_inhabited",
            "S04",
            "Number of villages Inhabited (col G), Total row",
            "count",
            "2011",
            "Inhabited villages",
        ),
        entry(
            "census_2011_towns",
            "S04",
            "Number of towns (col I), Total row",
            "count",
            "2011",
            "Towns",
        ),
        entry(
            "boundary_2011_name",
            "Census 2011 boundaries (datameet)",
            "DISTRICT",
            "text",
            "2011",
            "Polygon name used to assign OSM points",
        ),
        entry(
            "osm_mapped_charging_records",
            "S02 + Census 2011 boundaries",
            "amenity=charging_station features",
            "count of OSM records",
            "S02 retrieval date (not recorded in manifest)",
            "OSM charging-station records falling inside the 2011 district polygon. Mapped records only: "
            "not installed, operational or official charger counts; OSM coverage is incomplete and uneven",
        ),
    ]
    ma_defs = {
        "villages_surveyed": ("count of villages", "Villages surveyed in the district"),
        "tot_pop": ("persons", "Population of surveyed villages (rural only)"),
        "all_weather_road": ("count of villages", "Villages connected by an all-weather road"),
        "cc_road_full": (
            "count of villages",
            "Villages with internal cement-concrete roads, fully",
        ),
        "cc_road_partial": (
            "count of villages",
            "Villages with internal cement-concrete roads, partly",
        ),
        "cc_road_not": ("count of villages", "Villages without internal cement-concrete roads"),
        "pub_trans_bus": ("count of villages", "Villages with bus as public transport"),
        "pub_trans_no": ("count of villages", "Villages with no public transport"),
        "railway": ("count of villages", "Villages with a railway station"),
    }
    for col, (unit, definition) in ma_defs.items():
        rows.append(
            entry(
                f"ma2020_{col}",
                "S08",
                col,
                unit,
                "2020",
                definition + "; rural villages only, Gram Panchayat-reported",
            )
        )
    rows.append(
        entry(
            "ma2020_all_weather_road_share",
            "derived from S08",
            "all_weather_road / villages_surveyed",
            "fraction 0-1",
            "2020",
            "Share of surveyed villages with all-weather road connectivity; not a road-length or density measure",
        )
    )
    rows.append(
        entry(
            "ma2020_district_name", "S08", "district_name", "text", "2020", "District name in S08"
        )
    )
    for year, label in NFHS_ROUNDS.items():
        for ind, unit in NFHS_INDICATORS.items():
            rows.append(
                entry(
                    f"nfhs_{label}_{ind}",
                    "S07",
                    ind,
                    unit,
                    year,
                    f"NFHS sample-survey estimate, round {year}; no confidence interval in source",
                )
            )
    rows.append(
        entry(
            "nfhs_district_name",
            "S07",
            "district_name",
            "text",
            "latest round present",
            "District name in S07",
        )
    )
    return rows


# ---------------------------------------------------------------- output


def to_csv_bytes(columns: list[str], rows: list[dict[str, str]]) -> bytes:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def write_if_unchanged(path: Path, data: bytes, force: bool) -> str:
    if path.exists():
        if path.read_bytes() == data:
            return "unchanged"
        if not force:
            raise SystemExit(
                f"{path} exists with different content; rerun with --force to replace it"
            )
    path.write_bytes(data)
    return "written"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true", help="replace outputs whose content differs"
    )
    args = parser.parse_args(argv)

    columns, rows, report = build()
    table = to_csv_bytes(columns, rows)
    dictionary = dictionary_rows()
    dict_bytes = to_csv_bytes(list(dictionary[0]), dictionary)
    if [d["column"] for d in dictionary] != columns:
        raise DistrictTableError("Dictionary columns do not match table columns")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    status_table = write_if_unchanged(OUT_TABLE, table, args.force)
    status_dict = write_if_unchanged(OUT_DICT, dict_bytes, args.force)

    report["output_rows"] = len(rows)
    report["output_columns"] = len(columns)
    report["table_sha256"] = hashlib.sha256(table).hexdigest()
    report["dictionary_sha256"] = hashlib.sha256(dict_bytes).hexdigest()
    report["table_status"] = status_table
    report["dictionary_status"] = status_dict
    json.dump(report, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
