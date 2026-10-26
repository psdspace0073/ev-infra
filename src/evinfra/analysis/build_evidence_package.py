"""Build and audit the Round 1 evidence package (Stage 5 rebuild) from repository data.

Inputs (all read, none changed):
    data/processed/S26_summary.json, S28_summary.json, S28_ka_ev_monthly_state.csv,
    S28_ka_ev_annual_rto.csv          registrations (from S24, S27; checked against S01)
    data/processed/S18_S19_summary.json, S18_karnataka_bee_pcs_rows.csv,
    S19_karnataka_bee_pcs_sites.csv   BEE charger rows and candidate sites (from S15)
    data/processed/S12_karnataka_district_charger_join.csv   31 LGD districts, OSM counts
    configs/ka_rto_district_crosswalk.csv, configs/source_register.csv
    Optional: the manual Stage 3 BEE extraction CSV (untracked); used only to state why
    its count is superseded.

Outputs:
    outputs/reports/evidence_package/claim_register.csv
    outputs/reports/evidence_package/district_charger_supply.csv
    outputs/reports/evidence_package/audit.json
    docs/submission/claim_register.csv (tracked copy; written only with --update-docs,
    otherwise compared)

Statuses: verified_reproducible (recomputed from repo data in this run), official_reported
(value transcribed from an official document; the transcription is in the register),
unresolved (open discrepancy, cause not determined), not_computable (blocked by missing
evidence), superseded (do not cite).

The audit fails the build if a district-level demand claim is not "not_computable" while no
crosswalk row is verified, if a superseded figure appears in any other claim, if a register
ID is unknown, or if a transcribed official value is absent from its register row.

Uses only the standard library. Run from the repository root:
    python src/evinfra/analysis/build_evidence_package.py [--force] [--update-docs]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from evinfra.analysis import build_district_table as bdt

ROOT = bdt.ROOT
PROC = bdt.OUT_DIR
OUT_DIR = ROOT / "outputs" / "reports" / "evidence_package"
DOCS_COPY = ROOT / "docs" / "submission" / "claim_register.csv"
REGISTER = ROOT / "configs" / "source_register.csv"
CROSSWALK = ROOT / "configs" / "ka_rto_district_crosswalk.csv"
STAGE3_BEE = (
    ROOT
    / "data"
    / "manual inspection reports"
    / "improving the charging demand analysis"
    / "karnataka_bee_station_records_extracted_stage3.csv"
)
INPUTS = {
    "s26_summary": PROC / "S26_summary.json",
    "s28_summary": PROC / "S28_summary.json",
    "s28_monthly": PROC / "S28_ka_ev_monthly_state.csv",
    "s28_annual": PROC / "S28_ka_ev_annual_rto.csv",
    "s18_summary": PROC / "S18_S19_summary.json",
    "s18_rows": PROC / "S18_karnataka_bee_pcs_rows.csv",
    "s19_sites": PROC / "S19_karnataka_bee_pcs_sites.csv",
    "s12_join": PROC / "S12_karnataka_district_charger_join.csv",
    "s35_long": PROC / "S35_ka_bev_rto_class_month.csv",
    "s35_summary": PROC / "S35_summary.json",
    "s32_summary": PROC / "S32_summary.json",
    "crosswalk": CROSSWALK,
    "register": REGISTER,
}

# Official values read by hand from PDF/HTML sources. Each must appear, formatted as here,
# in the register row of its source (checked by the audit).
OFFICIAL = {
    "S25_sep_2026_new_registrations": ("S25", 181753),
    "S25_dec_2025_new_registrations": ("S25", 130313),
    "S17_ka_evcs_installed": ("S17", 6096),
    "S17_ka_evcs_fast": ("S17", 751),
    "S17_ka_evcs_slow": ("S17", 5345),
    "S03_ka_pcs_installed": ("S03", 6097),
}
SUPERSEDED_FIGURES = ("6,113",)
STATUSES = {
    "verified_reproducible",
    "official_reported",
    "unresolved",
    "not_computable",
    "superseded",
}
CLAIM_COLUMNS = [
    "claim_id",
    "topic",
    "metric",
    "geography_level",
    "claim",
    "register_ids",
    "derivation",
    "status",
    "caveat",
]
SUPPLY_COLUMNS = [
    "lgd_district_code",
    "lgd_district_name",
    "bee_rows_by_point",
    "bee_candidate_sites_by_point",
    "osm_mapped_records",
    "ev_registrations",
    "ev_registrations_status",
]


def n(value: int) -> str:
    return f"{value:,}"


def pct(num: float, den: float) -> str:
    return f"{100 * num / den:+.2f}%"


def read_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load(paths: dict[str, Path]) -> dict:
    return {
        "s26": read_json(paths["s26_summary"]),
        "s28": read_json(paths["s28_summary"]),
        "monthly": {r["month_end_date"]: r for r in bdt.read_csv(paths["s28_monthly"])},
        "annual": bdt.read_csv(paths["s28_annual"]),
        "s18": read_json(paths["s18_summary"]),
        "s18_rows": bdt.read_csv(paths["s18_rows"]),
        "s19_sites": bdt.read_csv(paths["s19_sites"]),
        "s12": bdt.read_csv(paths["s12_join"]),
        "s35": bdt.read_csv(paths["s35_long"]),
        "s35_summary": read_json(paths["s35_summary"]),
        "s32": read_json(paths["s32_summary"]),
        "crosswalk": bdt.read_csv(paths["crosswalk"]),
        "register": bdt.read_csv(paths["register"]),
    }


def coord_key(lat: str, lon: str) -> tuple[float, float] | None:
    try:
        return (round(float(lat), 6), round(float(lon), 6))
    except ValueError:
        return None


def compare_stage3(s18_rows: list[dict[str, str]], stage3: Path | None) -> dict | None:
    """Match the manual Stage 3 extraction to S18 by coordinate pair (multiset)."""
    if stage3 is None or not stage3.exists():
        return None
    rows = bdt.read_csv(stage3)
    c3 = Counter(coord_key(r["latitude"], r["longitude"]) for r in rows)
    c18 = Counter(coord_key(r["latitude"], r["longitude"]) for r in s18_rows)
    return {
        "sha256": hashlib.sha256(stage3.read_bytes()).hexdigest(),
        "rows": len(rows),
        "rows_without_coordinates": c3[None],
        "s18_rows_unmatched": sum(max(0, v - c3.get(k, 0)) for k, v in c18.items()),
        "stage3_rows_not_in_s18": sum(
            max(0, v - c18.get(k, 0)) for k, v in c3.items() if k is not None
        ),
    }


UNIT_COLUMNS = [
    "unit_lgd_codes",
    "unit_name",
    "rto_codes",
    "bev_registrations_2025",
    "bee_rows_by_point",
    "bee_candidate_sites_by_point",
    "bev_2025_per_bee_site",
]
UNIT_YEAR = "2025"
CAVEAT_OFFICE = (
    "Registration office geography, not owner residence: Vahan applications may be filed "
    "at any office in Karnataka (S30 section 3.3). Grouping as in the Transport "
    "Department's 2021-22 district statistics (check S31)."
)


def is_verified(row: dict[str, str]) -> bool:
    return row["status"].startswith("verified_official")


def district_units(data: dict) -> list[dict[str, str]]:
    """One row per crosswalk unit (one LGD code, or several joined by ';')."""
    names = {r["lgd_district_code"]: r["lgd_district_name"] for r in data["s12"]}
    rows_by = Counter(r["lgd_district_code_by_point"] for r in data["s18_rows"])
    sites_by = Counter(r["lgd_district_code_by_point"] for r in data["s19_sites"])
    bev_by_rto: Counter = Counter()
    for r in data["s35"]:
        if r["month_end_date"].startswith(UNIT_YEAR):
            bev_by_rto[r["rto_code"]] += int(r["bev_registrations"])
    units: dict[str, list[str]] = {}
    for r in data["crosswalk"]:
        if is_verified(r):
            units.setdefault(r["lgd_district_code"], []).append(r["rto_code_vahan"])
    out = []
    for unit, rtos in units.items():
        codes = unit.split(";")
        bev = sum(bev_by_rto[c] for c in rtos)
        sites = sum(sites_by.get(c, 0) for c in codes)
        out.append(
            {
                "unit_lgd_codes": unit,
                "unit_name": " + ".join(names.get(c, c) for c in codes),
                "rto_codes": " ".join(sorted(rtos, key=lambda c: int(c[2:]))),
                "bev_registrations_2025": str(bev),
                "bee_rows_by_point": str(sum(rows_by.get(c, 0) for c in codes)),
                "bee_candidate_sites_by_point": str(sites),
                "bev_2025_per_bee_site": f"{bev / sites:.1f}" if sites else "",
            }
        )
    return sorted(out, key=lambda r: -int(r["bev_registrations_2025"]))


def district_supply(data: dict, verified_rtos: int) -> list[dict[str, str]]:
    rows_by = Counter(r["lgd_district_code_by_point"] for r in data["s18_rows"])
    sites_by = Counter(r["lgd_district_code_by_point"] for r in data["s19_sites"])
    out = []
    for d in sorted(data["s12"], key=lambda r: r["lgd_district_name"]):
        code = d["lgd_district_code"]
        out.append(
            {
                "lgd_district_code": code,
                "lgd_district_name": d["lgd_district_name"],
                "bee_rows_by_point": str(rows_by.get(code, 0)),
                "bee_candidate_sites_by_point": str(sites_by.get(code, 0)),
                "osm_mapped_records": d["osm_mapped_charging_records"],
                "ev_registrations": "",
                "ev_registrations_status": (
                    "see district_unit_bev_supply.csv (registrations by district unit)"
                    if verified_rtos == len(data["crosswalk"])
                    else "not_computable: RTO-to-district crosswalk has "
                    f"{verified_rtos} of {len(data['crosswalk'])} RTOs verified"
                ),
            }
        )
    return out


def build_claims(data: dict, stage3: dict | None) -> tuple[list[dict[str, str]], dict]:
    s26, s28, s18 = data["s26"], data["s28"], data["s18"]
    monthly, annual = data["monthly"], data["annual"]
    verified_rtos = sum(1 for r in data["crosswalk"] if is_verified(r))
    complete = verified_rtos == len(data["crosswalk"])
    supply = district_supply(data, verified_rtos)
    units = district_units(data) if complete else []
    claims: list[dict[str, str]] = []

    def add(topic, metric, level, claim, ids, derivation, status, caveat=""):
        claims.append(
            {
                "claim_id": f"E{len(claims) + 1:02d}",
                "topic": topic,
                "metric": metric,
                "geography_level": level,
                "claim": claim,
                "register_ids": ids,
                "derivation": derivation,
                "status": status,
                "caveat": caveat,
            }
        )

    # Registrations
    add(
        "demand",
        "registration_rows",
        "state",
        f"The Karnataka VAHAN compilation has {n(s26['karnataka_source_rows'])} rows for "
        f"{s26['rtos']} RTOs over {s26['months']} months ({s26['first_month'][:7]} to "
        f"{s26['last_month'][:7]}).",
        "S24; S26",
        "S26_summary.json: karnataka_source_rows, rtos, months",
        "verified_reproducible",
        "Monthly new registrations (flows), not vehicle stock.",
    )
    bev = s28["annual_state_bev"]
    years = sorted(bev)
    add(
        "demand",
        "bev_new_registrations",
        "state",
        "Battery-EV new registrations in Karnataka: "
        + "; ".join(
            f"{y} {n(bev[y])}" + ("" if s28["annual_year_complete"][y] else " (Jan-Sep)")
            for y in years
        )
        + ".",
        "S24; S26; S28",
        "S28_summary.json: annual_state_bev",
        "verified_reproducible",
        "BEV = Electric(BOV) + Pure EV as published; hybrids are separate. The latest year "
        "is partial.",
    )
    peak = max(monthly.values(), key=lambda r: int(r["bev"]))
    add(
        "demand",
        "bev_new_registrations",
        "state",
        f"The highest monthly battery-EV registrations were {n(int(peak['bev']))} in "
        f"{peak['month_end_date'][:7]}.",
        "S26; S28",
        "S28_ka_ev_monthly_state.csv: max(bev)",
        "verified_reproducible",
    )
    last_full = max(y for y in years if s28["annual_year_complete"][y])
    top = sorted(
        (r for r in annual if r["year"] == last_full),
        key=lambda r: -float(r["share_of_state_bev"] or 0),
    )[:5]
    add(
        "demand",
        "bev_share_by_rto",
        "rto",
        f"Largest RTOs by {last_full} battery-EV registrations: "
        + "; ".join(
            f"{r['rto_code']} {r['rto_name']} {100 * float(r['share_of_state_bev']):.1f}%"
            for r in top
        )
        + ".",
        "S26; S28",
        "S28_ka_ev_annual_rto.csv: share_of_state_bev",
        "verified_reproducible",
        "RTO of registration, not where vehicles are used or charged. RTO names are not "
        "evidence of district membership.",
    )
    for y in years:
        chk = s26["s01_cross_check"][y]
        if "difference" not in chk:
            continue
        tri = data["s32"]["bev_triangulation"].get(y, {})
        in_missing = tri.get("vahan_bev_in_rto_months_missing_from_s24", 0)
        explained = abs(chk["difference"]) > 10 and abs(chk["difference"] + in_missing) <= 10
        status = (
            "verified_reproducible" if abs(chk["difference"]) <= 10 or explained else "unresolved"
        )
        if explained:
            caveat = (
                f"Battery-EV only. Explained (S32): S24 has no rows for RTO-months in which the "
                f"VAHAN dashboard now shows {in_missing} battery-EV registrations; current VAHAN "
                f"{n(tri['vahan_now_same_months'])} vs the S01 export "
                f"{tri['vahan_now_minus_s01']:+} (later revisions)."
            )
        elif status == "unresolved":
            caveat = (
                "Battery-EV only; not an all-fuel comparison. The S01 export date and filter "
                "settings were not recorded, so the cause cannot be located."
            )
        else:
            caveat = "Battery-EV only."
        add(
            "data_quality",
            "bev_new_registrations",
            "state",
            f"Battery-EV {y}: VAHAN compilation {n(chk['s26_bev'])} vs VAHAN dashboard export "
            f"{n(chk['s01_bev'])} (difference {chk['difference']:+,}, "
            f"{chk['difference_pct']:+.3f}%).",
            "S01; S24; S26; S29; S32" if explained else "S01; S24; S26",
            f"S26_summary.json: s01_cross_check.{y}"
            + ("; S32_summary.json: bev_triangulation" if explained else ""),
            status,
            caveat,
        )
    offset = data["s32"]["vahan_minus_official_pct"]
    for month, key in (
        ("2026-09-30", "S25_sep_2026_new_registrations"),
        ("2025-12-31", "S25_dec_2025_new_registrations"),
    ):
        ours = int(monthly[month]["all_fuel_total"])
        official = OFFICIAL[key][1]
        add(
            "data_quality",
            "all_fuel_new_registrations",
            "state",
            f"All-fuel new registrations {month[:7]}: VAHAN compilation {n(ours)} vs "
            f"Transport Department statement {n(official)} (difference {ours - official:+,}, "
            f"{pct(ours - official, official)} of the official value).",
            "S24; S25; S28; S29; S32",
            f"S28_ka_ev_monthly_state.csv: all_fuel_total {month}; S25 value transcribed "
            "from PDF (register S25); S32_summary.json: vahan_minus_official_pct",
            "unresolved",
            "All fuels, not battery-EV. A systematic difference: the VAHAN dashboard exceeds "
            f"the statements in {offset['months_vahan_higher']} of {offset['months']} months "
            f"({offset['min']}% to {offset['max']}%, median {offset['median']}%; S32). The "
            "cause (compilation cut-off or rules) is not published. No total was adjusted.",
        )
    by_rto = s28["rto_months_without_rows_by_rto"]
    missing_status = data["s32"]["missing_status"]
    add(
        "data_quality",
        "rto_month_coverage",
        "rto",
        f"{s28['rto_months_without_rows']} RTO-months have no published rows ("
        + ", ".join(f"{k} {v}" for k, v in sorted(by_rto.items()))
        + "); they are absent in both the fuel and class tables and are kept blank.",
        "S24; S26; S27; S28; S29; S32",
        "S28_summary.json: rto_months_without_rows_by_rto; S32_missing_rto_month_register.csv",
        "unresolved" if "no_vahan_evidence" in missing_status else "verified_reproducible",
        "Classified with VAHAN dashboard evidence (S32): "
        + "; ".join(f"{k} {v}" for k, v in sorted(missing_status.items()))
        + ". 'vahan_reports_registrations' months are absent from S24 only; "
        "'vahan_reports_zero' months show 0 for every vehicle class. Kept blank in S26; "
        "never imputed.",
    )
    cons = s28["s24_vs_s27_consistency"]
    add(
        "data_quality",
        "all_fuel_new_registrations",
        "rto",
        f"The fuel and vehicle-class tables agree on the total in {n(cons['equal_totals'])} "
        f"of {n(cons['rto_months_compared'])} RTO-months.",
        "S24; S27; S28",
        "S28_summary.json: s24_vs_s27_consistency",
        "verified_reproducible",
        "; ".join(
            f"{d['rto_code']} {d['month_end_date'][:7]} absent in the class table"
            for d in cons["differences"]
            if d["s27_class_total"] is None
        ),
    )
    s35 = data["s35_summary"]
    if s35.get("missing_exports") == []:
        total = sum(s35["class_totals"].values())
        status_count = s35["rto_month_status"]
        add(
            "demand",
            "bev_by_vehicle_class",
            "rto",
            f"Battery-EV registrations by vehicle class are available for {s35['offices']} "
            f"offices by month to {s35['last_month'][:7]} ({s35['vehicle_classes']} vehicle "
            "classes); largest classes over the period: "
            + "; ".join(
                f"{k} {100 * v / total:.1f}%" for k, v in list(s35["class_totals"].items())[:3]
            )
            + ".",
            "S29; S35",
            "S35_summary.json: class_totals, rto_month_status",
            "verified_reproducible",
            f"Per RTO-month the VAHAN total equals S26 in {n(status_count.get('equal', 0))} and "
            f"differs in {n(status_count.get('differs', 0))} (net {s35['sum_of_differences']:+}, "
            f"largest {s35['largest_abs_difference']}; later revisions). Registering office, "
            "not owner location.",
        )
    else:
        add(
            "demand",
            "bev_by_vehicle_class",
            "rto",
            "Battery-EV registrations by vehicle class at RTO level are not complete: "
            f"{len(s35.get('missing_exports', ['?']))} VAHAN exports missing.",
            "S29; S35",
            "S35_summary.json: missing_exports",
            "not_computable",
            "Complete the S29 bev_class_month batch and rebuild S35.",
        )

    # Charging supply
    add(
        "supply",
        "bee_charger_rows",
        "state",
        f"The BEE location-wise list has {n(s18['karnataka_rows'])} Karnataka rows "
        f"({n(s18['karnataka_connectors'])} connectors); {n(s18['rows_with_valid_coordinates'])}"
        f" have valid coordinates; they form {n(s18['candidate_physical_sites'])} candidate "
        "sites.",
        "S15; S16; S18; S19",
        "S18_S19_summary.json: karnataka_rows, karnataka_connectors, "
        "rows_with_valid_coordinates, candidate_physical_sites",
        "verified_reproducible",
        f"Installed, not operational: {s18['rows_with_known_operating_status']} rows have an "
        "operating status. Licence not stated. Extracted from a PDF; no official spreadsheet "
        "to compare with.",
    )
    if stage3 is not None:
        add(
            "supply",
            "bee_charger_rows",
            "state",
            f"A manual Stage 3 extraction of the same BEE PDF gave {n(stage3['rows'])} "
            f"Karnataka records. It is incomplete: {n(stage3['s18_rows_unmatched'])} S18 rows "
            f"have no match by coordinates, {n(stage3['rows_without_coordinates'])} Stage 3 "
            f"rows have no coordinates and {n(stage3['stage3_rows_not_in_s18'])} Stage 3 "
            "rows are absent from S18.",
            "S15; S18",
            f"Coordinate multiset match, Stage 3 file sha256 {stage3['sha256'][:12]}",
            "superseded",
            "Do not cite the Stage 3 count; use the S18 figures.",
        )
    add(
        "supply",
        "official_station_count",
        "state",
        f"MHI (Lok Sabha written reply, PIB, 16 Dec 2025): "
        f"{n(OFFICIAL['S17_ka_evcs_installed'][1])} EV charging stations installed in "
        f"Karnataka during the last five years ({n(OFFICIAL['S17_ka_evcs_fast'][1])} fast, "
        f"{n(OFFICIAL['S17_ka_evcs_slow'][1])} slow). PIB annexure with Ministry of Power "
        f"inputs (file dated Aug 2025): {n(OFFICIAL['S03_ka_pcs_installed'][1])} public EV "
        "charging stations installed.",
        "S03; S17",
        "Values transcribed from official documents (register S03, S17)",
        "official_reported",
        "Stations, not BEE list rows or connectors; different dates and definitions; "
        "fast/slow not defined on the page. Not forced to match S18.",
    )
    add(
        "supply",
        "osm_charger_records",
        "state",
        f"OpenStreetMap has {s18['osm_records']} charging-station records in Karnataka; "
        f"{s18['osm_records_with_bee_site_within_100m']} are within 100 m of a BEE site.",
        "S10; S11; S18",
        "S18_S19_summary.json: osm_records, osm_records_with_bee_site_within_100m",
        "verified_reproducible",
        "OSM is incomplete for chargers; used as a secondary layer.",
    )
    rows_in_districts = sum(int(r["bee_rows_by_point"]) for r in supply)
    top_d = sorted(supply, key=lambda r: -int(r["bee_rows_by_point"]))[:3]
    add(
        "supply",
        "bee_charger_rows",
        "district",
        "BEE rows by district (point in Census 2011 district polygon, mapped to the LGD "
        f"code): {n(rows_in_districts)} rows; "
        f"{sum(1 for r in supply if int(r['bee_rows_by_point']))} of {len(supply)} districts "
        "have at least one row; the largest are "
        + "; ".join(f"{r['lgd_district_name']} {n(int(r['bee_rows_by_point']))}" for r in top_d)
        + ".",
        "S06; S18; S20",
        "S18_karnataka_bee_pcs_rows.csv: lgd_district_code_by_point; district names S12",
        "verified_reproducible",
        "Charger location is a point, so district assignment is valid for supply. Census "
        "2011 polygons: rows in Vijayanagara are counted in Ballari (the 2011 polygon "
        f"includes it). Stated and point districts disagree for "
        f"{n(s18['district_check']['disagree'])} rows; the point is used.",
    )

    # Geography
    combined = [u for u in units if ";" in u["unit_lgd_codes"]]
    single = sum(len(u["rto_codes"].split()) for u in units if u not in combined)
    add(
        "geography",
        "rto_district_crosswalk",
        "rto",
        f"{verified_rtos} of {len(data['crosswalk'])} RTOs have a verified district grouping"
        + (
            f": {single} map to one district; "
            + "; ".join(
                f"{u['rto_codes'].replace(' ', ', ')} to {u['unit_name']}" for u in combined
            )
            + "."
            if complete
            else "."
        ),
        "S24; S29; S30",
        "configs/ka_rto_district_crosswalk.csv: status; check S31_rto_district_grouping_check.json",
        "verified_reproducible" if complete else "unresolved",
        "Each unit's offices sum exactly to the Transport Department's district totals "
        "(31-03-2021 stock and 2021-22 new registrations). Office names and addresses are not "
        "used as evidence. Combined units are not split.",
    )
    if complete:
        total = sum(int(u["bev_registrations_2025"]) for u in units)
        add(
            "demand",
            "bev_new_registrations",
            "district",
            f"Battery-EV registrations in {UNIT_YEAR} by district unit ({len(units)} units, "
            f"{n(total)} in total), largest: "
            + "; ".join(
                f"{u['unit_name']} {n(int(u['bev_registrations_2025']))} "
                f"({100 * int(u['bev_registrations_2025']) / total:.1f}%)"
                for u in units[:3]
            )
            + ".",
            "S29; S30; S35",
            "S35_ka_bev_rto_class_month.csv summed by crosswalk unit",
            "verified_reproducible",
            CAVEAT_OFFICE,
        )
        ranked = sorted(
            (u for u in units if u["bev_2025_per_bee_site"]),
            key=lambda u: -float(u["bev_2025_per_bee_site"]),
        )
        add(
            "gap",
            "registrations_per_charger",
            "district",
            f"{UNIT_YEAR} battery-EV registrations per BEE candidate site by district unit range "
            f"from {ranked[-1]['bev_2025_per_bee_site']} ({ranked[-1]['unit_name']}) to "
            f"{ranked[0]['bev_2025_per_bee_site']} ({ranked[0]['unit_name']}).",
            "S19; S29; S30; S35",
            "district_unit_bev_supply.csv: bev_2025_per_bee_site",
            "verified_reproducible",
            "A screening indicator, not adequacy: new registrations in one year over installed "
            "(not necessarily operational) sites. " + CAVEAT_OFFICE,
        )
    else:
        add(
            "demand",
            "bev_new_registrations",
            "district",
            "Battery-EV registrations by district are not computable.",
            "S26",
            "configs/ka_rto_district_crosswalk.csv",
            "not_computable",
            "Registrations are by RTO; they are not split by population, area or name.",
        )
        add(
            "gap",
            "registrations_per_charger",
            "district",
            "Registrations per charger by district, and any district gap ranking that uses "
            "registrations, are not computable.",
            "S18; S26",
            "Depends on the district demand claim above",
            "not_computable",
            "Gap analysis can be shown at state level, or with supply-only district indicators.",
        )
    return claims, {"supply": supply, "units": units, "verified_rtos": verified_rtos}


def audit(claims: list[dict[str, str]], data: dict, context: dict) -> list[str]:
    errors = []
    known_ids = {r["dataset_id"] for r in data["register"]}
    register_text = {r["dataset_id"]: " | ".join(r.values()) for r in data["register"]}
    seen = set()
    for c in claims:
        if c["claim_id"] in seen:
            errors.append(f"{c['claim_id']}: duplicate claim_id")
        seen.add(c["claim_id"])
        if c["status"] not in STATUSES:
            errors.append(f"{c['claim_id']}: unknown status {c['status']}")
        for rid in (s.strip() for s in c["register_ids"].split(";")):
            if rid not in known_ids:
                errors.append(f"{c['claim_id']}: register ID {rid} not in source register")
        if c["status"] != "superseded":
            for fig in SUPERSEDED_FIGURES:
                if fig in c["claim"]:
                    errors.append(f"{c['claim_id']}: superseded figure {fig} cited")
        district_demand = c["geography_level"] == "district" and c["topic"] in {"demand", "gap"}
        if district_demand and c["status"] != "not_computable":
            if context["verified_rtos"] < len(data["crosswalk"]):
                errors.append(f"{c['claim_id']}: district demand claim without verified crosswalk")
            elif "Registration office geography" not in c["caveat"]:
                errors.append(f"{c['claim_id']}: district demand claim lacks the office caveat")
        if c["topic"] == "data_quality" and "difference" in c["claim"]:
            expected = {
                "bev_new_registrations": "Battery-EV",
                "all_fuel_new_registrations": "All-fuel",
            }.get(c["metric"])
            if expected is None or not c["claim"].startswith(expected):
                errors.append(f"{c['claim_id']}: discrepancy metric not stated in the claim")
    for name, (rid, value) in OFFICIAL.items():
        if n(value) not in register_text.get(rid, ""):
            errors.append(f"{name}: {n(value)} not found in register row {rid}")
    if any(r["ev_registrations_district"] for r in data["s12"]):
        errors.append("S12 has district EV registrations; they belong in the unit table")
    if context["units"]:
        in_units = sum(int(u["bee_rows_by_point"]) for u in context["units"])
        if in_units != data["s18"]["rows_with_point_district"]:
            errors.append(f"district units hold {in_units} BEE rows, not all point-district rows")
    in_districts = sum(int(r["bee_rows_by_point"]) for r in context["supply"])
    if in_districts != data["s18"]["rows_with_point_district"]:
        errors.append(
            f"district supply sums to {in_districts}, "
            f"S18 rows_with_point_district is {data['s18']['rows_with_point_district']}"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="replace outputs that differ")
    parser.add_argument(
        "--update-docs", action="store_true", help="write the tracked claim register copy"
    )
    parser.add_argument("--stage3-bee", type=Path, default=STAGE3_BEE)
    args = parser.parse_args(argv)

    data = load(INPUTS)
    stage3 = compare_stage3(data["s18_rows"], args.stage3_bee)
    claims, context = build_claims(data, stage3)
    errors = audit(claims, data, context)
    claim_bytes = bdt.to_csv_bytes(CLAIM_COLUMNS, claims)
    outputs = {
        "claim_register.csv": claim_bytes,
        "district_charger_supply.csv": bdt.to_csv_bytes(SUPPLY_COLUMNS, context["supply"]),
        "district_unit_bev_supply.csv": bdt.to_csv_bytes(UNIT_COLUMNS, context["units"]),
    }
    report = {
        "inputs_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS.values()
        },
        "stage3_comparison": stage3,
        "claims": len(claims),
        "claims_by_status": dict(sorted(Counter(c["status"] for c in claims).items())),
        "verified_rtos": context["verified_rtos"],
        "audit_errors": errors,
        "outputs_sha256": {k: hashlib.sha256(v).hexdigest() for k, v in outputs.items()},
    }
    outputs["audit.json"] = (json.dumps(report, indent=2) + "\n").encode("utf-8")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    status = {k: bdt.write_if_unchanged(OUT_DIR / k, v, args.force) for k, v in outputs.items()}
    if args.update_docs and not errors:
        DOCS_COPY.parent.mkdir(parents=True, exist_ok=True)
        DOCS_COPY.write_bytes(claim_bytes)
        status["docs_copy"] = "written"
    else:
        # Newline-insensitive: git may check the tracked copy out with CRLF.
        same = DOCS_COPY.exists() and DOCS_COPY.read_bytes().replace(b"\r\n", b"\n") == claim_bytes
        status["docs_copy"] = "same" if same else "differs"
    json.dump({**report, "write_status": status}, sys.stdout, indent=2)
    print()
    return 1 if errors or status["docs_copy"] == "differs" else 0


if __name__ == "__main__":
    raise SystemExit(main())
