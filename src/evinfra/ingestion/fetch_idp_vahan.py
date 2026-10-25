"""Fetch India Data Portal "Vehicle Registrations" tables (compiled from the VAHAN dashboard).

India Data Portal (ISB Bharti Institute) publishes monthly VAHAN registrations by state
and RTO as separate one-attribute tables under ODC-BY. Each table is a different marginal
of the same registrations; no table crosses fuel type with vehicle class. Tables fetched:
    fuel_type      S24  registration_type = fuel label
    vehicle_class  S27  vehicle_class (Transport/Non Transport) + registration_type = class

The script reads resource metadata from the portal's CKAN API, downloads the CSV (the
portal redirects to signed storage), and saves it byte-for-byte to data/raw/ without
overwriting. A sidecar manifest records the CKAN metadata, final host, hash, size, header.

Uses only the standard library. Run from the repository root:
    python src/evinfra/ingestion/fetch_idp_vahan.py --table fuel_type|vehicle_class
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
CKAN = "https://ckandev.indiadataportal.com/api/3/action"
PACKAGE = "vehicle-registrations"
BASE_HEADER = ["id", "date", "state_name", "state_code", "rto", "rto_code"]
TABLES = {
    "fuel_type": {
        "dataset_id": "S24",
        "resource_id": "c9d109c7-8190-4a67-8166-0be1487db419",
        "stem": "S24_idp_vahan_registrations_by_fuel_type",
        "header": [*BASE_HEADER, "registration_type", "registrations"],
    },
    "vehicle_class": {
        "dataset_id": "S27",
        "resource_id": "cc32d3e2-7ea3-4b6b-94ab-85e57f6a0a3a",
        "stem": "S27_idp_vahan_registrations_by_vehicle_class",
        "header": [*BASE_HEADER, "vehicle_class", "registration_type", "registrations"],
    },
}
EXPECTED_HEADER = TABLES["fuel_type"]["header"]
USER_AGENT = "evinfra/0.1 (EV infrastructure research prototype)"


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())["result"]


def check_header(payload: bytes, expected: list[str] = EXPECTED_HEADER) -> list[str]:
    header = next(csv.reader(io.StringIO(payload[:4096].decode("utf-8-sig"))))
    if header != expected:
        raise ValueError(f"Unexpected CSV header: {header}")
    return header


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--table", choices=sorted(TABLES), default="fuel_type")
    args = parser.parse_args(argv)
    spec = TABLES[args.table]

    package = get_json(f"{CKAN}/package_show?id={PACKAGE}")
    resource = get_json(f"{CKAN}/resource_show?id={spec['resource_id']}")
    retrieved_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = RAW / f"{spec['stem']}_{retrieved_at[:10]}.csv"
    if out.exists():
        raise SystemExit(f"{out} already exists; raw files are never overwritten")

    request = urllib.request.Request(resource["url"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=900) as response:
        payload = response.read()
        final_host = urllib.parse.urlsplit(response.geturl()).netloc
    check_header(payload, spec["header"])
    if resource.get("size") and int(resource["size"]) != len(payload):
        raise SystemExit(f"Size mismatch: CKAN says {resource['size']}, got {len(payload)}")

    manifest = {
        "dataset_id": spec["dataset_id"],
        "package": {
            "name": package["name"],
            "title": package["title"],
            "license_id": package.get("license_id"),
            "license_title": package.get("license_title"),
            "metadata_modified": package.get("metadata_modified"),
        },
        "resource": {
            "id": resource["id"],
            "name": resource.get("name"),
            "url": resource["url"],
            "format": resource.get("format"),
            "size": resource.get("size"),
            "last_modified": resource.get("last_modified"),
        },
        "redirect_host": final_host,
        "retrieved_at": retrieved_at,
        "local_filename": out.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "header": spec["header"],
    }
    out.write_bytes(payload)
    out.with_name(out.name + ".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    json.dump(manifest, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
