"""Build S26: Karnataka monthly EV registrations by RTO from S24 (IDP compilation of VAHAN).

Inputs (read-only, data/raw/):
    S24  India Data Portal "Registrations by Fuel Type" CSV (newest file)
    S01  VAHAN dashboard export: Karnataka statewide EV registrations by calendar year

Output (data/processed/):
    S26_karnataka_ev_registrations_rto_month.csv   one row per (RTO, month)
    S26_summary.json                               validation results and the S01 cross-check

Semantics:
    - Counts are NEW registrations in the month (flows), as compiled from the VAHAN
      dashboard; the month is the source's month-end date. They are not cumulative stock.
    - Values are copied as published. The source never publishes zero counts, so an absent
      (RTO, month, fuel) combination may be zero or unreported: it is left blank, never 0.
    - An (RTO, month) with no source rows at all is kept as a row with blank values and
      rto_has_rows_in_month = "no".
    - ev_bov_plus_pure_published sums the published Electric(BOV) and Pure EV values (the
      VAHAN battery-EV labels used in S01); blank when neither is published.
    - Vehicle class is NOT available by fuel at RTO level in this source; no EV class split
      is inferred. RTO codes are kept as published (e.g. "KA1"); no district is assigned.

Uses only the standard library. Run from the repository root:
    python src/evinfra/analysis/build_ka_ev_registrations.py [--force]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from evinfra.analysis import build_district_table as bdt

RAW = bdt.RAW
OUT_DIR = bdt.OUT_DIR
S24_GLOB = "S24_idp_vahan_registrations_by_fuel_type_*.csv"
S01 = RAW / "S01_vahan_karnataka_ev_registrations_2022-2026.csv.csv"
OUT_TABLE = "S26_karnataka_ev_registrations_rto_month.csv"
OUT_SUMMARY = "S26_summary.json"
STATE_CODE = "29"
EV_LABELS = {
    "Electric(BOV)": "electric_bov",
    "Pure EV": "pure_ev",
    "Strong Hybrid EV": "strong_hybrid_ev",
    "Plug-in Hybrid EV": "plug_in_hybrid_ev",
}
BEV_LABELS = ("Electric(BOV)", "Pure EV")
COLUMNS = [
    "month_end_date",
    "rto_code",
    "rto_name",
    *EV_LABELS.values(),
    "ev_bov_plus_pure_published",
    "all_fuel_total_published",
    "source_rows",
    "rto_has_rows_in_month",
]


class RegistrationError(ValueError):
    """Raised when inputs are malformed or fail a consistency check."""


def read_s24(path: Path) -> list[dict[str, str]]:
    rows = [r for r in bdt.read_csv(path) if r["state_code"] == STATE_CODE]
    if not rows:
        raise RegistrationError("No Karnataka rows (state_code 29) in S24")
    seen = set()
    for r in rows:
        key = (r["date"], r["rto_code"], r["registration_type"])
        if key in seen:
            raise RegistrationError(f"Duplicate S24 row {key}")
        seen.add(key)
        if not r["registrations"].isdigit():
            raise RegistrationError(f"Invalid registration count {r['registrations']!r} in {key}")
    names = defaultdict(set)
    for r in rows:
        names[r["rto_code"]].add(r["rto"])
    clashes = {k: sorted(v) for k, v in names.items() if len(v) > 1}
    if clashes:
        raise RegistrationError(f"RTO codes with several names: {clashes}")
    return rows


def read_s01(path: Path) -> dict[str, int]:
    """Calendar-year ELECTRIC(BOV) + PURE EV totals from the S01 dashboard export."""
    text = path.read_text(encoding="utf-8-sig").replace("\\n", "\n")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    start = next(i for i, ln in enumerate(lines) if ln.startswith("Calendar Year"))
    out = {}
    for r in csv.DictReader(io.StringIO("\n".join(lines[start:]))):
        if r["Calendar Year"].isdigit():
            out[r["Calendar Year"]] = int(r["ELECTRIC(BOV)"]) + int(r["PURE EV"])
    return out


def build(s24: Path, s01: Path | None = S01) -> tuple[list[dict[str, str]], dict]:
    rows = read_s24(s24)
    months = sorted({r["date"] for r in rows})
    rtos = {r["rto_code"]: r["rto"] for r in rows}
    cells: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    for r in rows:
        cells[(r["date"], r["rto_code"])][r["registration_type"]] = int(r["registrations"])

    table = []
    for code in sorted(rtos, key=lambda c: (len(c), c)):
        for month in months:
            got = cells.get((month, code), {})
            out = dict.fromkeys(COLUMNS, "")
            out.update(month_end_date=month, rto_code=code, rto_name=rtos[code])
            for label, col in EV_LABELS.items():
                if label in got:
                    out[col] = str(got[label])
            bev = [got[k] for k in BEV_LABELS if k in got]
            out["ev_bov_plus_pure_published"] = str(sum(bev)) if bev else ""
            out["all_fuel_total_published"] = str(sum(got.values())) if got else ""
            out["source_rows"] = str(len(got))
            out["rto_has_rows_in_month"] = "yes" if got else "no"
            table.append(out)

    annual = Counter()
    for r in rows:
        if r["registration_type"] in BEV_LABELS:
            annual[r["date"][:4]] += int(r["registrations"])
    months_per_year = Counter(m[:4] for m in months)
    s01_totals = read_s01(s01) if s01 is not None and s01.exists() else {}
    cross_check = {}
    for year in sorted(set(annual) | set(s01_totals)):
        complete = months_per_year.get(year) == 12
        entry = {
            "s26_bev": annual.get(year),
            "s01_bev": s01_totals.get(year),
            "s26_months": months_per_year.get(year, 0),
        }
        if complete and year in s01_totals:
            entry["difference"] = annual[year] - s01_totals[year]
            entry["difference_pct"] = round(100 * entry["difference"] / s01_totals[year], 3)
        else:
            entry["note"] = "not comparable: incomplete year in S26 or S01 cut-off unknown"
        cross_check[year] = entry

    missing = [
        (r["rto_code"], r["month_end_date"]) for r in table if r["rto_has_rows_in_month"] == "no"
    ]
    summary = {
        "inputs": {s24.name: hashlib.sha256(s24.read_bytes()).hexdigest()},
        "karnataka_source_rows": len(rows),
        "months": len(months),
        "first_month": months[0],
        "last_month": months[-1],
        "rtos": len(rtos),
        "table_rows": len(table),
        "fuel_labels": dict(sorted(Counter(r["registration_type"] for r in rows).items())),
        "rto_months_without_rows": len(missing),
        "rto_months_without_rows_by_rto": dict(sorted(Counter(c for c, _ in missing).items())),
        "bev_definition": "Electric(BOV) + Pure EV, as published (absent = not published)",
        "s01_cross_check": cross_check,
    }
    if s01 is not None and s01.exists():
        summary["inputs"][s01.name] = hashlib.sha256(s01.read_bytes()).hexdigest()
    return table, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true", help="replace outputs whose content differs"
    )
    args = parser.parse_args(argv)

    files = sorted(p for p in RAW.glob(S24_GLOB))
    if not files:
        raise SystemExit(f"No S24 file matching {S24_GLOB}")
    table, summary = build(files[-1])
    table_bytes = bdt.to_csv_bytes(COLUMNS, table)
    summary["output_sha256"] = hashlib.sha256(table_bytes).hexdigest()
    summary_bytes = (json.dumps(summary, indent=2) + "\n").encode("utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    status = {
        OUT_TABLE: bdt.write_if_unchanged(OUT_DIR / OUT_TABLE, table_bytes, args.force),
        OUT_SUMMARY: bdt.write_if_unchanged(OUT_DIR / OUT_SUMMARY, summary_bytes, args.force),
    }
    json.dump({**summary, "write_status": status}, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
