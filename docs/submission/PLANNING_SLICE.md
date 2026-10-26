# Karnataka planning slice (R4-11, checklist Part L)

Date: 27 October 2026 · Branch `feature/ka-ev-registrations` · Code `src/evinfra/scoring/build_karnataka_planning_slice.py` · Parameters `configs/planning_slice_parameters.json` · Generated copies in `docs/submission/planning_slice/`

This slice is one reproducible run from the register datasets to proposed charger sites. Under stated rules and an illustrative budget, it shows that the pipeline joins demand evidence, charger evidence, policy clauses and candidate locations. **It is not a validated recommendation.** Every site is a *model-selected candidate*: land, parking, grid connection, outlet ownership and eligibility have not been checked.

## How to rerun

```
python src/evinfra/scoring/build_karnataka_planning_slice.py            # build and compare with the tracked copies
python src/evinfra/scoring/build_karnataka_planning_slice.py --update-docs
python -m pytest tests/unit/test_planning_slice.py
```

The builder reads only processed register datasets and raw files that are already in the repository (`inputs.csv` lists them with row counts and SHA-256). It also checks that the S33 and S34 PDFs match the hashes in the register. It uses only the standard library and runs in a few seconds.

**Reproducibility check on 27 Oct:** the output folder was deleted and rebuilt, and all 8 files came out byte-identical. A second build in the same process is also identical (test). The checklist's teammate rerun on another laptop (L-012 to L-014) has **not** been done.

## Method and result

| Step | Rule (basis) | Result |
| --- | --- | --- |
| 1. Demand | Observed battery-EV registrations, 2025, e-4W classes MOTOR CAR, MOTOR CAB and MAXI CAB (S35). Grouped by **registering office** into 29 district units (verified crosswalk, S30/S31) | e-4W per unit in `unit_screen.csv`. Not the location of vehicles (S30 §3.3) |
| 2. Charger evidence | BEE rows with valid coordinates (S18, 8,232) and OSM records (S11, 67). Each is classed for e-4W from the connector standard: confirmed, confirmed not (LEV), or unknown (assumption) | No record has an operating status; all are treated as listed, not working |
| 3. Unit screen | e-4W registrations per BEE site with an e-4W confirmed or unknown row; units need ≥ 500 e-4W registrations (assumption) | 4 of 29 units qualify. **Mysuru 35.4** (814 / 23); Dakshina Kannada 28.3; Bengaluru Urban 28.1; Udupi 26.6. The margin is small, so this ranking is not robust |
| 4. Candidates | OSM fuel stations (S23) in the unit within 3 km of an OSM city or town node (urban proxy, assumption). Rejected if an e-4W confirmed or unknown charger is within 1 km (S33 cl. 11(1)(a), advisory; used as a distance screen) | 147 fuel stations: 94 outside the urban proxy, 22 inside the 1 km radius, 31 eligible |
| 5. Selection | Greedy by coverage gap (distance to the nearest e-4W confirmed or unknown charger); at least 1 km apart; one site per settlement; illustrative public budget of INR 50 lakh (planner input) | 7 sites selected, public cost INR 43.97 lakh. **The budget did not bind:** INR 6.03 lakh remains, but the other 24 eligible stations break the spacing or one-per-settlement rule. The site count is set by those rules, not by the budget |
| 6. Cost split | 1 × CCS-II 50 kW at the BEE benchmark: upstream 6.04 + EVSE 7.25 = INR 13.29 lakh (S34 §7). Subsidy category from the OSM brand: B for PSU OMC outlets (80% upstream, 70% EVSE), otherwise C (80% upstream) (S34 §6 Table 2) | C: public 4.832, operator 8.458. B: public 9.907, operator 3.383 (INR lakh). Eligible is **modelled, not sanctioned** |

**Selected sites** (`docs/submission/planning_slice/proposal.csv`):
- KA-SLICE-01 Hunsur, 18.7 km to the nearest e-4W charger
- KA-SLICE-02 Bannur, 18.0 km
- KA-SLICE-03 Hullahalli, 12.9 km
- KA-SLICE-04 Periyapatna (HP, B), 5.1 km
- KA-SLICE-05 Nanjanagudu, 3.9 km
- KA-SLICE-06 Heggadadevanakote (HP, B), 2.8 km
- KA-SLICE-07 Mysuru edge, 1.7 km

The site card for KA-SLICE-01 is in `planning_slice/site_card.md`, and the map in `planning_slice/map.svg`. KA-SLICE-01 is named "Bharath Petrol bunk" in OSM but has no brand tag, so it is costed as Category C. A brand check could move it to B. This shows why category is a modelled field.

## What the slice shows (checklist Part L)

| Item | Status | Evidence |
| --- | --- | --- |
| L-001 One script from inputs to proposed sites | Done | Builder above. It starts from processed register datasets, each with its own reproducible builder; it does not start from `/data/raw` alone |
| L-002 Reads only `/data/raw` and `settings.yaml` | Not met | Reads `data/processed` and `configs/`; no `settings.yaml` exists (Part I not frozen) |
| L-003 Source names, dates, row counts | Done | `inputs.csv`, `summary.json` |
| L-004 Deduplication example | Partial | Proximity example (BEE row to OSM record, within 100 m). None in Mysuru (0 of 75 sites), so the example is from Bengaluru Urban. Not a merge: H-014 and H-018 are open |
| L-005 RTO joined to district and charger evidence | Done (district); DISCOM not done | `site_card.md`, `rto_served_bev.csv`: KA9, KA45 and KA55 → Mysuru |
| L-006 Charger count vs official figures | Done in the evidence package | Claims E14–E18 (`docs/submission/claim_register.csv`); not repeated here |
| L-007 Registrations per RTO by class | Done | S35; unit RTOs in `rto_served_bev.csv` |
| L-008 CEA consistency chart | Not done | CEA not acquired (GAP_CLOSURE_REPORT §7) |
| L-009 Proposed-site fields | Done except L-009e | Capacity range not computed: d, H and confidence scores are not frozen (I-013, I-014, I-024 to I-028). Listed chargers within 5 km are shown instead |
| L-010 Missing fields and fallbacks | Done | `site_card.md` |
| L-011 Map | Partial (SVG; chargers listed, not merged) | `planning_slice/map.svg` |
| L-012 to L-017 Teammate rerun, tag | Not done | Needs a second person |

## Stage status (R4-07)

| Stage | Status after this slice |
| --- | --- |
| 1. Charger evidence layer | **Partial.** Listed BEE and OSM records with e-4W state and proximity matches. No merged table and no confidence scores |
| 2. Demand by class at RTO level | **Demonstrated.** Observed registrations by RTO, class and month (S35), by registering office |
| 3. CEA calibration and gap analysis | **Method only** (CEA data not acquired) |
| 4. Budget-constrained site selection | **One example run demonstrated** (one unit, e-4W, greedy, illustrative budget). Optimiser, equity mode and other vehicle types are method only |
| 5. Proposal export | **One site card demonstrated**; no capacity range |
| 6. Validation | **Method only** |

## Limits (do not overstate)

- Rules were written on 27 Oct, before the e-4W results were computed, but after the all-class table (E21) was published. They are **not pre-registered** in the R4-19 sense, and no sensitivity test has been run.
- The coverage-gap objective rewards distance from listed chargers. It does not measure demand at the site, because registrations have no location inside a unit.
- Listed chargers with unknown status are treated as present. Chargers that do not work would make the gaps larger than shown.
- Costs are BEE benchmarks from August 2022, not quotes. Category B is inferred from the OSM brand tag.

## Logical Consistency Check (27 Oct 2026)

**Result: WARNING.** No arithmetic or rule discrepancy was found. One wording issue was fixed (the budget did not bind). The limits below remain. This targeted check of the slice does not validate the project as a whole.

| Check | Result | Evidence |
| --- | --- | --- |
| Scope | PASS with WARNING | The checklist, changelog, ADR-001 amendment, README and rules all name Karnataka. The base deep-scan report (Rev3, 22 Oct; the latest version in Downloads) still describes Telangana. It is kept unchanged as history, and ADR-001 overrides it on geography |
| Registrations | PASS | Unit screen totals equal the 2025 totals in S35: e-4W 21,174; all BEV 203,698 |
| Charger rows | PASS | 8,232 BEE rows with valid coordinates (8,246 − 8 outside polygons − 6 lat = lon) and 67 OSM records. Both sum exactly across the 29 units |
| Candidates | PASS | 147 = 94 outside the urban proxy + 22 inside the 1 km radius + 24 eligible but not selected + 7 selected. No duplicate OSM IDs. All coordinates inside the Karnataka bounding box |
| Cost split | PASS | For each site: public = subsidy + other public, and total = public + operator. Category C public 4.832, B 9.907; total public 43.974 ≤ 50 (INR lakh) |
| Budget semantics | WARNING (fixed in text) | The budget did not bind. The table above now says so. The result is unchanged |
| Map vs outputs | PASS | 7 site markers and 7 labels, matching `proposal.csv` |
| Labels | PASS | Registrations are labelled by registering office, not vehicle population. Chargers are "listed", none operational. Sites are "model-selected candidate". The basis of each parameter is stated |
| Method consistency | PASS | The code, the parameters file, this report, the site card and the changelog R4-11 status describe the same rules and figures |
| Reproducibility | PASS | Rebuild from an empty folder is byte-identical (8 files). The tracked copies compare "same". 160 tests pass |
| Progress integrity | PASS | The checklist marks complete only L-001, L-003, L-005, L-007, L-009a–d and f–h, and L-010. L-002, L-004, L-008, L-009e, L-011 and L-012–L-017 are open or partial |

**Unresolved limitations:**
- The slice starts from processed data, not raw files (L-002).
- No capacity range, merged charger table or CEA chart.
- The rules are not pre-registered and have no sensitivity test.
- There is no located demand inside a unit.
- Subsidy category is inferred from the OSM brand tag.
- No teammate rerun.

## Selection-method sensitivity (27 Oct 2026)

The alternatives were frozen in `configs/planning_slice_sensitivity.json` and committed (`e85461c`) before any was run. Each variant changes one baseline rule; the baseline parameters and outputs are unchanged. Rerun with `python src/evinfra/scoring/run_planning_slice_sensitivity.py`, which writes `planning_slice/sensitivity.csv`. All variants are reported. The unit screen is not varied, so every variant selects within Mysuru.

| Variant | Change | Eligible | Selected | Public cost (INR lakh) | Budget binds | Baseline sites kept |
| --- | --- | --- | --- | --- | --- | --- |
| V0 baseline | none | 31 | 7 | 43.974 | no | 7 of 7 |
| V1 | duplication radius 0.5 km | 41 | 7 | 43.974 | no | 7 of 7 |
| V2 | duplication radius 2 km | 20 | 6 | 39.142 | no | 6 of 7 |
| V3 | urban proxy 2 km | 18 | 6 | 39.142 | no | 5 of 7 |
| V4 | urban proxy 5 km | 50 | 8 | 48.806 | no | 6 of 7 |
| V5 | city nodes only | 10 | 1 | 4.832 | no | 1 of 7 |
| V6 | budget INR 25 lakh | 31 | 4 | 24.403 | yes | 4 of 7 |
| V7 | no one-per-settlement cap | 31 | 7 | 49.049 | yes | 5 of 7 |

**Reading:**
- **Stable:** the top four sites (Hunsur, Bannur, Hullahalli, Periyapatna) are selected in every variant except V5. The looser duplication radius (V1) changes nothing.
- **Sensitive:**
  - The town rule changes the most: city-only keeps only the Mysuru-edge site.
  - Without the per-settlement cap (V7), 5 of the 7 baseline sites are kept. Two are replaced by sites the cap had excluded, and the budget then binds.
  - The site count follows the eligibility rules, except when the budget is set below the baseline spend (V6).

**Budget: a ceiling, not an optimisation target.** The design intends budgets to drive allocation: R4-07 core stage 4, the public-cost constraint in R4-16, and the same-budget comparisons in R4-06. A defensible budget optimiser needs an objective measured in benefit per rupee, such as population or demand within reach of a compatible charger. That objective requires located demand (WorldPop is not acquired; registrations show only the registering office) and frozen capacity and accessibility definitions (Part I is open). Neither exists. So **budget optimisation is not implemented**. The slice keeps greedy selection by coverage gap, with the budget used only as a ceiling. "Budget-constrained site selection" stays method only beyond this ceiling.

**Limits:**
- Coverage gap is a distance proxy, not demand served.
- No variant is ground truth.
- Operational feasibility (land, grid, ownership, working chargers) is not tested.
- The variants are single-rule changes, not a full sensitivity analysis.
