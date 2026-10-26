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
| 5. Selection | Greedy by coverage gap (distance to the nearest e-4W confirmed or unknown charger); at least 1 km apart; one site per settlement; illustrative public budget of INR 50 lakh (planner input) | 7 sites selected, public cost INR 43.97 lakh |
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
