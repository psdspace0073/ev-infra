# Round 1 Evidence Package (Stage 5 rebuild)

Date: 26 October 2026 (regenerated after the gap closure, `docs/research/GAP_CLOSURE_REPORT.md`) · Branch: `feature/ka-ev-registrations` · Pilot geography: Karnataka (ADR-001)

This package replaces the manual Stage 5 package in `data/manual inspection reports/build submission ready evidence package/` (kept unchanged, untracked). Every figure now comes from repository data and uses register IDs from `configs/source_register.csv`.

- **Claim register:** `docs/submission/claim_register.csv` (21 claims, E01–E21). It is generated, so do not edit it by hand.
- **Generator and audit:** `python src/evinfra/analysis/build_evidence_package.py`. It writes `outputs/reports/evidence_package/` (claim register, district charger supply table, district-unit battery-EV and supply table, `audit.json` with input hashes). Inputs now include S32 (reconciliation) and S35 (battery-EV by RTO, class and month). It exits non-zero if the audit fails or the tracked register differs. `--update-docs` rewrites the tracked copy (only when the audit passes).
- **Tests:** `tests/unit/test_build_evidence_package.py`.

## 1. Rules the audit enforces

1. A district-level demand or gap claim must be `not_computable` unless every RTO in `configs/ka_rto_district_crosswalk.csv` is verified (`verified_official` or `verified_official_combined`). When all are verified (today 67 of 67), each such claim must carry the registering-office caveat. Combined units are never split.
2. The superseded figure 6,113 (Stage 3 BEE extraction) may appear only in its own `superseded` claim.
3. Each discrepancy claim states its metric in its first words: "Battery-EV" or "All-fuel". The 2025 −68 and the September 2026 +1.34% are separate claims with separate comparators.
4. Every register ID in a claim exists in the register. Every hand-transcribed official value (S03, S17, S25) appears, formatted the same way, in its register row.
5. S12 has no district EV registrations, and both the district supply table and the district-unit table sum to the S18 rows with a point district (8,232).

## 2. Claim statuses

| Status | Meaning | Claims |
| --- | --- | --- |
| verified_reproducible | Recomputed from repo data in this run | E01–E08, E11–E14, E17–E21 |
| official_reported | Transcribed from an official document; not recomputable | E16 |
| unresolved | Open discrepancy or open evidence gap | E09, E10 |
| not_computable | Blocked by missing evidence; do not estimate | none |
| superseded | Do not cite | E15 |

Changes on 26 Oct (later): E08 is explained (S24 lacks KA45 Nov–Dec 2025; S32). E11 is classified with VAHAN evidence (S32). E13 is available (S35). E19–E21 follow the verified crosswalk (S30, S31). E09 and E10 stay unresolved: the offset is measured over 42 months, but its cause is not published.

## 3. Corrections to the manual Stage 5 package

| Stage 5 item | Disposition | Rebuilt claim |
| --- | --- | --- |
| C-01 problem statement requirements | Kept (a document reference, not a data claim) | – |
| C-02 36,198 rows, Jan 2022–Sep 2026 | Verified | E01 |
| C-03 sum of rows 8,744,327 | Verified, but not carried: an all-fuel total over 57 months has no use in the analysis | – |
| C-04 67 RTOs, 25 fuel labels, 33 absent RTO-months | Verified | E01, E11 |
| C-05 6,113 BEE records | **Superseded.** S18 has 8,246 rows from the same PDF; 2,349 S18 rows have no Stage 3 match; 216 Stage 3 rows have no coordinates | E14 (use), E15 (superseded) |
| C-06 PIB/MHI 6,096 (751 fast, 5,345 slow) | Verified against register S17; S03 (6,097) added | E16 |
| C-07 district registrations-per-charger not defensible | Kept and made explicit at three levels | E19, E20, E21 |
| C-08 "68 and 1.3% unresolved" | **Split.** The 68 is a battery-EV gap against S01; the 1.3% is an all-fuel gap against S25. Both comparators are in the repo; Stage 5 said they were not | E08, E09 (plus E10, Dec 2025) |
| Notes: "7 columns" | Corrected: the source has 8 columns (with `id`) | – |

### Stage 5 source IDs mapped to register IDs

| Stage 5 | Register | Note |
| --- | --- | --- |
| S-01 problem statement | – | `docs/reference/MIH_PS_1_compressed (1).pdf` |
| S-02 registrations by fuel type CSV | S24 (derived S26, S28) | The uploaded copy matches the S24 Karnataka rows on every aggregate checked; its own hash cannot be checked |
| S-03 BEE PDF | S15 (S16, S18, S19) | |
| S-04 BEE e-mobility page | S15 | Landing page recorded in S15 |
| S-05 PIB/MHI 16 Dec 2025 | S17 | |
| S-06 Parivahan analytics / VAHAN report | S29 (VAHAN dashboard report view) | Exports obtained on 26 Oct; S01 kept as history |
| S-07 RTO-district evidence register | `configs/ka_rto_district_crosswalk.csv` | Same 67 RTOs; all verified from S30 (6 in combined units) |
| S-08 registration audit, missing RTO-months | S26, S28 summaries | |
| S-09 CEA EV charging reports | – | Not acquired; not required for Round 1 (report page returned HTTP 404 on 26 Oct) |
| S-10 Dataful | – | Not used |

## 4. Geography claims allowed in the submission

| Level | Demand (EV registrations) | Supply (chargers) | Gap |
| --- | --- | --- | --- |
| State | Yes (E02, E03) | Yes (E14, E16, E17) | Yes, with the caveat that registrations are yearly flows and chargers are installed stock |
| RTO | Yes, as RTO of registration (E04), also by vehicle class (E13) | No: there are no RTO polygons, so chargers cannot be assigned to an RTO | No |
| District unit | Yes (E20), as registrations at offices grouped under the unit | Yes, by point in polygon (E18; Vijayanagara counted in Ballari) | Yes, as a screening indicator (E21) |

District units: 27 single districts plus Kolar + Chikkaballapura and Ballari + Vijayanagar (29 units). Every district statement must say that it counts the **registering office**: S30 §3.3 allows Vahan applications at any office in Karnataka. Bengaluru Urban totals are the 11 offices grouped under it by the department (E19); do not build other "Bengaluru" totals from office names. Do not split RTO, unit or state totals by population, area or name.

## 5. Unresolved claims and evidence gaps

| Claim | What is open | What would close it |
| --- | --- | --- |
| E09 All-fuel Sep 2026 +2,441 (+1.34%) vs S25 | Measured: VAHAN exceeds the statements in all 42 months Apr 2023–Sep 2026 (median +1.17%, S32); the gap is in two-wheelers and cars. Cause not published | The Transport Department's compilation method (for example by RTI) |
| E10 All-fuel Dec 2025 +438 (+0.34%) | As E09 | As E09 |
| E14 BEE rows | Licence now known (BEE Copyright Policy; attribute BEE). Installed, not operational; PDF only; no newer release on 26 Oct | Official machine-readable list; operator status data |
| E19–E21 district units | Grouping as of FY2021-22; KA67 and KA34/KA35 splits not documented | A current jurisdiction order |

Closed on 26 Oct: E08 (−68 explained), E11 (33 RTO-months classified), E13 (S35), E19–E21 (S30/S31).

## 6. Are the remaining Part F sources essential for Round 1?

Round 1 asks for a concept: methodology, implementation roadmap and data strategy (problem statement, "Round 1: Concept & Roadmap Submission"; data strategy is 10% of the score). A source is **essential** only if the submission states a figure or rule that depends on it. Otherwise it is enough to list it in the data strategy with its true status ("planned" or "not acquired").

| Source (checklist) | Used for | Essential for Round 1? | Recommendation |
| --- | --- | --- | --- |
| CEA EVCS reports (F.3) | Core stage 3: energy consistency check and calibration (R4-05, R4-10) | **No.** R4-05 says calibration never blocks the core. | Write stage 3 as "method only" on 29 Oct unless one recent report is extracted first (the five Karnataka DISCOM rows). Never call CEA validation (R4-13) |
| DISCOM service areas (F-074) | RTO → DISCOM join (R4-03), CEA at DISCOM level | **No.** RTO → district is unverified, so RTO → DISCOM is blocked anyway. | Roadmap item. The electricity layer can be shown now with OSM power lines and points (S23) |
| WorldPop grid (F-077) | Population within reach (I-033), sub-district demand spreading | **No.** The district demographic layer exists (Census 2011, S04/S09). | Roadmap item for the finale. Revise the D.3 target "Verified (WorldPop)" to "Verified (Census 2011); Planned (WorldPop)" |
| MoP EV charging guidelines 2024 (F-085) | Spacing rules 1 km / 20 km / 100 km (I-001 to I-004) | **Yes, if the spacing rules are cited.** | **Acquired (S33):** clause 11(1)(a)–(c), page 7 of 36; advisory ('may be adopted') |
| PM E-DRIVE guidelines (F-084) | Site categories, subsidy rates and caps (R4-16, Part N) | **Yes, if any subsidy rate, cap or eligibility is stated.** | **Acquired (S34):** EV PCS operational guidelines, 26 Sep 2025, §6 Table 2 and §7 Tables 3–4 |
| NITI / WRI handbook (F-087) | Baseline method (R4-06) | Only if it is named as a baseline | Download if named, otherwise describe the baseline without attribution |
| Electricity (Rights of Consumers) Amendment Rules 2024 (F-086) | Delivery tracker connection deadlines (P1) | No | Roadmap item |

**Status (26 Oct, later):** both guideline PDFs are acquired and their clauses recorded (S33, S34; `GAP_CLOSURE_REPORT.md` §6). CEA, DISCOM areas and WorldPop are not required for Round 1; list them in the roadmap as "planned".
