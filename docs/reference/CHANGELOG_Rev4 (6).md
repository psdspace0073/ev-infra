# Changelog: Revision 4 (fixes from the judge review)

EV Infra Map India · Techfest 2026-27 · Track 1
Planned 22–30 Oct 2026 · Round 1 deadline: **30 Oct 2026** (team leader submits, one submission only)

Base document: `EV_Infra_Green_Mobility_AI_Challenge_Deep-Scan_Report_Rev3.md`

> **Geography change (25 Oct 2026):** the pilot geography is now **Karnataka**; Telangana is a future expansion geography. See [`docs/decisions/ADR-001-geography.md`](../decisions/ADR-001-geography.md). R4-01, R4-02, R4-03, R4-05, R4-06, R4-07, R4-09, R4-11, R4-19 and R4-20 are updated below. Remaining Telangana references are history (review summaries, earlier figures) or describe Telangana's future-expansion role. Methods, scoring, optimiser and validation design do not change.

**Priority:** P0 = must be done before submission · P1 = should be done · P2 = nice to have
**Owner:** still blank. **Blocker:** assign owners for data, modelling, validation, UI/export and submission before any other work on 24 Oct.

---

## Summary

The first review's two big points stand: **prove the data works** and **cut the promised scope**. Three of its five issues are already handled in Rev 3 and only need clearer wording. Two problems it missed are added here (CEA in Telangana, circular validation).

The second review (22 Oct) found no new structural holes. It sharpened definitions, and adds R4-15 to R4-19 plus changes to R4-05, R4-06 and R4-11.

The third review (23 Oct) found definition errors in R4-15 and R4-19: RTO-level registrations were being treated as if their location were known, and spacing rules were being converted into travel times. These are corrected as factual fixes under the review freeze. It also adds a deliverable map (R4-20) and turns R4-11 into a defined, reproducible slice. No new features.

**Review freeze:** no further review rounds before submission. New items are accepted only if they unblock the build or fix a factual error. The data work (R4-01 to R4-04) comes first, because everything else depends on it.

| # | Fix | Priority | Due | Owner |
| --- | --- | --- | --- | --- |
| R4-01 | Source-access matrix | P0 | 24 Oct | |
| R4-02 | Download core Karnataka datasets | P0 | 24 Oct | |
| R4-03 | One complete end-to-end join | P0 | 24 Oct | |
| R4-04 | Label every dataset: verified / planned / synthetic | P0 | 24 Oct | |
| R4-05 | National state-level CEA calibration | P0 | 26 Oct | |
| R4-06 | Non-circular validation metrics | P0 | 27 Oct | |
| R4-07 | Freeze scope: core vs stretch | P0 | 25 Oct | |
| R4-08 | Short Round 1 submission | P0 | 29 Oct | |
| R4-09 | Roadmap with owners, dependencies, cutoffs | P1 | 27 Oct | |
| R4-10 | "With vs without CEA" comparison | P1 | 27 Oct | |
| R4-11 | Reproducible Karnataka slice: raw files to one proposed site | P0 | 26 Oct | |
| R4-12 | Units on every equation | P1 | 28 Oct | |
| R4-13 | Wording fixes (confidence scores, "optimal") | P1 | 28 Oct | |
| R4-14 | Claim audit before submission | P1 | 29 Oct | |
| R4-15 | Estimated compatible charging capacity per vehicle type, as a range | P1 | 27 Oct | |
| R4-16 | Cost split: total, subsidy, operator share; subsidy caps checked | P1 | 27 Oct | |
| R4-17 | Tier label on every output site | P1 | 28 Oct | |
| R4-18 | Decision-maker acceptance test | P1 | 28 Oct | |
| R4-19 | Pre-registered metric definitions and thresholds | P0 | 25 Oct | |
| R4-20 | Deliverable map: Round 1 evidence vs finale commitment | P0 | 29 Oct | |

---

## Added

### R4-01 · Source-access matrix (P0)
**Why:** The judge's first question will be "show me these datasets exist and can be joined."
**What:** One table, one row per dataset, with these columns:
dataset · exact URL · format · geographic level · time period · licence or access limit · status (verified / planned / synthetic) · fallback if unavailable.
**Covers at minimum:** OSM, Open Charge Map, EV Yatra, MoP state counts, Karnataka real-plan candidates (reported PM E-DRIVE approvals, BESCOM portal; not verified), VAHAN (dashboard or India Data Portal), CEA EVCS report, DataMeet boundaries, WorldPop, IHMCL.
**Done when:** every row has been opened and checked by a team member, with the date checked.

### R4-02 · Download core Karnataka datasets (P0)
**What:**
- Charger records for Karnataka from at least 3 sources (OSM, OCM, state or DISCOM list such as the BESCOM portal, if verified).
- VAHAN Karnataka EV registrations by RTO (KA codes) × vehicle class × month. **Status:** the file in the repo (S01) holds statewide calendar-year totals only; an RTO × class × month export is not verified to exist. Record the result either way.
- CEA rows for BESCOM, MESCOM, HESCOM, GESCOM and CESC.
- Karnataka RTO and district boundaries: 31 current LGD districts vs 30 Census 2011 districts (Vijayanagar split from Ballari).

**Done when:** files are saved in the repo's raw folder with retrieval dates and file hashes, as in the M11 raw layer.

**Status (25 Oct):** OSM done (register S10, inventory S11, district join S12; 67 mapped records, one lineage). Open Charge Map blocked: API key needed (S13). RTO-level VAHAN not obtained: the India Data Portal package has no download URL (S14), and the dashboard needs manual download. CEA rows, RTO list and DISCOM lists not started.

### R4-03 · One complete end-to-end join (P0)
**What:** RTO (KA codes) → district/DISCOM (BESCOM, MESCOM, HESCOM, GESCOM, CESC) → charger records → H3 cells for Karnataka, producing one table.
**Blocked:** needs an RTO-level VAHAN export and an RTO jurisdiction list. Until then only the district-level join (S09) exists; no RTO split is invented.
**Includes:** the first version of the RTO-to-DISCOM crosswalk, built by hand if needed.
**Done when:** a single query returns, per RTO, the EV count by class, the charger count, and the DISCOM it belongs to.

### R4-04 · Data status labels (P0)
**What:** every dataset and every number in the submission is tagged **Verified** (downloaded and checked), **Planned** (source exists, not yet pulled) or **Synthetic** (made up for the demo, documented per Rule 5).
**Rule:** UBC, Delhi OpenEV, substation capacity and site-level sessions are **Planned**, never described as working.

### R4-05 · National state-level CEA calibration (P0) · *missed by the review*
**Problem:** Karnataka has five DISCOMs (BESCOM, MESCOM, HESCOM, GESCOM, CESC), so in the demo state CEA checks just five totals a month (Telangana, the earlier demo state, has two). The public-charging rates per vehicle class can only be estimated across many utilities (~55 nationally), which quietly needs VAHAN for every reporting state.
**Fix:**
- Calibrate public-charging rates **nationally**, using **state-level** VAHAN totals by class for the ~15 CEA-reporting states (easy dashboard downloads).
- Keep RTO-level detail for **Karnataka only** (needs an RTO-level VAHAN export, not yet verified).
- State this split openly in the methodology (update M3).

**Go/no-go check by 26 Oct.** Before committing, confirm:
- Which states have usable class-specific registration totals for the same months as CEA.
- That CEA's "excluding heavy duty" energy covers the same charging population the model represents.
- How missing classes, hybrids and unregistered vehicles are handled (M3 rules).
- That calibrated rates stay stable when each state is left out once (leave-one-state-out).

**Fallback (no-go):** national calibration becomes a research objective in the roadmap; the submission uses the Karnataka-only aggregate check with wide bands, stated openly. No precision is invented to keep the architecture.

**Calibration never blocks the core.** It runs in parallel with the join, the map and site selection, and never delays them. If the national rates are unstable in the leave-one-state-out check, report the instability and its size; do not adjust the method until it passes.

**Done when:** either one national calibration run produces rates with bootstrap intervals and passes the leave-one-state-out check, or the fallback is written into the methodology.

### R4-06 · Non-circular validation metrics (P0) · *missed by the review*
**Problem:** if "demand served" is measured with our own demand model, our optimiser wins by construction.
**Fix:** compare all methods on the **same budget** using measures our model does not produce:
- Share of population within X minutes of a working charger.
- Registered EVs per RTO within reach of a charger.
- Overlap with a real published Karnataka site-level plan (reported as agreement, never as accuracy). **Method only / not evaluated:** no verified Karnataka plan is established yet (candidates to check: reported 1,571 PM E-DRIVE approvals, BESCOM portal).
- Duplication of existing chargers within 1 km.
- Public cost per site.

**Methods compared:**
1. A simple baseline (proportional-to-EVs or nearest-demand).
2. The NITI/WRI grid-cell method.
3. A real Karnataka plan, if one is verified (otherwise method only / not evaluated).
4. Our engine.

Our own "demand served" number is reported separately, labelled as model-based. Every metric uses the fixed definitions in R4-19. Update M7 test C.

### R4-10 · "With vs without CEA" comparison (P1)
**What:** run the allocation twice, with and without the CEA calibration, and report how many selected sites change.
**Why:** this shows whether calibration actually matters for decisions. If it changes nothing, say so honestly. Add as M7 test H.

### R4-11 · Reproducible Karnataka slice: raw files to one proposed site (P0)
**Why:** checklist targets are not proof. One reproducible path from raw files to a recommendation is the strongest evidence of execution, and a small working slice beats a national architecture diagram.
**What the slice must show, end to end:**
- Source names, retrieval dates and row counts for every input file.
- A deduplication example: one charger appearing in several sources, with its lineage groups and merged record.
- One RTO-level result joined to its district/DISCOM and its nearby charger evidence.
- Reconciled Karnataka charger count vs the official figures: 6,097 public charging stations installed (MoP annexure, in S03; publication date not stated in the file), 6,805 (reported MHI figure, March 2026, **not yet verified**) and the Karnataka OMC values in the Rajya Sabha annexure (**not yet verified**). First record what each figure counts: date, stations or charge points, public only or all, installed or operational. Any gap is treated as a definition or date difference until shown otherwise. Deduplication keeps every record's lineage. (Previous Telangana figures: 1,063 state, 1,173 OMC.)
- EV registrations per RTO by class (observed totals), if an RTO-level export is obtained; otherwise statewide totals only, with the gap stated.
- One CEA comparison chart, labelled a **consistency check**, not validation, because Karnataka's DISCOM totals feed the calibration.
- One proposed site with its rationale, estimated cost split (R4-16), compatibility, uncertainty range and tier label (R4-17).
- A list of missing fields and the fallback used for each.
- One map screenshot.

**Done when:** a teammate who did not build it can rerun it from the raw files and get the same output.

### R4-15 · Estimated compatible charging capacity per vehicle type, as a range (P1)
**Problem:** M2 discounts each charger by its public and working scores, but treats capacity as one pool. A car fast charger doesn't serve e-rickshaws, and a single number hides that status is often unknown. A count of listed chargers is also not the same as capacity.
**Name:** the output is called **estimated compatible charging capacity** (kWh/day), never "observed" or "service" capacity, because only connector types, counts and rated power are known.
**Fix:**
- Compute capacity separately per vehicle type, counting a charger only for the types its connector and power serve.
- State every assumption that turns rated power into daily capacity: uptime (from the confidence score and network prior), usable power (rated kW less derating), simultaneous use (whether connectors share power) and usable hours per day. Each is a named value in M8 with a range.
- No session or usage data is invented to fill gaps.
- Report a range instead of one number: **low** = high-confidence chargers only (C\_functional ≥ 0.7); **high** = all listed chargers; **central** = the confidence-weighted value (M2).
- Gaps and site choices are shown at the central value, with the low and high values alongside.
- Low, central and high are **scenarios, not bounds**: the same assumptions apply to all three, and "high" is what the listings would deliver under those assumptions, not a ceiling on real delivered energy.

**Calculation (fixes the definition; values set on 25 Oct with sources, ranges in M8).** For each charger i:

- Compatibility has three recorded states per charger and type: **confirmed**, **confirmed not**, or **unknown**. The scenario value k^s\_{i,c} is 1 if confirmed, 0 if confirmed not, and for unknown: 0 in the low and central scenarios, 1 (provisionally) in the high scenario. Every k used below is this scenario value.
- Usable power U\_i (kW) = min(n\_i × P\_i, S\_i) × d, where n\_i is the number of connectors, P\_i the rated kW per connector, S\_i the site power limit when connectors share power (otherwise S\_i = n\_i × P\_i), and d the derating factor.
- Daily energy E\_i (kWh/day) = U\_i × H, where H is usable hours per day.

The physical term E\_i is **identical in all three scenarios**. Scenarios differ only in the weight w\_i given to each charger:

| Scenario | Weight w\_i |
| --- | --- |
| Low | 1 if C\_functional ≥ 0.7 and C\_public ≥ 0.7, else 0 |
| Central (confidence-weighted) | C\_functional × C\_public: a heuristic discount, not a probability-derived expected capacity (M2); thresholds and weights sensitivity-tested in M7 test E |
| High | 1 for every listed compatible charger |

**Local capacity indicator** for zone z and type c in scenario s: Q^s\_{z,c} = Σ over chargers i near z of k^s\_{i,c} × w^s\_i × E\_i. Neighbouring zones share the same chargers, so this is a **display indicator only**: it is never summed across zones and never used for adequacy or unmet demand.

Rules:
- **No double-counted uptime.** Operating status enters only through C\_functional, which already contains the network uptime prior. No separate uptime multiplier is applied on top.
- **No double-counted chargers across types.** A charger serving several types counts for each in accessibility, but in capacity adequacy its energy is shared by an explicit allocation: variables y\_{i,z,c} ≥ 0 (kWh/day from charger i to zone z, type c), allowed only where k\_{i,c} = 1 and z is within the accessibility threshold, with
  - Σ over z and c of y\_{i,z,c} ≤ w^s\_i × E\_i for every charger i (a charger never gives out more than its energy);
  - Σ over i of y\_{i,z,c} ≤ D\_{z,c} for every zone and type (no more than the demand);
  - residual demand R\_{z,c} = D\_{z,c} − Σ over i of y\_{i,z,c} ≥ 0, which is the unmet demand that feeds the gap analysis when demand exceeds capacity.
  The allocation maximises total allocated energy (a small linear program, solved per scenario), so it is reproducible.
- **Unknown compatibility** follows the three-state rule above.
- **Allocatable capacity** is the energy actually assigned by the allocation, Σ over i of y\_{i,z,c}. Capacity adequacy, unmet demand and every total reported across zones use this quantity, never Q^s\_{z,c}.

Update M2 (Q\_z becomes Q^s\_{z,c}) and the M7 test E conservative variant.

### R4-16 · Policy-correct cost split (P1)
**Problem:** M4 applies PM E-DRIVE subsidy rates by site category but outputs only public cost. A proposal must show who pays what.
**Fix:**
- Every proposed site shows these fields, each counted exactly once:

| Field | Definition |
| --- | --- |
| Total project cost | Upstream (grid) cost + equipment cost, central scenario with low/high range (M4) |
| PM E-DRIVE subsidy (modelled eligible) | σ\_up × upstream + σ\_eq × equipment, by site category (M4) |
| Other public funding | Planner input, such as a state top-up; default 0 |
| Public cost | PM E-DRIVE subsidy + other public funding |
| Operator share | Total project cost − public cost |

- "Government contribution" is not a separate amount: it is the **public cost** row, and the subsidy is never added to it a second time.
- The budget constraint applies to public cost (or to the PM E-DRIVE portion alone, if the planner chooses); the operator share is reported so viability can be judged.
- Read the PM E-DRIVE charger guidelines for any per-charger or per-site subsidy caps and eligibility conditions before writing them in. Nothing is assumed: if a cap is not found, write "no cap identified" with the document checked.
- **Eligible is not sanctioned.** The output shows "eligible subsidy (modelled)"; a sanctioned amount appears only where a published sanction list confirms it. Every eligibility rule and cap carries a reference to the clause it comes from.

Update M4 and the proposal export fields.

### R4-17 · Tier label on every output site (P1)
**Already designed** in M5 (deployable, feasible candidate, planning candidate, excluded). The fix is making it visible everywhere.
**Rule:** every site on the map, in the proposal and in the export carries one of three claims:

| Label | Meaning | M5 tier |
| --- | --- | --- |
| Model-selected candidate | Chosen by the optimiser from an eligible category; land, parking and grid not checked | Planning or feasible candidate |
| Feasibility-checked | Land category, access and grid-connection risk screened from available evidence | Feasible candidate with screening done |
| Field-verified | Confirmed by the nodal agency or a site visit | Deployable |

No site is ever described with a stronger claim than its label. For Round 1 and most of the finale, nearly every site will be "model-selected" or "feasibility-checked", and that is stated.

### R4-18 · Decision-maker acceptance test (P1)
**Why:** the user is a state nodal officer, not a researcher. A clever dashboard fails if its recommendations can't be understood or exported.
**Test:** given a budget and PM E-DRIVE site categories, a person outside the team must, without help and within about 10 minutes:
1. Run a plan for the budget.
2. Open a selected site and explain in their own words why it was chosen.
3. See its uncertainty (capacity range, stability score) and its tier label.
4. Compare it with a rejected site and say why that one lost.
5. Export the proposal without rebuilding any calculation by hand.

**Pass:** all five steps completed; anything they got stuck on is fixed before the finale. Write the test into the Round 1 validation section; run it with a friend in early December.

### R4-19 · Pre-registered metric definitions and thresholds (P0)
**Why:** choosing thresholds after seeing results is the easiest thing for a judge to attack. These definitions go into the submission **before any results exist** and do not change afterwards. If one must change, the change and reason are logged.

| Metric | Fixed definition |
| --- | --- |
| Guideline spacing checks | Stay **distance-based**, exactly as the rules are written: one station per 1 km × 1 km urban grid cell; a station every 20 km on both sides of highways; fast charging every 100 km. Reported as compliance with each rule, never converted to minutes |
| Accessibility | A **separate** measure: road-network travel time via OSRM, with its own numeric threshold per vehicle type and a written rationale; thresholds, routing profiles and network assumptions are frozen as numbers on 25 Oct, before any method is compared. Routing profile stated per type; cells with no road connection or no route are reported as "unreachable", not dropped |
| Compatibility | A charger counts for a vehicle type only if it serves that type (R4-15) |
| Population within reach | Share of WorldPop population in cells within the accessibility threshold of a compatible charger, reported at the low, central and high capacity values |
| EV registrations | **Observed totals** per RTO by class, reported as they are. RTO data does not say where inside the RTO vehicles are, so no count of "EVs within reach" is claimed |
| EV reach proxy (optional) | RTO EVs × share of the RTO's population within reach, labelled **estimated proxy**, shown under all three spatial priors (M3), never presented as a count |
| Capacity adequacy | A **separate output** from accessibility: estimated demand vs estimated compatible capacity per zone. Being near a charger is not the same as the charger having room |
| Duplication | A new site counts as a duplicate if it is within a fixed distance (set before results) of an existing high-confidence charger of the same type |
| Real-plan overlap | Share of sites in a verified published Karnataka site-level plan within a fixed distance of a recommended site; reported as **agreement with an existing plan**, never as accuracy. **Method only / not evaluated** until such a plan is verified (previously: TGREDCO tender sites) |
| Cost | Public cost per site and per unit of population reached (R4-16) |

### R4-20 · Deliverable map (P0)
**Why:** the brief lists Track 1 deliverables (national GIS platform, estimation and recommendation module, dashboard, demo video, methodology, scalability roadmap), while the core is deliberately Karnataka-first (ADR-001). One page in the submission shows how each deliverable is covered now and what is promised for the finale.
**Round 1 itself** asks only for team information, a methodology document and an implementation roadmap (official brief). Prototype evidence is supporting material that strengthens feasibility, not a Round 1 requirement.

| Track 1 deliverable | Round 1 evidence | Finale commitment |
| --- | --- | --- |
| Web platform / unified view | Architecture and the Karnataka slice (R4-11) | Working Karnataka planning app |
| Interactive national GIS map | National data architecture and stated limits | Karnataka live; Telangana next; national as a state-by-state pipeline, explained |
| Methodology document | This submission | Completed methodology with results |
| Estimation and recommendation module | One reproducible site-selection example | Budget-constrained allocation and proposal export |
| Decision-support dashboard | Mock-up or screenshot from the slice | Dashboard passing the acceptance test (R4-18) |
| Demo for one geography | Karnataka chosen and justified (ADR-001) | Demo video and live demo for Karnataka |
| Scalability roadmap | Roadmap with owners and cutoffs (R4-09) | Updated roadmap with measured solve times |

This is a mapping template, not a claim that any deliverable is complete. Check it against the official brief before submission.

---

## Changed

### R4-07 · Freeze scope: core vs stretch (P0)
**Core (promised in Round 1, must work at the finale):**
1. Charger evidence layer: multi-source, deduplicated, lineage kept, uncertainty shown.
2. Demand by vehicle class at RTO level (no fake district precision).
3. CEA calibration at its real granularity, plus a gap analysis against effective capacity.
4. Budget-constrained site selection in efficiency and equity modes.
5. Proposal export with demand, nearby capacity, configuration, cost, coverage gain, confidence and reason per site.
6. Validation against baselines (and a real Karnataka plan only if one is verified), using R4-06 metrics.

**Status of each stage in the submission.** Every core stage carries exactly one status. The target is below; the final column is filled on 29 Oct from what actually runs, and anything not working by then is downgraded to "method only".

| Stage | Target status in Round 1 | Status on 29 Oct |
| --- | --- | --- |
| 1. Charger evidence layer | Demonstrated (Karnataka, R4-11) | |
| 2. Demand by class at RTO level | Demonstrated (Karnataka), only if an RTO-level VAHAN export is obtained; otherwise method only | |
| 3. CEA calibration and gap analysis | Consistency check demonstrated; national calibration method only unless R4-05 passes | |
| 4. Budget-constrained site selection | One example run demonstrated; equity mode method only | |
| 5. Proposal export | One site card demonstrated | |
| 6. Validation | Method only (metrics fixed by R4-19) | |

Labels: **Demonstrated** = runs on real data and is reproducible; **Method only** = specified, not built; **Finale commitment** = promised for December. A box in the architecture diagram is not a working feature.

**Plus two differentiators:**
- Source-independent confidence scoring (already designed, cheap).
- Delivery tracker (high judge value; falls back to a schema if stage dates aren't public).

**Moved to Stretch (named in the submission as "if time allows", not promised):**
- N-1 corridor resilience
- Typed configuration menu, including battery swapping
- Site-security factor
- Busy-month sizing
- Corridor flow model (IHMCL)
- Latent-fleet plan runs beyond the documented method
- UPNEDA replay

**Stays Roadmap:** UBC ingestion, silent-failure test, reliability ML, Bayesian adoption, public transparency page, operator scorecard.

### R4-08 · Short Round 1 submission (P0)
**Why:** the brief says the submission "should be concise". The Rev 3 report (~135 KB) becomes the internal reference, not the submission.
**Target:** 10–12 pages plus an appendix.

| Section | Length | Content |
| --- | --- | --- |
| Team information | ½ page | Team name, ID, institution, contacts |
| Problem | 1 page | No adequacy assessment, fragmented and unreliable charger data, the PM E-DRIVE allocation gap |
| Solution | 1 page | Proposal engine for the state nodal agency; scope boundary (planner, not operator) |
| Methodology | 3 pages | The six core stages in plain language; equations in the appendix |
| Data strategy | 1–2 pages | Source-access matrix (R4-01) with status labels |
| Validation | 1 page | Baselines and non-circular metrics (R4-06), plus stated limits |
| Roadmap | 2 pages | Core vs stretch, owners, dates, kill rules (R4-09) |
| Appendix | As needed | Equations with units, confidence-score rules, AI and tool disclosure (Rule 6) |

### R4-09 · Roadmap with owners, dependencies and cutoffs (P1)
**What:** each core stage gets an owner, start date, dependency and cutoff date. Example format:

| Stage | Owner | Depends on | Build window | Cutoff / fallback |
| --- | --- | --- | --- | --- |
| Charger evidence layer | | R4-02 | 8–18 Nov | If dedup is poor by 18 Nov: hand-QA Bengaluru Urban only |
| Demand by class | | R4-03 | 8–15 Nov | Stay at RTO level |
| CEA calibration | | R4-05 | 12–22 Nov | Karnataka-only check with wide bands |
| Site selection | | Stages 1–3 | 18 Nov–2 Dec | Efficiency mode only |
| Proposal export | | Stage 4 | 25 Nov–5 Dec | Static PDF export |
| Validation | | Stages 1–5 | 1–12 Dec | Baseline comparison only |

Build weeks: 8 Nov–14 Dec. Finale: 16–18 Dec.

### R4-12 · Units on every equation (P1)
**What:** every symbol in M1–M6 gets a unit (kWh/day, km/day, kWh/km, ₹, minutes, sessions/hour). Equations move to the submission appendix.

### R4-13 · Wording fixes (P1)
- "Confidence score" becomes **"heuristic evidence-confidence score (not a probability)"** everywhere in the submission.
- "Optimal" always becomes **"optimal for the stated objective and constraints"**, with the solver gap.
- "Validated" is used only for things actually tested against data; otherwise "to be validated by test X".
- CEA is always **"an aggregate check on totals"**, never "ground truth".

---

## Removed

- **Provisional "84/100" score** from the review: an invented estimate with no jury data. Keep the reasoning, drop the number from any notes or slides.
- **Live-API language** for UBC, Delhi OpenEV or any source not yet accessed: replaced by "Planned" (R4-04).

---

## Unchanged (already covered in Rev 3, no new work)

| Review issue | Where Rev 3 already handles it | Only action |
| --- | --- | --- |
| CEA could be over-interpreted | M3: CEA checks totals only; spreading demand within an RTO is an assumption tested under three spatial priors | Add R4-10 |
| Confidence scores look too scientific | M2 title says "not probabilities"; M7 tests B (hand-labelled sample) and E (ablation) | Wording fix R4-13 |
| Novelty needs measurable proof | M7 test C compares against NITI/WRI, proportional and current deployment | Make metrics non-circular, R4-06 |
| Kill criteria exist | Build priority and kill-criteria tables | Apply them via R4-07; R4-05 now has its own go/no-go |
| Candidate vs recommended sites (second review) | M5 deployability tiers and the site ladder (judge Q18) | Make the label visible everywhere, R4-17 |
| Data leakage in validation (second review) | M7 test A holds out whole states and the last quarter | Karnataka CEA chart labelled a consistency check, R4-11 |

---

## Checklist before submission (30 Oct)

- [ ] R4-14 claim audit: every "first", "only", "novel", "optimal", "validated", "live" re-checked or downgraded.
- [ ] Every number in the submission traces to a source in the access matrix.
- [ ] Metric definitions and thresholds (R4-19) written in before any results are shown.
- [ ] Calibration evidence and evaluation evidence kept separate; anything that reuses calibration data is called a consistency check.
- [ ] Every site carries a tier label; no stronger claim than its label (R4-17).
- [ ] Every scheme-eligibility or subsidy claim checked against the PM E-DRIVE guidelines (R4-16).
- [ ] Synthetic data clearly marked (Rule 5).
- [ ] AI tools, third-party software and datasets disclosed (Rule 6).
- [ ] Roadmap promises only core plus two differentiators.
- [ ] Owners named for data, modelling, validation, UI/export and submission.
- [ ] Spacing checks stay distance-based; accessibility is a separate travel-time measure (R4-19).
- [ ] No claim of "EVs within reach" as a count; RTO totals reported as observed (R4-19).
- [ ] Accessibility and capacity adequacy reported separately.
- [ ] Capacity always called "estimated compatible charging capacity", with assumptions stated (R4-15).
- [ ] Deliverable map included (R4-20).
- [ ] Team leader submits; one submission only.

---

## Go / no-go rule for 29 Oct

**GO** if all of these hold:
- At least one real, traceable data path from raw sources to a joined Karnataka result (R4-11).
- A site-selection example that can be reproduced and explained.
- A written fallback for national calibration if the evidence is weak (R4-05).
- Validation metrics that claim no more than the data supports (R4-19).
- Clear separation of working features, planned capabilities and synthetic data (R4-04).
- A concise submission mapped to the challenge deliverables (R4-08, R4-20).

**NO-GO on the current claims** if the join still fails, the only convincing outputs use ambiguously labelled synthetic data, or reach and capacity are shown as observed facts. That does not mean abandoning the entry: shrink every claim to the smallest working system that can be defended, and submit that.

---

## Day plan

| Date | Work |
| --- | --- |
| 24 Oct | Assign owners first; R4-01 to R4-04: access matrix, downloads, one join, labels |
| 25 Oct | R4-07 scope freeze; R4-19 definitions frozen (spacing vs accessibility, RTO reach limit) |
| 26 Oct | R4-05 calibration decision (run or fallback, in parallel); R4-11 reproducible slice complete |
| 27 Oct | R4-06 baselines on a fixed budget; R4-09 roadmap; R4-10 CEA comparison; R4-15 capacity assumptions; R4-16 cost and subsidy accounting |
| 28 Oct | R4-12, R4-13: units and wording; R4-17 labels; R4-18 acceptance test written up |
| 29 Oct | R4-08 final draft with R4-20 deliverable map; R4-14 claim audit; go/no-go check |
| 30 Oct | Review and submit |
