"""Tests for S28 (EV registration analysis), the crosswalk validator and the S27 fetch spec."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from evinfra.analysis import analyse_ka_ev_registrations as ana
from evinfra.analysis import build_ka_ev_registrations as kev
from evinfra.ingestion import fetch_idp_vahan as fetch


def write(path: Path, columns: list[str], rows: list[dict]) -> Path:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return path


def s26_row(code, month, bov="", pure="", shev="", phev="", total="", has="yes"):
    bev = [int(v) for v in (bov, pure) if v]
    return {
        "month_end_date": month,
        "rto_code": code,
        "rto_name": f"{code} RTO",
        "electric_bov": bov,
        "pure_ev": pure,
        "strong_hybrid_ev": shev,
        "plug_in_hybrid_ev": phev,
        "ev_bov_plus_pure_published": str(sum(bev)) if bev else "",
        "all_fuel_total_published": total,
        "source_rows": "1" if has == "yes" else "0",
        "rto_has_rows_in_month": has,
    }


def xw_row(code, status="unresolved", **kw):
    row = dict.fromkeys(ana.CROSSWALK_COLUMNS, "")
    row.update(rto_code_vahan=code, rto_name_vahan=f"{code} RTO", status=status, **kw)
    return row


@pytest.fixture
def inputs(tmp_path):
    s26 = write(
        tmp_path / "s26.csv",
        kev.COLUMNS,
        [
            s26_row("KA1", "2025-01-31", bov="10", pure="20", shev="5", total="100"),
            s26_row("KA1", "2025-02-28", pure="30", phev="1", total="120"),
            s26_row("KA2", "2025-01-31", bov="10", total="50"),
            s26_row("KA2", "2025-02-28", has="no"),
        ],
    )
    s27 = write(
        tmp_path / "s27.csv",
        fetch.TABLES["vehicle_class"]["header"],
        [
            {
                "id": 1,
                "date": "2025-01-31",
                "state_name": "Karnataka",
                "state_code": "29",
                "rto": "x",
                "rto_code": "KA1",
                "vehicle_class": "Transport",
                "registration_type": "Bus",
                "registrations": 100,
            },
            {
                "id": 2,
                "date": "2025-02-28",
                "state_name": "Karnataka",
                "state_code": "29",
                "rto": "x",
                "rto_code": "KA1",
                "vehicle_class": "Non Transport",
                "registration_type": "Car",
                "registrations": 119,
            },
            {
                "id": 3,
                "date": "2025-01-31",
                "state_name": "Karnataka",
                "state_code": "29",
                "rto": "y",
                "rto_code": "KA2",
                "vehicle_class": "Transport",
                "registration_type": "Bus",
                "registrations": 50,
            },
        ],
    )
    xw = write(tmp_path / "xw.csv", ana.CROSSWALK_COLUMNS, [xw_row("KA1"), xw_row("KA2")])
    return s26, s27, xw


def test_monthly_state_keeps_bev_and_hybrids_separate(inputs):
    monthly, _, _ = ana.build(*inputs)
    jan, feb = monthly
    assert (jan["bev"], jan["electric_bov"], jan["pure_ev"], jan["strong_hybrid_ev"]) == (
        "40",
        "20",
        "20",
        "5",
    )
    assert (feb["bev"], feb["plug_in_hybrid_ev"], feb["all_fuel_total"]) == ("30", "1", "120")
    assert (feb["rtos_with_rows"], feb["rtos_without_rows"]) == ("1", "1")


def test_annual_rto_shares_and_partial_year_flag(inputs):
    _, annual, summary = ana.build(*inputs)
    ka1 = next(r for r in annual if r["rto_code"] == "KA1")
    assert (ka1["bev"], ka1["hybrids"], ka1["all_fuel_total"]) == ("60", "6", "220")
    assert ka1["year_complete_in_source"] == "no" and ka1["months_in_source"] == "2"
    assert ka1["share_of_state_bev"] == f"{60 / 70:.4f}"
    ka2 = next(r for r in annual if r["rto_code"] == "KA2")
    assert ka2["months_with_rows"] == "1"
    assert summary["annual_state_bev"] == {"2025": 70}
    assert summary["annual_year_complete"] == {"2025": False}


def test_s24_vs_s27_consistency_reports_differences(inputs):
    _, _, summary = ana.build(*inputs)
    c = summary["s24_vs_s27_consistency"]
    assert c["rto_months_compared"] == 3 and c["equal_totals"] == 2
    assert c["differences"] == [
        {
            "rto_code": "KA1",
            "month_end_date": "2025-02-28",
            "s24_fuel_total": 120,
            "s27_class_total": 119,
        }
    ]
    assert c["missing_rto_months_also_absent_in_s27"] == 1


def test_crosswalk_must_cover_every_rto_once(inputs, tmp_path):
    s26, s27, _ = inputs
    for rows, msg in (
        ([xw_row("KA1")], "missing"),
        ([xw_row("KA1"), xw_row("KA1"), xw_row("KA2")], "Duplicate"),
        ([xw_row("KA1"), xw_row("KA2"), xw_row("KA9")], "extra"),
    ):
        xw = write(tmp_path / "bad.csv", ana.CROSSWALK_COLUMNS, rows)
        with pytest.raises(ana.AnalysisError, match=msg):
            ana.build(s26, s27, xw)


def test_crosswalk_verified_rows_need_evidence(inputs, tmp_path):
    s26, s27, _ = inputs
    bad = write(
        tmp_path / "x.csv",
        ana.CROSSWALK_COLUMNS,
        [xw_row("KA1", "verified_official", lgd_district_code="525"), xw_row("KA2")],
    )
    with pytest.raises(ana.AnalysisError, match="verified row lacks"):
        ana.build(s26, s27, bad)
    guessed = write(
        tmp_path / "y.csv",
        ana.CROSSWALK_COLUMNS,
        [xw_row("KA1", lgd_district_code="525"), xw_row("KA2")],
    )
    with pytest.raises(ana.AnalysisError, match="unresolved row"):
        ana.build(s26, s27, guessed)
    ok = write(
        tmp_path / "z.csv",
        ana.CROSSWALK_COLUMNS,
        [
            xw_row(
                "KA1",
                "verified_official",
                lgd_district_code="525",
                jurisdiction_basis="notification",
                source_url="https://example.gov.in/x",
                source_retrieved_at="2026-10-25",
            ),
            xw_row("KA2"),
        ],
    )
    assert ana.build(s26, s27, ok)[2]["crosswalk_status"] == {
        "unresolved": 1,
        "verified_official": 1,
    }


def test_unknown_crosswalk_status_raises(inputs, tmp_path):
    s26, s27, _ = inputs
    xw = write(tmp_path / "x.csv", ana.CROSSWALK_COLUMNS, [xw_row("KA1", "guessed"), xw_row("KA2")])
    with pytest.raises(ana.AnalysisError, match="unknown status"):
        ana.build(s26, s27, xw)


def test_build_is_deterministic(inputs):
    assert ana.build(*inputs) == ana.build(*inputs)


def test_fetch_table_specs():
    assert fetch.TABLES["fuel_type"]["dataset_id"] == "S24"
    assert fetch.TABLES["vehicle_class"]["dataset_id"] == "S27"
    header = fetch.TABLES["vehicle_class"]["header"]
    payload = ",".join(f'"{h}"' for h in header).encode() + b"\n"
    assert fetch.check_header(payload, header) == header
    with pytest.raises(ValueError):
        fetch.check_header(payload)  # default expects the fuel-type header
