"""Fetch S15: BEE location-wise list of EV public charging stations (official PDF).

BEE (Central Nodal Agency for EV public charging) links the list from its EV page as
"EV Public Charging Stations Data till 26th October 2025 (Click to view the detailed
list)". The PDF is saved byte-for-byte to data/raw/ and never overwritten. A sidecar
manifest (<raw file>.manifest.json) records the URLs, HTTP validators, retrieval time,
size and hash.

Uses only the standard library. Run from the repository root:
    python src/evinfra/ingestion/fetch_bee_pcs.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
LISTING_PAGE = "https://www.beeindia.gov.in/show_content.php?lang=1&level=2&lid=67&ls_id=345"
LINK_TEXT = (
    "EV Public Charging Stations Data till 26th October 2025 (Click to view the detailed list)"
)
URL = "https://www.beeindia.gov.in/WriteReadData/RTF1984/EV_PCS_Data_29277.pdf"
USER_AGENT = "Mozilla/5.0 (evinfra research prototype)"


def check_pdf(payload: bytes) -> None:
    if not payload.startswith(b"%PDF-"):
        raise ValueError("Response is not a PDF (missing %PDF- header)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=URL)
    args = parser.parse_args(argv)

    retrieved_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = RAW / f"S15_bee_ev_public_charging_stations_29277_{retrieved_at[:10]}.pdf"
    if out.exists():
        raise SystemExit(f"{out} already exists; raw files are never overwritten")

    request = urllib.request.Request(args.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=300) as response:
        payload = response.read()
        headers = {k: response.headers.get(k) for k in ("Last-Modified", "ETag", "Content-Type")}
    check_pdf(payload)

    manifest = {
        "dataset_id": "S15",
        "listing_page": LISTING_PAGE,
        "link_text": LINK_TEXT,
        "url": args.url,
        "http_headers": headers,
        "retrieved_at": retrieved_at,
        "local_filename": out.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
    }
    out.write_bytes(payload)
    manifest_path = out.with_name(out.name + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    json.dump(manifest, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
