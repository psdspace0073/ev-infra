"""Tests for the S24 fetch header check and the S26 Karnataka EV registration build."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from evinfra.analysis import build_ka_ev_registrations as kev
from evinfra.ingestion import fetch_idp_vahan as fetch

HEADER = fetch.EXPECTED_HEADER


def write_s24(path: Path, rows: list[tuple]) -> Path:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        w.writerow(HEADER)
        for i, (date, state, rto, code, fuel, n) in enumerate(rows, start=1):
            w.writerow(
                [i, date, "Karnataka" if state == "29" else "Kerala", state, rto, code, fuel, n]
            )
    return path


def write_s01(path: Path, years: dict[str, tuple[int, int]]) -> Path:
    lines = [
        '"Title line for Karnataka (2022-2026)"\\n\\nCalendar Year,ELECTRIC(BOV),PURE EV,Total'
    ]
    lines += [f"{y},{a},{b},{a + b}" for y, (a, b) in years.items()]
    lines.append("Total,0,0,0")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


ROWS = [
    ("2022-01-31", "29", "Bengaluru Central RTO", "KA1", "Electric(BOV)", 10),
    ("2022-01-31", "29", "Bengaluru Central RTO", "KA1", "Pure EV", 5),
    ("2022-01-31", "29", "Bengaluru Central RTO", "KA1", "Petrol", 100),
    ("2022-01-31", "29", "Mandya RTO", "KA11", "Petrol", 40),
    ("2022-02-28", "29", "Bengaluru Central RTO", "KA1", "Strong Hybrid EV", 2),
    ("2022-01-31", "32", "Thiruvananthapuram RTO", "KL1", "Electric(BOV)", 99),
]


@pytest.fixture
def files(tmp_path):
    return write_s24(tmp_path / "s24.csv", ROWS), write_s01(tmp_path / "s01.csv", {"2022": (10, 6)})


def by_key(table):
    return {(r["rto_code"], r["month_end_date"]): r for r in table}


def test_fetch_header_check():
    good = ",".join(f'"{h}"' for h in HEADER).encode() + b"\n1,2\n"
    assert fetch.check_header(good) == HEADER
    with pytest.raises(ValueError, match="Unexpected CSV header"):
        fetch.check_header(b'"id","date"\n')


def test_only_karnataka_and_full_rto_month_grid(files):
    table, summary = kev.build(*files)
    assert {r["rto_code"] for r in table} == {"KA1", "KA11"}
    assert len(table) == 4  # 2 RTOs x 2 months
    assert summary["karnataka_source_rows"] == 5


def test_values_copied_and_absent_values_blank_not_zero(files):
    t = by_key(kev.build(*files)[0])
    jan = t[("KA1", "2022-01-31")]
    assert (jan["electric_bov"], jan["pure_ev"], jan["strong_hybrid_ev"]) == ("10", "5", "")
    assert jan["ev_bov_plus_pure_published"] == "15"
    assert jan["all_fuel_total_published"] == "115"
    feb = t[("KA1", "2022-02-28")]
    assert feb["ev_bov_plus_pure_published"] == "" and feb["strong_hybrid_ev"] == "2"
    mandya = t[("KA11", "2022-01-31")]
    assert mandya["electric_bov"] == "" and mandya["all_fuel_total_published"] == "40"


def test_rto_month_without_rows_is_flagged(files):
    table, summary = kev.build(*files)
    gap = by_key(table)[("KA11", "2022-02-28")]
    assert gap["rto_has_rows_in_month"] == "no" and gap["all_fuel_total_published"] == ""
    assert summary["rto_months_without_rows"] == 1
    assert summary["rto_months_without_rows_by_rto"] == {"KA11": 1}


def test_cross_check_only_for_complete_years(tmp_path, files):
    _, summary = kev.build(*files)
    assert summary["s01_cross_check"]["2022"]["s01_bev"] == 16
    assert "note" in summary["s01_cross_check"]["2022"]  # only 2 months in fixture
    rows = [
        (f"2022-{m:02d}-28", "29", "Mandya RTO", "KA11", "Electric(BOV)", 1) for m in range(1, 13)
    ]
    s24 = write_s24(tmp_path / "full.csv", rows)
    _, summary = kev.build(s24, files[1])
    assert summary["s01_cross_check"]["2022"]["difference"] == 12 - 16


def test_duplicates_and_invalid_counts_raise(tmp_path):
    dup = write_s24(tmp_path / "dup.csv", [ROWS[0], ROWS[0]])
    with pytest.raises(kev.RegistrationError, match="Duplicate"):
        kev.build(dup, None)
    bad = write_s24(tmp_path / "bad.csv", [ROWS[0][:5] + (-3,)])
    with pytest.raises(kev.RegistrationError, match="Invalid registration count"):
        kev.build(bad, None)


def test_rto_code_with_two_names_raises(tmp_path):
    rows = [ROWS[0], ("2022-02-28", "29", "Renamed RTO", "KA1", "Petrol", 1)]
    with pytest.raises(kev.RegistrationError, match="several names"):
        kev.build(write_s24(tmp_path / "x.csv", rows), None)


def test_no_karnataka_rows_raises(tmp_path):
    with pytest.raises(kev.RegistrationError, match="No Karnataka rows"):
        kev.build(write_s24(tmp_path / "x.csv", [ROWS[-1]]), None)


def test_build_is_deterministic(tmp_path, files):
    reordered = write_s24(tmp_path / "r.csv", list(reversed(ROWS)))
    assert kev.build(files[0], files[1])[0] == kev.build(reordered, files[1])[0]
