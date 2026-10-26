"""Run the frozen planning-slice sensitivity variants (configs/planning_slice_sensitivity.json).

Each variant reruns the slice with one baseline rule overridden. The parameters file and the
baseline outputs are not changed. Writes outputs/reports/planning_slice/sensitivity.csv and,
with --update-docs, the tracked copy docs/submission/planning_slice/sensitivity.csv
(otherwise compared; exit 1 if it differs).

    python src/evinfra/scoring/run_planning_slice_sensitivity.py [--update-docs]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

from evinfra.analysis import build_district_table as bdt
from evinfra.scoring import build_karnataka_planning_slice as ps

VARIANTS = ps.ROOT / "configs" / "planning_slice_sensitivity.json"
NAME = "sensitivity.csv"
COLUMNS = [
    "variant",
    "why",
    "eligible_candidates",
    "selected_sites",
    "public_cost_inr_lakh",
    "budget_inr_lakh",
    "budget_binding",
    "baseline_sites_kept",
    "selected_osm_ids",
]


def run(path: Path = VARIANTS) -> list[dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        variants = json.load(f)["variants"]
    with open(ps.PARAMS, encoding="utf-8") as f:
        base = json.load(f)
    rows, base_ids = [], None
    for v in variants:
        outputs, summary = ps.build(overrides=v["overrides"])
        cands = list(csv.DictReader(io.StringIO(outputs["candidates.csv"].decode("utf-8"))))
        chosen = [c for c in cands if c["status"] == "selected"]
        ids = [c["osm_id"] for c in sorted(chosen, key=lambda c: int(c["selection_order"]))]
        base_ids = ids if base_ids is None else base_ids
        budget = ps.merge(base, v["overrides"])["public_budget_inr_lakh"]["value"]
        rows.append(
            {
                "variant": v["id"],
                "why": v["why"],
                "eligible_candidates": str(
                    sum(
                        c["status"] == "selected" or c["status"].startswith("eligible")
                        for c in cands
                    )
                ),
                "selected_sites": str(len(ids)),
                "public_cost_inr_lakh": f"{summary['public_cost_selected_inr_lakh']:.3f}",
                "budget_inr_lakh": str(budget),
                "budget_binding": "yes"
                if any(c["status"].endswith("(budget)") for c in cands)
                else "no",
                "baseline_sites_kept": f"{len(set(ids) & set(base_ids))} of {len(base_ids)}",
                "selected_osm_ids": " ".join(ids),
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--update-docs", action="store_true")
    args = parser.parse_args(argv)
    rows = run()
    data = bdt.to_csv_bytes(COLUMNS, rows)
    ps.OUT_DIR.mkdir(parents=True, exist_ok=True)
    (ps.OUT_DIR / NAME).write_bytes(data)
    doc = ps.DOCS_DIR / NAME
    if args.update_docs:
        doc.write_bytes(data)
        status = "written"
    else:
        same = doc.exists() and doc.read_bytes().replace(b"\r\n", b"\n") == data
        status = "same" if same else "differs"
    sys.stdout.write(data.decode("utf-8") + f"docs copy: {status}\n")
    return 1 if status == "differs" else 0


if __name__ == "__main__":
    raise SystemExit(main())
