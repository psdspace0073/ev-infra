# Karnataka EV Registrations: Sources, Validation and Geographic Limits

Date: 25 October 2026 · Branch: `feature/ka-ev-registrations` · Register: S01, S14, S24–S28

## 1. Sources

| Source | Register | What it gives | Access | Status |
| --- | --- | --- | --- | --- |
| India Data Portal "Vehicle Registrations": Registrations by Fuel Type | S24 | Monthly new registrations by state, RTO and fuel type (VAHAN compilation) | Direct CSV, no login; ODC-BY | Acquired |
| India Data Portal "Vehicle Registrations": Registrations by Vehicle Class | S27 | Same registrations by RTO and vehicle class (all fuels) | Direct CSV, no login; ODC-BY | Acquired (consistency check only) |
| Karnataka Transport Department, monthly vehicle statements | S25 | State and Bengaluru totals by vehicle category: stock and new registrations. No fuel, no RTO | PDF, no login | Two months acquired |
| VAHAN dashboard (vahan.parivahan.gov.in/vahan4dashboard) | S01 (earlier statewide export) | The primary source; can show RTO x class x fuel x month on screen | TCP connection to port 443 fails from the project machine (25 Oct, twice); parivahan.gov.in answers. On a team member's machine (26 Oct, user-observed): the analytics dashboard loaded once, then failed to load data; the tabular report and the 1-/5-year downloads did not open after CAPTCHA (see `MANUAL_INSPECTION_REVIEW.md`) | Reachable on 26 Oct: report-view exports acquired as S29 (no login, no CAPTCHA on the report view) |
| India Data Portal norm and maker tables | – | Same one-attribute layout (norm, maker) | Checked headers only | Not needed |
| data.gov.in "KAxx ... Vehicle Newly Registered In The Year 2021-2022" | – | One file per RTO, 2021-22, all fuels (about 1.7 KB each) | Download returns HTTP 403 without the portal's download form or API key; GODL-India | Not acquired |
| Dataful (dataful.in) VAHAN-derived sets | – | Third-party paid copies | Custom licence | Not used |

Links: [IDP package API](https://ckandev.indiadataportal.com/api/3/action/package_show?id=vehicle-registrations) · [Transport Department monthly statistics](https://transport.karnataka.gov.in/50/Monthwise%20Vehicle%20Statistics%20Report/en)

**No IDP table crosses vehicle class with fuel.** Every IDP table is a single attribute by RTO and month. S24 and S27 must not be combined to estimate EVs by class.

> **UPDATE (26 Oct):** the VAHAN dashboard report view gives battery-EV registrations by RTO x vehicle class x month directly (S29 exports, table S35). See `GAP_CLOSURE_REPORT.md`.

## 2. Data and definitions

- **Coverage:** S24 Karnataka has 36,198 rows covering 67 VAHAN RTOs over 57 months (January 2022 to September 2026). Counts are **new registrations per month** (flows); the `date` column is month end.
- **Battery EVs:** BEV = `Electric(BOV)` + `Pure EV`. "Pure EV" first appears in March 2024 and takes over from "Electric(BOV)" over the following months, while their sum stays continuous. This is consistent with a relabelling of the same battery-electric category.
- **Hybrids:** `Strong Hybrid EV` (from March 2024) and `Plug-in Hybrid EV` (5 Karnataka rows) are kept separate.
- **Zero counts:** the source never publishes a zero (minimum 1). An absent RTO, month and fuel combination is therefore zero or unreported; it stays blank and is never set to 0.

## 3. Validation findings

| Check | Result |
| --- | --- |
| Duplicates, invalid or negative counts, RTO code-name conflicts | None (S24 and S27) |
| S24 BEV vs S01 VAHAN dashboard export, calendar years | 2022 +1 · 2023 −3 · 2024 +5 · 2025 −68 (−0.03%). 2026 not comparable (S01 cut-off unknown) |
| S24 vs S27 totals per RTO-month | Equal in 3,785 of 3,786. KA16 (Chitradurga) April 2026 is absent from S27; S24 has 3,560, in line with March (4,019) and May (3,227). The gap is in S27, not S24 |
| 33 RTO-months without rows (KA45 9, KA46 7, KA57 17) | Absent identically in S24 and S27, so this is not a fuel-table defect. Whether these months were genuine zeros or unreported cannot be determined. KA57 (STU and Autorikshaw, Shanthinagar) is a specialised office, so zero months are plausible but unproven |
| S24 all-fuel vs official statement (S25), Sep 2026 | 184,194 vs 181,753 (+2,441, +1.3%). By S27 class: non-transport +2,366 (160,062 vs 157,696), transport +75 (24,132 vs 24,057). The gap is almost all non-transport |
| S24 all-fuel vs official statement, Dec 2025 | 130,751 vs 130,313 from the stock difference (+438, +0.3%) |

**Resolved on 26 Oct (S29, S32; details in `GAP_CLOSURE_REPORT.md`):**
- **2025 BEV gap (−68):** current VAHAN gives 203,698 for 2025 (S01 203,693, +5 later revisions). S24 has 203,625 because it has no rows for KA45 in November and December 2025, where VAHAN shows 45 and 30 battery-EV registrations (75 in total). The −68 is a gap in S24, not in S01.
- **33 RTO-months without rows:** all classified with VAHAN evidence in `S32_missing_rto_month_register.csv`. KA45 and KA46 months have registrations in VAHAN (missing from S24 only); the KA57 months show zero in VAHAN for every vehicle class.
- **Official statement gaps (Sep 2026 +1.3%, Dec 2025 +0.3%):** not an S24 defect. The VAHAN dashboard is higher than the Transport Department statement in all 42 comparable months (Apr 2023 to Sep 2026, median +1.17%). The difference is in two-wheelers and cars. The cause (compilation cut-off or rules) is not published.

No total was adjusted to match.

## 4. Trends (S28)

| Year | BEV | All fuels | BEV share | Hybrids |
| --- | --- | --- | --- | --- |
| 2022 | 95,770 | 1,532,362 | 6.2% | 0 |
| 2023 | 152,711 (+59.5%) | 1,746,740 | 8.7% | 0 |
| 2024 | 179,230 (+17.4%) | 1,888,157 | 9.5% | 6,293 |
| 2025 | 203,625 (+13.6%) | 1,911,489 | 10.7% | 11,228 |
| 2026 (Jan–Sep) | 231,645 | 1,665,579 | 13.9% | 9,662 |

- **Peak month:** July 2026, with 29,665 BEV registrations.
- **2025 RTO concentration:** the largest RTOs by BEV registrations are KA5 Bengaluru South (11.0% of the state), KA2 Bengaluru West (6.9%), KA3 Bengaluru East (6.7%), KA1 Bengaluru Central (6.6%) and KA51 Electronic City (6.0%).
- **These are RTO figures, not district figures.** Registrations are counted where vehicles are registered, not where they are used or charged.

## 5. RTO-to-district crosswalk

`configs/ka_rto_district_crosswalk.csv` lists all 67 VAHAN RTO codes. A row can become `verified_official` only with an LGD district code, a jurisdiction basis, a source URL and a retrieval date; the S28 build enforces this.

> **UPDATE (26 Oct):** all 67 rows are verified from the Transport Department's Annual Report 2021-22 (S30): each unit's offices sum exactly to the department's district totals (check S31). 61 RTOs map to one district; KA7, KA8, KA40, KA67 form Kolar + Chikkaballapura and KA34, KA35 form Ballari + Vijayanagar (`verified_official_combined`). Details: `GAP_CLOSURE_REPORT.md` §1. The history below is kept.

Sources tried (25 Oct 2026):
- **Transport Department site:** there is no office-jurisdiction page, and the contact page has no list.
- **Parivahan state page:** returns 404.
- **Transport Department annual reports:** the 2018-19 and 2021-22 mirrors on data.opencity.in now return 404, and the dataset is gone. (26 Oct: the department's own site still hosts both reports; the 2021-22 report is S30.)
- **Government of Karnataka contact directory:** rendered client-side, with no transport offices exposed.
- **Web search:** returned only insurance and aggregator pages, which contradict each other (for example KA-29 and KA-41).

None of these were used. A manual inspection (Stage 2, 26 Oct) found two more leads: the Uttara Kannada district page for RTO Karwar (https://uttarakannada.nic.in/en/rto-karwar/, KA30) and the Tumakuru district RTO page (https://tumkur.nic.in/en/regional-transport-office/). Both are office or context pages, not jurisdiction records, so no row changed. Office names (for example "Hunsur ARTO") are **not** treated as jurisdiction evidence. Jurisdictions follow taluks and can change, for example with the creation of Vijayanagara district in 2021 or new ARTOs such as KA70 and KA71.

## 6. Method for joining registrations to charging infrastructure

1. **Statewide:** compare S28 statewide BEV flows with the charger inventory (S15/S18, BEE stations; S11/S23, OSM). This is valid now.
2. **RTO level:** registrations stay at RTO. A charger can be related to an RTO only through a verified jurisdiction polygon or list. None exists yet, so no charger-per-RTO ratio is produced.
3. **District level:** allowed only for RTOs whose crosswalk row is verified. A district total is reported only if **every** RTO serving that district is verified; otherwise it is "not computable". Combined units (Kolar + Chikkaballapura; Ballari + Vijayanagar) are reported only as units. District totals describe the **registering office**: S30 §3.3 allows Vahan applications at any office in Karnataka, irrespective of residence or business.
4. **Never:** split RTO or state totals by population, roads or names. Never treat registrations as vehicle locations (R4-19). Never use S24/S27 to infer an EV vehicle-class mix.

## 7. Manual VAHAN export (needs a network that can reach the dashboard)

> **UPDATE (26 Oct):** done by script: `src/evinfra/ingestion/fetch_vahan_dashboard.py` (S29). The report view had no CAPTCHA. The labels below were confirmed on the page; files are saved as `data/raw/S29_vahan_dashboard_ka_<job>_<date>/<RTO>_<year>.xlsx` with a batch manifest.

1. Open https://vahan.parivahan.gov.in/vahan4dashboard/ and go to the report view.
2. Set the type to "Actual Value", the state to "Karnataka", the RTO to one office (repeat for each), the Y-axis to "Vehicle Class", the X-axis to "Month Wise", and the year to the calendar year (repeat for 2022 to 2026).
3. Under the fuel filter, select only ELECTRIC(BOV) and PURE EV. Record the exact labels shown. Export hybrids separately.
4. Click Refresh, then download the Excel file. If a CAPTCHA appears, solve it by hand; do not automate it.
5. Save each file unchanged as `data/raw/S29_vahan_ka_<RTO>_<year>_class_month_bev.xlsx` and record the export time and filter settings.
6. Check whether each export's class totals per month sum to S24's BEV for that RTO and month.

## 8. Next priority

Updated 26 Oct after the gap closure (`docs/research/GAP_CLOSURE_REPORT.md`). Items 2–4 of the previous list are done.

1. **Use S35 for demand by vehicle class** (RTO x class x month, battery-EV) and the district-unit table of the evidence package for district demand, always with the registering-office caveat.
2. **Ask the Transport Department how the monthly statements are compiled** (for example by RTI) if the VAHAN-vs-statement offset must be explained; until then report it as a measured, systematic difference.
