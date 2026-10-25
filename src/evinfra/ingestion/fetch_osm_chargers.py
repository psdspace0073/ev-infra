"""Fetch S10: OSM amenity=charging_station elements for Karnataka from the Overpass API.

The response is saved byte-for-byte to data/raw/ and never overwritten. A sidecar
manifest (<raw file>.manifest.json) records the endpoint, query text and hash,
retrieval time, file hash and element counts.

Uses only the standard library. Run from the repository root:
    python src/evinfra/ingestion/fetch_osm_chargers.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
QUERY = ROOT / "src" / "queries" / "osm_chargers_ka.overpassql"
ENDPOINT = "https://overpass-api.de/api/interpreter"
USER_AGENT = "evinfra/0.1 (EV infrastructure research prototype)"


def summarise(payload: bytes) -> dict:
    """Element counts from an Overpass JSON response. Raises if it is not usable."""
    data = json.loads(payload)
    if "remark" in data:
        raise ValueError(f"Overpass returned a remark (partial or failed result): {data['remark']}")
    elements = data["elements"]
    if not elements:
        raise ValueError("Overpass returned no elements")
    return {
        "osm_base_timestamp": data.get("osm3s", {}).get("timestamp_osm_base"),
        "element_count": len(elements),
        "element_types": dict(sorted(Counter(e["type"] for e in elements).items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--endpoint", default=ENDPOINT)
    args = parser.parse_args(argv)

    query = QUERY.read_bytes()
    retrieved_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = RAW / f"S10_osm_karnataka_charging_stations_overpass_{retrieved_at[:10]}.json"
    if out.exists():
        raise SystemExit(f"{out} already exists; raw files are never overwritten")

    body = urllib.parse.urlencode({"data": query.decode("utf-8")}).encode("ascii")
    request = urllib.request.Request(args.endpoint, data=body, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=240) as response:
        payload = response.read()

    manifest = {
        "dataset_id": "S10",
        "endpoint": args.endpoint,
        "query_file": QUERY.relative_to(ROOT).as_posix(),
        "query_sha256": hashlib.sha256(query).hexdigest(),
        "retrieved_at": retrieved_at,
        "local_filename": out.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        **summarise(payload),
    }
    out.write_bytes(payload)
    manifest_path = out.with_name(out.name + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    json.dump(manifest, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
