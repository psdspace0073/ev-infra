# Data-Collection Gap Closure (26 October 2026)

Branch: `feature/ka-ev-registrations` · Follows `MANUAL_INSPECTION_REVIEW.md` (gaps G1–G8) and `docs/submission/EVIDENCE_PACKAGE.md` §5–6.

Every item below is marked **COMPLETE**, **BLOCKED** or **NOT REQUIRED**. Register IDs refer to `configs/source_register.csv`. Raw files are in `data/raw/` (gitignored) with manifests; derived files are in `data/processed/` (gitignored) and are rebuilt by the scripts named.

## Summary

| # | Gap | Status | Evidence |
| --- | --- | --- | --- |
| 1 | RTO-to-district mapping | **COMPLETE** (67 of 67; 6 in combined units) | S30 Tables 27–29, check S31 |
| 2 | Battery-EV by vehicle class per RTO and month | **COMPLETE** | S29 exports → S35 |
| 3 | 33 RTO-months missing from S24 | **COMPLETE** (all 33 classified) | S29 → S32 register |
| 4a | 2025 battery-EV −68 | **COMPLETE** (explained) | S29, S32 |
| 4b | Dec 2025 and Sep 2026 all-fuel differences | **COMPLETE** as measured and located; root cause **BLOCKED** (not published) | S25 (42 statements), S29, S32 |
| 4c | S01 export metadata | **BLOCKED** (not recoverable); superseded by S29 | S29 manifests |
| 5 | BEE charging data: machine-readable file and licence | Licence **COMPLETE**; machine-readable file **BLOCKED** (not published) | S15 policy page |
| 6 | Policy documents (MoP 2024, PM E-DRIVE) | **COMPLETE** | S33, S34 |
| 7 | CEA, DISCOM areas, WorldPop | **NOT REQUIRED** for Round 1 | `EVIDENCE_PACKAGE.md` §6 |

## 1. RTO-to-district mapping — COMPLETE

**Source.** Transport Department Annual Report 2021-22 (S30, English part, official site). Table 27 gives each office's vehicles on 31-03-2021 and new registrations 2021-22. Tables 28 and 29 give the same two figures for each district.

**Method.** `src/evinfra/analysis/verify_rto_district_grouping.py` reads the rotated tables from the PDF and checks every crosswalk unit. The offices assigned to a unit must sum exactly to the unit's district totals on both measures. For units of up to four offices it also counts every other subset of offices that would match both totals.

**Result (S31).** 29 of 29 units match exactly. 27 units have no alternative subset. Bengaluru Urban (11 offices) and Belagavi (6) are too large to enumerate but match exactly.
- **KA57** (STU and Autorikshaw, Shanthinagar) is not in Table 27. Bengaluru Urban exceeds its listed offices by 4,573 vehicles and 566 new registrations. KA57's FY2021-22 new registrations on the VAHAN dashboard are exactly 566 (S29). KA57 is assigned to Bengaluru Urban.
- **KA67 Chintamani** is counted under Kolar in the report, although Chintamani sub-district is in Chikkaballapura (Census 2011 district 582 in S04 = LGD 630 in S06). KA7, KA8, KA40 and KA67 form one unit, Kolar + Chikkaballapura (`verified_official_combined`).
- **KA34 Bellary and KA35 Hospet** are in the report's pre-2021 Bellary column. They form one unit, Ballari + Vijayanagar (`verified_official_combined`).
- **61 RTOs** map to one district (`verified_official`).

**Limits.** This is the department's statistical grouping as of 2021-22; later jurisdiction changes were not checked. S30 §3.3 says Vahan applications may be filed at any office in Karnataka irrespective of residence or business, so district totals describe the **registering office**, not where owners live. Office names and addresses were not used as evidence.

**Searched without result:** the Transport Department site (no jurisdiction page; menu is script-rendered), the data.opencity.in mirror of the 2018-19 report (still HTTP 404), web search (insurance and aggregator pages only). Not needed after S30: gazette notifications.

## 2. Battery-EV by vehicle class per RTO — COMPLETE

The VAHAN dashboard report view (vahan.parivahan.gov.in/vahan4dashboard) was reachable on 26 Oct 2026 (it was not on 25 Oct). The report view has no login and no CAPTCHA. `src/evinfra/ingestion/fetch_vahan_dashboard.py` sends the same requests as the page (state, office, Y = Vehicle Class, X = Month Wise, calendar year, fuel = ELECTRIC(BOV) + PURE EV) and saves the official Excel export unchanged. The fuel filter is not printed in the export, so it is recorded in the batch manifest. It is checked by totals: for example, KA5 2025 gives 22,381, equal to S28.

**Collection (S29, 26 Oct 2026).** 340 of 340 battery-EV exports were collected (68 offices × 2022–2026). One request timed out (HTTP 408); the script started a new session and resumed from the manifest: 219 files before, 121 after, none fetched twice. Also collected:
- 8 all-fuel exports for KA45, KA46 and KA57.
- 5 statewide fuel × month exports (2022–2026).
- 2 statewide vehicle class × month exports (2025–2026).

Every export title was checked for office and year, and every file hash is in its batch manifest.

**Table (S35, `src/evinfra/analysis/build_ka_ev_class_rto_month.py`).** 14,445 non-zero cells: month × RTO × vehicle class, January 2022 to September 2026, 24 vehicle classes.
- **Largest classes over the period:** M-CYCLE/SCOOTER 682,370 (79.0%), MOTOR CAR 65,683 (7.6%), MOTOR CYCLE/SCOOTER-USED FOR HIRE 32,898 (3.8%), THREE WHEELER (PASSENGER) 23,822, MOPED 22,705.
- **Check against S26 (S24), per RTO-month:**
  - 3,662 equal.
  - 124 differ, by at most 7 each, net +64 (later revisions).
  - 33 are the months S24 does not publish.
  - KA99 is not in S24 (57 months, all zero).
- **Annual state totals from S35** (2022–2026): 95,770 / 152,715 / 179,238 / 203,698 / 232,343. These equal the separate statewide VAHAN export exactly.
- **Limits:** counts are by registering office. VAHAN revises recent months after month end. Hybrids were not exported by class (not needed for the battery-EV definition).

## 3. The 33 RTO-months missing from S24 — COMPLETE

`S32_missing_rto_month_register.csv` classifies all 33 RTO-months with VAHAN dashboard evidence (S29). Nothing was imputed; S26 keeps them blank.

| RTO | Months | VAHAN all fuels | VAHAN battery-EV | Status |
| --- | --- | --- | --- | --- |
| KA45 Hunsur | Nov 2025 – Jul 2026 (9) | 704 – 1,116 per month | 30 – 96 per month | `vahan_reports_registrations`: missing from S24 only |
| KA46 Sakaleshpura | Jan – Jul 2026 (7) | 452 – 637 per month | 13 – 31 per month | `vahan_reports_registrations`: missing from S24 only |
| KA57 STU and Autorikshaw | 17 months 2022–2026 | 0 | 0 | `vahan_reports_zero`: VAHAN shows 0 for every vehicle class |

"Zero" means zero in VAHAN as of 26 Oct 2026. KA57 is a functional office (STU fleets and autorickshaws) with irregular months, for example 248 registrations in November 2022 and 0 from April to October 2022. All three offices were live on VAHAN-4 before 2022 (start dates in the S29 manifests).

## 4. Registration discrepancies

**4a. 2025 battery-EV −68 — COMPLETE (explained).** Three measurements of 2025 battery-EV registrations (S32):
- S01, the earlier dashboard export: 203,693.
- S24: 203,625.
- The VAHAN dashboard now (S29): 203,698.

S24 has no rows for KA45 in November and December 2025, where VAHAN shows 45 and 30 battery-EV registrations (75). That accounts for S24's shortfall against current VAHAN (+73; the other −2 are revisions in other months). Current VAHAN is 5 above S01, which is consistent with revisions after the S01 export. **The −68 is a coverage gap in S24, not an error in S01.**

For 2026 (January to September), S24 is 698 below current VAHAN. Of that, 644 is in the KA45 and KA46 months missing from S24; the other 54 are revisions. Claim E08 is now `verified_reproducible` with this explanation.

**4b. All-fuel monthly totals vs Transport Department statements — measured and located; cause BLOCKED.** All 42 comparable monthly statements were acquired (S25, Apr 2023 to Sep 2026). The VAHAN dashboard total is higher than the statement in **every** month: from +0.05% to +2.42%, median +1.17% (S32). September 2026 (+1.42%) and December 2025 (+0.87%) are typical. By category for September 2026 (S29 state class × month), one-to-one categories agree: tractors 4,212 vs 4,211, trailers 1,061 vs 1,062, goods three-wheelers 800 vs 800, articulated vehicles 90 vs 90, passenger three-wheelers 6,896 vs 6,893. The difference is in two-wheelers and cars. Recent VAHAN months keep rising after month end (Sep 2026: S24 184,194, now 184,328), which is consistent with a cut-off-date difference. The department does not publish its compilation method, so the cause stays unconfirmed. No total was adjusted.

Statement anomalies recorded in S25 and S32:
- The file published as "KAR AUG 2026" repeats the September 2026 figures. August is derived from the July closing and September opening stocks (184,532).
- The April 2025 opening stock is rebased (32,930,363 vs March closing 33,471,365). The statement is used as published.
- The statements before April 2023 use cumulative or different bases and are not compared.

**4c. S01 export metadata — BLOCKED.** The date and filter settings of the earlier dashboard export are not recorded anywhere and cannot be recovered. S29 replaces S01 for validation, with full metadata per file.

## 5. Charging-station data and licence

- **Licence — COMPLETE.** BEE's website Copyright Policy (last updated 17 Jan 2025) allows reproduction free of charge in any format without specific permission, provided the material is reproduced accurately, is not used in a derogatory or misleading context, and the source is prominently acknowledged. It does not cover material marked as third-party copyright. The page is saved as S15 evidence. **Attribution to use:** "Source: Bureau of Energy Efficiency (BEE), Ministry of Power".
- **Machine-readable file — BLOCKED.** BEE's charging page still links only the PDF "EV Public Charging Stations Data till 26th October 2025". The live file is byte-identical to S15 (SHA-256 `f519218f…`), so there is no newer release. EV Yatra (evyatra.beeindia.gov.in) failed to connect from the project machine. Web search found no official CSV or XLSX. S18 (8,246 rows) stays the source; nothing was replaced.

## 6. Policy documents — COMPLETE

The methodology plan cites spacing rules (checklist I-001 to I-004, R4-19) and subsidy rules (R4-16, Part N), so both documents are needed.

- **S33 — MoP "Guidelines for Installation and Operation of EV Charging Infrastructure-2024".** Letter No. 12/2/2018-EV, 17 Sep 2024; BEE-hosted copy. Clause 11(1) Density, page 7 of 36:
  - (a) Urban areas: by FY 2030, at least one charging station within a 1 km × 1 km grid in urban areas notified by state governments.
  - (b) Highways: every 20 km on both sides of highways, expressways and major roads.
  - (c) Long-range and heavy-duty EVs: a fast-charging station (clause 12(7)) every 100 km on each side of designated expressways, highways and major roads.

  The clause says these "may be adopted", so they are **advisory**. The July 2024 draft on powermin.gov.in was not used.
- **S34 — MHI "Operational Guidelines for Deployment of EV PCS under the PM E-DRIVE Scheme"**, 26 Sep 2025, plus the MHI FAQ.
  - Eligible entities: GoI ministries and States/UTs through nodal agencies (§2).
  - Charging must comply with S33 (§4).
  - Subsidy is a percentage of the BEE benchmark cost or the actual cost, whichever is lower (§6). Categories in Table 2:
    - A — government premises with free public access: 100% upstream and 100% EVSE.
    - B — government or PSU-controlled locations: 80% upstream and 70% EVSE.
    - C — all other locations: 80% upstream.
    - D — battery swapping or charging stations: 80% upstream.
  - Benchmark costs (BEE, Aug 2022; Tables 3–4): upstream INR 6.04 / 14.80 / 19.00 / 24.00 lakh for up to 50 / 100 / 150 / above 150 kW. EVSE: CCS-II 50 kW 7.25, 100 kW 11.68 lakh.
  - **Eligible is not sanctioned.** The MHI letter of 29.10.2025 on the same page is a scanned image and was not read.

## 7. Optional sources — NOT REQUIRED

- **CEA EV charging reports.** The report page (cea.nic.in/electric-vehicle-charging-reports) returned HTTP 404 to a plain request from the project machine. Not pursued further: calibration "never blocks the core" (R4-05), and Round 1 asks for method and roadmap.
- **DISCOM service areas.** Needed only for a DISCOM-level CEA comparison, which is not being made.
- **WorldPop.** District population is available from Census 2011 (S04/S09). The grid is a finale item.

## 8. Failed or blocked attempts (log)

| Date (2026) | Target | Result |
| --- | --- | --- |
| 25 Oct | vahan.parivahan.gov.in | TCP to port 443 failed (earlier report) |
| 26 Oct | vahan.parivahan.gov.in report view | HTTP 200; exports obtained (S29) |
| 26 Oct | data.opencity.in 2018-19 annual report mirror | HTTP 404 (CKAN: "Not found") |
| 26 Oct | transport.karnataka.gov.in jurisdiction page | None found; menu script-rendered |
| 26 Oct | beeindia.gov.in consolidated-guidelines links (two URLs) | HTML page instead of the PDF; final PDF found at another BEE URL (S33) |
| 26 Oct | evyatra.beeindia.gov.in | Connection failed |
| 26 Oct | cea.nic.in EV charging report page | HTTP 404 |
| 26 Oct | pmedrive.heavyindustries.gov.in, MHI letter 29.10.2025 | PDF is a scan without text; not read |

## 9. Remaining blockers

1. Cause of the VAHAN-vs-statement offset: needs the Transport Department's compilation method (for example by an RTI request).
2. A machine-readable BEE station list, and operational status of chargers: not published.
3. Post-2022 changes in office jurisdictions, and the KA67 and KA34/KA35 splits: not documented. Combined units are used.
