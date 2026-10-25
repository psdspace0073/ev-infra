"""Fetch S21: the Karnataka-only OSM extract from download.openstreetmap.fr.

OpenStreetMap France publishes daily state-level extracts for India. This script saves,
byte-for-byte and never overwriting, into data/raw/:
    the .osm.pbf extract, its published .md5 file, the replication state file and the
    .poly polygon used to cut the extract,
then checks the MD5, walks every PBF block (each zlib payload must inflate to its
declared size) and reads the PBF header (bounding box, replication timestamp). A
sidecar manifest records URLs, HTTP validators, hashes and the checks.

Uses only the standard library. Run from the repository root:
    python src/evinfra/ingestion/fetch_osm_karnataka_extract.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import urllib.request
import zlib
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
BASE = "https://download.openstreetmap.fr"
URLS = {
    "pbf": f"{BASE}/extracts/asia/india/karnataka.osm.pbf",
    "md5": f"{BASE}/extracts/asia/india/karnataka.osm.pbf.md5",
    "state": f"{BASE}/extracts/asia/india/karnataka.state.txt",
    "poly": f"{BASE}/polygons/asia/india/karnataka.poly",
}
USER_AGENT = "evinfra/0.1 (EV infrastructure research prototype)"


class PbfError(ValueError):
    """Raised when a file is not a structurally valid OSM PBF."""


# ---------------------------------------------------------------- protobuf helpers


def varint(buf: bytes, pos: int) -> tuple[int, int]:
    result = shift = 0
    while True:
        if pos >= len(buf):
            raise PbfError("Truncated varint")
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            return result, pos
        shift += 7


def fields(buf: bytes):
    """Yield (field number, wire type, value) for a protobuf message."""
    pos = 0
    while pos < len(buf):
        key, pos = varint(buf, pos)
        num, wire = key >> 3, key & 7
        if wire == 0:
            value, pos = varint(buf, pos)
        elif wire == 2:
            size, pos = varint(buf, pos)
            value, pos = buf[pos : pos + size], pos + size
        elif wire == 1:
            value, pos = buf[pos : pos + 8], pos + 8
        elif wire == 5:
            value, pos = buf[pos : pos + 4], pos + 4
        else:
            raise PbfError(f"Unsupported wire type {wire}")
        yield num, wire, value


def zigzag(n: int) -> int:
    return (n >> 1) ^ -(n & 1)


def blob_data(blob: bytes) -> bytes:
    raw_size, raw, zdata = None, None, None
    for num, _, value in fields(blob):
        if num == 1:
            raw = value
        elif num == 2:
            raw_size = value
        elif num == 3:
            zdata = value
    if raw is not None:
        return raw
    if zdata is None:
        raise PbfError("Blob has neither raw nor zlib data")
    data = zlib.decompress(zdata)
    if raw_size is not None and len(data) != raw_size:
        raise PbfError(f"Blob inflated to {len(data)} bytes, header says {raw_size}")
    return data


def check_pbf(payload: bytes) -> dict:
    """Walk every block; return header facts and block counts."""
    pos, blocks, header = 0, {}, None
    while pos < len(payload):
        if pos + 4 > len(payload):
            raise PbfError("Truncated block length")
        (hlen,) = struct.unpack(">I", payload[pos : pos + 4])
        pos += 4
        btype, datasize = None, None
        for num, _, value in fields(payload[pos : pos + hlen]):
            if num == 1:
                btype = value.decode("utf-8")
            elif num == 3:
                datasize = value
        pos += hlen
        if btype is None or datasize is None or pos + datasize > len(payload):
            raise PbfError(f"Malformed or truncated block header at byte {pos}")
        data = blob_data(payload[pos : pos + datasize])
        pos += datasize
        blocks[btype] = blocks.get(btype, 0) + 1
        if btype == "OSMHeader":
            header = parse_header(data)
    if header is None:
        raise PbfError("No OSMHeader block")
    if not blocks.get("OSMData"):
        raise PbfError("No OSMData blocks")
    return {**header, "blocks": blocks}


def parse_header(data: bytes) -> dict:
    out: dict = {"required_features": [], "optional_features": []}
    for num, _, value in fields(data):
        if num == 1:
            box = {n: zigzag(v) / 1e9 for n, _, v in fields(value)}
            out["bbox"] = {
                "min_lon": box.get(1),
                "max_lon": box.get(2),
                "max_lat": box.get(3),
                "min_lat": box.get(4),
            }
        elif num == 4:
            out["required_features"].append(value.decode("utf-8"))
        elif num == 5:
            out["optional_features"].append(value.decode("utf-8"))
        elif num == 16:
            out["writing_program"] = value.decode("utf-8")
        elif num == 32:
            out["replication_timestamp"] = datetime.fromtimestamp(value, UTC).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        elif num == 33:
            out["replication_sequence_number"] = value
        elif num == 34:
            out["replication_base_url"] = value.decode("utf-8")
    return out


def parse_state(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().replace("\\:", ":")
    return out


# ---------------------------------------------------------------- main


def get(url: str) -> tuple[bytes, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=600) as response:
        payload = response.read()
        headers = {k: response.headers.get(k) for k in ("Last-Modified", "ETag", "Content-Length")}
    return payload, headers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)

    retrieved_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    got = {name: get(url) for name, url in URLS.items()}
    state = parse_state(got["state"][0].decode("utf-8"))
    snapshot = state.get("timestamp", retrieved_at)[:10]
    stem = f"S21_osmfr_karnataka_{snapshot}"
    names = {
        "pbf": f"{stem}.osm.pbf",
        "md5": f"{stem}.osm.pbf.md5",
        "state": f"{stem}.state.txt",
        "poly": f"{stem}.poly",
    }
    for name in names.values():
        if (RAW / name).exists():
            raise SystemExit(f"{RAW / name} already exists; raw files are never overwritten")

    pbf = got["pbf"][0]
    published_md5 = got["md5"][0].decode("ascii").split()[0].lower()
    actual_md5 = hashlib.md5(pbf).hexdigest()
    if actual_md5 != published_md5:
        raise SystemExit(f"MD5 mismatch: published {published_md5}, downloaded {actual_md5}")
    if b"\nEND" not in got["poly"][0]:  # first line is a free-text name; rings end with END
        raise SystemExit("Polygon file does not look like an Osmosis .poly file")
    pbf_check = check_pbf(pbf)

    files = {}
    for key, name in names.items():
        payload, headers = got[key]
        (RAW / name).write_bytes(payload)
        files[key] = {
            "url": URLS[key],
            "local_filename": (RAW / name).relative_to(ROOT).as_posix(),
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "http_headers": headers,
        }
    manifest = {
        "dataset_id": "S21",
        "publisher": "OpenStreetMap France (download.openstreetmap.fr); data (c) OpenStreetMap contributors, ODbL 1.0",
        "retrieved_at": retrieved_at,
        "replication_state": state,
        "md5_published": published_md5,
        "md5_verified": True,
        "pbf_check": pbf_check,
        "files": files,
    }
    manifest_path = RAW / f"{names['pbf']}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    json.dump(manifest, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
