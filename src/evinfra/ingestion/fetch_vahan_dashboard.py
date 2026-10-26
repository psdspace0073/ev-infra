"""Fetch Karnataka report exports from the public VAHAN dashboard (register S29).

The VAHAN dashboard report view (vahan.parivahan.gov.in/vahan4dashboard, "Report View")
is a public JSF page with no login and no CAPTCHA (checked 26 Oct 2026). This script sends
the same requests as the page: choose state, office (RTO), Y-axis, X-axis and calendar
year, press Refresh, tick fuel filters in the side panel and press its refresh, then
click "Download EXCEL file". The .xlsx returned is saved unchanged; it is never
overwritten. The export title states the office and year but NOT the fuel filter, so the
filter is recorded in the batch manifest for every file.

Jobs:
    bev_class_month     each Karnataka office x calendar year 2022-2026; Y = Vehicle Class,
                        X = Month Wise; fuel = ELECTRIC(BOV) + PURE EV (battery-EV)
    allfuel_class_month offices/years with months absent from S24 (KA45, KA46, KA57);
                        Y = Vehicle Class, X = Month Wise; no fuel filter (all fuels)
    state_fuel_month    all Karnataka offices together, 2022-2026; Y = Fuel, X = Month Wise;
                        no fuel filter
    state_class_month   all Karnataka offices together, 2025-2026; Y = Vehicle Class,
                        X = Month Wise; no fuel filter (to compare with the Transport
                        Department's monthly statements by vehicle category)

Requests are spaced by --delay seconds (default 1.0). Uses only the standard library.
Run from the repository root:
    python src/evinfra/ingestion/fetch_vahan_dashboard.py --job bev_class_month [--out DIR]
"""

from __future__ import annotations

import argparse
import hashlib
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
USER_AGENT = "evinfra/0.1 (EV infrastructure research prototype)"
FORM = "masterLayout_formlogin"
STATE = "KA"
YEARS = ["2022", "2023", "2024", "2025", "2026"]
BEV_FUELS = {"4": "ELECTRIC(BOV)", "23": "PURE EV"}
REFRESH = ("j_idt68", "VhCatg norms fuel VhClass combTablePnl groupingTable msg vhCatgPnl")
FILTER_REFRESH = ("j_idt77", "combTablePnl")
# KA57 2021 is added to test KA57 against the Transport Department's 2021-22 district totals.
GAP_YEARS = {"45": ["2025", "2026"], "46": ["2026"], "57": ["2021", "2022", "2023", "2025", "2026"]}
JOBS = {
    "bev_class_month": {"yaxis": "Vehicle Class", "fuels": list(BEV_FUELS)},
    "allfuel_class_month": {"yaxis": "Vehicle Class", "fuels": []},
    "state_fuel_month": {"yaxis": "Fuel", "fuels": []},
    "state_class_month": {"yaxis": "Vehicle Class", "fuels": [], "years": ["2025", "2026"]},
}
OFFICE_RE = re.compile(r"^(?P<name>.*?)\s+-\s+KA(?P<code>\d+)\(\s*(?P<since>[^)]*?)\s*\)$")


class DashboardError(RuntimeError):
    pass


class Session:
    """One JSF view; keeps cookies, form values and the current ViewState."""

    def __init__(self, delay: float):
        self.delay = delay
        jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        page = self._open(None).decode("utf-8", "replace")
        self.fields = form_fields(page)
        self.view_state = view_state(page)
        self.fuel_labels = fuel_labels(page)

    def _open(self, items: list[tuple[str, str]] | None, ajax: bool = False) -> bytes:
        time.sleep(self.delay)
        headers = {"User-Agent": USER_AGENT}
        body = None
        if items is not None:
            body = urllib.parse.urlencode(items).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        if ajax:
            headers.update({"Faces-Request": "partial/ajax", "X-Requested-With": "XMLHttpRequest"})
        request = urllib.request.Request(URL, body, headers)
        with self.opener.open(request, timeout=120) as response:
            return response.read()

    def ajax(self, source, render, process="@all", event=None, values=None, fuels=()):
        if values:
            self.fields.update(values)
        items = list(self.fields.items()) + [("fuel", f) for f in fuels]
        items += [
            ("javax.faces.partial.ajax", "true"),
            ("javax.faces.source", source),
            ("javax.faces.partial.execute", process),
            ("javax.faces.partial.render", render),
            ("javax.faces.ViewState", self.view_state),
        ]
        if event:
            items += [("javax.faces.behavior.event", event), ("javax.faces.partial.event", event)]
        else:
            items.append((source, source))
        text = self._open(items, ajax=True).decode("utf-8", "replace")
        match = re.search(r'javax.faces.ViewState[^"]*"><!\[CDATA\[([^\]]+)\]\]>', text)
        if match:
            self.view_state = match.group(1)
        if "<error>" in text or "viewExpired" in text:
            raise DashboardError(f"{source}: dashboard returned an error")
        return text

    def change(self, select_id: str, value: str, render: str) -> str:
        return self.ajax(select_id, render, select_id, "change", {f"{select_id}_input": value})

    def export(self, fuels=()) -> tuple[bytes, str]:
        items = list(self.fields.items()) + [("fuel", f) for f in fuels]
        items += [
            ("groupingTable:xls", "groupingTable:xls"),
            ("javax.faces.ViewState", self.view_state),
        ]
        data = self._open(items)
        if not data.startswith(b"PK"):
            raise DashboardError("export did not return an xlsx file")
        return data, xlsx_title(data)


def form_fields(page: str) -> dict[str, str]:
    fields = {}
    for name, value in re.findall(
        r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', page
    ):
        fields[name] = html.unescape(value)
    for sid, body in re.findall(
        r'<select id="([^"]+)" name="[^"]*"[^>]*>(.*?)</select>', page, re.DOTALL
    ):
        chosen = re.search(r'<option value="([^"]*)" selected', body) or re.search(
            r'<option value="([^"]*)"', body
        )
        fields[sid] = html.unescape(chosen.group(1)) if chosen else ""
    fields.pop("javax.faces.ViewState", None)
    fields[FORM] = FORM
    return fields


def view_state(page: str) -> str:
    match = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', page)
    if not match:
        raise DashboardError("no ViewState on the report page")
    return match.group(1)


def fuel_labels(page: str) -> dict[str, str]:
    pairs = re.findall(
        r'<input id="fuel:\d+" name="fuel" type="checkbox" value="([^"]*)"[^>]*/?>\s*'
        r"(?:<[^>]*>\s*)*?<label[^>]*>([^<]*)",
        page,
    )
    return {value: html.unescape(label) for value, label in pairs}


def select_options(xml: str, select_id: str) -> list[tuple[str, str]]:
    match = re.search(
        rf'<select id="{re.escape(select_id)}_input"[^>]*>(.*?)</select>', xml, re.DOTALL
    )
    if not match:
        return []
    return [
        (v, html.unescape(t).strip())
        for v, t in re.findall(r'<option value="([^"]*)"[^>]*>([^<]*)</option>', match.group(1))
    ]


def parse_offices(options: list[tuple[str, str]]) -> list[dict[str, str]]:
    offices = []
    for value, label in options:
        match = OFFICE_RE.match(label)
        if match:
            offices.append(
                {
                    "value": value,
                    "rto_code": f"KA{int(match.group('code'))}",
                    "office_name": re.sub(r"\s+", " ", match.group("name")).strip(),
                    "vahan4_since": match.group("since"),
                }
            )
    return offices


def xlsx_title(data: bytes) -> str:
    """Text of the first shared string (the report title) without unpacking to disk."""
    import io
    import zipfile

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        shared = z.read("xl/sharedStrings.xml").decode("utf-8")
    match = re.search(r"<t[^>]*>([^<]*)</t>", shared)
    return html.unescape(match.group(1)).strip() if match else ""


def check_title(title: str, rto_code: str | None, year: str) -> None:
    if f"({year})" not in title:
        raise DashboardError(f"export title {title!r} does not show year {year}")
    if rto_code and not re.search(rf"- {rto_code}\s*,", title):
        raise DashboardError(f"export title {title!r} does not show office {rto_code}")


def tasks(job: str, offices: list[dict[str, str]]) -> list[tuple[dict | None, str]]:
    if job.startswith("state_"):
        return [(None, y) for y in JOBS[job].get("years", YEARS)]
    if job == "allfuel_class_month":
        by_value = {o["value"]: o for o in offices}
        return [(by_value[v], y) for v, years in GAP_YEARS.items() for y in years]
    return [(o, y) for o in offices for y in YEARS]


def run(job: str, out: Path, delay: float, limit: int | None = None) -> dict:
    spec = JOBS[job]
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {"dataset_id": "S29", "source_url": URL, "job": job, "files": {}}
    )
    session = Session(delay)
    for value, label in BEV_FUELS.items() if spec["fuels"] else []:
        if session.fuel_labels.get(value) != label:
            raise DashboardError(f"fuel {value} is {session.fuel_labels.get(value)!r}, not {label}")
    states = session.change("j_idt37", STATE, "selectedRto yaxisVar")
    session.fields["j_idt27_input"] = "A"  # Actual Value
    offices = parse_offices(select_options(states, "selectedRto"))
    if not offices:
        raise DashboardError("no Karnataka offices listed")
    manifest.update(
        {
            "offices": offices,
            "fuel_labels_on_page": session.fuel_labels,
            "settings": {
                "type": "Actual Value",
                "state": "Karnataka",
                "y_axis": spec["yaxis"],
                "x_axis": "Month Wise",
                "year_type": "Calendar Year",
                "fuel_filter": {v: BEV_FUELS[v] for v in spec["fuels"]} or "none (all fuels)",
            },
        }
    )
    current_office = object()
    done = 0
    for office, year in tasks(job, offices):
        code = office["rto_code"] if office else "KA_all"
        name = f"{code}_{year}.xlsx"
        if name in manifest["files"] and (out / name).exists():
            continue
        if limit is not None and done >= limit:
            break
        if office is not current_office:
            session.change("selectedRto", office["value"] if office else "-1", "yaxisVar")
            session.change("yaxisVar", spec["yaxis"], "xaxisVar")
            session.change("xaxisVar", "Month Wise", "multipleYear")
            session.change("selectedYearType", "C", "selectedYear")
            current_office = office
        session.change("selectedYear", year, "selectedYear")
        session.ajax(*REFRESH)
        if spec["fuels"]:
            session.ajax(*FILTER_REFRESH, fuels=spec["fuels"])
        data, title = session.export(spec["fuels"])
        check_title(title, office["rto_code"] if office else None, year)
        path = out / name
        if path.exists():
            if path.read_bytes() != data:
                raise DashboardError(f"{path} exists with different content; not overwritten")
        else:
            path.write_bytes(data)
        manifest["files"][name] = {
            "rto_code": code,
            "office_value": office["value"] if office else "-1",
            "year": year,
            "title": title,
            "retrieved_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        done += 1
        print(f"{name}: {title}", flush=True)
    return {"job": job, "fetched": done, "files": len(manifest["files"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--job", choices=sorted(JOBS), required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args(argv)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    out = args.out or RAW / f"S29_vahan_dashboard_ka_{args.job}_{stamp}"
    for attempt in range(1, 4):
        try:
            print(json.dumps(run(args.job, out, args.delay, args.limit)))
            return 0
        except (DashboardError, OSError) as exc:  # new session, resume from manifest
            print(f"attempt {attempt}: {exc}", file=sys.stderr, flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
