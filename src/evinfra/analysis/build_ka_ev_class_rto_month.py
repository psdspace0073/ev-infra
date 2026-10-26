"""Build S35: Karnataka battery-EV registrations by RTO, vehicle class and month (from S29).

Input: the S29 VAHAN dashboard exports of job bev_class_month (one .xlsx per office and
calendar year; Y = Vehicle Class, X = Month Wise, fuel = ELECTRIC(BOV) + PURE EV), with the
batch manifest that records the filter. The exports are read, never changed.

Outputs (data/processed/):
    S35_ka_bev_rto_class_month.csv   long table: month, RTO, vehicle class, BEV registrations
                                     (cells VAHAN prints as 0 are omitted)
    S35_rto_month_check.csv          per RTO and month: S35 total vs S26 BEV (from S24)
    S35_summary.json                 coverage, class totals, agreement with S26

Months after the last complete month of S26 (September 2026) are excluded; the dashboard's
current month is incomplete. The office KA99 (State Transport Authority) is not in S24; it
is kept and flagged.

Uses only the standard library. Run from the repository root:
    python src/evinfra/analysis/build_ka_ev_class_rto_month.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from evinfra.analysis import build_district_table as bdt

RAW = bdt.RAW
OUT_DIR = bdt.OUT_DIR
S29_GLOB = "S29_vahan_dashboard_ka_bev_class_month_*"
S26 = OUT_DIR / "S26_karnataka_ev_registrations_rto_month.csv"
OUT_LONG = "S35_ka_bev_rto_class_month.csv"
OUT_CHECK = "S35_rto_month_check.csv"
OUT_SUMMARY = "S35_summary.json"
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
MONTH_END = {
    1: "31", 2: "28", 3: "31", 4: "30", 5: "31", 6: "30",
    7: "31", 8: "31", 9: "30", 10: "31", 11: "30", 12: "31",
}  # fmt: skip
BEV_FILTER = {"4": "ELECTRIC(BOV)", "23": "PURE EV"}
LONG_COLUMNS = ["month_end_date", "rto_code", "vehicle_class", "bev_registrations"]
CHECK_COLUMNS = [
    "month_end_date",
    "rto_code",
    "s35_bev_total",
    "s26_bev",
    "s26_rto_has_rows",
    "difference",
    "status",
]


class ClassTableError(RuntimeError):
    pass


def month_end(year: int, month: int) -> str:
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    day = "29" if month == 2 and leap else MONTH_END[month]
    return f"{year}-{month:02d}-{day}"


def number(text: str | None) -> int:
    text = (text or "0").replace(",", "").strip()
    if not text.isdigit():
        raise ClassTableError(f"not a count: {text!r}")
    return int(text)


def read_export(path: Path) -> dict[tuple[int, str], int]:
    """{(month number, vehicle class): count} from one VAHAN class x month export."""
    rows = bdt.read_xlsx_rows(path)
    header = next((r for r in rows if r.get("C") == "JAN"), None)
    if header is None:
        raise ClassTableError(f"{path.name}: no month header row")
    columns = {col: MONTHS.index(m) + 1 for col, m in header.items() if m in MONTHS}
    total_col = next((c for r in rows[:4] for c, v in r.items() if "TOTAL" in v), None)
    out = {}
    for r in rows:
        if not r.get("A", "").strip().isdigit():
            continue
        vclass = r["B"].strip()
        values = {m: number(r.get(col)) for col, m in columns.items()}
        if total_col and r.get(total_col) and number(r[total_col]) != sum(values.values()):
            raise ClassTableError(f"{path.name}: {vclass} months do not add up to its TOTAL")
        for m, v in values.items():
            out[(m, vclass)] = v
    return out


def load_batch(directory: Path) -> tuple[dict, dict]:
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if manifest["settings"]["fuel_filter"] != BEV_FILTER:
        raise ClassTableError(f"batch fuel filter is {manifest['settings']['fuel_filter']}")
    if manifest["settings"]["y_axis"] != "Vehicle Class":
        raise ClassTableError("batch Y-axis is not Vehicle Class")
    for name, entry in manifest["files"].items():
        digest = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise ClassTableError(f"{name}: hash differs from the manifest")
    return manifest, {
        (e["rto_code"], int(e["year"])): directory / name for name, e in manifest["files"].items()
    }


def build(directory: Path, s26_path: Path) -> tuple[list, list, dict]:
    manifest, files = load_batch(directory)
    s26 = {(r["rto_code"], r["month_end_date"]): r for r in bdt.read_csv(s26_path)}
    s26_months = sorted({m for _, m in s26})
    last = s26_months[-1]
    s26_rtos = {c for c, _ in s26}
    offices = {o["rto_code"] for o in manifest["offices"]}
    years = sorted({y for _, y in files})
    missing_files = sorted(f"{c}_{y}" for c in offices for y in years if (c, y) not in files)
    long_rows, totals = [], defaultdict(int)
    class_totals: Counter = Counter()
    for (code, year), path in sorted(files.items(), key=lambda kv: (int(kv[0][0][2:]), kv[0][1])):
        for (month, vclass), value in sorted(read_export(path).items()):
            date = month_end(year, month)
            if date > last or value == 0:
                continue
            long_rows.append(
                {
                    "month_end_date": date,
                    "rto_code": code,
                    "vehicle_class": vclass,
                    "bev_registrations": str(value),
                }
            )
            totals[(code, date)] += value
            class_totals[vclass] += value
    long_rows.sort(key=lambda r: (r["month_end_date"], int(r["rto_code"][2:]), r["vehicle_class"]))
    check_rows, status_count = [], Counter()
    for code in sorted(offices | s26_rtos, key=lambda c: int(c[2:])):
        for date in s26_months:
            ours = totals.get((code, date), 0) if (code, int(date[:4])) in files else None
            ref = s26.get((code, date))
            ref_bev = ref["ev_bov_plus_pure_published"] if ref else ""
            has_rows = ref["rto_has_rows_in_month"] if ref else "not_in_s24"
            if ours is None:
                status = "no_vahan_export"
            elif has_rows == "not_in_s24":
                status = "office_not_in_s24"
            elif has_rows == "no":
                status = "s24_month_missing"
            elif int(ref_bev or 0) == ours:
                status = "equal"
            else:
                status = "differs"
            diff = "" if ours is None or has_rows != "yes" else str(ours - int(ref_bev or 0))
            check_rows.append(
                {
                    "month_end_date": date,
                    "rto_code": code,
                    "s35_bev_total": "" if ours is None else str(ours),
                    "s26_bev": ref_bev,
                    "s26_rto_has_rows": has_rows,
                    "difference": diff,
                    "status": status,
                }
            )
            status_count[status] += 1
    diffs = [int(r["difference"]) for r in check_rows if r["status"] == "differs"]
    state = defaultdict(int)
    for (_, date), v in totals.items():
        state[date[:4]] += v
    summary = {
        "source_batch": directory.name,
        "fuel_filter": manifest["settings"]["fuel_filter"],
        "offices": len(offices),
        "years": years,
        "exports": len(files),
        "missing_exports": missing_files,
        "last_month": last,
        "rows": len(long_rows),
        "vehicle_classes": len(class_totals),
        "class_totals": dict(class_totals.most_common()),
        "annual_state_bev": dict(sorted(state.items())),
        "rto_month_status": dict(sorted(status_count.items())),
        "rto_months_differing": len(diffs),
        "sum_of_differences": sum(diffs),
        "largest_abs_difference": max((abs(d) for d in diffs), default=0),
    }
    return long_rows, check_rows, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="replace outputs that differ")
    parser.add_argument("--batch", type=Path, help="S29 bev_class_month directory")
    args = parser.parse_args(argv)
    batches = sorted(RAW.glob(S29_GLOB))
    directory = args.batch or (batches[-1] if batches else None)
    if directory is None:
        raise SystemExit("no S29 bev_class_month batch in data/raw")
    long_rows, check_rows, summary = build(directory, S26)
    outputs = {
        OUT_LONG: bdt.to_csv_bytes(LONG_COLUMNS, long_rows),
        OUT_CHECK: bdt.to_csv_bytes(CHECK_COLUMNS, check_rows),
    }
    summary["inputs_sha256"] = {
        "manifest.json": hashlib.sha256((directory / "manifest.json").read_bytes()).hexdigest(),
        S26.name: hashlib.sha256(S26.read_bytes()).hexdigest(),
    }
    summary["outputs_sha256"] = {k: hashlib.sha256(v).hexdigest() for k, v in outputs.items()}
    outputs[OUT_SUMMARY] = (json.dumps(summary, indent=2) + "\n").encode("utf-8")
    status = {k: bdt.write_if_unchanged(OUT_DIR / k, v, args.force) for k, v in outputs.items()}
    json.dump({**summary, "write_status": status}, sys.stdout, indent=2)
    print()
    return 0 if not summary["missing_exports"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
