"""Extract S16: every table row of the S15 BEE PDF into a staging CSV (all states).

This is the staging layer. Each output row is one PDF table row, with its page and row
position as a stable source_row_id. Cell text is kept as printed; the only change is
that line breaks inside a cell (PDF word-wrap) are replaced by single spaces. Repeated
header rows are dropped and counted. No row is filtered, cleaned or deduplicated here.

Needs pdfplumber (optional extra: python -m pip install -e ".[pdf]"). Run from the
repository root:
    python src/evinfra/ingestion/extract_bee_pcs.py [--force]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "interim" / "S16_bee_pcs_rows_all_states.csv"
S15_GLOB = "S15_bee_ev_public_charging_stations_29277_*.pdf"

SOURCE_HEADER = [
    "CPO Name",
    "Govt/Private",
    "State",
    "District",
    "City/Village",
    "Location",
    "Latitude",
    "Longitude",
    "Types of Chargers Installed/ Connector",
    "Charger Rating",
    "Connector Rating",
    "No. of Connector",
]
FIELDS = [
    "cpo_name",
    "govt_private",
    "state",
    "district",
    "city_village",
    "location",
    "latitude",
    "longitude",
    "charger_type",
    "charger_rating",
    "connector_rating",
    "no_of_connector",
]
COLUMNS = ["source_row_id", "page", "row_on_page", *FIELDS]


class ExtractionError(ValueError):
    """Raised when the PDF table does not have the expected structure."""


def find_s15(raw: Path) -> Path:
    files = sorted(p for p in raw.glob(S15_GLOB) if p.suffix == ".pdf")
    if not files:
        raise ExtractionError(f"No S15 file matching {S15_GLOB} in {raw}")
    return files[-1]


def cell_text(cell: str | None) -> str:
    return " ".join((cell or "").split("\n")).strip() if cell else ""


def normalise_rows(pages: list[list[list[str | None]]]) -> tuple[list[dict[str, str]], dict]:
    """Turn per-page table rows into staging records. Pure function, used by tests."""
    rows: list[dict[str, str]] = []
    report = {"pages": len(pages), "header_rows": 0, "blank_rows": 0, "pages_without_rows": 0}
    for page_no, table_rows in enumerate(pages, start=1):
        kept = 0
        for row_no, cells in enumerate(table_rows, start=1):
            if len(cells) != len(FIELDS):
                raise ExtractionError(
                    f"Page {page_no} row {row_no}: {len(cells)} cells, expected {len(FIELDS)}"
                )
            values = [cell_text(c) for c in cells]
            if [" ".join(v.split()) for v in values] == SOURCE_HEADER:
                report["header_rows"] += 1
                continue
            if not any(values):
                report["blank_rows"] += 1
                continue
            rows.append(
                {
                    "source_row_id": f"S15-p{page_no:04d}-r{row_no:02d}",
                    "page": str(page_no),
                    "row_on_page": str(row_no),
                    **dict(zip(FIELDS, values)),
                }
            )
            kept += 1
        if kept == 0:
            report["pages_without_rows"] += 1
    report["data_rows"] = len(rows)
    return rows, report


def read_pdf_tables(path: Path) -> list[list[list[str | None]]]:
    import pdfplumber

    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if len(tables) != 1:
                raise ExtractionError(f"Page {i}: {len(tables)} tables, expected 1")
            pages.append(tables[0])
    return pages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="replace output whose content differs")
    args = parser.parse_args(argv)

    src = find_s15(RAW)
    rows, report = normalise_rows(read_pdf_tables(src))
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    data = buf.getvalue().encode("utf-8")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists() and OUT.read_bytes() != data and not args.force:
        raise SystemExit(f"{OUT} exists with different content; rerun with --force")
    status = "unchanged" if OUT.exists() and OUT.read_bytes() == data else "written"
    if status == "written":
        OUT.write_bytes(data)
    report.update(
        {
            "input": src.name,
            "input_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "output": OUT.relative_to(ROOT).as_posix(),
            "output_sha256": hashlib.sha256(data).hexdigest(),
            "status": status,
        }
    )
    json.dump(report, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
