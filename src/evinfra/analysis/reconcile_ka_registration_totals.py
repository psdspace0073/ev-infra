"""Build S32: reconcile Karnataka registration totals across sources, and classify the
RTO-months that S24 does not publish.

Inputs (read only):
    S25  data/raw/S25_ka_transport_monthly_statement_KAR_<YYYY-MM>.pdf (Transport Department
         monthly statements; new registrations, all fuels, by category; no RTO, no fuel)
    S29  VAHAN dashboard exports: state_fuel_month (all offices, fuel x month) and, for
         KA45, KA46 and KA57, allfuel_class_month and bev_class_month
    S28  data/processed/S28_ka_ev_monthly_state.csv (S24 statewide monthly totals)
    S26  data/processed/S26_karnataka_ev_registrations_rto_month.csv and S26_summary.json
         (S24 by RTO and month; S01 annual cross-check)

Outputs (data/processed/):
    S32_ka_monthly_total_reconciliation.csv  month: official (S25) vs VAHAN now vs S24
    S32_missing_rto_month_register.csv       the RTO-months without S24 rows, with what the
                                             VAHAN dashboard reports for them
    S32_summary.json                         annual battery-EV triangulation (S01, S24,
                                             VAHAN now), offsets, statement anomalies

Status of a missing RTO-month (never imputed):
    vahan_reports_registrations  VAHAN shows registrations: absent from S24 only
    vahan_reports_zero           VAHAN shows 0 for every vehicle class in that month
    no_vahan_evidence            no S29 export covers it

Needs the optional extra 'pdf' (pdfplumber) to read S25. Run from the repository root:
    python src/evinfra/analysis/reconcile_ka_registration_totals.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

from evinfra.analysis import build_district_table as bdt
from evinfra.analysis.build_ka_ev_class_rto_month import MONTHS, number

RAW = bdt.RAW
OUT_DIR = bdt.OUT_DIR
S25_GLOB = "S25_ka_transport_monthly_statement_KAR_*.pdf"
S28_MONTHLY = OUT_DIR / "S28_ka_ev_monthly_state.csv"
S26 = OUT_DIR / "S26_karnataka_ev_registrations_rto_month.csv"
S26_SUMMARY = OUT_DIR / "S26_summary.json"
BEV_LABELS = ("ELECTRIC(BOV)", "PURE EV")
OUT_MONTHLY = "S32_ka_monthly_total_reconciliation.csv"
OUT_MISSING = "S32_missing_rto_month_register.csv"
OUT_SUMMARY = "S32_summary.json"
MONTHLY_COLUMNS = [
    "month",
    "official_new_registrations",
    "official_basis",
    "vahan_now_all_fuel",
    "s24_all_fuel",
    "vahan_minus_official",
    "vahan_minus_official_pct",
    "vahan_minus_s24",
    "vahan_now_bev",
    "s24_bev",
    "vahan_minus_s24_bev",
]
MISSING_COLUMNS = [
    "rto_code",
    "month_end_date",
    "s24_rows",
    "vahan_all_fuel",
    "vahan_bev",
    "status",
    "evidence",
]
TITLE = re.compile(r"REGISTERED AS ON (\d\d)-(\d\d)-(\d{4}) IN KARNATAKA STATE")
TOTAL = re.compile(r"TOTAL\s*\(A\)\s*\+\s*\(B\)\s*\n?\s*(\d+)\s+(\d+)\s+(\d+)")


class ReconcileError(RuntimeError):
    pass


def read_statement(path: Path) -> dict:
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        text = "\n".join(p.extract_text() or "" for p in pdf.pages[:2])
    title, total = TITLE.search(text), TOTAL.search(text)
    if not title or not total:
        raise ReconcileError(f"{path.name}: title or TOTAL (A)+(B) row not found")
    stock_start, new, stock_end = (int(x) for x in total.groups())
    return {
        "file": path.name,
        "printed_month": f"{title.group(3)}-{title.group(2)}",
        "stock_start": stock_start,
        "new": new,
        "stock_end": stock_end,
    }


def official_series(statements: list[dict]) -> tuple[dict, list[str]]:
    """{month: (new, basis)} from the statements.

    A statement is not used when its figures repeat another month's statement and its
    opening stock does not continue from the previous month; that month is then derived
    as (next opening stock - previous closing stock). Other chain breaks are reported but
    the statement is used, because its own figures are consistent (stock rebasing).
    """
    by_month = {}
    for s in statements:
        key = s["file"].rsplit("_", 1)[-1][:-4]  # month in the file name (as published)
        if key != s["printed_month"]:
            raise ReconcileError(f"{s['file']}: prints {s['printed_month']}")
        if s["stock_end"] - s["stock_start"] != s["new"]:
            raise ReconcileError(f"{s['file']}: closing - opening stock != new registrations")
        by_month[key] = s
    keys = sorted(by_month)
    series, notes, rejected = {}, [], set()
    for i, key in enumerate(keys):
        s = by_month[key]
        prev_key = keys[i - 1] if i else None
        prev = by_month[prev_key] if prev_key else None
        nxt = by_month[keys[i + 1]] if i + 1 < len(keys) else None
        twins = [
            k
            for k, o in by_month.items()
            if k != key
            and (o["stock_start"], o["new"], o["stock_end"])
            == (s["stock_start"], s["new"], s["stock_end"])
        ]
        # a rejected predecessor cannot show a break
        breaks = (
            prev is not None and prev_key not in rejected and prev["stock_end"] != s["stock_start"]
        )
        if twins and breaks and nxt is not None:
            rejected.add(key)
            series[key] = (nxt["stock_start"] - prev["stock_end"], "stock_difference")
            notes.append(
                f"{s['file']} repeats the figures of {twins[0]}; new registrations derived "
                f"from the {prev_key} closing and {keys[i + 1]} opening stocks"
            )
            continue
        if breaks:
            notes.append(
                f"{s['file']}: opening stock {s['stock_start']} differs from the "
                f"{prev_key} closing stock {prev['stock_end']} (statement used)"
            )
        series[key] = (s["new"], "statement")
    return series, notes


def read_month_table(path: Path) -> dict[tuple[int, str], int]:
    rows = bdt.read_xlsx_rows(path)
    header = next(r for r in rows if r.get("C") == "JAN")
    columns = {col: MONTHS.index(m) + 1 for col, m in header.items() if m in MONTHS}
    return {
        (m, r["B"].strip()): number(r.get(col))
        for r in rows
        if r.get("A", "").strip().isdigit()
        for col, m in columns.items()
    }


def latest(pattern: str) -> Path | None:
    found = sorted(RAW.glob(pattern))
    return found[-1] if found else None


def vahan_state(directory: Path) -> tuple[dict, dict]:
    all_fuel, bev = {}, {}
    for path in sorted(directory.glob("KA_all_*.xlsx")):
        year = int(path.stem.rsplit("_", 1)[-1])
        for (month, label), value in read_month_table(path).items():
            key = f"{year}-{month:02d}"
            all_fuel[key] = all_fuel.get(key, 0) + value
            if label in BEV_LABELS:
                bev[key] = bev.get(key, 0) + value
    return all_fuel, bev


def office_month(directory: Path | None, code: str, year: int, month: int) -> int | None:
    if directory is None or not (directory / f"{code}_{year}.xlsx").exists():
        return None
    table = read_month_table(directory / f"{code}_{year}.xlsx")
    return sum(v for (m, _), v in table.items() if m == month)


def build() -> tuple[list, list, dict]:
    statements = [read_statement(p) for p in sorted(RAW.glob(S25_GLOB))]
    official, notes = official_series(statements)
    state_dir = latest("S29_vahan_dashboard_ka_state_fuel_month_*")
    allfuel_dir = latest("S29_vahan_dashboard_ka_allfuel_class_month_*")
    bev_dir = latest("S29_vahan_dashboard_ka_bev_class_month_*")
    if state_dir is None:
        raise ReconcileError("no S29 state_fuel_month batch")
    v_all, v_bev = vahan_state(state_dir)
    s28 = {r["month_end_date"][:7]: r for r in bdt.read_csv(S28_MONTHLY)}
    monthly = []
    for key in sorted(s28):
        off, basis = official.get(key, (None, ""))
        va, vb = v_all.get(key), v_bev.get(key)
        sa, sb = int(s28[key]["all_fuel_total"]), int(s28[key]["bev"])
        monthly.append(
            {
                "month": key,
                "official_new_registrations": "" if off is None else str(off),
                "official_basis": basis,
                "vahan_now_all_fuel": "" if va is None else str(va),
                "s24_all_fuel": str(sa),
                "vahan_minus_official": "" if off is None or va is None else str(va - off),
                "vahan_minus_official_pct": ""
                if off is None or va is None
                else f"{100 * (va - off) / off:.2f}",
                "vahan_minus_s24": "" if va is None else str(va - sa),
                "vahan_now_bev": "" if vb is None else str(vb),
                "s24_bev": str(sb),
                "vahan_minus_s24_bev": "" if vb is None else str(vb - sb),
            }
        )
    missing = []
    for r in bdt.read_csv(S26):
        if r["rto_has_rows_in_month"] != "no":
            continue
        year, month = int(r["month_end_date"][:4]), int(r["month_end_date"][5:7])
        code = r["rto_code"]
        va = office_month(allfuel_dir, code, year, month)
        vb = office_month(bev_dir, code, year, month)
        status = (
            "no_vahan_evidence"
            if va is None
            else "vahan_reports_registrations"
            if va > 0
            else "vahan_reports_zero"
        )
        evidence = [
            f"{d.name}/{code}_{year}.xlsx"
            for d in (allfuel_dir, bev_dir)
            if d is not None and (d / f"{code}_{year}.xlsx").exists()
        ]
        missing.append(
            {
                "rto_code": code,
                "month_end_date": r["month_end_date"],
                "s24_rows": "0",
                "vahan_all_fuel": "" if va is None else str(va),
                "vahan_bev": "" if vb is None else str(vb),
                "status": status,
                "evidence": "; ".join(evidence),
            }
        )
    s01 = json.loads(S26_SUMMARY.read_text(encoding="utf-8"))["s01_cross_check"]
    triangulation = {}
    for year, chk in s01.items():
        months = [m for m in monthly if m["month"].startswith(year)]
        vahan = sum(int(m["vahan_now_bev"]) for m in months if m["vahan_now_bev"])
        in_missing = sum(
            int(x["vahan_bev"] or 0) for x in missing if x["month_end_date"].startswith(year)
        )
        triangulation[year] = {
            "s01_export": chk["s01_bev"],
            "s24": chk["s26_bev"],
            "vahan_now_same_months": vahan,
            "months_compared": len(months),
            "s24_minus_s01": chk["s26_bev"] - chk["s01_bev"],
            "vahan_now_minus_s01": vahan - chk["s01_bev"],
            "vahan_now_minus_s24": vahan - chk["s26_bev"],
            "vahan_bev_in_rto_months_missing_from_s24": in_missing,
        }
    offsets = [
        float(m["vahan_minus_official_pct"])
        for m in monthly
        if m["vahan_minus_official_pct"] and m["month"] >= "2023-04"
    ]
    summary = {
        "statements": len(statements),
        "statement_notes": notes,
        "official_months": len(official),
        "official_derived_from_stock": sorted(
            k for k, (_, b) in official.items() if b != "statement"
        ),
        "vahan_minus_official_pct": {
            "months": len(offsets),
            "min": min(offsets, default=None),
            "median": statistics.median(offsets) if offsets else None,
            "max": max(offsets, default=None),
            "months_vahan_higher": sum(o > 0 for o in offsets),
        },
        "bev_triangulation": triangulation,
        "missing_rto_months": len(missing),
        "missing_status": {
            s: sum(1 for x in missing if x["status"] == s)
            for s in sorted({x["status"] for x in missing})
        },
        "sources": {
            "state_fuel_month": state_dir.name,
            "allfuel_class_month": allfuel_dir.name if allfuel_dir else None,
            "bev_class_month": bev_dir.name if bev_dir else None,
        },
    }
    return monthly, missing, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="replace outputs that differ")
    args = parser.parse_args(argv)
    monthly, missing, summary = build()
    outputs = {
        OUT_MONTHLY: bdt.to_csv_bytes(MONTHLY_COLUMNS, monthly),
        OUT_MISSING: bdt.to_csv_bytes(MISSING_COLUMNS, missing),
    }
    summary["outputs_sha256"] = {k: hashlib.sha256(v).hexdigest() for k, v in outputs.items()}
    outputs[OUT_SUMMARY] = (json.dumps(summary, indent=2) + "\n").encode("utf-8")
    status = {k: bdt.write_if_unchanged(OUT_DIR / k, v, args.force) for k, v in outputs.items()}
    json.dump({**summary, "write_status": status}, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
