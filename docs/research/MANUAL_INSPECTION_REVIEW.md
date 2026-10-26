# Manual Inspection Reports: Verification, Progress and Completion Plan

Date: 26 October 2026 · Branch: `feature/ka-ev-registrations` · Round 1 deadline: 30 October 2026

The folder `data/manual inspection reports/` (not tracked in git) holds five stage reports. They were made outside this repository from an uploaded CSV, `Registrations by Fuel Type_Filtered_Data-2.csv`, and the BEE PDF. This document checks each claim against the repository datasets (register IDs in `configs/source_register.csv`). The reports themselves are kept unchanged.

Verification commands (scripts in a scratch directory, not committed): recompute every number from `data/raw/S24_*.csv`, `data/processed/S18_*.csv`, `S26_summary.json` and `configs/ka_rto_district_crosswalk.csv`, and compare row by row with the report CSVs.

> **NOTE:** The stage reports use their own IDs (S-01 to S-10 in Stage 5). They are **not** the register IDs. For example, Stage 5 "S-02" is the register S24 content, and Stage 5 "S-05" is register S17.

## 1. Verification summary

| Stage | Claim | Result against repo |
| --- | --- | --- |
| 1 VAHAN access | Uploaded CSV: 36,198 rows, 57 months (Jan 2022–Sep 2026), 67 RTOs, 25 fuel labels, 0 duplicates, 0 zero or negative counts, 33 absent RTO-months | **Verified.** The Karnataka rows of S24 give the same values. Sum 8,744,327 is the same |
| 1 | Label sums: Pure EV 408,512, Electric(BOV) 454,469, Strong Hybrid EV 27,178, Plug-in Hybrid EV 5 | **Verified** (S24) |
| 1 | India Data Portal route "not yet verified" | **Superseded.** S24 (fuel) and S27 (class) were downloaded from India Data Portal on 25 Oct, ODC-BY, with manifests. The uploaded CSV matches S24 on all aggregate checks. Its SHA-256 (`3b0a91…`) cannot be checked because the file is not in the repo |
| 1 | VAHAN analytics dashboard loaded once, then failed; tabular report and 1-/5-year downloads failed after CAPTCHA (user-observed, Mac/Safari, 26 Oct) | **New evidence, not reproducible here.** The repo recorded only a TCP failure to vahan.parivahan.gov.in from the project machine. The CAPTCHA is now user-observed on the analytics routes. The screenshots are not in the repo |
| 1 | No source gives month × RTO × class × fuel | **Agrees** with `KA_EV_REGISTRATIONS_REPORT.md` |
| 2 RTO-district | 67-row evidence register, all `unresolved`, confidence `none` | **Verified.** The 67 code-name pairs are identical to S24 and to `configs/ka_rto_district_crosswalk.csv` (all 67 `unresolved`) |
| 2 | Leads: uttarakannada.nic.in RTO Karwar page (KA30), tumkur.nic.in RTO page | **New leads**, not in the repo. Both are office or context pages, not jurisdiction orders. KA30 stays `unresolved` |
| 2 | "Karnataka Transport Department https://karnataka-etc.in/" | **Not confirmed.** The repo uses transport.karnataka.gov.in. The status of the karnataka-etc.in domain was not checked |
| 3 Demand | Monthly all-fuel totals, RTOs and fuel labels per month (57 rows) | **Verified**, 0 mismatches |
| 3 | Monthly and annual EV label tables; BEV (Pure EV + Electric(BOV)) 2022–2026: 95,770 / 152,711 / 179,230 / 203,625 / 231,645 | **Verified**, 0 mismatches; equal to S28 |
| 3 | BEE extraction: 6,113 Karnataka records, 216 without coordinates, 5,093 unique coordinates, 293 pages | **Incomplete; superseded by S18.** S18 (table extraction of the same PDF) has 8,246 rows, all with coordinates, 6,069 unique pairs, 292 pages. Every Stage 3 coordinate pair is in S18; 2,349 S18 rows have no Stage 3 match (on 117 pages). Do not use 6,113 |
| 3 | PIB/MHI benchmark 6,096 Karnataka EVCS (751 fast, 5,345 slow), 16 Dec 2025 | **Verified** (register S17) |
| 4 Quality gaps | 2025 all-fuel 1,911,489; Sep 2026 all-fuel 184,194; monthly reconciliation register | **Verified** (all 57 months: total, rows, RTOs, labels) |
| 4 | 33 missing RTO-months kept blank | **Verified**: same 33 (KA45 9, KA46 7, KA57 17) as S26; all counts blank |
| 4 | DQ-01 "2025 total differs by 68", observed value 1,911,489, comparator not available | **Error.** The −68 is a **BEV** difference, not all-fuel: S24 BEV 203,625 vs S01 VAHAN export 203,693 (−68, −0.03%). The comparator is in the repo (S01). The open question is the S01 export date and filters |
| 4 | DQ-02 "Sep 2026 differs by 1.3%", comparator not available | **Comparator is in the repo.** S25 official statement: 181,753 new registrations; S24 184,194; +2,441 (+1.34% of the official value). By class (S27): non-transport +2,366, transport +75. Cause still not determined |
| 5 Evidence package | Consolidated baseline, claim register (C-01 to C-08), source register, notes | **Partly valid.** C-02, C-03, C-04, C-06 verified. C-05 (6,113) must be replaced with S18 figures. C-08 must state the −68 as BEV. Notes say the CSV has 7 columns; it has 8 (with `id`) |

**Definition difference (not an error):** Stages 1, 3 and 5 keep Pure EV and Electric(BOV) separate. The repo adds them as BEV, because S01 (the VAHAN export) reports their total, and Pure EV takes over from Electric(BOV) after March 2024 while the sum stays continuous. The submission should show the sum and state that both labels are included.

## 2. Completed work (verified in the repo)

- **Registrations:** S24, S27 acquired; S26 (RTO × month BEV), S28 (trends); validation against S01 and S25; 33 missing RTO-months documented, never set to 0.
- **Chargers:** BEE location list S15 → S16 → S18 (8,246 Karnataka rows, 8,232 valid coordinates, district by point) and S19 (6,056 candidate sites); OSM S10/S11 (67 records) and S21–S23 layers; official aggregates S03 (6,097) and S17 (6,096).
- **Geography:** S06 LGD districts, S20 boundaries, S09/S12 district tables. Crosswalk scaffold with a validator that blocks unsupported district assignment.
- **Tests:** 122 unit tests pass (`python -m pytest -q`, 26 Oct).

## 3. Remaining gaps

| ID | Gap | Effect |
| --- | --- | --- |
| G1 | No verified RTO-to-district jurisdiction for any of 67 RTOs | No district-level demand, no registrations-per-charger by district |
| G2 | No EV by vehicle class at RTO level (no joint class × fuel source) | Capacity and charger-type need cannot use class mix |
| G3 | S01 export date and filters not recorded | The −68 (2025 BEV) cannot be explained |
| G4 | Only 2 of the S25 monthly statements acquired (listed Apr 2024–Sep 2026) | Monthly all-fuel totals not reconciled for 28 other months, including the October peaks |
| G5 | 33 RTO-months without rows (KA45, KA46, KA57) | Unknown if zero or unreported |
| G6 | BEE list: licence not stated; no operational status (0 rows) | Charger counts are installed, not operational |
| G7 | Stage 5 evidence package uses the Stage 3 count and its own source IDs | Not usable for submission without rebuild |
| G8 | Checklist Part F items not started: CEA reports (F.3), DISCOM lists (F-074), WorldPop (F-077), policy documents (F.11), OMC counts (F-036) | No energy calibration, no DISCOM join, no population grid. Not covered by the five stage reports |

## 4. Blockers

1. **VAHAN dashboard:** not reachable from the project machine (TCP, 25 Oct); on the user's machine, report and download routes fail after CAPTCHA (26 Oct). Blocks G2 and G3.
2. **No official RTO jurisdiction list** found online. Blocks G1. Needs a Transport Department document, gazette notification or official reply.
3. **No machine-readable BEE file.** S18 depends on PDF table extraction (validated by structure checks, not against an official spreadsheet).

## 5. Completion plan (26–30 October, in priority order)

1. **Freeze the submission geography (26–27 Oct).** Use what is valid now: charger supply by district (S18 points in S20/S06 polygons), EV demand at state and RTO level (S26/S28), and an explicit "not computable" for district demand. Record this in the decision log. This removes G1 from the critical path.
2. **Rebuild the evidence package from register IDs (27–28 Oct).** Start from Stage 5's structure. Replace the 6,113 BEE count with S18/S19 figures; restate DQ-01 as BEV −68 vs S01; add the S25 comparator for DQ-02; map S-01…S-10 to register IDs.
3. **Acquire the remaining S25 monthly statements (27 Oct, low effort).** Save unchanged with manifests; add them to the monthly reconciliation (G4). Do not adjust S24.
4. **One more VAHAN attempt (by 28 Oct)** on a different network or browser, with the steps in `KA_EV_REGISTRATIONS_REPORT.md` §7. Record URL, time, browser and result in an access log. If it fails, record G2 and G3 as limitations (checklist Part W).
5. **Continue RTO jurisdiction search** (parallel, not on the critical path): gazette notifications for RTO/ARTO creation, district administration pages that state jurisdiction (start with the Stage 2 leads), or an official request. Fill a crosswalk row only with LGD code, jurisdiction basis, URL and retrieval date.
6. **Decide on G8 by 27 Oct:** for each open Part F item, either acquire it or record it as out of Round 1 scope in the decision log (checklist Part J).
7. **Keep G5 and G6 as stated limitations.** Do not impute zeros. Do not call installed chargers operational.

## 6. Files in the folder (not tracked)

The folder is untracked and is not committed with this review. It holds two ZIP bundles (ignored by `*.zip`) and a 3.8 MB extraction CSV. Decide separately whether to keep it outside git, move it under `data/interim/`, or record it in the register.
