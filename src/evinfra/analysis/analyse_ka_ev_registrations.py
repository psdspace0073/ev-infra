"""Build S28: Karnataka EV registration trends, RTO comparison, missingness and checks.

Inputs:
    S26  data/processed/S26_karnataka_ev_registrations_rto_month.csv (from S24)
    S27  data/raw/S27_idp_vahan_registrations_by_vehicle_class_*.csv (consistency check only)
    configs/ka_rto_district_crosswalk.csv (validated; districts used only where verified)

Outputs (data/processed/):
    S28_ka_ev_monthly_state.csv   statewide monthly flows: BEV, hybrids (separate), all fuels
    S28_ka_ev_annual_rto.csv      per RTO and calendar year: BEV, hybrids, all fuels, shares
    S28_summary.json              missingness, S24-vs-S27 consistency, crosswalk status

Definitions:
    BEV = Electric(BOV) + Pure EV as published. "Pure EV" appears from March 2024 and
    replaces "Electric(BOV)" while their sum stays continuous, so both are treated as
    battery-electric. Hybrids (Strong Hybrid EV, Plug-in Hybrid EV) are kept separate.
    All values are monthly NEW registrations (flows). Unpublished values stay unpublished:
    sums include published values only and say how many RTO-months contributed.

Not done here, by design: no district totals or rankings (the RTO-to-district crosswalk
has no verified rows), no vehicle-class split of EVs, no demand model.

Uses only the standard library. Run from the repository root:
    python src/evinfra/analysis/analyse_ka_ev_registrations.py [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from evinfra.analysis import build_district_table as bdt

ROOT = bdt.ROOT
RAW = bdt.RAW
OUT_DIR = bdt.OUT_DIR
S26 = OUT_DIR / "S26_karnataka_ev_registrations_rto_month.csv"
S27_GLOB = "S27_idp_vahan_registrations_by_vehicle_class_*.csv"
CROSSWALK = ROOT / "configs" / "ka_rto_district_crosswalk.csv"
OUT_MONTHLY = "S28_ka_ev_monthly_state.csv"
OUT_ANNUAL = "S28_ka_ev_annual_rto.csv"
OUT_SUMMARY = "S28_summary.json"
STATE_CODE = "29"
# verified_official_combined: the evidence fixes the office to a group of districts (codes
# joined by ";"), not to one of them.
CROSSWALK_STATUS = {"unresolved", "verified_official", "verified_official_combined"}
CROSSWALK_COLUMNS = [
    "rto_code_vahan",
    "rto_name_vahan",
    "lgd_district_code",
    "lgd_district_name",
    "jurisdiction_basis",
    "source_url",
    "source_retrieved_at",
    "status",
    "notes",
]
MONTHLY_COLUMNS = [
    "month_end_date",
    "bev",
    "electric_bov",
    "pure_ev",
    "strong_hybrid_ev",
    "plug_in_hybrid_ev",
    "all_fuel_total",
    "rtos_with_rows",
    "rtos_without_rows",
]
ANNUAL_COLUMNS = [
    "year",
    "rto_code",
    "rto_name",
    "months_in_source",
    "months_with_rows",
    "year_complete_in_source",
    "bev",
    "hybrids",
    "all_fuel_total",
    "bev_share_of_all_fuel",
    "share_of_state_bev",
]


class AnalysisError(ValueError):
    """Raised when inputs are malformed or fail a consistency check."""


def num(value: str) -> int:
    return int(value) if value else 0


def validate_crosswalk(rows: list[dict[str, str]], rto_codes: set[str]) -> dict:
    """Every RTO exactly once; status known; verified rows carry district and evidence."""
    if not rows or list(rows[0]) != CROSSWALK_COLUMNS:
        raise AnalysisError("Crosswalk columns do not match the expected schema")
    codes = [r["rto_code_vahan"] for r in rows]
    if len(codes) != len(set(codes)):
        raise AnalysisError("Duplicate RTO codes in crosswalk")
    if set(codes) != rto_codes:
        raise AnalysisError(
            f"Crosswalk RTOs differ from S26: missing {sorted(rto_codes - set(codes))}, "
            f"extra {sorted(set(codes) - rto_codes)}"
        )
    for r in rows:
        if r["status"] not in CROSSWALK_STATUS:
            raise AnalysisError(f"{r['rto_code_vahan']}: unknown status {r['status']!r}")
        if r["status"].startswith("verified_official"):
            missing = [
                c
                for c in (
                    "lgd_district_code",
                    "jurisdiction_basis",
                    "source_url",
                    "source_retrieved_at",
                )
                if not r[c]
            ]
            if missing:
                raise AnalysisError(f"{r['rto_code_vahan']}: verified row lacks {missing}")
            combined = r["status"] == "verified_official_combined"
            if combined != (len(r["lgd_district_code"].split(";")) > 1):
                raise AnalysisError(
                    f"{r['rto_code_vahan']}: status {r['status']} does not match district "
                    f"code {r['lgd_district_code']!r}"
                )
        elif r["lgd_district_code"]:
            raise AnalysisError(f"{r['rto_code_vahan']}: district given on an unresolved row")
    return dict(sorted(Counter(r["status"] for r in rows).items()))


def class_totals(path: Path) -> dict[tuple[str, str], int]:
    out: Counter = Counter()
    for r in bdt.read_csv(path):
        if r["state_code"] == STATE_CODE:
            out[(r["rto_code"], r["date"])] += int(r["registrations"])
    return dict(out)


def build(s26: Path, s27: Path | None, crosswalk: Path) -> tuple[list, list, dict]:
    table = bdt.read_csv(s26)
    months = sorted({r["month_end_date"] for r in table})
    rtos = {r["rto_code"]: r["rto_name"] for r in table}
    xw_status = validate_crosswalk(bdt.read_csv(crosswalk), set(rtos))

    by_month: dict[str, list[dict]] = defaultdict(list)
    for r in table:
        by_month[r["month_end_date"]].append(r)
    monthly = []
    for m in months:
        rs = by_month[m]
        row = {"month_end_date": m}
        for col in ("electric_bov", "pure_ev", "strong_hybrid_ev", "plug_in_hybrid_ev"):
            row[col] = str(sum(num(r[col]) for r in rs))
        row["bev"] = str(sum(num(r["ev_bov_plus_pure_published"]) for r in rs))
        row["all_fuel_total"] = str(sum(num(r["all_fuel_total_published"]) for r in rs))
        row["rtos_with_rows"] = str(sum(1 for r in rs if r["rto_has_rows_in_month"] == "yes"))
        row["rtos_without_rows"] = str(sum(1 for r in rs if r["rto_has_rows_in_month"] == "no"))
        monthly.append(row)

    months_per_year = Counter(m[:4] for m in months)
    agg: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for r in table:
        a = agg[(r["month_end_date"][:4], r["rto_code"])]
        a["bev"] += num(r["ev_bov_plus_pure_published"])
        a["hybrids"] += num(r["strong_hybrid_ev"]) + num(r["plug_in_hybrid_ev"])
        a["all"] += num(r["all_fuel_total_published"])
        a["months_with_rows"] += r["rto_has_rows_in_month"] == "yes"
    state_bev = Counter()
    for (year, _), a in agg.items():
        state_bev[year] += a["bev"]
    annual = []
    for year, code in sorted(agg, key=lambda k: (k[0], len(k[1]), k[1])):
        a = agg[(year, code)]
        annual.append(
            {
                "year": year,
                "rto_code": code,
                "rto_name": rtos[code],
                "months_in_source": str(months_per_year[year]),
                "months_with_rows": str(a["months_with_rows"]),
                "year_complete_in_source": "yes" if months_per_year[year] == 12 else "no",
                "bev": str(a["bev"]),
                "hybrids": str(a["hybrids"]),
                "all_fuel_total": str(a["all"]),
                "bev_share_of_all_fuel": f"{a['bev'] / a['all']:.4f}" if a["all"] else "",
                "share_of_state_bev": f"{a['bev'] / state_bev[year]:.4f}"
                if state_bev[year]
                else "",
            }
        )

    missing = [
        (r["rto_code"], r["month_end_date"]) for r in table if r["rto_has_rows_in_month"] == "no"
    ]
    summary: dict = {
        "inputs": {
            s26.name: hashlib.sha256(s26.read_bytes()).hexdigest(),
            crosswalk.name: hashlib.sha256(crosswalk.read_bytes()).hexdigest(),
        },
        "months": len(months),
        "first_month": months[0],
        "last_month": months[-1],
        "rtos": len(rtos),
        "bev_definition": "Electric(BOV) + Pure EV (published values); hybrids separate",
        "annual_state_bev": {y: state_bev[y] for y in sorted(state_bev)},
        "annual_year_complete": {y: months_per_year[y] == 12 for y in sorted(months_per_year)},
        "rto_months_without_rows": len(missing),
        "rto_months_without_rows_by_rto": dict(sorted(Counter(c for c, _ in missing).items())),
        "crosswalk_status": xw_status,
    }
    if s27 is not None:
        summary["inputs"][s27.name] = hashlib.sha256(s27.read_bytes()).hexdigest()
        fuel = {
            (r["rto_code"], r["month_end_date"]): num(r["all_fuel_total_published"])
            for r in table
            if r["rto_has_rows_in_month"] == "yes"
        }
        cls = class_totals(s27)
        keys = set(fuel) | set(cls)
        diffs = sorted(k for k in keys if fuel.get(k) != cls.get(k))
        summary["s24_vs_s27_consistency"] = {
            "rto_months_compared": len(keys),
            "equal_totals": len(keys) - len(diffs),
            "differences": [
                {
                    "rto_code": c,
                    "month_end_date": m,
                    "s24_fuel_total": fuel.get((c, m)),
                    "s27_class_total": cls.get((c, m)),
                }
                for c, m in diffs
            ],
            "missing_rto_months_also_absent_in_s27": sum(1 for k in missing if k not in cls),
        }
    return monthly, annual, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--force", action="store_true", help="replace outputs whose content differs"
    )
    args = parser.parse_args(argv)

    s27_files = sorted(RAW.glob(S27_GLOB))
    monthly, annual, summary = build(S26, s27_files[-1] if s27_files else None, CROSSWALK)
    outputs = {
        OUT_MONTHLY: bdt.to_csv_bytes(MONTHLY_COLUMNS, monthly),
        OUT_ANNUAL: bdt.to_csv_bytes(ANNUAL_COLUMNS, annual),
    }
    summary["outputs_sha256"] = {k: hashlib.sha256(v).hexdigest() for k, v in outputs.items()}
    outputs[OUT_SUMMARY] = (json.dumps(summary, indent=2) + "\n").encode("utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    status = {k: bdt.write_if_unchanged(OUT_DIR / k, v, args.force) for k, v in outputs.items()}
    json.dump({**summary, "write_status": status}, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
