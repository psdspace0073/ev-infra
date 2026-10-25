"""Minimal standard-library reader for OSM PBF files (DenseNodes, ways, relations).

Written because pyosmium's native extension is blocked by Windows Application Control on
the project machine. It supports what the S23 layer build needs and nothing more:

    select(path, specs) -> {layer: [element, ...]}

reads a PBF in three streaming passes (relations, then ways, then nodes) and returns
Overpass-style element dicts for every element accepted by a layer spec:
    nodes      {"type": "node", "id", "lat", "lon", "tags"}
    ways       {"type": "way", "id", "tags", "geometry": [{"lat", "lon"}, ...]}
    relations  {"type": "relation", "id", "tags", "members": [{"type", "ref", "role",
               "geometry": [...] for way members}]}
Coordinates are only kept for nodes that a selected element needs, in compact arrays.
Missing referenced nodes or ways (outside the extract) are counted, never invented.
"""

from __future__ import annotations

import struct
import zlib
from array import array
from bisect import bisect_left
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from itertools import accumulate
from pathlib import Path

Tags = dict[str, str]


@dataclass(frozen=True)
class LayerSpec:
    """Which elements a layer takes. `match` sees the element's tags."""

    name: str
    match: Callable[[Tags], bool]
    node: bool = True
    way: bool = True
    relation: bool = True


class PbfReadError(ValueError):
    """Raised when the PBF cannot be decoded."""


# ---------------------------------------------------------------- protobuf


def varint(buf: bytes, pos: int) -> tuple[int, int]:
    result = shift = 0
    while True:
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if b < 0x80:
            return result, pos
        shift += 7


def fields(buf: bytes) -> Iterator[tuple[int, int | bytes]]:
    pos, n = 0, len(buf)
    while pos < n:
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
            raise PbfReadError(f"Unsupported wire type {wire}")
        yield num, value


def unpack(buf: bytes) -> list[int]:
    """Packed unsigned varints."""
    out: list[int] = []
    append = out.append
    v = shift = 0
    for b in buf:
        if b < 0x80:
            append(v | (b << shift))
            v = shift = 0
        else:
            v |= (b & 0x7F) << shift
            shift += 7
    return out


def zz(v: int) -> int:
    return (v >> 1) ^ -(v & 1)


def int64(v: int) -> int:
    """Plain (non-zigzag) int64 varint: negative values arrive as two's complement."""
    return v - (1 << 64) if v >= 1 << 63 else v


def unpack_delta(buf: bytes) -> list[int]:
    """Packed zigzag (sint64) varints, delta-coded."""
    return list(accumulate(map(zz, unpack(buf))))


def blocks(path: Path) -> Iterator[bytes]:
    """Yield the decompressed payload of every OSMData block."""
    with open(path, "rb") as f:
        while True:
            head = f.read(4)
            if not head:
                return
            if len(head) < 4:
                raise PbfReadError("Truncated block length")
            (hlen,) = struct.unpack(">I", head)
            btype, datasize = None, None
            for num, value in fields(f.read(hlen)):
                if num == 1:
                    btype = value.decode("utf-8")
                elif num == 3:
                    datasize = value
            if datasize is None:
                raise PbfReadError("Block header without datasize")
            blob = f.read(datasize)
            if btype != "OSMData":
                continue
            raw = zdata = None
            for num, value in fields(blob):
                if num == 1:
                    raw = value
                elif num == 3:
                    zdata = value
            if raw is None and zdata is None:
                raise PbfReadError("Unsupported blob compression")
            yield raw if raw is not None else zlib.decompress(zdata)


def primitive_block(data: bytes) -> tuple[list[str], list[bytes], tuple[int, int, int]]:
    strings: list[str] = []
    groups: list[bytes] = []
    gran, lat_off, lon_off = 100, 0, 0
    for num, value in fields(data):
        if num == 1:
            strings = [s.decode("utf-8") for n, s in fields(value) if n == 1]
        elif num == 2:
            groups.append(value)
        elif num == 17:
            gran = value
        elif num == 19:
            lat_off = int64(value)
        elif num == 20:
            lon_off = int64(value)
    return strings, groups, (gran, lat_off, lon_off)


def kv_tags(keys: list[int], vals: list[int], strings: list[str]) -> Tags:
    return {strings[k]: strings[v] for k, v in zip(keys, vals)}


# ---------------------------------------------------------------- element streams


def iter_relations(path: Path) -> Iterator[tuple[int, Tags, list[tuple[str, int, str]]]]:
    types = ("node", "way", "relation")
    for data in blocks(path):
        strings, groups, _ = primitive_block(data)
        for group in groups:
            for num, rel in fields(group):
                if num != 4:
                    continue
                rid, keys, vals, roles, memids, mtypes = 0, [], [], [], [], []
                for n, v in fields(rel):
                    if n == 1:
                        rid = v
                    elif n == 2:
                        keys = unpack(v)
                    elif n == 3:
                        vals = unpack(v)
                    elif n == 8:
                        roles = unpack(v)
                    elif n == 9:
                        memids = unpack_delta(v)
                    elif n == 10:
                        mtypes = unpack(v)
                members = [(types[t], ref, strings[r]) for t, ref, r in zip(mtypes, memids, roles)]
                yield rid, kv_tags(keys, vals, strings), members


def iter_ways(path: Path) -> Iterator[tuple[int, Tags, bytes]]:
    """Yield (id, tags, packed refs). Refs stay packed until a way is selected."""
    for data in blocks(path):
        strings, groups, _ = primitive_block(data)
        for group in groups:
            for num, way in fields(group):
                if num != 3:
                    continue
                wid, keys, vals, refs = 0, [], [], b""
                for n, v in fields(way):
                    if n == 1:
                        wid = v
                    elif n == 2:
                        keys = unpack(v)
                    elif n == 3:
                        vals = unpack(v)
                    elif n == 8:
                        refs = v
                yield wid, kv_tags(keys, vals, strings), refs


def iter_nodes(path: Path) -> Iterator[tuple[int, float, float, Tags]]:
    for data in blocks(path):
        strings, groups, (gran, lat_off, lon_off) = primitive_block(data)
        for group in groups:
            for num, value in fields(group):
                if num == 2:  # DenseNodes
                    ids = lats = lons = kv = None
                    for n, v in fields(value):
                        if n == 1:
                            ids = unpack_delta(v)
                        elif n == 8:
                            lats = unpack_delta(v)
                        elif n == 9:
                            lons = unpack_delta(v)
                        elif n == 10:
                            kv = unpack(v)
                    if ids is None:
                        continue
                    k = 0
                    for i, nid in enumerate(ids):
                        tags: Tags = {}
                        if kv:
                            while kv[k]:
                                tags[strings[kv[k]]] = strings[kv[k + 1]]
                                k += 2
                            k += 1
                        yield (
                            nid,
                            (lat_off + gran * lats[i]) * 1e-9,
                            (lon_off + gran * lons[i]) * 1e-9,
                            tags,
                        )
                elif num == 1:  # plain Node
                    nid, keys, vals, lat, lon = 0, [], [], 0, 0
                    for n, v in fields(value):
                        if n == 1:
                            nid = zz(v)
                        elif n == 2:
                            keys = unpack(v)
                        elif n == 3:
                            vals = unpack(v)
                        elif n == 8:
                            lat = zz(v)
                        elif n == 9:
                            lon = zz(v)
                    yield (
                        nid,
                        (lat_off + gran * lat) * 1e-9,
                        (lon_off + gran * lon) * 1e-9,
                        kv_tags(keys, vals, strings),
                    )


# ---------------------------------------------------------------- selection


def select(path: Path, specs: list[LayerSpec]) -> tuple[dict[str, list[dict]], dict]:
    report: dict = {"missing_way_members": 0, "missing_node_refs": 0}

    # Pass 1: relations.
    rel_hits: dict[int, tuple[Tags, list]] = {}
    rel_layers: dict[int, list[str]] = {}
    for rid, tags, members in iter_relations(path):
        names = [s.name for s in specs if s.relation and s.match(tags)]
        if names:
            rel_hits[rid] = (tags, members)
            rel_layers[rid] = names
    member_ways = {ref for _, mem in rel_hits.values() for t, ref, _ in mem if t == "way"}
    member_nodes = {ref for _, mem in rel_hits.values() for t, ref, _ in mem if t == "node"}

    # Pass 2: ways (selected by tags, or members of selected relations).
    way_refs: dict[int, list[int]] = {}
    way_tags: dict[int, Tags] = {}
    way_layers: dict[int, list[str]] = {}
    for wid, tags, refs in iter_ways(path):
        names = [s.name for s in specs if s.way and s.match(tags)]
        if names or wid in member_ways:
            way_refs[wid] = unpack_delta(refs)
            if names:
                way_tags[wid] = tags
                way_layers[wid] = names
    report["missing_way_members"] = len(member_ways - way_refs.keys())

    # Pass 3: nodes (tagged hits, plus coordinates for every needed node).
    needed = sorted({n for refs in way_refs.values() for n in refs} | member_nodes)
    need_ids = array("q", needed)
    need_lat = array("d", bytes(8 * len(needed)))
    need_lon = array("d", bytes(8 * len(needed)))
    found = bytearray(len(needed))
    out: dict[str, list[dict]] = {s.name: [] for s in specs}
    for nid, lat, lon, tags in iter_nodes(path):
        if need_ids:
            i = bisect_left(need_ids, nid)
            if i < len(need_ids) and need_ids[i] == nid:
                need_lat[i], need_lon[i], found[i] = lat, lon, 1
        if tags:
            for s in specs:
                if s.node and s.match(tags):
                    out[s.name].append(
                        {
                            "type": "node",
                            "id": nid,
                            "lat": round(lat, 7),
                            "lon": round(lon, 7),
                            "tags": tags,
                        }
                    )
    report["missing_node_refs"] = len(found) - sum(found)

    def coord(nid: int) -> dict | None:
        i = bisect_left(need_ids, nid)
        if i < len(need_ids) and need_ids[i] == nid and found[i]:
            return {"lat": round(need_lat[i], 7), "lon": round(need_lon[i], 7)}
        return None

    def way_geometry(wid: int) -> list[dict | None]:
        return [coord(n) for n in way_refs.get(wid, [])]

    for wid, names in way_layers.items():
        element = {"type": "way", "id": wid, "tags": way_tags[wid], "geometry": way_geometry(wid)}
        for name in names:
            out[name].append(element)
    for rid, (tags, members) in rel_hits.items():
        mem = []
        for t, ref, role in members:
            m = {"type": t, "ref": ref, "role": role}
            if t == "way":
                m["geometry"] = way_geometry(ref) if ref in way_refs else []
            elif t == "node":
                c = coord(ref)
                if c:
                    m.update(c)
            mem.append(m)
        for name in rel_layers[rid]:
            out[name].append({"type": "relation", "id": rid, "tags": tags, "members": mem})
    report["needed_nodes"] = len(needed)
    return out, report
