"""Download official documents unchanged into data/raw/ with a sidecar manifest.

Each document in DOCUMENTS has a register ID, a URL and a local file name. The file is
saved byte-for-byte and never overwritten; a re-download must be byte-identical or the
script stops. The manifest records the URL, final URL, HTTP status, content type,
Last-Modified, size, SHA-256 and retrieval time.

Uses only the standard library. Run from the repository root:
    python src/evinfra/ingestion/fetch_official_documents.py [ID ...]
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
USER_AGENT = "evinfra/0.1 (EV infrastructure research prototype)"
KT = "https://transport.karnataka.gov.in"

# Karnataka State monthly statements (S25), keyed by the 'AS ON' month printed in the file.
# The file published as 'KAR AUG 2026' prints 'AS ON 31-08-2026' but repeats the September
# 2026 figures; it is kept as published (see register S25).
S25_STATEMENTS = {
    "2023-04": f"{KT}/storage/pdf-files/apr%2023%20kar%20data%20new1.pdf",
    "2023-05": f"{KT}/storage/pdf-files/MAY%2023%20KAR%20DATA.pdf",
    "2023-06": f"{KT}/storage/pdf-files/JUN%2023%20KAR%20DATA.pdf",
    "2023-07": f"{KT}/storage/pdf-files/JULYKAR23.pdf",
    "2023-08": f"{KT}/storage/pdf-files/AUGKAR23.pdf",
    "2023-09": f"{KT}/storage/pdf-files/SEPKAR23.pdf",
    "2023-10": f"{KT}/storage/pdf-files/OCTKAR23.pdf",
    "2023-11": f"{KT}/storage/pdf-files/NOVKAR23.pdf",
    "2023-12": f"{KT}/storage/pdf-files/deckar23.pdf",
    "2024-01": f"{KT}/storage/pdf-files/JANKAR2024.pdf",
    "2024-02": f"{KT}/storage/pdf-files/VEHKAR2024.pdf",
    "2024-03": f"{KT}/storage/pdf-files/MARKARDATA.pdf",
    "2024-04": f"{KT}/storage/pdf-files/APRILKARDATA.pdf",
    "2024-05": f"{KT}/storage/pdf-files/may24kardata.pdf",
    "2024-06": f"{KT}/storage/pdf-files/KARJUN24.pdf",
    "2024-07": f"{KT}/storage/pdf-files/JULYKAR24.pdf",
    "2024-08": f"{KT}/storage/pdf-files/AUGKAR2024.pdf",
    "2024-09": f"{KT}/storage/pdf-files/sepkar24.pdf",
    "2024-10": f"{KT}/storage/pdf-files/KAROCT24.pdf",
    "2024-11": f"{KT}/storage/pdf-files/KARNOV24.pdf",
    "2024-12": f"{KT}/storage/pdf-files/DECKAR24.pdf",
    "2025-01": f"{KT}/storage/pdf-files/KARJAN25.pdf",
    "2025-02": f"{KT}/storage/pdf-files/KARFEB25.pdf",
    "2025-03": f"{KT}/storage/pdf-files/KARMAR25.pdf",
    "2025-04": f"{KT}/uploads/media_to_upload1757142005.pdf",
    "2025-05": f"{KT}/uploads/media_to_upload1757142098.pdf",
    "2025-06": f"{KT}/uploads/media_to_upload1757142173.pdf",
    "2025-07": f"{KT}/uploads/media_to_upload1757142333.pdf",
    "2025-08": f"{KT}/uploads/media_to_upload1757142424.pdf",
    "2025-09": f"{KT}/uploads/media_to_upload1770021624.pdf",
    "2025-10": f"{KT}/uploads/media_to_upload1770023874.pdf",
    "2025-11": f"{KT}/uploads/media_to_upload1770023947.pdf",
    "2025-12": f"{KT}/uploads/media_to_upload1770024233.pdf",
    "2026-01": f"{KT}/uploads/KAR%20JAN%202026_1779690274.pdf",
    "2026-02": f"{KT}/uploads/KAR%20FEB%202026_1779691311.pdf",
    "2026-03": f"{KT}/uploads/KAR%20MAR%202026_1779692199.pdf",
    "2026-04": f"{KT}/uploads/KAR%20APR%202026_1779693400.pdf",
    "2026-05": f"{KT}/uploads/KAR%20MAY%202026_1782132604.pdf",
    "2026-06": f"{KT}/uploads/KAR%20June%202026_1783928001.pdf",
    "2026-07": f"{KT}/uploads/KAR%20July%202026_1792134229.pdf",
    "2026-08": f"{KT}/uploads/KAR%20AUG%202026_1792135291.pdf",
    "2026-09": f"{KT}/uploads/KAR%20SEP%202026_1792135895.pdf",
}

# (register ID, key, URL, local file name)
DOCUMENTS = [
    (
        "S30",
        "kt_annual_report_2021_22_en",
        f"{KT}/storage/pdf-files/annual%20report%202022-202-397.pdf",
        "S30_ka_transport_annual_report_2021-22_english.pdf",
    ),
    *(
        (
            "S25",
            f"kt_statement_kar_{month}",
            url,
            f"S25_ka_transport_monthly_statement_KAR_{month}.pdf",
        )
        for month, url in S25_STATEMENTS.items()
    ),
    (
        "S15",
        "bee_copyright_policy",
        "https://www.beeindia.gov.in/show_content.php?lang=1&level=1&ls_id=379&lid=232",
        "S15_bee_website_copyright_policy_2026-10-26.html",
    ),
    (
        "S33",
        "mop_evci_guidelines_2024",
        "https://beeindia.gov.in/WriteReadData/L45218/2841453721548450.pdf",
        "S33_mop_evci_guidelines_2024-09-17.pdf",
    ),
    (
        "S34",
        "mhi_pm_edrive_ev_pcs_guidelines",
        (
            "https://pmedrive.heavyindustries.gov.in/docs/policy_document/"
            "EV%20PCS%20operational%20guidelines_F.pdf"
        ),
        "S34_mhi_pm_edrive_ev_pcs_operational_guidelines_2025-09-26.pdf",
    ),
    (
        "S34",
        "mhi_pm_edrive_ev_pcs_faq",
        (
            "https://pmedrive.heavyindustries.gov.in/docs/policy_document/"
            "FAQs-Operational%20Guidelines%20for%20EV%20PCS%20under%20PM%20E-DRIVE.pdf"
        ),
        "S34_mhi_pm_edrive_ev_pcs_faq.pdf",
    ),
]


def fetch(url: str) -> tuple[bytes, dict]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=300) as response:
        data = response.read()
        meta = {
            "final_url": response.geturl(),
            "http_status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "last_modified": response.headers.get("Last-Modified"),
        }
    return data, meta


def save(dataset_id: str, key: str, url: str, name: str, raw: Path = RAW) -> dict:
    path = raw / name
    data, meta = fetch(url)
    digest = hashlib.sha256(data).hexdigest()
    if path.exists():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"{path} exists with different content; not overwritten")
        status = "unchanged"
    else:
        raw.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        status = "written"
    manifest = {
        "dataset_id": dataset_id,
        "document": key,
        "source_url": url,
        **meta,
        "retrieved_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "local_filename": f"data/raw/{name}",
        "bytes": len(data),
        "sha256": digest,
    }
    manifest_path = path.with_name(path.name + ".manifest.json")
    if status == "written" or not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"file": name, "status": status, "sha256": digest, "bytes": len(data)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ids", nargs="*", help="register IDs or keys (default: all)")
    args = parser.parse_args(argv)
    chosen = [d for d in DOCUMENTS if not args.ids or d[0] in args.ids or d[1] in args.ids]
    results = [save(*d) for d in chosen]
    json.dump(results, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
