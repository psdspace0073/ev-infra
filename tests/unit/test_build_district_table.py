"""Tests for evinfra.analysis.build_district_table using small temporary fixtures."""

from __future__ import annotations

import copy
import csv
import json
import os
import struct
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import pytest

from evinfra.analysis import build_district_table as bdt

# ---------------------------------------------------------------- fixture writers


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(path: Path, rows: list[dict[str, str]]) -> None:
    """Minimal one-sheet workbook. Codes with leading zeros are stored as shared strings."""
    shared: list[str] = []
    xml_rows = []
    for r, row in enumerate(rows, start=1):
        cells = []
        for col, value in row.items():
            ref = f"{col}{r}"
            numeric = value.replace(".", "", 1).isdigit() and not (
                len(value) > 1 and value.startswith("0")
            )
            if numeric:
                cells.append(f'<c r="{ref}"><v>{value}</v></c>')
            else:
                shared.append(value)
                cells.append(f'<c r="{ref}" t="s"><v>{len(shared) - 1}</v></c>')
        xml_rows.append(f'<row r="{r}">{"".join(cells)}</row>')
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    sheet = f'<worksheet xmlns="{ns}"><sheetData>{"".join(xml_rows)}</sheetData></worksheet>'
    sst = f'<sst xmlns="{ns}">' + "".join(f"<si><t>{escape(s)}</t></si>" for s in shared) + "</sst>"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/sharedStrings.xml", sst)
        z.writestr("xl/worksheets/sheet1.xml", sheet)


DBF_FIELDS = [
    ("DISTRICT", "C", 28),
    ("ST_NM", "C", 24),
    ("ST_CEN_CD", "N", 9),
    ("DT_CEN_CD", "N", 9),
    ("censuscode", "N", 14),
]


def write_shapefile_zip(path: Path, records: list[tuple[dict[str, str], list]]) -> None:
    """Write 2011_Dist.{shp,shx,dbf} with Polygon records into a zip."""
    shp_body, shx_body = b"", b""
    offset = 100
    all_x, all_y = [], []
    for recno, (_, rings) in enumerate(records, start=1):
        pts = [p for ring in rings for p in ring]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        all_x += xs
        all_y += ys
        parts, start = [], 0
        for ring in rings:
            parts.append(start)
            start += len(ring)
        flat = [c for p in pts for c in p]
        content = (
            struct.pack("<i", 5)
            + struct.pack("<4d", min(xs), min(ys), max(xs), max(ys))
            + struct.pack("<2i", len(parts), len(pts))
            + struct.pack(f"<{len(parts)}i", *parts)
            + struct.pack(f"<{len(flat)}d", *flat)
        )
        shp_body += struct.pack(">2i", recno, len(content) // 2) + content
        shx_body += struct.pack(">2i", offset // 2, len(content) // 2)
        offset += 8 + len(content)

    def header(file_len: int) -> bytes:
        return (
            struct.pack(">7i", 9994, 0, 0, 0, 0, 0, file_len // 2)
            + struct.pack("<2i", 1000, 5)
            + struct.pack("<4d", min(all_x), min(all_y), max(all_x), max(all_y))
            + struct.pack("<4d", 0, 0, 0, 0)
        )

    shp = header(100 + len(shp_body)) + shp_body
    shx = header(100 + len(shx_body)) + shx_body

    header_len = 32 + 32 * len(DBF_FIELDS) + 1
    record_len = 1 + sum(length for _, _, length in DBF_FIELDS)
    dbf = struct.pack("<B3BIHH20x", 3, 126, 10, 24, len(records), header_len, record_len)
    for name, ftype, length in DBF_FIELDS:
        dbf += name.encode().ljust(11, b"\0") + ftype.encode() + b"\0" * 4
        dbf += bytes([length, 0]) + b"\0" * 14
    dbf += b"\r"
    for attrs, _ in records:
        dbf += b" "
        for name, ftype, length in DBF_FIELDS:
            value = attrs[name]
            dbf += (value.ljust(length) if ftype == "C" else value.rjust(length)).encode()
    dbf += b"\x1a"

    with zipfile.ZipFile(path, "w") as z:
        z.writestr("2011_Dist.shp", shp)
        z.writestr("2011_Dist.shx", shx)
        z.writestr("2011_Dist.dbf", dbf)


def square(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    return [(x0, y0), (x0, y1), (x1, y1), (x1, y0), (x0, y0)]


# ---------------------------------------------------------------- default fixture data
#
# Karnataka (state 29): Bagalkote (524 / census 556), Ballari (528 / 565),
# Ramanagara a.k.a. Bengaluru South (631 / 584), Vijayanagar (738 / no 2011 code).
# One Andhra Pradesh district (state 28) checks that other states are filtered out.


def lgd(name, code, c2011, state="29", state_name="Karnataka"):
    return {
        "id": code,
        "district_name": name,
        "district_code": code,
        "census_2001_district_code": "None",
        "census_2011_district_code": c2011,
        "state_name": state_name,
        "state_code": state,
    }


def census_rows(state, code, name, total, rural, urban, kind="DISTRICT", sub="00000"):
    rows = []
    for tru, pop in (("Total", total), ("Rural", rural), ("Urban", urban)):
        rows.append(
            {
                "A": state,
                "B": code,
                "C": sub,
                "D": kind,
                "E": name,
                "F": tru,
                "G": "100" if tru != "Urban" else "0",
                "I": "5" if tru != "Rural" else "0",
                "J": str(pop // 4),
                "K": str(pop),
                "N": "1000.5",
                "O": str(pop // 1000),
            }
        )
    return rows


def nfhs(code, name, year, state="29", **values):
    row = {
        "id": f"{code}-{year}",
        "year": year,
        "state_name": "Karnataka" if state == "29" else "Andhra Pradesh",
        "state_code": state,
        "district_name": name,
        "district_code": code,
    }
    for i, ind in enumerate(bdt.NFHS_INDICATORS):
        row[ind] = values.get(ind, str(10 + i))
    return row


def ma(code, name, state="29", **values):
    row = {
        "id": code,
        "year": "2020",
        "state_name": "Karnataka" if state == "29" else "Andhra Pradesh",
        "state_code": state,
        "district_name": name,
        "district_code": code,
    }
    defaults = {
        "villages_surveyed": "200",
        "tot_pop": "500000",
        "all_weather_road": "150",
        "cc_road_full": "20",
        "cc_road_partial": "100",
        "cc_road_not": "80",
        "pub_trans_bus": "180",
        "pub_trans_no": "20",
        "railway": "3",
    }
    for col in bdt.MA_COLUMNS:
        row[col] = values.get(col, defaults[col])
    return row


def boundary(name, c2011, state="29"):
    return {
        "DISTRICT": name,
        "ST_NM": "Karnataka" if state == "29" else "Andhra Pradesh",
        "ST_CEN_CD": state,
        "DT_CEN_CD": "1",
        "censuscode": c2011,
    }


def point(x, y):
    return {
        "type": "Feature",
        "properties": {"amenity": "charging_station"},
        "geometry": {"type": "Point", "coordinates": [x, y]},
    }


def default_data() -> dict:
    return {
        "s06": [
            lgd("Bagalkote", "524", "556"),
            lgd("Ballari", "528", "565"),
            lgd("Ramanagara", "631", "584"),
            lgd("Vijayanagar", "738", "0"),
            lgd("Anantapur", "502", "553", state="28", state_name="Andhra Pradesh"),
        ],
        "s04": [
            {"A": "State  Code", "B": "District Code", "E": "Name", "F": "Total/Rural/Urban"},
            *census_rows("29", "000", "KARNATAKA", 7000, 4000, 3000, kind="STATE"),
            *census_rows("29", "556", "Bagalkot", 3000, 2000, 1000),
            *census_rows(
                "29", "556", "Some taluk", 900, 600, 300, kind="SUB-DISTRICT", sub="05555"
            ),
            *census_rows("29", "565", "Bellary", 2500, 1500, 1000),
            *census_rows("29", "584", "Ramanagara", 1500, 500, 1000),
            *census_rows("28", "553", "Anantapur", 4000, 3000, 1000),
        ],
        "s07": [
            nfhs("524", "Bagalkote", "2015-16", population_60plus="", women_literate="None"),
            nfhs("524", "Bagalkote", "2019-21"),
            nfhs("524", "Bagalkote", "2023-24"),
            nfhs("528", "Ballari", "2019-21"),
            nfhs("631", "Bengaluru South", "2023-24"),
            nfhs("502", "Anantapur", "2019-21", state="28"),
        ],
        "s08": [
            ma("524", "Bagalkot"),
            ma("528", "Ballari"),
            ma("631", "Ramanagara", villages_surveyed="0", all_weather_road="0", cc_road_full=""),
            ma("502", "Anantapur", state="28"),
        ],
        "boundaries": [
            (boundary("Bagalkot", "556"), [square(0, 0, 1, 1)]),
            (boundary("Bellary", "565"), [square(1, 0, 2, 1)]),
            (boundary("Ramanagara", "584"), [square(0, 1, 1, 2)]),
            (boundary("Anantapur", "553", state="28"), [square(5, 5, 6, 6)]),
        ],
        "s02": [point(0.5, 0.5), point(1.5, 0.25), point(1.5, 0.75), point(10, 10)],
    }


def install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: dict) -> Path:
    """Write fixture files and point the builder's module paths at them."""
    raw = tmp_path / "raw"
    raw.mkdir(exist_ok=True)
    paths = {
        "S06": raw / "s06.csv",
        "S04": raw / "s04.xlsx",
        "S07": raw / "s07.csv",
        "S08": raw / "s08.csv",
        "S02": raw / "s02.geojson",
        "BOUNDARIES": raw / "bounds.zip",
    }
    write_csv(paths["S06"], data["s06"])
    write_xlsx(paths["S04"], data["s04"])
    write_csv(paths["S07"], data["s07"])
    write_csv(paths["S08"], data["s08"])
    paths["S02"].write_text(
        json.dumps({"type": "FeatureCollection", "features": data["s02"]}), encoding="utf-8"
    )
    write_shapefile_zip(paths["BOUNDARIES"], data["boundaries"])
    for name, path in paths.items():
        monkeypatch.setattr(bdt, name, path)
    out = tmp_path / "processed"
    monkeypatch.setattr(bdt, "OUT_DIR", out)
    monkeypatch.setattr(bdt, "OUT_TABLE", out / "table.csv")
    monkeypatch.setattr(bdt, "OUT_DICT", out / "dictionary.csv")
    return out


@pytest.fixture
def data() -> dict:
    return default_data()


def build_rows(tmp_path, monkeypatch, data):
    install(tmp_path, monkeypatch, data)
    columns, rows, report = bdt.build()
    return columns, {r["lgd_district_code"]: r for r in rows}, report


# ---------------------------------------------------------------- joins and schema


def test_joins_karnataka_districts_on_official_codes(tmp_path, monkeypatch, data):
    _, rows, report = build_rows(tmp_path, monkeypatch, data)

    assert list(rows) == ["524", "528", "631", "738"]
    assert report["spine_districts"] == 4
    assert report["census_2011_district_rows"] == 3
    assert report["nfhs_karnataka_rows"] == 5
    assert report["mission_antyodaya_karnataka_rows"] == 3

    bagalkote = rows["524"]
    assert bagalkote["census_2011_district_code"] == "556"
    assert bagalkote["census_2011_name"] == "Bagalkot"
    assert bagalkote["census_2011_population_total"] == "3000"
    assert bagalkote["census_2011_population_rural"] == "2000"
    assert bagalkote["census_2011_population_urban"] == "1000"
    assert bagalkote["census_2011_households_total"] == "750"
    assert bagalkote["census_2011_area_sqkm"] == "1000.5"
    assert bagalkote["census_2011_villages_inhabited"] == "100"
    assert bagalkote["census_2011_towns"] == "5"
    assert bagalkote["boundary_2011_name"] == "Bagalkot"
    assert bagalkote["ma2020_district_name"] == "Bagalkot"
    assert bagalkote["ma2020_all_weather_road"] == "150"
    assert bagalkote["ma2020_all_weather_road_share"] == "0.7500"
    assert bagalkote["nfhs_2019_21_population_under_15"] == "10"
    assert bagalkote["nfhs_district_name"] == "Bagalkote"


def test_output_schema_matches_dictionary(tmp_path, monkeypatch, data):
    columns, rows, _ = build_rows(tmp_path, monkeypatch, data)

    assert len(columns) == len(set(columns))
    assert columns[:4] == [
        "lgd_district_code",
        "lgd_district_name",
        "census_2011_district_code",
        "boundary_note",
    ]
    for label in ("2015_16", "2019_21", "2023_24"):
        for ind in bdt.NFHS_INDICATORS:
            assert f"nfhs_{label}_{ind}" in columns
    assert [d["column"] for d in bdt.dictionary_rows()] == columns
    assert all(list(r) == columns for r in rows.values())


def test_other_states_are_excluded(tmp_path, monkeypatch, data):
    _, rows, report = build_rows(tmp_path, monkeypatch, data)

    assert "502" not in rows
    assert report["census_2011_population_sum"] == 3000 + 2500 + 1500
    assert report["boundary_polygons"] == 3


# ---------------------------------------------------------------- duplicate and missing codes


def test_duplicate_lgd_code_in_spine_raises(tmp_path, monkeypatch, data):
    data["s06"].append(lgd("Bagalkote again", "524", "556"))
    install(tmp_path, monkeypatch, data)
    with pytest.raises(ValueError, match="Duplicate LGD district codes"):
        bdt.build()


def test_duplicate_census_row_raises(tmp_path, monkeypatch, data):
    data["s04"] += census_rows("29", "556", "Bagalkot", 3000, 2000, 1000)
    install(tmp_path, monkeypatch, data)
    with pytest.raises(ValueError, match="Duplicate Census 2011 total row for district 556"):
        bdt.build()


def test_duplicate_nfhs_row_raises(tmp_path, monkeypatch, data):
    data["s07"].append(nfhs("524", "Bagalkote", "2019-21"))
    install(tmp_path, monkeypatch, data)
    with pytest.raises(ValueError, match="Duplicate NFHS row"):
        bdt.build()


def test_duplicate_mission_antyodaya_row_raises(tmp_path, monkeypatch, data):
    data["s08"].append(ma("528", "Ballari"))
    install(tmp_path, monkeypatch, data)
    with pytest.raises(ValueError, match="Duplicate Mission Antyodaya row 528"):
        bdt.build()


def test_spine_census_code_without_census_row_raises(tmp_path, monkeypatch, data):
    data["s06"][0]["census_2011_district_code"] = "999"
    install(tmp_path, monkeypatch, data)
    with pytest.raises(ValueError, match="No Census 2011 row for code 999"):
        bdt.build()


def test_census_district_missing_from_spine_is_rejected(tmp_path, monkeypatch, data):
    data["s04"] += census_rows("29", "570", "Chikmagalur", 1000, 800, 200)
    install(tmp_path, monkeypatch, data)
    with pytest.raises(bdt.DistrictTableError, match="census-only \\{'570'\\}"):
        bdt.build()


def test_source_code_missing_from_spine_is_rejected(tmp_path, monkeypatch, data):
    data["s08"].append(ma("599", "Unknown district"))
    install(tmp_path, monkeypatch, data)
    with pytest.raises(bdt.DistrictTableError, match="Mission Antyodaya codes not in spine"):
        bdt.build()


def test_nfhs_code_missing_from_spine_is_rejected(tmp_path, monkeypatch, data):
    data["s07"].append(nfhs("599", "Unknown district", "2019-21"))
    install(tmp_path, monkeypatch, data)
    with pytest.raises(bdt.DistrictTableError, match="NFHS codes not in spine"):
        bdt.build()


def test_census_code_without_boundary_polygon_raises(tmp_path, monkeypatch, data):
    data["boundaries"] = [b for b in data["boundaries"] if b[0]["censuscode"] != "584"]
    install(tmp_path, monkeypatch, data)
    with pytest.raises(ValueError, match="No 2011 boundary polygon for code 584"):
        bdt.build()


# ---------------------------------------------------------------- boundary mismatches


def test_vijayanagar_gets_no_allocated_values(tmp_path, monkeypatch, data):
    columns, rows, _ = build_rows(tmp_path, monkeypatch, data)
    vijayanagar = rows["738"]

    identity = {"lgd_district_code", "lgd_district_name", "boundary_note"}
    for col in columns:
        if col not in identity:
            assert vijayanagar[col] == "", col
    assert vijayanagar["lgd_district_name"] == "Vijayanagar"
    assert "Ballari" in vijayanagar["boundary_note"]
    assert "Nothing allocated" in vijayanagar["boundary_note"]


def test_ballari_keeps_unsplit_values_and_is_flagged(tmp_path, monkeypatch, data):
    _, rows, _ = build_rows(tmp_path, monkeypatch, data)
    ballari = rows["528"]

    assert ballari["census_2011_population_total"] == "2500"
    assert ballari["osm_mapped_charging_records"] == "2"
    assert "Vijayanagar" in ballari["boundary_note"]


def test_bengaluru_south_keeps_source_names_and_is_flagged(tmp_path, monkeypatch, data):
    _, rows, _ = build_rows(tmp_path, monkeypatch, data)
    row = rows["631"]

    assert row["lgd_district_name"] == "Ramanagara"
    assert row["census_2011_name"] == "Ramanagara"
    assert row["ma2020_district_name"] == "Ramanagara"
    assert row["nfhs_district_name"] == "Bengaluru South"
    assert row["nfhs_2023_24_population_under_15"] == "10"
    assert "Ramanagara" in row["boundary_note"]
    assert rows["524"]["boundary_note"] == ""


# ---------------------------------------------------------------- point assignment


POLYGONS = [
    {"census_code": "A", "bbox": (0, 0, 1, 1), "rings": [square(0, 0, 1, 1)]},
    {"census_code": "B", "bbox": (1, 0, 2, 1), "rings": [square(1, 0, 2, 1)]},
]


def test_point_inside_exactly_one_polygon():
    assert bdt.assign_points([(0.5, 0.5), (1.5, 0.5)], POLYGONS) == ["A", "B"]


def test_point_outside_all_polygons_is_unassigned():
    assert bdt.assign_points([(3.0, 0.5), (0.5, -0.1)], POLYGONS) == [None, None]


def test_point_on_shared_edge_is_assigned_once():
    assert bdt.assign_points([(1.0, 0.5)], POLYGONS) == ["B"]


def test_point_in_overlapping_polygons_raises():
    overlapping = POLYGONS + [
        {
            "census_code": "C",
            "bbox": (0.25, 0.25, 0.75, 0.75),
            "rings": [square(0.25, 0.25, 0.75, 0.75)],
        }
    ]
    with pytest.raises(ValueError, match="several districts"):
        bdt.assign_points([(0.5, 0.5)], overlapping)


def test_point_in_polygon_hole_is_outside():
    with_hole = [
        {
            "census_code": "A",
            "bbox": (0, 0, 3, 3),
            "rings": [square(0, 0, 3, 3), square(1, 1, 2, 2)],
        }
    ]
    assert bdt.assign_points([(1.5, 1.5), (0.5, 0.5)], with_hole) == [None, "A"]


def test_build_counts_assigned_points_and_reports_unassigned(tmp_path, monkeypatch, data):
    _, rows, report = build_rows(tmp_path, monkeypatch, data)

    assert report["osm_features"] == 4
    assert report["osm_assigned"] == 3
    assert report["osm_unassigned"] == 1
    assert report["osm_records_in_table"] == 3
    assert rows["524"]["osm_mapped_charging_records"] == "1"
    assert rows["528"]["osm_mapped_charging_records"] == "2"


def test_overlapping_boundaries_abort_the_build(tmp_path, monkeypatch, data):
    data["boundaries"][2] = (boundary("Ramanagara", "584"), [square(0, 0, 1, 2)])
    install(tmp_path, monkeypatch, data)
    with pytest.raises(ValueError, match="several districts"):
        bdt.build()


# ---------------------------------------------------------------- missing values


def test_missing_indicators_stay_missing(tmp_path, monkeypatch, data):
    _, rows, _ = build_rows(tmp_path, monkeypatch, data)

    bagalkote = rows["524"]
    assert bagalkote["nfhs_2015_16_population_60plus"] == ""
    assert bagalkote["nfhs_2015_16_women_literate"] == ""
    assert bagalkote["nfhs_2015_16_population_under_15"] == "10"

    ballari = rows["528"]
    for ind in bdt.NFHS_INDICATORS:
        assert ballari[f"nfhs_2015_16_{ind}"] == ""
        assert ballari[f"nfhs_2023_24_{ind}"] == ""
        assert ballari[f"nfhs_2019_21_{ind}"] != ""

    ramanagara = rows["631"]
    assert ramanagara["ma2020_cc_road_full"] == ""
    assert ramanagara["ma2020_villages_surveyed"] == "0"
    assert ramanagara["ma2020_all_weather_road_share"] == ""


def test_district_with_polygon_but_no_points_counts_zero_records(tmp_path, monkeypatch, data):
    _, rows, _ = build_rows(tmp_path, monkeypatch, data)

    assert rows["631"]["osm_mapped_charging_records"] == "0"
    assert rows["738"]["osm_mapped_charging_records"] == ""


# ---------------------------------------------------------------- determinism and writing


def test_output_is_deterministic_and_independent_of_input_order(tmp_path, monkeypatch, data):
    (tmp_path / "a").mkdir()
    install(tmp_path / "a", monkeypatch, data)
    first = bdt.to_csv_bytes(*bdt.build()[:2])
    second = bdt.to_csv_bytes(*bdt.build()[:2])
    assert first == second

    shuffled = copy.deepcopy(data)
    shuffled["s06"].reverse()
    shuffled["s07"].reverse()
    shuffled["s08"].reverse()
    shuffled["s02"].reverse()
    header, body = shuffled["s04"][0], shuffled["s04"][1:]
    shuffled["s04"] = [header, *reversed(body)]
    (tmp_path / "b").mkdir()
    install(tmp_path / "b", monkeypatch, shuffled)
    assert bdt.to_csv_bytes(*bdt.build()[:2]) == first


def test_main_writes_then_reports_unchanged(tmp_path, monkeypatch, data, capsys):
    out = install(tmp_path, monkeypatch, data)

    assert bdt.main([]) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["table_status"] == "written"
    assert first["dictionary_status"] == "written"
    table_bytes = (out / "table.csv").read_bytes()

    assert bdt.main([]) == 0
    second = json.loads(capsys.readouterr().out)
    assert second["table_status"] == "unchanged"
    assert second["table_sha256"] == first["table_sha256"]
    assert (out / "table.csv").read_bytes() == table_bytes


def test_main_refuses_to_overwrite_differing_output_without_force(
    tmp_path, monkeypatch, data, capsys
):
    out = install(tmp_path, monkeypatch, data)
    out.mkdir()
    (out / "table.csv").write_bytes(b"hand-edited\n")

    with pytest.raises(SystemExit, match="--force"):
        bdt.main([])
    assert (out / "table.csv").read_bytes() == b"hand-edited\n"

    assert bdt.main(["--force"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["table_status"] == "written"
    assert (out / "table.csv").read_bytes() != b"hand-edited\n"
    assert (out / "table.csv").read_bytes().startswith(b"lgd_district_code,")


# ---------------------------------------------------------------- malformed inputs


def census_row(data, code, row_type):
    return next(
        r
        for r in data["s04"]
        if r.get("B") == code and r.get("D") == "DISTRICT" and r.get("F") == row_type
    )


def test_rural_plus_urban_mismatch_raises(tmp_path, monkeypatch, data):
    census_row(data, "556", "Rural")["K"] = "2100"
    install(tmp_path, monkeypatch, data)
    with pytest.raises(
        bdt.DistrictTableError,
        match=r"Bagalkot \(556\): rural \+ urban != total \(2100 \+ 1000 != 3000\)",
    ):
        bdt.build()


@pytest.mark.parametrize("row_type", ["Rural", "Urban", "Total"])
def test_missing_census_row_type_raises(tmp_path, monkeypatch, data, row_type):
    data["s04"].remove(census_row(data, "565", row_type))
    install(tmp_path, monkeypatch, data)
    with pytest.raises(
        bdt.DistrictTableError, match=rf"district 565 \(Bellary\) has no {row_type} row"
    ):
        bdt.build()


def test_unexpected_census_row_type_raises(tmp_path, monkeypatch, data):
    census_row(data, "565", "Urban")["F"] = "Peri-urban"
    install(tmp_path, monkeypatch, data)
    with pytest.raises(bdt.DistrictTableError, match="unexpected Total/Rural/Urban value"):
        bdt.build()


def test_blank_census_population_raises(tmp_path, monkeypatch, data):
    del census_row(data, "556", "Total")["K"]
    install(tmp_path, monkeypatch, data)
    with pytest.raises(
        bdt.DistrictTableError,
        match=r"Bagalkot \(556\) total population: expected an integer, got ''",
    ):
        bdt.build()


def test_na_token_is_treated_as_missing(tmp_path, monkeypatch, data):
    data["s07"][1]["population_electricity"] = "NA"
    data["s08"][1]["railway"] = "NA"
    _, rows, _ = build_rows(tmp_path, monkeypatch, data)

    assert rows["524"]["nfhs_2019_21_population_electricity"] == ""
    assert rows["524"]["nfhs_2019_21_population_under_15"] == "10"
    assert rows["528"]["ma2020_railway"] == ""
    assert rows["528"]["ma2020_pub_trans_bus"] == "180"


@pytest.mark.parametrize("value", ["", "NA", "None", "  "])
def test_blank_villages_surveyed_raises(tmp_path, monkeypatch, data, value):
    data["s08"][1]["villages_surveyed"] = value
    install(tmp_path, monkeypatch, data)
    with pytest.raises(
        bdt.DistrictTableError, match=r"villages_surveyed is blank for district 528 \(Ballari\)"
    ):
        bdt.build()


def test_non_numeric_villages_surveyed_raises(tmp_path, monkeypatch, data):
    data["s08"][1]["villages_surveyed"] = "two hundred"
    install(tmp_path, monkeypatch, data)
    with pytest.raises(bdt.DistrictTableError, match="villages_surveyed for district 528 is not"):
        bdt.build()


def test_blank_all_weather_road_leaves_share_missing(tmp_path, monkeypatch, data):
    data["s08"][1]["all_weather_road"] = ""
    _, rows, _ = build_rows(tmp_path, monkeypatch, data)

    assert rows["528"]["ma2020_villages_surveyed"] == "200"
    assert rows["528"]["ma2020_all_weather_road"] == ""
    assert rows["528"]["ma2020_all_weather_road_share"] == ""


# ---------------------------------------------------------------- optimized Python

OPTIMIZED_SCRIPT = textwrap.dedent(
    """
    import json, sys
    from pathlib import Path
    from evinfra.analysis import build_district_table as bdt

    print("optimize", sys.flags.optimize)
    for name, path in json.loads(sys.argv[1]).items():
        setattr(bdt, name, Path(path))
    try:
        bdt.build()
    except bdt.DistrictTableError as exc:
        print("REJECTED", exc)
        sys.exit(3)
    print("ACCEPTED")
    """
)


def run_optimized(tmp_path, monkeypatch, data):
    install(tmp_path, monkeypatch, data)
    paths = {
        name: str(getattr(bdt, name)) for name in ("S02", "S04", "S06", "S07", "S08", "BOUNDARIES")
    }
    src = str(Path(bdt.__file__).resolve().parents[2])
    env = {**os.environ, "PYTHONPATH": src}
    return subprocess.run(
        [sys.executable, "-O", "-c", OPTIMIZED_SCRIPT, json.dumps(paths)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


def test_valid_inputs_build_under_optimized_python(tmp_path, monkeypatch, data):
    result = run_optimized(tmp_path, monkeypatch, data)

    assert "optimize 1" in result.stdout
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ACCEPTED" in result.stdout


def test_join_validation_runs_under_optimized_python(tmp_path, monkeypatch, data):
    data["s04"] += census_rows("29", "570", "Chikmagalur", 1000, 800, 200)
    result = run_optimized(tmp_path, monkeypatch, data)

    assert "optimize 1" in result.stdout
    assert result.returncode == 3, result.stdout + result.stderr
    assert "census-only {'570'}" in result.stdout


def test_population_validation_runs_under_optimized_python(tmp_path, monkeypatch, data):
    census_row(data, "556", "Rural")["K"] = "2100"
    result = run_optimized(tmp_path, monkeypatch, data)

    assert "optimize 1" in result.stdout
    assert result.returncode == 3, result.stdout + result.stderr
    assert "rural + urban != total" in result.stdout
