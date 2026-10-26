"""Tests for the VAHAN dashboard fetcher, official-document fetcher, RTO-district grouping
check, S35 class table and S32 reconciliation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from test_build_district_table import write_xlsx

from evinfra.analysis import build_ka_ev_class_rto_month as cls
from evinfra.analysis import reconcile_ka_registration_totals as rec
from evinfra.analysis import verify_rto_district_grouping as grp
from evinfra.ingestion import fetch_official_documents as docs
from evinfra.ingestion import fetch_vahan_dashboard as vd

MONTH_COLS = "CDEFGHIJKLMN"


def vahan_export(path: Path, title: str, months: list[str], rows: dict[str, list[int]]) -> Path:
    """Workbook laid out like a VAHAN 'Month Wise' export."""
    total = MONTH_COLS[len(months)] if len(months) < 12 else "O"
    sheet = [
        {"A": title},
        {"A": "S No", "B": "Vehicle Class", "C": "Month Wise", total: "TOTAL"},
        {},
        {"A": "-", "B": "-", **dict(zip(MONTH_COLS, months, strict=False)), total: "-"},
    ]
    for i, (name, values) in enumerate(rows.items(), start=1):
        row = {"A": str(i), "B": name}
        row.update({MONTH_COLS[j]: f"{v:,}" for j, v in enumerate(values)})
        row[total] = f"{sum(values):,}"
        sheet.append(row)
    write_xlsx(path, sheet)
    return path


# ---------------------------------------------------------------- VAHAN dashboard fetcher


def test_parse_offices_and_titles():
    options = [
        ("-1", "All Vahan4 Running Office(68/68)"),
        ("45", "HUNSUR  ARTO - KA45( 11-JUL-2018 )"),
        ("57", "STU AND AUTORIKSHAW,  SHANTHINAGAR RTO - KA57( 26-APR-2021 )"),
    ]
    offices = vd.parse_offices(options)
    assert [o["rto_code"] for o in offices] == ["KA45", "KA57"]
    assert offices[0] == {
        "value": "45",
        "rto_code": "KA45",
        "office_name": "HUNSUR ARTO",
        "vahan4_since": "11-JUL-2018",
    }
    vd.check_title(
        "Vehicle Class Month Wise Data  of HUNSUR  ARTO - KA45 , Karnataka (2026)", "KA45", "2026"
    )
    with pytest.raises(vd.DashboardError, match="year"):
        vd.check_title("... - KA45 , Karnataka (2025)", "KA45", "2026")
    with pytest.raises(vd.DashboardError, match="office"):
        vd.check_title("... - KA4 , Karnataka (2026)", "KA45", "2026")


def test_tasks_cover_jobs():
    offices = [
        {"value": "45", "rto_code": "KA45"},
        {"value": "46", "rto_code": "KA46"},
        {"value": "57", "rto_code": "KA57"},
        {"value": "1", "rto_code": "KA1"},
    ]
    assert len(vd.tasks("bev_class_month", offices)) == 4 * len(vd.YEARS)
    gap = vd.tasks("allfuel_class_month", offices)
    assert {(o["rto_code"], y) for o, y in gap} >= {("KA45", "2025"), ("KA57", "2021")}
    assert all(o["rto_code"] != "KA1" for o, _ in gap)
    assert vd.tasks("state_class_month", offices) == [(None, "2025"), (None, "2026")]


def test_form_parsing():
    page = (
        '<input type="hidden" name="masterLayout_formlogin" value="masterLayout_formlogin" />'
        '<input type="hidden" name="javax.faces.ViewState" id="v" value="abc:1" />'
        '<select id="yaxisVar_input" name="yaxisVar_input"><option value="Vehicle Class" '
        'selected="selected">Vehicle Class</option><option value="Fuel">Fuel</option></select>'
        '<input id="fuel:0" name="fuel" type="checkbox" value="4" /></div><div></div>'
        '<label for="fuel:0">ELECTRIC(BOV)</label>'
    )
    fields = vd.form_fields(page)
    assert fields["yaxisVar_input"] == "Vehicle Class"
    assert "javax.faces.ViewState" not in fields
    assert vd.view_state(page) == "abc:1"
    assert vd.fuel_labels(page) == {"4": "ELECTRIC(BOV)"}


def test_xlsx_title(tmp_path):
    path = vahan_export(
        tmp_path / "x.xlsx", "Fuel Month Wise Data  of Karnataka (2022)", ["JAN"], {"PETROL": [5]}
    )
    assert vd.xlsx_title(path.read_bytes()) == "Fuel Month Wise Data  of Karnataka (2022)"


# ---------------------------------------------------------------- official documents


def test_save_never_overwrites(tmp_path, monkeypatch):
    payload = {"data": b"%PDF-1"}
    monkeypatch.setattr(
        docs,
        "fetch",
        lambda url: (
            payload["data"],
            {
                "final_url": url,
                "http_status": 200,
                "content_type": "application/pdf",
                "last_modified": None,
            },
        ),
    )
    first = docs.save("S99", "k", "https://example.gov.in/a.pdf", "S99_a.pdf", raw=tmp_path)
    assert first["status"] == "written"
    manifest = json.loads((tmp_path / "S99_a.pdf.manifest.json").read_text(encoding="utf-8"))
    assert manifest["sha256"] == hashlib.sha256(b"%PDF-1").hexdigest()
    assert (
        docs.save("S99", "k", "https://example.gov.in/a.pdf", "S99_a.pdf", raw=tmp_path)["status"]
        == "unchanged"
    )
    payload["data"] = b"%PDF-2"
    with pytest.raises(SystemExit, match="not overwritten"):
        docs.save("S99", "k", "https://example.gov.in/a.pdf", "S99_a.pdf", raw=tmp_path)
    assert (tmp_path / "S99_a.pdf").read_bytes() == b"%PDF-1"


def test_document_list_is_consistent():
    names = [d[3] for d in docs.DOCUMENTS]
    assert len(names) == len(set(names))
    assert all(n.startswith(d[0] + "_") for d, n in zip(docs.DOCUMENTS, names, strict=True))


# ---------------------------------------------------------------- RTO-district grouping


def office(stock, new):
    return {"name": "X", "stock_2021": stock, "new_2021_22": new, "stock_2022": stock + new}


@pytest.fixture
def grouping(monkeypatch):
    monkeypatch.setattr(
        grp,
        "TABLE27_ROWS",
        {1: ("KA1", None), 2: ("KA2", None), 3: ("KA3", None), 4: ("KA4", None)},
    )
    offices = {1: office(100, 10), 2: office(50, 5), 3: office(70, 7), 4: office(30, 3)}
    stock = {"525": 150 + 9, "542": 70, "630": 30}  # 9 = office not in Table 27
    new = {"525": 15 + 2, "542": 7, "630": 3}
    return offices, stock, new


def xw(code, lgd, status="verified_official"):
    return {"rto_code_vahan": code, "lgd_district_code": lgd, "status": status}


def test_grouping_exact_and_combined(grouping):
    offices, stock, new = grouping
    crosswalk = [
        xw("KA1", "525"),
        xw("KA2", "525"),
        xw("KA57", "525"),
        xw("KA3", "542;630", "verified_official_combined"),
        xw("KA4", "542;630", "verified_official_combined"),
    ]
    result = grp.check(offices, stock, new, crosswalk, {"KA57": 2})
    assert result["units_matched"] == result["units_total"] == 2
    assert result["units"]["525"]["stock_residual"] == 9
    assert result["units"]["542;630"]["report_columns"] == ["542", "630"]
    assert result["table28_minus_table27_stock"] == 9
    assert result["table27_offices_unassigned"] == []


def test_grouping_detects_wrong_assignment(grouping):
    offices, stock, new = grouping
    crosswalk = [
        xw("KA1", "525"),
        xw("KA2", "525"),
        xw("KA57", "525"),
        xw("KA3", "542"),
        xw("KA4", "630"),
    ]
    result = grp.check(offices, stock, new, crosswalk, {"KA57": 2})
    assert result["units"]["542"]["exact_match"] and result["units"]["630"]["exact_match"]
    crosswalk[3], crosswalk[4] = xw("KA3", "630"), xw("KA4", "542")
    swapped = grp.check(offices, stock, new, crosswalk, {"KA57": 2})
    assert not swapped["units"]["542"]["exact_match"]
    with pytest.raises(grp.GroupingError, match="no VAHAN figure"):
        grp.check(offices, stock, new, crosswalk, {"KA57": None})


def test_grouping_unit_must_match_report_columns(grouping):
    offices, stock, new = grouping
    crosswalk = [
        xw("KA1", "525"),
        xw("KA2", "525"),
        xw("KA57", "525"),
        xw("KA3", "542;999", "verified_official_combined"),
        xw("KA4", "630"),
    ]
    with pytest.raises(grp.GroupingError, match="does not match"):
        grp.check(offices, stock, new, crosswalk, {"KA57": 2})


def test_rotated_cells_and_headings():
    assert grp.cells(" 45 |  HUNSUR  ARTO | 233724 ") == ["45", "HUNSUR ARTO", "233724"]
    assert grp.normalise_heading("B�LORE(U)") == "B'LORE(U)"
    assert grp.REPORT_DISTRICTS["BELLARY"] == "528;738"


# ---------------------------------------------------------------- S35 class table


def test_month_end_and_numbers():
    assert cls.month_end(2024, 2) == "2024-02-29"
    assert cls.month_end(2026, 2) == "2026-02-28"
    assert cls.number("1,281") == 1281
    with pytest.raises(cls.ClassTableError):
        cls.number("n/a")


def test_read_export_checks_totals(tmp_path):
    path = vahan_export(tmp_path / "a.xlsx", "t", ["JAN", "FEB"], {"MOTOR CAR": [3, 4]})
    assert cls.read_export(path) == {(1, "MOTOR CAR"): 3, (2, "MOTOR CAR"): 4}
    write_xlsx(
        tmp_path / "b.xlsx",
        [
            {"A": "t"},
            {"A": "S No", "B": "Vehicle Class", "E": "TOTAL"},
            {},
            {"C": "JAN", "D": "FEB"},
            {"A": "1", "B": "MOTOR CAR", "C": "3", "D": "4", "E": "8"},
        ],
    )
    with pytest.raises(cls.ClassTableError, match="TOTAL"):
        cls.read_export(tmp_path / "b.xlsx")


def make_batch(tmp_path: Path, fuel_filter=None) -> Path:
    batch = tmp_path / "S29_vahan_dashboard_ka_bev_class_month_2026-10-26"
    batch.mkdir()
    files = {}
    for code, values in {"KA1": [2, 3], "KA45": [1, 0]}.items():
        p = vahan_export(
            batch / f"{code}_2026.xlsx",
            f"... - {code} , Karnataka (2026)",
            ["JAN", "FEB"],
            {"M-CYCLE/SCOOTER": values, "MOTOR CAR": [1, 1]},
        )
        files[p.name] = {
            "rto_code": code,
            "year": "2026",
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
    manifest = {
        "settings": {"y_axis": "Vehicle Class", "fuel_filter": fuel_filter or cls.BEV_FILTER},
        "offices": [{"rto_code": "KA1"}, {"rto_code": "KA45"}],
        "files": files,
    }
    (batch / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return batch


def s26_file(tmp_path: Path) -> Path:
    import csv

    path = tmp_path / "s26.csv"
    rows = [
        ("2026-01-31", "KA1", "3", "yes"),
        ("2026-02-28", "KA1", "5", "yes"),
        ("2026-01-31", "KA45", "", "no"),
        ("2026-02-28", "KA45", "1", "yes"),
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["month_end_date", "rto_code", "ev_bov_plus_pure_published", "rto_has_rows_in_month"]
        )
        w.writerows(rows)
    return path


def test_class_table_build_and_check(tmp_path):
    long_rows, check, summary = cls.build(make_batch(tmp_path), s26_file(tmp_path))
    assert summary["annual_state_bev"] == {"2026": 10}
    assert {(r["rto_code"], r["month_end_date"], r["vehicle_class"]) for r in long_rows} >= {
        ("KA45", "2026-01-31", "M-CYCLE/SCOOTER")
    }
    assert all(r["bev_registrations"] != "0" for r in long_rows)
    status = {(r["rto_code"], r["month_end_date"]): r["status"] for r in check}
    assert status[("KA1", "2026-01-31")] == "equal"
    assert status[("KA1", "2026-02-28")] == "differs"
    assert status[("KA45", "2026-01-31")] == "s24_month_missing"
    assert summary["sum_of_differences"] == -1


def test_class_table_rejects_wrong_filter_and_tampering(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    with pytest.raises(cls.ClassTableError, match="fuel filter"):
        cls.build(make_batch(tmp_path / "a", {"1": "PETROL"}), s26_file(tmp_path))
    batch = make_batch(tmp_path / "b")
    vahan_export(batch / "KA1_2026.xlsx", "t", ["JAN", "FEB"], {"MOTOR CAR": [9, 9]})
    with pytest.raises(cls.ClassTableError, match="hash"):
        cls.build(batch, s26_file(tmp_path))


# ---------------------------------------------------------------- S32 reconciliation


def statement(month, start, new, end):
    return {
        "file": f"S25_x_KAR_{month}.pdf",
        "printed_month": month,
        "stock_start": start,
        "new": new,
        "stock_end": end,
    }


def test_official_series_handles_duplicates_and_rebasing():
    statements = [
        statement("2026-06", 100, 10, 110),
        statement("2026-07", 110, 12, 122),
        statement("2026-08", 140, 15, 155),  # repeats September
        statement("2026-09", 140, 15, 155),
        statement("2026-10", 500, 20, 520),  # rebased opening stock
    ]
    series, notes = rec.official_series(statements)
    assert series["2026-08"] == (140 - 122, "stock_difference")
    assert series["2026-09"] == (15, "statement")
    assert series["2026-10"] == (20, "statement")
    assert any("repeats the figures of 2026-09" in n for n in notes)
    assert any("2026-10" in n and "statement used" in n for n in notes)


def test_official_series_rejects_inconsistent_statement():
    with pytest.raises(rec.ReconcileError, match="closing - opening"):
        rec.official_series([statement("2026-06", 100, 10, 111)])
    bad = statement("2026-06", 100, 10, 110)
    bad["printed_month"] = "2026-05"
    with pytest.raises(rec.ReconcileError, match="prints"):
        rec.official_series([bad])


def test_office_month_reads_exports(tmp_path):
    vahan_export(
        tmp_path / "KA45_2026.xlsx", "t", ["JAN", "FEB"], {"MOPED": [0, 4], "MOTOR CAR": [0, 6]}
    )
    assert rec.office_month(tmp_path, "KA45", 2026, 1) == 0
    assert rec.office_month(tmp_path, "KA45", 2026, 2) == 10
    assert rec.office_month(tmp_path, "KA46", 2026, 2) is None
    assert rec.office_month(None, "KA45", 2026, 2) is None
