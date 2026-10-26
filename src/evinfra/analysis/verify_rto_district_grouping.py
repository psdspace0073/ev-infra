"""Check RTO-to-district assignments against the Transport Department's own district totals.

Source (register S30): Karnataka Transport Department Annual Report 2021-22 (English part).
    Table 27  office-wise vehicles: total as on 31-03-2021, newly registered 2021-22
    Table 28  district-wise total vehicles registered (equals the 31-03-2021 column)
    Table 29  district-wise newly registered vehicles in 2021-22
The tables are printed rotated; text is read from character positions (pdfplumber).

For every report district, the offices assigned to it in configs/ka_rto_district_crosswalk.csv
must sum EXACTLY to the district's Table 28 total and Table 29 total. Every office in Table
27 must be assigned once. For districts with up to four offices the script also counts all
other office subsets that would match both totals (expected: none), so the grouping is
not just consistent but unique.

The report predates the Ballari/Vijayanagara split, so its BELLARY column is the pre-2021
district (LGD 528 + 738). Section 3.3 of the report lets the public file Vahan applications
at any office in Karnataka, so a district total counts registrations at the offices grouped
under the district, not vehicles owned by its residents.

Needs the optional extra 'pdf' (pdfplumber). Run from the repository root:
    python src/evinfra/analysis/verify_rto_district_grouping.py
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from evinfra.analysis import build_district_table as bdt

ROOT = bdt.ROOT
S30 = bdt.RAW / "S30_ka_transport_annual_report_2021-22_english.pdf"
CROSSWALK = ROOT / "configs" / "ka_rto_district_crosswalk.csv"
OUT = bdt.OUT_DIR / "S31_rto_district_grouping_check.json"

# Table 27 serial number -> VAHAN office code, with a word that must appear in the name.
TABLE27_ROWS = {sl: (f"KA{sl}", None) for sl in range(1, 57)}
TABLE27_ROWS.update(
    {
        57: ("KA59", "CHANDAPURA"),
        58: ("KA63", "DHARWAD EAST"),
        59: ("KA64", "MADHUGIRI"),
        60: ("KA65", "DANDELI"),
        61: ("KA66", "TARIKERE"),
        62: ("KA67", "CHINTAMANI"),
        63: ("KA68", "RANIBENNUR"),
        64: ("KA69", "RAMDURGA"),
        65: ("KA70", "BANTWALA"),
        66: ("KA71", "ATHANI"),
    }
)
# Report column heading -> LGD district code(s) (S06). BELLARY is pre-split.
REPORT_DISTRICTS = {
    "B'LORE(U)": "525",
    "B'LORE (R)": "526",
    "TUMKUR": "548",
    "KOLAR": "542",
    "C.B.PURA": "630",
    "RAM NAGAR": "631",
    "RAM": "631",  # Table 28 prints "RAM NAGAR" on two lines
    "MYSORE": "545",
    "MYSURU": "545",
    "MANDYA": "544",
    "MADIKERI": "541",
    "CHAMRAJNGR": "531",
    "HASSAN": "539",
    "SHIMOGA": "547",
    "SHIVAMOGGA": "547",
    "CHITRADURGA": "533",
    "DAVANAGERE": "535",
    "C-M'LORE": "532",
    "MLORE": "534",
    "UDUPI": "549",
    "BELGAUM": "527",
    "BELAGAVI": "527",
    "GADAG": "537",
    "DHARWAD": "536",
    "HAVERI": "540",
    "BIJAPUR": "530",
    "VIJAYAPUR": "530",
    "BAGALKOTE": "524",
    "KARWAR": "550",
    "KALBURGI": "538",
    "YADGIR": "635",
    "RAICHUR": "546",
    "BELLARY": "528;738",
    "KOPPAL": "543",
    "BIDAR": "529",
}
NUM = re.compile(r"^\d+$")
FY_2021 = {"APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"}
FY_2022 = {"JAN", "FEB", "MAR"}
OFF_TABLE_OFFICES = ("KA57",)  # verified in the crosswalk but absent from Table 27


class GroupingError(RuntimeError):
    pass


def page_lines(page) -> list[str]:
    """Rows of a page printed rotated by 90 degrees: one printed row has a constant x."""
    rows = defaultdict(list)
    for c in page.chars:
        rows[round(c["x0"] / 3)].append(c)
    lines = []
    for key in sorted(rows):
        text, prev = "", None
        for c in sorted(rows[key], key=lambda c: -c["top"]):
            if prev is not None and prev - c["bottom"] > 4:
                text += " | "
            text += c["text"]
            prev = c["top"]
        lines.append(text.strip())
    return lines


def cells(line: str) -> list[str]:
    return [re.sub(r"\s+", " ", c).strip() for c in line.split("|") if c.strip()]


def normalise_heading(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("�", "'").replace("’", "'")).strip()


def read_tables(pdf_path: Path) -> tuple[dict, dict, dict]:
    import pdfplumber

    offices, stock, new = {}, {}, {}
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.rotation not in (90, 270):
                continue
            lines = page_lines(page)
            title = " ".join(lines[:4])
            if "Regional Transport Office wise total vehicle registered" in title or any(
                "OFFICE NAME" in x and "NEWLY REGISTERED FROM" in x for x in lines
            ):  # the second page of Table 27 has the column header but no title
                for line in lines:
                    parts = cells(line)
                    # serial number = the number just before the (non-numeric) office name;
                    # margin text can add stray characters before it
                    idx = next(
                        (
                            i
                            for i in range(len(parts) - 4)
                            if NUM.match(parts[i])
                            and not NUM.match(parts[i + 1])
                            and all(NUM.match(n) for n in parts[i + 2 : i + 5])
                        ),
                        None,
                    )
                    if idx is None:
                        continue
                    sl, name, *nums = parts[idx : idx + 5]
                    if int(sl) in TABLE27_ROWS:
                        offices[int(sl)] = {
                            "name": name,
                            "stock_2021": int(nums[0]),
                            "new_2021_22": int(nums[1]),
                            "stock_2022": int(nums[2]),
                        }
            target = (
                stock
                if "District Wise Total Vehicle Registered" in title
                else new
                if "District Wise Newly Registered" in title
                else None
            )
            if target is None:
                continue
            header = next((cells(x) for x in lines if "CATEGORY OF VEHICLES" in x), None)
            total = next((cells(x) for x in lines if "TOTAL (A)+(B)" in x), None)
            if not header or not total:
                continue
            names = header[header.index("CATEGORY OF VEHICLES") + 1 :]
            values = [int(v) for v in total[total.index("TOTAL (A)+(B)") + 1 :] if NUM.match(v)]
            for name, value in zip(names, values, strict=False):
                heading = normalise_heading(name)
                if heading in REPORT_DISTRICTS:
                    target[REPORT_DISTRICTS[heading]] = value
    return offices, stock, new


def vahan_fy_new(code: str, raw: Path = bdt.RAW) -> int | None:
    """FY2021-22 new registrations (all fuels) of an office from the S29 VAHAN exports."""
    files = {}
    for year in ("2021", "2022"):
        found = sorted(raw.glob(f"S29_vahan_dashboard_ka_allfuel_class_month_*/{code}_{year}.xlsx"))
        if not found:
            return None
        files[year] = found[-1]
    total = 0
    for year, months in (("2021", FY_2021), ("2022", FY_2022)):
        rows = bdt.read_xlsx_rows(files[year])
        header = next(r for r in rows if r.get("C") == "JAN")
        cols = [c for c, m in header.items() if m in months]
        total += sum(
            int(r.get(c, "0").replace(",", "") or 0)
            for r in rows
            if r.get("A", "").isdigit()
            for c in cols
        )
    return total


def check(
    offices: dict,
    stock: dict,
    new: dict,
    crosswalk: list[dict[str, str]],
    off_table_new: dict[str, int | None] | None = None,
) -> dict:
    """Compare each crosswalk unit with the report districts it covers.

    A unit is the crosswalk lgd_district_code: one LGD code, or several joined by ';'.
    off_table_new: offices verified in the crosswalk but absent from Table 27, with their
    FY2021-22 new registrations from VAHAN; their stock is the unit's unexplained residual.
    """
    off_table_new = off_table_new or {}
    by_code = {}
    for sl, row in offices.items():
        code, token = TABLE27_ROWS[sl]
        if token and token not in row["name"]:
            raise GroupingError(f"Table 27 row {sl} is {row['name']!r}, expected {token}")
        by_code[code] = row
    if len(by_code) != len(TABLE27_ROWS):
        raise GroupingError(f"Table 27: {len(by_code)} offices read, {len(TABLE27_ROWS)} expected")
    if set(stock) != set(new):
        raise GroupingError(f"district columns differ: {sorted(set(stock) ^ set(new))}")
    units = defaultdict(list)
    for row in crosswalk:
        if row["status"].startswith("verified"):
            units[row["lgd_district_code"]].append(row["rto_code_vahan"])
    subsets = defaultdict(list)  # (stock, new) -> Table 27 office subsets of size 1-4
    pool = sorted(by_code)
    for k in range(1, 5):
        for combo in itertools.combinations(pool, k):
            key = (
                sum(by_code[c]["stock_2021"] for c in combo),
                sum(by_code[c]["new_2021_22"] for c in combo),
            )
            subsets[key].append(sorted(combo))
    results, used, covered = {}, set(), set()
    for unit in sorted(units):
        codes = sorted(units[unit], key=lambda c: int(c[2:]))
        unit_codes = set(unit.split(";"))
        columns = [k for k in stock if set(k.split(";")) <= unit_codes]
        if {c for k in columns for c in k.split(";")} != unit_codes:
            raise GroupingError(f"unit {unit} does not match the report's district columns")
        listed = [c for c in codes if c in by_code]
        extra = [c for c in codes if c not in by_code]
        d_stock = sum(stock[k] for k in columns)
        d_new = sum(new[k] for k in columns)
        s = sum(by_code[c]["stock_2021"] for c in listed)
        n = sum(by_code[c]["new_2021_22"] for c in listed)
        extra_new = [off_table_new.get(c) for c in extra]
        if any(v is None for v in extra_new):
            raise GroupingError(f"unit {unit}: no VAHAN figure for {extra}")
        n_all = n + sum(extra_new)
        alternatives = None
        if not extra and len(listed) <= 4:
            matches = subsets.get((d_stock, d_new), [])
            alternatives = sum(1 for combo in matches if set(combo) != set(listed))
        results[unit] = {
            "report_columns": columns,
            "offices": codes,
            "offices_not_in_table27": extra,
            "district_stock_31_03_2021": d_stock,
            "table27_offices_stock_sum": s,
            "stock_residual": d_stock - s,
            "district_new_2021_22": d_new,
            "offices_new_sum": n_all,
            "new_from_vahan_for_offices_not_in_table27": dict(zip(extra, extra_new, strict=True)),
            "exact_match": n_all == d_new and (d_stock == s or (extra and d_stock > s)),
            "other_matching_subsets_up_to_4": alternatives,
        }
        used.update(listed)
        covered.update(columns)
    total_residual = sum(stock.values()) - sum(r["stock_2021"] for r in by_code.values())
    explained = sum(r["stock_residual"] for r in results.values() if r["offices_not_in_table27"])
    return {
        "units": results,
        "units_matched": sum(bool(r["exact_match"]) for r in results.values()),
        "units_total": len(results),
        "report_columns_not_covered": sorted(set(stock) - covered),
        "table27_offices": len(by_code),
        "table27_offices_unassigned": sorted(set(by_code) - used, key=lambda c: int(c[2:])),
        "table28_minus_table27_stock": total_residual,
        "stock_residual_in_units_with_off_table_offices": explained,
        "table28_stock_sum": sum(stock.values()),
        "table29_new_sum": sum(new.values()),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--crosswalk", type=Path, default=CROSSWALK)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    offices, stock, new = read_tables(S30)
    off_table = {c: vahan_fy_new(c) for c in OFF_TABLE_OFFICES}
    result = check(offices, stock, new, bdt.read_csv(args.crosswalk), off_table)
    result["inputs_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (S30, args.crosswalk)
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    bad = [u for u, r in result["units"].items() if not r["exact_match"]]
    summary = {k: v for k, v in result.items() if k != "units"} | {"mismatch": bad}
    json.dump(summary, sys.stdout, indent=2)
    print()
    ok = (
        not bad
        and not result["table27_offices_unassigned"]
        and not result["report_columns_not_covered"]
        and result["stock_residual_in_units_with_off_table_offices"]
        == result["table28_minus_table27_stock"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
