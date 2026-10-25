"""Fetch S22: Karnataka thematic OSM layers from the Overpass API (one query per layer).

Each src/queries/osm_ka_<layer>.overpassql is run in turn, and its response is saved
byte-for-byte to data/raw/S22_osm_ka_<layer>_overpass_<UTC timestamp>.json with a
sidecar manifest (endpoint, query hash, retrieval time, OSM base timestamp, counts).
Existing files are never overwritten; every run adds new timestamped snapshots, and
consumers use the newest file per layer.
Requests are sequential, with a pause between them and a bounded retry on 429/502/504.

Uses only the standard library. Run from the repository root:
    python src/evinfra/ingestion/fetch_osm_karnataka_layers.py [--layers roads_major fuel ...]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
QUERIES = ROOT / "src" / "queries"
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
USER_AGENT = "evinfra/0.1 (EV infrastructure research prototype)"
RETRY_CODES = {429, 502, 503, 504}
PAUSE_S = 10


def layer_names() -> list[str]:
    return sorted(p.stem.removeprefix("osm_ka_") for p in QUERIES.glob("osm_ka_*.overpassql"))


def summarise(payload: bytes) -> dict:
    """Counts from an Overpass JSON response. Raises if it is not usable."""
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


def post(endpoint: str, query: str) -> bytes:
    body = urllib.parse.urlencode({"data": query}).encode("ascii")
    request = urllib.request.Request(endpoint, data=body, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=960) as response:
        return response.read()


def fetch(query: str) -> tuple[bytes, str, list[str]]:
    """Try each endpoint with one retry; return payload, endpoint and the attempt log."""
    attempts = []
    for endpoint in ENDPOINTS:
        for attempt in range(2):
            try:
                payload = post(endpoint, query)
                summarise(payload)
                attempts.append(f"{endpoint}: ok")
                return payload, endpoint, attempts
            except urllib.error.HTTPError as exc:
                attempts.append(f"{endpoint}: HTTP {exc.code}")
                if exc.code not in RETRY_CODES:
                    break
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                attempts.append(f"{endpoint}: {type(exc).__name__}: {exc}"[:300])
            time.sleep(PAUSE_S * (attempt + 1))
    raise RuntimeError("All Overpass attempts failed: " + " | ".join(attempts))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--layers", nargs="*", default=None, help="subset of layers to fetch")
    args = parser.parse_args(argv)

    layers = args.layers or layer_names()
    unknown = set(layers) - set(layer_names())
    if unknown:
        raise SystemExit(f"Unknown layers: {sorted(unknown)}")

    report = {}
    for i, layer in enumerate(layers):
        query_path = QUERIES / f"osm_ka_{layer}.overpassql"
        query = query_path.read_text(encoding="utf-8")
        retrieved_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        stamp = retrieved_at.replace(":", "").replace("-", "")  # e.g. 20261025T151303Z
        out = RAW / f"S22_osm_ka_{layer}_overpass_{stamp}.json"
        if out.exists():
            report[layer] = {"status": "exists", "local_filename": out.name}
            continue
        if i:
            time.sleep(PAUSE_S)
        try:
            payload, endpoint, attempts = fetch(query)
        except RuntimeError as exc:
            report[layer] = {"status": "failed", "error": str(exc)}
            continue
        manifest = {
            "dataset_id": "S22",
            "layer": layer,
            "endpoint": endpoint,
            "attempts": attempts,
            "query_file": query_path.relative_to(ROOT).as_posix(),
            "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
            "retrieved_at": retrieved_at,
            "local_filename": out.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            **summarise(payload),
        }
        out.write_bytes(payload)
        out.with_name(out.name + ".manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        report[layer] = {
            "status": "written",
            **{
                k: manifest[k]
                for k in ("bytes", "element_count", "element_types", "osm_base_timestamp")
            },
        }
        print(f"{layer}: {report[layer]}", file=sys.stderr, flush=True)

    json.dump(report, sys.stdout, indent=2)
    print()
    return 1 if any(v["status"] == "failed" for v in report.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
