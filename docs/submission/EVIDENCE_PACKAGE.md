# Round 1 Evidence Package (Stage 5 rebuild)

Date: 26 October 2026 · Branch: `feature/ka-ev-registrations` · Pilot geography: Karnataka (ADR-001)

This package replaces the manual Stage 5 package in `data/manual inspection reports/build submission ready evidence package/` (kept unchanged, untracked). Every figure now comes from repository data and uses register IDs from `configs/source_register.csv`.

- **Claim register:** `docs/submission/claim_register.csv` (21 claims, E01–E21). It is generated, so do not edit it by hand.
- **Generator and audit:** `python src/evinfra/analysis/build_evidence_package.py`. It writes `outputs/reports/evidence_package/` (claim register, district charger supply table, `audit.json` with input hashes). It exits non-zero if the audit fails or the tracked register differs. `--update-docs` rewrites the tracked copy (only when the audit passes).
- **Tests:** `tests/unit/test_build_evidence_package.py`.

## 1. Rules the audit enforces

1. A district-level demand or gap claim must be `not_computable` while no RTO in `configs/ka_rto_district_crosswalk.csv` is `verified_official`. Today 0 of 67 are verified.
2. The superseded figure 6,113 (Stage 3 BEE extraction) may appear only in its own `superseded` claim.
3. Each discrepancy claim states its metric in its first words: "Battery-EV" or "All-fuel". The 2025 −68 and the September 2026 +1.34% are separate claims with separate comparators.
4. Every register ID in a claim exists in the register. Every hand-transcribed official value (S03, S17, S25) appears, formatted the same way, in its register row.
5. S12 has no district EV registrations, and the district supply table sums to the S18 rows with a point district (8,232).

## 2. Claim statuses

| Status | Meaning | Claims |
| --- | --- | --- |
| verified_reproducible | Recomputed from repo data in this run | E01–E07, E12, E14, E17, E18 |
| official_reported | Transcribed from an official document; not recomputable | E16 |
| unresolved | Open discrepancy or open evidence gap | E08, E09, E10, E11, E19 |
| not_computable | Blocked by missing evidence; do not estimate | E13, E20, E21 |
| superseded | Do not cite | E15 |

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
| S-06 Parivahan analytics / VAHAN report | S01 route | No export obtained; access failures recorded in `docs/research/KA_EV_REGISTRATIONS_REPORT.md` |
| S-07 RTO-district evidence register | `configs/ka_rto_district_crosswalk.csv` | Same 67 RTOs, all unresolved |
| S-08 registration audit, missing RTO-months | S26, S28 summaries | |
| S-09 CEA EV charging reports | – | Not acquired (checklist F.3) |
| S-10 Dataful | – | Not used |

## 4. Geography claims allowed in the submission

| Level | Demand (EV registrations) | Supply (chargers) | Gap |
| --- | --- | --- | --- |
| State | Yes (E02, E03) | Yes (E14, E16, E17) | Yes, with the caveat that registrations are yearly flows and chargers are installed stock |
| RTO | Yes, as RTO of registration (E04) | No: there are no RTO polygons, so chargers cannot be assigned to an RTO | No |
| District | **No** (E20) | Yes, by point in polygon (E18; Vijayanagara counted in Ballari) | **No** (E21) |

Do not write "Bengaluru" totals by grouping KA1–KA5, KA41, KA51 or other RTOs. Do not split RTO or state totals by population, area or name.

## 5. Unresolved claims and evidence gaps

| Claim | What is open | What would close it |
| --- | --- | --- |
| E08 Battery-EV 2025 −68 vs S01 | S01 export date and filters not recorded | A fresh VAHAN export with recorded filters and time |
| E09 All-fuel Sep 2026 +2,441 (+1.34%) vs S25 | Cut-off or category rules not known | Same-month comparison over more S25 statements; the definitions in the statement |
| E10 All-fuel Dec 2025 +438 (+0.34%) | As E09 | As E09 |
| E11 33 RTO-months without rows (KA45, KA46, KA57) | Zero or unreported | RTO-level VAHAN view for those months, or an official RTO activity record |
| E13 Battery-EV by vehicle class at RTO level | No accessible source | Manual VAHAN export per RTO (dashboard failed on 25 and 26 Oct) |
| E19–E21 RTO-to-district | 0 of 67 RTOs verified | Transport Department jurisdiction list or gazette notifications |
| E14 BEE rows | Licence not stated; installed, not operational; PDF extraction only | Official machine-readable list; operator status data |

## 6. Are the remaining Part F sources essential for Round 1?

Round 1 asks for a concept: methodology, implementation roadmap and data strategy (problem statement, "Round 1: Concept & Roadmap Submission"; data strategy is 10% of the score). A source is **essential** only if the submission states a figure or rule that depends on it. Otherwise it is enough to list it in the data strategy with its true status ("planned" or "not acquired").

| Source (checklist) | Used for | Essential for Round 1? | Recommendation |
| --- | --- | --- | --- |
| CEA EVCS reports (F.3) | Core stage 3: energy consistency check and calibration (R4-05, R4-10) | **No.** R4-05 says calibration never blocks the core. | Write stage 3 as "method only" on 29 Oct unless one recent report is extracted first (the five Karnataka DISCOM rows). Never call CEA validation (R4-13) |
| DISCOM service areas (F-074) | RTO → DISCOM join (R4-03), CEA at DISCOM level | **No.** RTO → district is unverified, so RTO → DISCOM is blocked anyway. | Roadmap item. The electricity layer can be shown now with OSM power lines and points (S23) |
| WorldPop grid (F-077) | Population within reach (I-033), sub-district demand spreading | **No.** The district demographic layer exists (Census 2011, S04/S09). | Roadmap item for the finale. Revise the D.3 target "Verified (WorldPop)" to "Verified (Census 2011); Planned (WorldPop)" |
| MoP EV charging guidelines 2024 (F-085) | Spacing rules 1 km / 20 km / 100 km (I-001 to I-004) | **Yes, if the spacing rules are cited.** The clause must be read and recorded; do not cite the numbers from memory. | Download (one PDF) and record clauses, or remove the numeric spacing rules from the text |
| PM E-DRIVE guidelines (F-084) | Site categories, subsidy rates and caps (R4-16, Part N) | **Yes, if any subsidy rate, cap or eligibility is stated.** | Download and cite clauses, or write the cost section without subsidy numbers ("not checked") |
| NITI / WRI handbook (F-087) | Baseline method (R4-06) | Only if it is named as a baseline | Download if named, otherwise describe the baseline without attribution |
| Electricity (Rights of Consumers) Amendment Rules 2024 (F-086) | Delivery tracker connection deadlines (P1) | No | Roadmap item |

**Minimum action before 30 Oct:** decide whether the methodology cites spacing rules and subsidy rules. If it does, get the two guideline PDFs (S19 and S20 in checklist numbering), record them in the register with hashes, and record the clauses. All other sources go into the roadmap as "planned", with their status stated.
