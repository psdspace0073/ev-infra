"""Tests for S21 checks, the stdlib PBF reader, S22 response checks and the S23 build."""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

import pytest

from evinfra.analysis import build_osm_karnataka_layers as bol
from evinfra.ingestion import fetch_osm_karnataka_extract as fox
from evinfra.ingestion import fetch_osm_karnataka_layers as fol
from evinfra.ingestion import osm_pbf

# ---------------------------------------------------------------- tiny PBF writer


def enc_varint(n: int) -> bytes:
    n &= (1 << 64) - 1
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def f_bytes(num: int, value: bytes) -> bytes:
    return enc_varint(num << 3 | 2) + enc_varint(len(value)) + value


def f_int(num: int, value: int) -> bytes:
    return enc_varint(num << 3) + enc_varint(value)


def zz_enc(v: int) -> int:
    return (v << 1) ^ (v >> 63)


def packed(values) -> bytes:
    return b"".join(enc_varint(v) for v in values)


def packed_delta(values) -> bytes:
    prev, out = 0, []
    for v in values:
        out.append(zz_enc(v - prev))
        prev = v
    return packed(out)


def block(btype: str, data: bytes, corrupt_size: bool = False) -> bytes:
    blob = f_int(2, len(data) + (1 if corrupt_size else 0)) + f_bytes(3, zlib.compress(data))
    header = f_bytes(1, btype.encode()) + f_int(3, len(blob))
    return struct.pack(">I", len(header)) + header + blob


def header_block() -> bytes:
    return (
        f_bytes(4, b"OsmSchema-V0.6")
        + f_bytes(4, b"DenseNodes")
        + f_bytes(16, b"test-writer")
        + f_int(32, 1_792_721_345)  # 2026-10-23T02:09:05Z
        + f_int(33, 7340635)
    )


class PbfBuilder:
    """Collect nodes, ways and relations and encode one PrimitiveBlock per element kind."""

    def __init__(self):
        self.strings = [""]
        self.nodes, self.ways, self.relations = [], [], []

    def s(self, text: str) -> int:
        if text not in self.strings:
            self.strings.append(text)
        return self.strings.index(text)

    def node(self, nid, lon, lat, **tags):
        self.nodes.append((nid, lon, lat, tags))

    def way(self, wid, refs, **tags):
        self.ways.append((wid, refs, tags))

    def relation(self, rid, members, **tags):
        self.relations.append((rid, members, tags))

    def _block(self, group: bytes) -> bytes:
        table = f_bytes(1, b"".join(f_bytes(1, s.encode()) for s in self.strings))
        return block("OSMData", table + f_bytes(2, group))

    def encode(self) -> bytes:
        nodes = sorted(self.nodes)
        kv = []
        for _, _, _, tags in nodes:
            for k, v in tags.items():
                kv += [self.s(k), self.s(v)]
            kv.append(0)
        ways = b""
        for wid, refs, tags in self.ways:
            ks = [self.s(k) for k in tags]
            vs = [self.s(v) for v in tags.values()]
            ways += f_bytes(
                3,
                f_int(1, wid)
                + f_bytes(2, packed(ks))
                + f_bytes(3, packed(vs))
                + f_bytes(8, packed_delta(refs)),
            )
        rels = b""
        types = {"node": 0, "way": 1, "relation": 2}
        for rid, members, tags in self.relations:
            ks = [self.s(k) for k in tags]
            vs = [self.s(v) for v in tags.values()]
            rels += f_bytes(
                4,
                f_int(1, rid)
                + f_bytes(2, packed(ks))
                + f_bytes(3, packed(vs))
                + f_bytes(8, packed([self.s(r) for _, _, r in members]))
                + f_bytes(9, packed_delta([ref for _, ref, _ in members]))
                + f_bytes(10, packed([types[t] for t, _, _ in members])),
            )
        dense = (
            f_bytes(1, packed_delta([n[0] for n in nodes]))
            + f_bytes(8, packed_delta([round(n[2] * 1e7) for n in nodes]))
            + f_bytes(9, packed_delta([round(n[1] * 1e7) for n in nodes]))
            + f_bytes(10, packed(kv))
        )
        out = block("OSMHeader", header_block()) + self._block(f_bytes(2, dense))
        if ways:
            out += self._block(ways)
        if rels:
            out += self._block(rels)
        return out


# ---------------------------------------------------------------- S21 checks


def test_check_pbf_reads_header_and_counts_blocks():
    payload = block("OSMHeader", header_block()) + block("OSMData", b"x" * 50) * 2
    out = fox.check_pbf(payload)
    assert out["blocks"] == {"OSMHeader": 1, "OSMData": 2}
    assert out["required_features"] == ["OsmSchema-V0.6", "DenseNodes"]
    assert out["writing_program"] == "test-writer"
    assert out["replication_timestamp"] == "2026-10-23T02:09:05Z"
    assert out["replication_sequence_number"] == 7340635


def test_check_pbf_rejects_truncated_file():
    payload = block("OSMHeader", header_block()) + block("OSMData", b"x" * 50)
    with pytest.raises(fox.PbfError):
        fox.check_pbf(payload[:-5])


def test_check_pbf_rejects_size_mismatch():
    payload = block("OSMHeader", header_block()) + block("OSMData", b"x", corrupt_size=True)
    with pytest.raises(fox.PbfError, match="inflated"):
        fox.check_pbf(payload)


def test_check_pbf_requires_header_and_data():
    with pytest.raises(fox.PbfError, match="OSMHeader"):
        fox.check_pbf(block("OSMData", b"x"))
    with pytest.raises(fox.PbfError, match="OSMData"):
        fox.check_pbf(block("OSMHeader", header_block()))


def test_parse_state_unescapes_colons():
    state = fox.parse_state("sequenceNumber=7340635\ntimestamp=2026-10-23T02\\:09\\:05Z\n")
    assert state == {"sequenceNumber": "7340635", "timestamp": "2026-10-23T02:09:05Z"}


# ---------------------------------------------------------------- PBF reader


def test_varint_helpers():
    assert osm_pbf.unpack(packed([0, 1, 300, 2**40])) == [0, 1, 300, 2**40]
    assert osm_pbf.unpack_delta(packed_delta([5, 3, -10, 2**35])) == [5, 3, -10, 2**35]
    assert osm_pbf.int64(2**64 - 7) == -7  # two's-complement int64
    assert osm_pbf.int64(7) == 7


def test_reader_roundtrips_nodes_ways_relations(tmp_path):
    b = PbfBuilder()
    b.node(1, 77.5, 12.9, amenity="fuel", name="A")
    b.node(2, 77.6, 13.0)
    b.node(3, -0.5, -1.25)
    b.way(10, [1, 2, 3], highway="primary")
    b.relation(20, [("way", 10, "outer"), ("node", 1, "")], type="multipolygon", amenity="parking")
    path = tmp_path / "t.osm.pbf"
    path.write_bytes(b.encode())
    nodes = list(osm_pbf.iter_nodes(path))
    assert [n[0] for n in nodes] == [1, 2, 3]
    assert nodes[0][1] == pytest.approx(12.9) and nodes[0][2] == pytest.approx(77.5)
    assert nodes[2][1] == pytest.approx(-1.25) and nodes[2][2] == pytest.approx(-0.5)
    assert nodes[0][3] == {"amenity": "fuel", "name": "A"} and nodes[1][3] == {}
    ((wid, wtags, refs),) = list(osm_pbf.iter_ways(path))
    assert (wid, wtags, osm_pbf.unpack_delta(refs)) == (10, {"highway": "primary"}, [1, 2, 3])
    ((rid, rtags, members),) = list(osm_pbf.iter_relations(path))
    assert rid == 20 and rtags["amenity"] == "parking"
    assert members == [("way", 10, "outer"), ("node", 1, "")]


def test_select_keeps_only_needed_coordinates_and_counts_missing(tmp_path):
    b = PbfBuilder()
    b.node(1, 1.0, 1.0)
    b.node(2, 2.0, 2.0)
    b.node(5, 5.0, 5.0, amenity="fuel")
    b.way(10, [1, 2, 99], highway="primary")  # node 99 is not in the file
    b.way(11, [1, 2], highway="residential")
    path = tmp_path / "t.osm.pbf"
    path.write_bytes(b.encode())
    specs = [
        osm_pbf.LayerSpec("roads", lambda t: t.get("highway") == "primary", node=False),
        osm_pbf.LayerSpec("fuel", lambda t: t.get("amenity") == "fuel"),
    ]
    out, report = osm_pbf.select(path, specs)
    (road,) = out["roads"]
    assert road["id"] == 10
    assert road["geometry"][:2] == [{"lat": 1.0, "lon": 1.0}, {"lat": 2.0, "lon": 2.0}]
    assert road["geometry"][2] is None
    assert report["missing_node_refs"] == 1
    assert [e["id"] for e in out["fuel"]] == [5]


# ---------------------------------------------------------------- S22 checks


def test_layer_response_rejects_remark_and_empty():
    with pytest.raises(ValueError, match="remark"):
        fol.summarise(json.dumps({"remark": "timeout", "elements": [{"type": "node"}]}).encode())
    with pytest.raises(ValueError, match="no elements"):
        fol.summarise(json.dumps({"elements": []}).encode())


def test_layer_queries_use_karnataka_area_and_full_geometry():
    for layer in fol.layer_names():
        q = (fol.QUERIES / f"osm_ka_{layer}.overpassql").read_text(encoding="utf-8")
        assert '"ISO3166-2"="IN-KA"' in q
        assert "out geom tags" not in q  # 'tags' verbosity drops geometry
    for layer in ("roads_major", "power_lines", "boundary"):
        q = (fol.QUERIES / f"osm_ka_{layer}.overpassql").read_text(encoding="utf-8")
        assert q.strip().endswith("out geom;")


# ---------------------------------------------------------------- S23 geometry

POLY = "karnataka\n1\n 0.0 0.0\n 10.0 0.0\n 10.0 10.0\n 0.0 10.0\n 0.0 0.0\nEND\nEND\n"


def test_parse_poly_single_ring_closed():
    rings = bol.parse_poly(POLY)
    assert len(rings) == 1
    assert rings[0][0] == rings[0][-1] == (0.0, 0.0)


def test_parse_poly_rejects_holes_and_truncation():
    with pytest.raises(bol.LayerError, match="holes"):
        bol.parse_poly(POLY.replace("END\nEND\n", "END\n!2\n 1 1\n 2 2\n 1 1\nEND\nEND\n"))
    with pytest.raises(bol.LayerError, match="Malformed"):
        bol.parse_poly("karnataka\n1\n 0 0\n 1 1\n")


def test_banded_polygon_matches_simple_cases():
    poly = bol.BandedPolygon(
        [[(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)], [(1, 1), (2, 1), (2, 2), (1, 2), (1, 1)]]
    )
    assert poly.contains(3, 3)
    assert not poly.contains(1.5, 1.5)  # hole
    assert not poly.contains(5, 5)


def test_assemble_rings_joins_reversed_segments():
    rings = bol.assemble_rings([[(0, 0), (1, 0)], [(1, 1), (1, 0)], [(1, 1), (0, 1), (0, 0)]])
    assert len(rings) == 1 and rings[0][0] == rings[0][-1] and len(rings[0]) == 5


def test_assemble_rings_rejects_open_ring():
    with pytest.raises(bol.LayerError, match="does not close"):
        bol.assemble_rings([[(0, 0), (1, 0)], [(1, 0), (1, 1)]])


def member(coords, role="outer", ref=1):
    return {
        "type": "way",
        "ref": ref,
        "role": role,
        "geometry": [{"lon": x, "lat": y} for x, y in coords],
    }


def test_relation_multipolygon_orients_rings_and_places_holes():
    rel = {
        "members": [
            member([(0, 0), (0, 4), (4, 4), (4, 0), (0, 0)]),
            member([(1, 1), (2, 1), (2, 2), (1, 2), (1, 1)], role="inner"),
            member([(10, 10), (11, 10), (11, 11), (10, 10)]),
        ]
    }
    polys = bol.relation_multipolygon(rel)
    assert len(polys) == 2
    assert bol.signed_area(polys[0][0]) > 0 and len(polys[0]) == 2
    assert bol.signed_area(polys[0][1]) < 0
    assert len(polys[1]) == 1


def test_boundary_with_missing_member_nodes_is_an_error():
    m = member([(0, 0), (0, 4), (4, 4), (0, 0)])
    m["geometry"][1] = None
    with pytest.raises(bol.LayerError, match="missing nodes"):
        bol.relation_multipolygon({"members": [m]})
    with pytest.raises(bol.LayerError, match="no outer member geometry"):
        bol.relation_multipolygon({"members": []})


def test_feature_points_centres_and_lines():
    f, _ = bol.feature(
        {"type": "node", "id": 1, "lat": 2.0, "lon": 3.0, "tags": {"amenity": "x"}}, False
    )
    assert f["geometry"] == {"type": "Point", "coordinates": [3.0, 2.0]}
    assert f["properties"] == {"@id": "node/1", "@type": "node", "amenity": "x"}
    way = {
        "type": "way",
        "id": 2,
        "tags": {},
        "geometry": [{"lat": 0, "lon": 0}, None, {"lat": 2, "lon": 4}],
    }
    centre, missing = bol.feature(way, False)
    assert (
        centre["geometry"]["coordinates"] == [2.0, 1.0]
        and centre["properties"]["@geometry"] == "center"
    )
    assert missing == 1
    line, missing = bol.feature(way, True)
    assert line["geometry"]["coordinates"] == [[0, 0], [4, 2]] and missing == 1
    none, _ = bol.feature({"type": "way", "id": 3, "tags": {}, "geometry": [None]}, True)
    assert none is None


# ---------------------------------------------------------------- S23 build


def install(raw: Path) -> None:
    raw.mkdir(parents=True)
    (raw / "S21_osmfr_karnataka_2026-10-23.poly").write_text(POLY, encoding="utf-8")
    b = PbfBuilder()
    corners = [(101, 1, 1), (102, 9, 1), (103, 9, 9), (104, 1, 9)]
    for nid, x, y in corners:
        b.node(nid, x, y)
    b.way(201, [101, 102, 103])
    b.way(202, [104, 103][::-1] + [101])  # 103 -> 104 -> 101, joins to close the ring
    b.relation(
        300,
        [("way", 201, "outer"), ("way", 202, "outer")],
        boundary="administrative",
        admin_level="4",
        **{"ISO3166-2": "IN-KA"},
        name="Karnataka",
    )
    b.node(1, 5, 5, amenity="fuel")
    b.node(2, 9.5, 9.5, amenity="fuel")  # outside admin boundary, inside extract polygon
    b.node(3, 2, 2)
    b.node(4, 3, 3)
    b.way(400, [3, 4], highway="primary")
    b.way(401, [3, 4, 999], highway="secondary")  # node 999 missing
    b.way(402, [3, 4], highway="residential")
    b.node(5, 6, 6)
    b.node(6, 7, 6)
    b.node(7, 7, 7)
    b.way(500, [5, 6, 7, 5], amenity="parking")
    (raw / "S21_osmfr_karnataka_2026-10-23.osm.pbf").write_bytes(b.encode())
    overpass = {
        "osm3s": {"timestamp_osm_base": "2026-10-25T00:00:00Z"},
        "elements": [{"type": "node", "id": 1, "lat": 5, "lon": 5}],
    }
    (raw / "S22_osm_ka_fuel_overpass_2026-10-25.json").write_text(
        json.dumps(overpass), encoding="utf-8"
    )


def test_build_layers_flags_and_boundaries(tmp_path):
    install(tmp_path / "raw")
    outputs, summary = bol.build(tmp_path / "raw")
    admin = outputs[bol.OUT_ADMIN]["features"]
    assert len(admin) == 1 and len(outputs[bol.OUT_POLY]["features"]) == 1
    assert admin[0]["geometry"]["type"] == "MultiPolygon"
    assert summary["boundary"]["outer_vertices_outside_extract_polygon"] == 0

    fuel = outputs["S23_osm_ka_fuel.geojson"]["features"]
    assert [f["properties"]["@id"] for f in fuel] == ["node/1", "node/2"]
    assert fuel[1]["properties"]["@outside_admin_boundary"] == "yes"
    assert "@outside_admin_boundary" not in fuel[0]["properties"]
    assert summary["layers"]["fuel"]["inside_admin_boundary"] == 1
    assert summary["overpass_cross_check"]["fuel"]["elements"] == 1

    roads = {
        f["properties"]["@id"]: f for f in outputs["S23_osm_ka_roads_major.geojson"]["features"]
    }
    assert sorted(roads) == ["way/400", "way/401"]  # residential excluded
    assert summary["layers"]["roads_major"]["features_with_missing_vertices"] == 1
    assert summary["pbf_read"]["missing_node_refs"] == 1

    (parking,) = outputs["S23_osm_ka_parking.geojson"]["features"]
    assert parking["geometry"]["coordinates"] == [6.5, 6.5]
    assert parking["properties"]["@geometry"] == "center"


def test_build_requires_exactly_one_admin_relation(tmp_path):
    raw = tmp_path / "raw"
    install(raw)
    b = PbfBuilder()
    b.node(1, 5, 5, amenity="fuel")
    (raw / "S21_osmfr_karnataka_2026-10-23.osm.pbf").write_bytes(b.encode())
    with pytest.raises(bol.LayerError, match="Expected 1 Karnataka admin relation"):
        bol.build(raw)


def test_build_is_deterministic(tmp_path):
    install(tmp_path / "a")
    install(tmp_path / "b")
    assert bol.build(tmp_path / "a") == bol.build(tmp_path / "b")
