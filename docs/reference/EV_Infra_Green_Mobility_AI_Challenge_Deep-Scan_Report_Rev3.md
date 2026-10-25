# EV Infra & Green Mobility AI Challenge — Deep-Scan Intelligence Report

Oct 8, 2026 · @anusha · Revision 3: 22 Oct 2026

> **Note (25 Oct 2026):** the pilot geography has changed from Telangana to Karnataka; Telangana is now a future expansion geography. See [ADR-001](../decisions/ADR-001-geography.md). This report is unchanged; its Telangana findings remain as historical reference.

> **Revision 3 (22 Oct 2026)** adds the operating-scope boundary, source-independent confidence scoring, pre-merge source checks, status signals and silent-failure detection, a site-security factor, hybrids in demand, an expanded configuration menu, busy-month sizing, an N-1 corridor resilience check, adoption forecasting with policy scenarios, the data architecture and update pipeline, a delivery tracker with grid-delay flags and a feedback loop, and a privacy and governance section. Summary in "Revision 3" below; details in Formal methods M2, M3, M5, M6 and new M10–M13.

## Executive verdict

Build Track 1 as an evidence-backed PM E-DRIVE proposal engine that turns fragmented and uncertain Indian evidence into budget-feasible charger proposals a state nodal agency can submit, defend and audit. The scheme has a ₹2,000 crore charging envelope and no state or district targets, and MHI told Parliament it has not assessed charger adequacy against registered EVs.

| Question | Answer |
| --- | --- |
| Recommended track | Track 1, EV Infra Map India |
| Why | Live sponsor decision; public data supports a measured, validated answer; the PS's recognition section points at real ULB planning |
| Biggest competitive opportunity | The PM E-DRIVE proposal workflow itself, backed by CEA aggregate energy and a UBC/UEI-ready ingestion layer |
| Biggest technical risk | Demand built on VAHAN alone, which misses the unregistered low-speed fleet and mixes vehicle classes |
| Biggest data risk | Conflicting charger counts (29,277 vs 52,718) and no public operational-status feed |
| Biggest novelty opportunity | Not an algorithm: integrating fragmented Indian evidence into an auditable proposal package, with an evidence ledger, decision stability and a reason per site |
| What NOT to build | A driver-facing app, an LLM chatbot, GA/PSO siting, a GNN forecaster with no Indian training data, or anything that operates chargers (CCTV or CV surveillance, maintenance dispatch, theft response) |
| Scope boundary | We build the planner, not the operator: the engine consumes operating signals (status, uptime, delivery stages) and turns them into planning evidence |

### Track comparison

Scores 1–5 by judgement from Parts II–VI; higher always means better for us (more room, more data, less risk); overall = simple average.

| Dimension | Track 1 | T1 | Track 2 | T2 |
| --- | --- | --- | --- | --- |
| Existing solutions | Many maps and apps; no allocation tool | 3 | NEERI DB (2016), ITF tool, ICCT studies | 4 |
| Global maturity | High (NREL EVI-X) | 3 | High (ecoinvent, Brightway) | 3 |
| India maturity | Handbooks, city studies | 3 | Fragmented, old inventory | 4 |
| Open-source maturity | Strong GIS / OR stack | 5 | Strong LCA stack | 5 |
| Academic density | Very high (crowded) | 2 | Moderate | 3 |
| Data availability | Good | 4 | Literature-derived | 2 |
| India-specific data | VAHAN, CEA, IHMCL, MoP | 4 | Thin primary data | 2 |
| Convincing prototype difficulty | Moderate | 4 | Moderate–high | 3 |
| Novelty potential | High at the input/validation layer | 4 | High but hard to prove | 4 |
| AI opportunity | Entity resolution, reliability | 3 | Data gap-filling | 3 |
| GIS opportunity | Core | 5 | Minor (logistics) | 2 |
| Optimisation opportunity | Core | 5 | Material/design choices | 3 |
| Policy relevance | PM E-DRIVE, MoP, UBC | 5 | ESG, BWMR, CAFE | 4 |
| ICAT / MHI relevance | MHI owns the scheme and UBC | 5 | ICAT testing expertise | 4 |
| Competitor sophistication | Assume competent teams | 3 | Fewer teams, deeper | 3 |
| Judge wow-factor | Live re-solve on a map | 5 | Comparison charts | 3 |
| Defensibility | Validation against measured data | 4 | Depends on assumed inventories | 2 |
| Scalability | Per-state pipeline | 5 | Per-product datasets | 3 |
| Time-to-build | Fits 5 build weeks | 4 | Inventory collection slow | 2 |
| Risk of unverifiable claims | Manageable via CEA | 4 | High | 2 |
| Genuinely novel contribution | Calibrated planner | 4 | Open India automotive LCI | 4 |
| **Overall winning potential** |  | **4.0** |  | **3.1** |

Where judges will see ten near-identical entries: Track 1 charger maps with heatmaps. Where there is room: Track 1's allocation and validation layer, and Track 2's India inventory, which is harder to substantiate in the time available.

## Revision 3 — 22 October 2026

This revision answers the team's operating, data and governance questions. It changes no core method; it adds safeguards and four features (delivery tracker, source-independent confidence, N-1 corridor resilience, site-security factor) and draws a clear line around what the product does not do.

### Scope boundary: planner, not operator

| Layer | Examples | Who owns it | What our system does with it |
| --- | --- | --- | --- |
| Operating chargers | Repairs, software fixes, theft and vandalism response, site staff, CCTV | Charge point operator (CPO), under its tender or concession contract and uptime clause | Nothing operational; it reads the outcomes |
| Monitoring | Heartbeats, status, sessions, payment failures, user reports, delivery stages | CPOs report; UBC, Delhi OpenEV, CEA and state agencies aggregate | Turns signals into confidence scores (M2) and delivery flags (M12) |
| Planning | Where, how many, what type, how much subsidy, in what order | State nodal agency, using our engine | Core product |

Every question about operating chargers is answered by naming who handles it and how the planner uses the resulting signal. Networked chargers report heartbeats, status and sessions to the operator's central management system over OCPP (Open Charge Point Protocol); most software faults are fixed remotely, hardware faults by a technician, and the contract's uptime clause (TGREDCO's Hyderabad tender asks for 95%) is the enforcement. We consume the resulting status, not the repair process.

### What changed and where

| Change | Question it answers | Section | Round |
| --- | --- | --- | --- |
| Source-independence rule for agreement | Several stale copies of one list looked like strong agreement | M2 | Round 1 |
| Pre-merge source checks and source reliability ratings | No dataset gets a straight pass | M2 | Round 1 |
| Status signals, silent-failure test, "unknown" label | Installed ≠ working; false "available" signals; low-usage roads | M2 | Design in Round 1; live test only where data allows |
| Stratified spot-checks including high-score records | Confident false positives | M2, M7 | Round 1 |
| Site-security factor | Theft and vandalism risk, without building surveillance | M5 | Finale |
| Hybrids and plug-in hybrids in demand | Mixed fleets on the same roads | M3 | Round 1 |
| Busy-month sizing from IHMCL seasonality | Seasonal and festival peaks | M6 | Finale |
| Typed configuration menu (AC, light-EV DC, buffered DC, swapping) and mobile contingency | Right charger type per site | M6 | Finale (swapping only as a stated assumption) |
| N-1 corridor resilience check | Diversions and single points of failure | M6 | Finale (one or two corridors) |
| Adoption forecasting with backtest and policy switches | How to forecast; how policy changes enter | M10 | Method in Round 1; run in finale |
| Three-layer data architecture, versioning, incremental recompute | Super table vs graph; updates without full reruns | M11 | Design in Round 1 |
| Delivery tracker with grid-delay flags | Following up recommendations; grid delays; accountability | M12 | Finale |
| Feedback loop and post-deployment bug handling | Improving over time without scrapping progress | M12 | Design in Round 1; site level on roadmap |
| Privacy, legal basis, review-by-exception governance | Data laws, privacy, who validates outputs | M13 | Round 1 |

### Fact updates since 8 October

| Item | Update | Effect on the plan |
| --- | --- | --- |
| PM E-DRIVE | Extended to 31 Mar 2028; total outlay ₹11,900 crore, including ₹2,000 crore for public charging, ₹4,391 crore for 14,028 e-buses and ₹780 crore for testing agencies; claims close 31 Dec 2027; fund-limited ([PIB factsheet, Oct 2026](https://www.pib.gov.in/FactsheetDetails.aspx?Id=151062)) | The subsidised planning horizon is explicit: proposals must be sanctioned and claimed before end-2027 |
| e-2W purchase subsidy | Halved to ₹5,000 for the extension period ([Entrepreneur, Aug 2026](https://india.entrepreneur.com/business-news/government-extends-pm-e-drive-scheme-till-march-31-2028-e2w-incentive-cut)) | First real policy switch for the adoption scenarios (M10) |
| UBC | Pilot began in Maharashtra, Karnataka, Delhi-NCR, Haryana and Rajasthan ([MHI on X, Sep 2026](https://x.com/MHI_GoI/status/2095490089631809683)) | Telangana is not in the pilot: UBC stays a roadmap source for the demo state; design the adapter, do not depend on it |
| Grid connection deadlines | Electricity (Rights of Consumers) Amendment Rules 2024: new connections within 3 days (metro), 7 (municipal), 15 (rural), 30 (hilly rural); separate EV connection on request ([Business Standard, Feb 2024](https://www.business-standard.com/india-news/govt-tweaks-rules-for-speedy-electricity-connection-rooftop-installation-124022300594_1.html)) | Legal yardstick for standard connections in the delivery tracker (M12); connections that need network augmentation take longer and are flagged separately |
| FAME-II charger audit | CAG found OMC stations missing the deadline, chargers without power supply, removed chargers and untrained staff ([Down To Earth](https://www.downtoearth.org.in/energy/cag-flags-rs-468-crore-in-fame-incentives-to-ev-makers-violating-localisation-norms)) | "Commissioned on paper" is a known failure; the tracker checks energy after commissioning (M12) |
| VAHAN data sharing | MoRTH scrapped its 2019 Bulk Data Sharing Policy in June 2020 over privacy ([IFF](https://saveourprivacy.in/blog/bulk-data-sharing-policy-scrapped-is-an-incremental-victory-that-requires-follow-up-action-saveourprivacy)); the 2025 National Transport Repository data-sharing policy allows API, portal and bulk access with masking and compliance memoranda under the DPDP Act ([MoRTH policy](https://morth.nic.in/sites/default/files/circulars_document/Data-Sharing-policy-20082025-merged.pdf), [summary](https://ssrana.in/articles/digitization-of-transport-data-and-securing-personal-information/)) | Public aggregates only for now; the NTR policy is the legal production path (M13) |

### International practice behind the additions

| Practice | Where | Use here |
| --- | --- | --- |
| New chargers placed from usage data of existing stations instead of resident requests, from 1 Jan 2026 | Voorschoten, Netherlands ([municipality](https://en.voorschoten.nl/oplaadpalen-elektrische-autos)) | Supports the feedback loop (M12): placement learns from observed use |
| Highway expansion prioritised where daily utilisation exceeds 40% | China, 2026 service-area plan ([China EV Home](https://chinaevhome.com/2026/02/06/china-targets-10000-ev-chargers-at-highway-service-areas-in-2026/)) | An explicit expansion trigger once utilisation data exists (roadmap) |
| 97% uptime and real-time availability reporting for public chargers | California, cited by [IEEFA](https://ieefa.org/sites/default/files/2026-05/IEEFA_Feedback%20on%20the%20draft%20Delhi%20Electric%20Vehicle%20%28EV%29%20Policy%202026%20%281%29.pdf) | Benchmark for the uptime and reporting clauses each proposal recommends |

## Verification update — 8 October 2026

Primary sources change three things in this report: the widely quoted "18% offline" figure covers only oil-company stations, about 69% of CEA's charging energy is heavy-duty PCS (mainly buses; trucks possible), and MHI told Parliament in March 2026 that it has not assessed charger adequacy against registered EVs at all.

&#91;embedded content: Rajya Sabha unstarred Q.3910, answered 27 Mar 2026, annexure · OMC stations in 18 states with 500+ installed\]

The official reliability data exists only for OMC petrol-pump chargers; for every other network, operational status still has to be estimated.

&#91;embedded content: CEA EV PCS monthly report, March 2026 (FY26 totals, light-duty column) ÷ MoP state counts via PIB, Aug 2025 · 15 reporting states\]

With heavy-duty energy removed, the gap persists: Karnataka has the most stations but among the lowest energy per station. Treat it as a signal to investigate, not proof of over-supply; the model uses this column only as an aggregate constraint.

| Item | Earlier in this report | Now, from the primary source | Effect on the plan |
| --- | --- | --- | --- |
| 27,737 installed / 22,753 operational | Read as national; "18% offline" | OMC stations only ([Rajya Sabha Q.3910](https://www.heavyindustries.gov.in/sites/default/files/2026-03/rsauq3910.pdf), 27 Mar 2026) | Use as a reliability prior for OMC sites, not for all networks |
| Adequacy assessment | Not known | MHI: "no such assessment" of chargers vs registered EVs; NH and Tier-2/3 data "not centrally maintained"; no roadmap or targets; no PM E-DRIVE charger funds released as of 24 Mar 2026 | The strongest problem statement for Round 1: quote it |
| CEA energy | 1,460 MU FY26, state level | [1,558.69 MU FY26](https://cea.nic.in/wp-content/uploads/ev_charging_rep/2026/08/Mar_26_EV.pdf): 378.09 excluding heavy-duty, 1,081.87 heavy-duty PCS, 98.74 other than PCS; state AND DISCOM; \~5-month lag; 2026 format has no station counts | Use the excluding-heavy-duty column as an aggregate constraint on non-heavy-duty public PCS demand (local plus corridor) and the heavy-duty column for the fleet/depot module; Telangana splits into TGSPDCL (Hyderabad) and TGNPDCL |
| Energy per station | Earlier chat estimate \~500 kWh/day for Delhi | \~90 kWh/day excluding heavy-duty (Delhi) vs \~16 (Karnataka) | Ratio (\~5×) survives, but kWh per station is not utilisation: dates, definitions and charger capacity differ |
| Delhi's share | "\~40%" from one blog | 27.9% of FY26 PCS energy (CEA) | Use the CEA figure |
| "Half / most chargers broken" | Unsourced | [IEEFA, Sep 2026](https://ieefa.org/sites/default/files/2026-09/EV%20charging%20experience%20in%20India.pdf): a 2024 IEEFA sample in Delhi found \~84% of examined chargers not functional | A sampled audit, not national; cite as such |
| UBC | Discovery rail, access unknown | IEEFA: PM E-DRIVE support requires chargers connected to UBC, which is "yet to be operationalised"; open [UEI spec](https://www.github.com/beckn/Unified-Energy-Interface) and [Beckn Onix](https://github.com/keyabist/onixguide) let you run a local network now | Build the discovery client against a local Beckn network; UBC becomes the registry for every subsidised charger |
| PM E-DRIVE capacity | \~72,300 chargers | IEEFA estimates ₹2,000 crore buys \~18,811 points at 100% subsidy under the target mix | Confirmed: ₹688.84 crore approved for 6,562 chargers (\~₹10.5 lakh each) by 22 Jul 2026; treat 72,300 as a scheme envelope and model the ₹ budget |
| 52,718 stations | Definition unclear | IEEFA gives the number without defining station vs point | Still open; do not use as a station count |
| Telangana count | 1,063 operational (state) | OMC annexure alone lists 1,173 operational OMC stations in Telangana | Definitions differ; the truth layer must reconcile them |

## Red-team revision — 8 October 2026

The product changes from "a CEA-calibrated charger allocator" to **an evidence-backed PM E-DRIVE proposal engine**: a decision-support engine that converts fragmented and uncertain Indian EV, charger, traffic and energy evidence into budget-feasible, auditable PM E-DRIVE charging proposals for one user, the state nodal agency. It must work fully without UBC. Slide tagline: "Auditable PM E-DRIVE proposals from imperfect Indian data." The map becomes the viewing layer, not the product.

### Revised thesis

Track 1 is still the stronger bet, but not because India lacks charging-location research. 2026 Indian papers already combine GIS and multi-criteria siting, AI demand forecasting with siting and sizing ([Sci Rep, Jan 2026](https://www.nature.com/articles/s41598-026-37080-2)) and equity frameworks ([Kerala, May 2026](https://link.springer.com/article/10.1186/s42162-026-00666-1)). The opening is to move from suitability mapping to proposals that fit the scheme's actual workflow: locations, charger counts, segment, capacity, subsidy and justification. No single algorithm is the moat; the integration into a defensible government decision is.

### Claims that are now wrong or weak

| Earlier claim | Problem | Replacement |
| --- | --- | --- |
| "\~72,300 chargers to place" | It is the scheme's design envelope; ₹688.84 crore was approved for 6,562 chargers (5,871 in 9 states + 691 via 3 OMCs) as of 22 Jul 2026, nothing spent ([Business Today](https://www.businesstoday.in/latest/economy/story/rs689-crore-approved-for-ev-charging-network-under-pm-e-drive-but-no-funds-spent-yet-544488-2026-07-22)); at \~₹10.5 lakh per charger, ₹2,000 crore buys \~19,000 | Model the ₹ budget; separate envelope, approved, tendered, installed and operational |
| CEA as "ground truth" | Utility-reported, incomplete, state/DISCOM aggregates | "Aggregate calibration constraint"; checks totals, not where demand sits within a DISCOM |
| CEA "light-duty" and "e-bus" columns | CEA's categories are "excluding heavy duty", "heavy duty PCS" and "other than PCS" | Use CEA's own labels; heavy-duty is mainly buses but may include trucks |
| kWh per station = over-supply | Mismatched dates, definitions, capacity and station age | Capacity-normalised under-utilisation risk, labelled as a risk signal |
| "Exact MIP proves optimality" | Only optimal for the stated model and inputs | "Optimal for the stated objective and constraints" + solver gap |
| "Chosen in 92% of 500 futures" | Fake precision without stated distributions | Latin-hypercube sampling over documented ranges → decision-stability score |
| Shadow-fleet multipliers | One uncertain multiplier swings the optimiser | Three plans: registered-only, moderate, high latent fleet; report sites that survive all three |
| RTO → district Voronoi fallback | Invents administrative boundaries | Stay at RTO level if boundaries are unavailable |
| H3 cells ≈ MoP 1 km rule | A hexagon is not the regulatory 1 km × 1 km grid | H3 for computation; a separate layer for guideline alignment |
| Grid "feasibility" | Substation lists are a proxy | "Grid-connection screening" with a connection-risk score |
| OSM sites as available land | A bus depot on a map is not land offered | Deployability tiers: deployable, feasible candidate, planning candidate, excluded (Formal methods, M5) |
| Reliability classifier | Too few status labels | Rule-based confidence scores first (not probabilities); calibrated ML only once labels exist |
| Backtest overlap = validation | Actual deployment reflects land, politics and tenders, not optimality | Compare coverage, travel time, equity and cost against actual deployment and baselines |
| Competitor percentages | Informal guesses | Removed from any submission; assume capable competitors |
| UBC as live truth | Hub "yet to be operationalised"; even when live, it carries what operators report | "UBC/UEI-ready" ingestion, tested on a local Beckn network |

### What the proposal engine outputs per site

| Field | Source |
| --- | --- |
| Site ID, GPS, land category | Candidate ladder (OSM, state lists, nodal agency input) |
| Vehicle segment, charger type, count, kW | Segment demand + queueing approximation |
| Estimated demand and coverage gain | Demand model, travel-time coverage |
| Existing effective usable capacity nearby | Charger evidence fusion |
| Grid-connection risk and likely upstream cost | Substation screening |
| Subsidy requested | PM E-DRIVE tier rules |
| Marginal coverage per crore | Optimiser |
| Decision stability | Scenario runs |
| Policy checks | MoP spacing rules, PM E-DRIVE eligibility |
| Evidence ledger and justification | Provenance of every input; why here / why not here |

### Revised optimisation, in plain words

The optimiser chooses sites to get the most charging service per rupee, under a budget, site-eligibility rules and an optional ceiling on unserved population per district, and it builds only where benefit per rupee clears a minimum threshold. It runs in three modes: efficiency (most demand served), equity (fewest underserved people) and balanced. It reports what each extra crore buys, so a planner sees the trade-off instead of one answer; the frontier is traced with the ε-constraint method (Formal methods, M6), not arbitrary weights. Local, corridor and fleet/depot demand are modelled separately, and battery swapping is stated as an explicit assumption for 2W/3W. Optimisation is hierarchical: national envelope → state → city or corridor → site, with national corridor links so state borders do not leave gaps.

### Build priority

| Tier | What | Why |
| --- | --- | --- |
| Round 1 document (by 30 Oct) | Methodology and roadmap as the PS asks; every claim limited to what the build blocks below will deliver; Revision 3 sections (scope boundary, M2 independence and gates, M10–M13) written into the methodology | Round 1 is judged as a document, and its roadmap is a contract for Round 2 |
| Smallest working slice (start now) | Telangana charger evidence fusion; RTO × segment demand; CEA aggregate check by DISCOM; one budgeted site/configuration run exported as a proposal package with evidence ledger; NITI/WRI baseline on the same budget; lineage groups and pre-merge gates inside the fusion step | Data plumbing is the expensive, slow part, so it starts first |
| Cheap additions to the slice | Equity mode, alternative spatial priors, peak-hour sizing, confidence ablation | Same model with different weights, an extra objective or one constraint; added if time allows, otherwise first in the finale block |
| Finale (16–18 Dec) | Budget-portfolio screen; cost scenarios with joint stability; latent-fleet plans; revealed-preference ranking; data-corruption tests; TGREDCO and UPNEDA replays; scalability benchmark; why-not-here cards; grid-connection risk; corridor model; demo where the answer changes as evidence improves; N-1 resilience on one or two corridors; delivery tracker on TGREDCO data; site-security factor; busy-month sizing; typed configuration menu | Robustness and usability are 45% of Round 2 |
| Roadmap only | Hierarchical national run; Bayesian adoption; queue simulation; live UBC ingestion; reliability ML; "did it work?" prompt at the UBC payment step; host-staff check-ins as a tender clause; site-level feedback loop; public transparency page; operator scorecard | Too large for five build weeks; promising them risks the roadmap contract |

**Kill criteria.** Each ambitious module has a stated condition for dropping or deferring it, so the roadmap never promises what the data cannot support.

| Module | What gets built | Kill or defer if |
| --- | --- | --- |
| UEI/UBC adapter | Client against a local Beckn network | No usable access by 30 Nov: keep as design only |
| Delhi OpenEV status feed | API ingestion | No key granted by 15 Nov |
| Reliability ML | Classifier on charger status labels | Fewer than \~300 independently checked labels |
| Corridor model | FASTag-anchored flow-refuelling | Directional plaza counts unavailable for demo corridors |
| Grid screening | Substation-based connection risk | No capacity data for Telangana: report "not assessed" |
| Bayesian adoption | Adoption intervals by district | Intervals too wide to change any decision |
| Silent-failure test | Zero-session test on live status or sessions | No session or status feed (Delhi OpenEV, UBC) by 30 Nov: describe the method only |
| N-1 resilience | Check on one or two corridors | Rerouting around a blocked segment not working by 1 Dec: run on one corridor or describe only |
| Delivery tracker | Stage table with dated flags for Telangana | Stage dates not public: show the schema with whichever stages are dated |
| Adoption curve | S-curve forecast (M10) | Does not beat both baselines in the backtest: use the better baseline with bands |
| Swapping configuration | Swap option in the configuration menu | No defensible range for swap share: drop from the menu, keep in roadmap |

New real plans to replay beyond Telangana: [UPNEDA's 238 PM E-DRIVE stations across 10 UP cities in 20 clusters](https://powerpeakdigest.com/upneda-invites-bids-238-ev-charging-stations/). Telangana's 169-station TGNPDCL tender covers 16 locations; the 116-location Phase-I PM E-DRIVE sanction is a separate decision. How the sanction and the tender relate, and whether they overlap, is unverified, so each is replayed separately. Never call the 116 locations "116 chargers" or "116 sites".

### Claim-audit rule

Before submission, every use of first, only, novel, nobody, live, operational, ground truth, optimal, validated or proven gets a fresh counter-example search; if one exists, the claim is downgraded. Unverified in this pass: the September 2026 *Sustainable Energy, Grids and Networks* paper cited by the critique (not found in two searches) and Indian GitHub repos doing MCLP for Hyderabad/Bengaluru (not checked).

## Formal methods

These are the equations and rules the Round 1 methodology document should state. Every symbol maps to a named public source, and anything weakly identified is labelled as such. Initial weights and ranges below are starting values to be tuned and published, not findings.

### M1 Notation

| Symbol | Meaning | Source |
| --- | --- | --- |
| z | Demand zone (H3 cell), nested in RTO r(z) and DISCOM d(z) | H3 over state boundary |
| c | Segment: e-2W, e-3W, e-4W (local); corridor; fleet/depot | — |
| j, m | Candidate site; charger configuration (mix, count, kW) | OSM, state lists, agency input |
| τ\_j | Deployability tier of site j (M5) | Evidence ladder |
| S\_{r,c} | Registered EV stock by RTO and segment | VAHAN / PM E-DRIVE dashboard |
| L\_{r,c}, λ | Latent (unregistered) fleet estimate; plan multiplier | Customs and industry ranges |
| VKT\_c, e\_c | Daily km; kWh per km | Literature priors |
| π\_c | Public-charging propensity | Prior, then calibration |
| a\_d | DISCOM scaling factor | Calibration, shrunk toward 1 |
| E\_{d,t} | CEA energy "excluding heavy duty", DISCOM d, month t | CEA monthly report |
| w\_z | Zone weight (population, POIs, night lights) | WorldPop, OSM, VIIRS |
| t\_{zj}, T\_c | Network travel time; coverage threshold by segment | OSRM; stated per segment |
| u\_{jm}, k\_{jm}, σ\_j | Upstream cost, equipment cost, subsidy rates | Cost table (M4) |
| B | Public budget in ₹ | Planner input |

### M2 Charger confidence scores (not probabilities)

Each deduplicated charger i gets five scores in \[0, 1\]: C\_real, C\_public, C\_current, C\_functional, C\_location. Each comes from a bounded evidence-scoring function: additive positive evidence, multiplied by a recency decay δ with a 180-day half-life, minus a penalty ν for each explicit negative report, clipped to \[0, 1\]. One missing factor lowers a score instead of zeroing it.

```latex
C_x(i) = \operatorname{clip}_{[0,1]}\Big( \delta(\text{age}_i) \sum_k \omega_{x,k}\, f_k(i) \;-\; \nu\, n^{\text{neg}}_i \Big), \qquad \delta(\text{age}) = 0.5^{\,\text{age}/180}
```

| Evidence factor f\_k | Initial rule |
| --- | --- |
| Source quality | Government registry 0.35; operator or UEI/UBC listing 0.30; OSM 0.15; OCM 0.10 |
| Cross-source agreement | +0.20 per additional independent source, up to +0.40 |
| Recency | Multiply by a decay with a 180-day half-life since last confirmation |
| Coordinate consistency | +0.10 if sources agree within 50 m |
| Negative evidence | −0.50 for an explicit closed or non-working report |

The hand-labelled sample (M7, test B) tunes these weights, and an ablation (M7, test E) checks whether the scores change decisions at all. Calibrated probabilities are a later phase, only once enough status labels exist. Existing capacity becomes an effective usable capacity proxy by discounting rated capacity with two scores. Multiplying two scores is a deliberate heuristic discount, not a probability calculation:

```latex
Q_z = \sum_{i \in N(z)} C_{\text{func}}(i)\, C_{\text{pub}}(i)\, P_i\, H_i
```

Here P\_i is rated kW and H\_i the assumed usable hours per day.

**Source independence (Revision 3).** Agreement adds confidence only when sources are independent. Each source is assigned a lineage group by where its records originate: an aggregator that republishes EV Yatra listings joins EV Yatra's group; an operator's own locator forms its own group. The agreement bonus counts lineage groups, not sources, and a source of unknown lineage counts as dependent until shown otherwise (for example by holding records no other source has). Five stale copies of one list earn the same bonus as one copy, and recency decay still applies to all of them.

```latex
\text{agree}(i) = \min\big(0.40,\; 0.20\,(G_i - 1)\big), \qquad G_i = \text{distinct lineage groups confirming } i
```

**Pre-merge source checks.** Every source passes a gate before the merge. Failures are logged in the evidence ledger, never silently dropped.

| Check | Rule | On failure |
| --- | --- | --- |
| Geography | Coordinates inside India and inside the stated state or district polygon | Record quarantined |
| Internal duplicates | Same operator and name within 50 m inside one source | Collapsed before the merge |
| Plausibility | Power, connector and segment consistent (for example no 500 kW e-2W charger) | Field nulled, record kept and flagged |
| Freshness | Source date or last-update field present | Treated as the oldest plausible date |
| Totals | Source's state total vs the MoP state count | Reported as a coverage ratio |
| Source reliability | Precision of the source on the hand-labelled sample (M7, test B) | Replaces the initial source-quality weight once measured |

**Status signals and silent failures.** C\_functional uses whichever operating signals exist, strongest first:

| Signal | Available for Telangana now? | Effect |
| --- | --- | --- |
| Explicit closed or faulted report (operator, agency, audit) | Partly (official lists, tenders) | −0.50 per report, as above |
| Operator status feed (OCPP-derived, via UBC/UEI or Delhi OpenEV) | No (Telangana is not in the UBC pilot) | Strong positive or negative evidence when present |
| Sessions vs expected sessions | No site-level sessions | Silent-failure test, below |
| Payment failures at the charger (UBC) | No | Negative evidence (roadmap) |
| Host-staff check-in: weekly scan-and-test by pump, toll or site staff | No | Positive evidence valid for 7 days (roadmap; proposed as a tender clause) |
| Network prior (OMC 82% operational; IEEFA Delhi sample) | Yes | Starting value only |

The silent-failure test is used only where session data exists. If a site's expected sessions over a window are λ\_w and it records none, the chance of that under normal operation is e^(−λ\_w); the site is flagged "suspected silent failure" when that chance is below 0.05, which needs λ\_w of about 3 or more. A busy site going quiet is evidence; a quiet site staying quiet is not, so low-usage sites are never flagged by silence alone. The 0.05 threshold is an initial value (M8).

**Display labels.** C\_functional ≥ 0.7 shows "likely working", 0.4–0.7 "uncertain", below 0.4 "unknown or likely down". On low-usage roads with no recent evidence, decay moves a charger towards "unknown" instead of leaving it green; the planner sees honest uncertainty, and the effective-capacity proxy already discounts that capacity.

**Spot-checks.** The hand-labelled sample (M7, test B) is stratified by score band and deliberately includes the highest band, because confident false positives (many sources, all stale) are the costliest error.

### M3 Demand and CEA calibration

Demand has two layers. The physical layer is the energy vehicles use; the public layer is the share of it charged at public stations. CEA constrains only the public layer's totals, never the physical layer. L is the latent fleet included under the plan in use (table below), and λ switches it on (1) or off (0):

```latex
\begin{aligned}
D^{\text{phys}}_{r,c} &= \left(S_{r,c} + \lambda\, L_{r,c}\right)\, \mathrm{VKT}_c\, e_c \\
D_{r,c} &= D^{\text{phys}}_{r,c}\, \pi_c
\end{aligned}
```

**Latent-fleet plans.** The latent fleet has two parts, each sized from an external estimate, and the plans switch them on in turn.

| Plan | Latent fleet included | Evidence for its size |
| --- | --- | --- |
| Registered only | None | VAHAN |
| Moderate | Unregistered e-rickshaws | \~4.75 lakh nationally (EVMS estimate, via [JMK Research](https://jmkresearch.com/mandatory-registration-of-all-electric-rickshaws-across-states-in-india/)) |
| High | E-rickshaws + low-speed e-2W | Adds \~22.35 lakh low-speed e-2W kits imported Nov 2023–Oct 2025, against \~25.05 lakh high-speed e-2W registrations in the same period ([EVreporter, customs data](https://evreporter.com/the-e-2w-sales-india-doesnt-track-why-should-it-bother-us/)) |

National totals are spread to RTOs by a stated assumption: e-rickshaws in proportion to registered e-rickshaw stock; low-speed e-2W weighted toward North and East India, as the customs analysis indicates. Low-speed e-2W mostly use lead-acid batteries and charge at home, so their public-charging propensity starts near zero. The latent fleet is therefore expected to matter mainly through e-rickshaws, and the plans test whether it changes any site at all. A site is robust to the latent fleet only if all three plans select it:

```latex
\text{Robust}_{\text{fleet}} = \bigcap_{p\,\in\,\{\text{reg},\ \text{mod},\ \text{high}\}} \text{Selected}(p)
```

Modelled non-heavy-duty public PCS energy for DISCOM d in month t includes both local and corridor public charging, because CEA's excluding-heavy-duty series also contains highway charging; leaving corridor energy out would inflate the local public-charging share. Fleet/depot demand is excluded (n\_t = days in month):

```latex
\hat{E}_{d,t} = a_d \Big( \sum_{r \in d} \sum_{c \in C_{\text{local}}} D_{r,c,t} + D^{\text{corr}}_{d,t} \Big)\, n_t
```

Calibration fits π\_c and a\_d in log space, pulled toward literature priors π\_c⁰ and toward a\_d = 1:

```latex
\min_{\pi,\,a}\ \sum_{d,t}\left(\log E_{d,t}-\log \hat{E}_{d,t}\right)^2+\sum_{c}\left(\frac{\log \pi_c-\log \pi_c^{0}}{s_c}\right)^2+\sum_{d}\left(\frac{\log a_d}{s_a}\right)^2
```

Each π\_c is also held inside hard bounds (π\_c^min ≤ π\_c ≤ π\_c^max) taken from published ranges, so calibration is regularised and bounded, not free fitting. The bounds limit how far a wrong VKT or efficiency assumption can push π\_c, though they do not make π\_c identifiable. In plain words: the model matches reported totals where the data insists and otherwise stays near published values. What is identified: total demand per DISCOM. What is weakly identified: segment-level π\_c, which only separates through differences in segment mix across roughly 55 reporting utilities over 12 months. Report bootstrap intervals for π\_c, and say so. Propensity is fitted per segment, not per segment and region: region-specific propensities would add parameters CEA cannot identify, and a\_d already absorbs regional differences. DISCOMs with no CEA data get no constraint and wider bands. CEA's \~5-month lag means calibration describes the last reported year, not today. The heavy-duty column constrains the fleet/depot module separately.

Spreading RTO demand to zones is an assumption CEA cannot check, and site choice depends on it. So it runs under three spatial priors: population-led (residential population), mobility-led (road class, centrality, traffic) and activity-led (POIs, night lights). A site counts as robust only if selected under all three:

```latex
D_{z,c} = D_{r(z),c}\, \frac{w_{z,c}}{\sum_{z' \in r(z)} w_{z',c}}
```

Residual demand R\_{zc} is D\_{z,c} minus what existing capacity serves, after the effective usable capacity proxy is assigned to zones by the same capacity-respecting allocation, so no existing charger is counted twice. Corridor demand comes from directional IHMCL counts × EV share × charge-stop probability given range, solved as a flow-refuelling problem on NH segments. Fleet/depot demand (e-buses, logistics) is a separate module tied to the heavy-duty column and depot allocations.

**Hybrids and plug-in hybrids (Revision 3).** Conventional (strong and mild) hybrids never plug in and are excluded from charging demand. Plug-in hybrids form their own small segment with a lower public-charging propensity than battery EVs, because they can fall back on petrol. VAHAN's exact fuel labels for hybrids are confirmed before use (open item). Petrol and diesel traffic enters only on corridors, as total flow multiplied by EV share.

### M4 Cost model

Public cost of configuration m at site j applies PM E-DRIVE subsidy rates to upstream and equipment costs:

```latex
g_{jm} = \sigma^{\text{up}}_j\, u_{jm} + \sigma^{\text{eq}}_j\, k_{jm}
```

| Component | Basis | Source | Status |
| --- | --- | --- | --- |
| Subsidy rates σ | 100% at government premises with free access; 80% upstream + 70% equipment at transit hubs, OMC outlets, toll plazas; 80% upstream at malls and highway roadside | PM E-DRIVE guidelines | Known |
| Equipment cost k | Range per charger type (2W/3W AC, 4W DC 30/60 kW, 120 kW+) | State tenders, operator disclosures | To collect |
| Upstream cost u | Range by grid-risk tier; can be up to \~50% of station cost | DISCOM estimates, tenders, IEEFA | To collect |
| Anchor | ₹688.84 crore ÷ 6,562 approved chargers ≈ ₹10.5 lakh public support each | MHI reply, Jul 2026 | Known |

All costs enter as ranges with three named scenarios (low, central, high). A site is reported as stable only if it survives both demand and cost uncertainty.

### M5 Deployability tiers

| Tier | Rule | In the optimiser |
| --- | --- | --- |
| Deployable | Eligible PM E-DRIVE category, land confirmed by the agency, grid risk low or medium | Allowed |
| Feasible candidate | Eligible category; land or grid not yet confirmed | Allowed, tagged |
| Planning candidate | Attractive location, weak eligibility evidence | Allowed in planning view only, flagged |
| Excluded | Ineligible category or fails a policy condition | Not allowed |

A "deployable only" switch restricts candidates to the first tier. Weak-evidence sites are tagged rather than filtered, so the planner still sees attractive areas that need confirmation.

**Site-security factor (Revision 3).** Theft and vandalism are handled by operators and hosts, not by our system, but they change how much working capacity a proposed site is likely to deliver. Each candidate gets a security class that multiplies the operator or network uptime prior in the effective-capacity term. Multipliers are initial assumptions, published and sensitivity-tested (M8), not findings.

| Class | Typical sites | Initial uptime multiplier |
| --- | --- | --- |
| High | Staffed 24×7 with CCTV: OMC outlets, toll plazas, police or government premises, transit hubs | 1.00 |
| Medium | Staffed part of the day: malls, hotels, dhabas, markets | 0.95 |
| Low | Unstaffed roadside or open lots | 0.85 |

The class appears on every proposal card and is never a hard filter. Hosted sites also tend to have an existing grid connection, which the grid-connection risk score already rewards.

### M6 Optimisation

Decision variables: x\_{jm} ∈ {0, 1} builds configuration m at site j; s\_{zjc} ≥ 0 is daily energy from zone z, segment c served at site j; u\_z ∈ {0, 1} marks an underserved zone. Each site has a small menu of 3–4 configurations m (for example 2 × 60 kW, 4 × 60 kW, 2 × 120 kW), chosen jointly with the site in one MIP. Choosing sites first and sizing them later is avoided, because it can pick sites that cannot be sized within budget. κ\_{jm} is usable daily energy capacity of a configuration, limited by the peak-hour sizing rule below.

Efficiency mode maximises demand served within the budget:

```latex
\begin{aligned}
\max\ & \sum_{z,j,c} s_{zjc} \\
\text{s.t. } & \textstyle\sum_j s_{zjc} \le R_{zc} && \forall z,c \\
& s_{zjc} = 0 \ \text{ if } t_{zj} > T_c \\
& \textstyle\sum_{z,c} s_{zjc} \le \sum_m \kappa_{jm} x_{jm} && \forall j \\
& \textstyle\sum_m x_{jm} \le 1 && \forall j \\
& \textstyle\sum_{j,m} g_{jm} x_{jm} \le B \\
& x_{jm} = 0 \ \text{ if } \tau_j = \text{excluded} \\
& \textstyle\sum_{z \in h} w_z u_z \le U^{\max}_h && \forall \text{ districts } h \ (\text{optional}) \\
& \textstyle\sum_{z,c} s_{zjc} \ge \beta \sum_m g_{jm} x_{jm} && \forall j
\end{aligned}
```

The second-last line is an optional access floor: unserved population in district h stays below a planner-set level. It replaces any rule forcing a charger into every district, which would spend money where there is no gap. The last line is a minimum-benefit hurdle: a site is built only if it serves at least β kWh/day per rupee of public cost. Without it the optimiser spends the whole budget whenever any site adds even tiny value; with it, "no investment recommended here" becomes a real output. Equity mode minimises population in underserved zones. A zone's service level a\_z is the share of its demand actually served, by existing capacity plus new sites, using the served-energy variables that respect each charger's capacity; a charger shared by ten zones is never counted ten times. A zone is underserved (u\_z = 1) if a\_z falls below θ (initial 0.8). One charger within reach no longer makes a large zone "served":

```latex
\begin{aligned}
\min\ & \sum_z w_z u_z \\
\text{s.t. } & a_z = \frac{\sum_c \big(D_{z,c} - R_{zc}\big) + \sum_{j,c} s_{zjc}}{\sum_c D_{z,c}} && \forall z \\
& a_z \ge \theta\,(1 - u_z),\quad u_z \in \{0,1\} && \forall z
\end{aligned}
```

The trade-off is traced with the ε-constraint method: maximise served demand subject to all constraints plus Σ w\_z u\_z ≤ ε, for a grid of ε from the equity optimum to the efficiency optimum. Balanced mode is the planner's chosen point on that frontier, not a weighted sum with arbitrary weights. Re-solving for budgets of ₹10, 25, 50 and 100 crore gives budget portfolios, the main planner screen: for each, the sites, chargers, demand served, population reached, unserved population, grid risk, expected utilisation and stability. Every run reports its MIP gap (target ≤ 1%). Highways use a separate flow-refuelling model with guideline-alignment checks on spacing. Hierarchy: cross-border corridor segments are solved first and fixed, then state problems run within their budget envelopes.

**Peak-hour sizing.** Daily sessions at site j are served energy ÷ energy per session; peak-hour arrivals λ\_j are daily sessions × the peak-hour share. With service rate μ per plug and c\_m plugs in configuration m, the configuration is allowed only if utilisation stays below a ceiling (initial ρ\_max = 0.7). Using daily arrivals instead would undersize sites at the busy hour. This is a sizing constraint, not a queue prediction.

**Busy-month sizing (Revision 3).** For corridor sites the peak-hour share is applied to the busiest month, not the average: daily demand is scaled by the ratio of the peak month's IHMCL count to the annual monthly average at the governing plaza, which captures festival and pre-monsoon peaks. Urban sites use a stated seasonal factor (initial 1.1, an assumption in M8) until better evidence exists.

**Configuration menu (Revision 3).** The 3–4 configurations per site are drawn from a typed menu, so the optimiser chooses charger type as well as count and kW:

| Type | Serves | Offered at |
| --- | --- | --- |
| AC 3–7 kW, including lamp-post or bollard units | e-2W, e-3W, overnight e-4W | Apartment-dense zones, long-dwell sites |
| Light-EV DC | e-2W, e-3W | Markets, transit hubs, 3W stands |
| DC 30–60 kW | e-4W | Urban hubs, OMC outlets |
| DC 120 kW+ | e-4W corridor, light commercial | Corridor sites under the 100 km guideline |
| Battery-buffered DC | e-4W | Sites with high grid-connection risk: higher equipment cost, lower upstream cost |
| Battery swapping | e-2W, e-3W fleets | Only under an explicit swapping-share assumption; no Indian open data on swap demand |
| Depot ≥ 240 kW | e-buses | Fleet/depot module only |

Van-mounted mobile chargers are not a site configuration; they are the listed contingency for corridor segments that fail the resilience check below, and for festival peaks.

```latex
\rho_{jm} = \frac{\lambda_j}{c_m\, \mu} \le \rho_{\max}
```

**Outcomes reported for every plan.** Two are optimised: demand served (kWh/day) and unserved population. The rest are reported, so the frontier stays two-dimensional and readable: accessibility (share of target population in zones whose service level a\_z is at least θ), expected utilisation of new capacity, public cost, grid-connection risk and decision stability.

**Under-utilisation risk.** For an existing or proposed site, UR\_j = 1 − expected demand ÷ usable capacity, where usable capacity adjusts for rated kW, connectors, uptime, operating hours and segment. It is reported as a risk, never as measured utilisation, because no site-level usage data exists.

**Decision stability.** Draw about 200 Latin-hypercube samples over documented ranges for π\_c, VKT\_c, e\_c, λ, cost multiplier, adoption growth and charger uptime; re-solve each. A site's stability is the share of samples in which it is selected: ≥ 0.8 stable, < 0.5 fragile. Sites chosen under all three latent-fleet plans, all three spatial priors and all three cost scenarios are flagged as robust. Stability measures robustness to the stated ranges, not the probability of being right.

**N-1 corridor resilience (Revision 3).** Corridor plans are checked the way power grids are checked for single failures. For each selected corridor site, and each road segment between consecutive plazas, remove it and test whether a vehicle with usable range R\_c (rated range less a 20% reserve) can still travel the corridor end to end, on the alternate route OSRM returns when the segment is blocked. The resilience score is the share of single removals that leave the corridor passable. Single points of failure are listed with the cheapest fix: an extra site, a larger configuration at a neighbouring site, or a mobile-charger contingency. On one or two demo corridors the check can be imposed as a constraint (passable under any single failure); nationally it stays a check, because the constraint multiplies model size.

```latex
\text{Res}(k) = \frac{1}{|F_k|} \sum_{f \in F_k} \mathbb{1}\big[\text{corridor } k \text{ passable with range } R_c \text{ after removing } f\big]
```

**Why here / why not here.** For a selected site, remove it and re-solve: the loss in objective is its value, alongside nearest reliable charger time, tier, cost and stability. For a rejected site, force it in and re-solve: report the change in objective, which sites it displaces and the binding reason (tier, cost, or overlap with existing confidence-weighted supply). All numbers come from model output; an LLM may only reword them.

### M7 Validation protocol

The central evaluation question: does evidence reconciliation, CEA calibration and uncertainty-aware optimisation make better decisions on Telangana than simpler Indian planning baselines, despite imperfect data?

| Test | What it checks | Method | Metric |
| --- | --- | --- | --- |
| A. Demand | Do demand totals predict unseen energy? | Hold out 3–4 whole states or DISCOM groups (spatial) and the last quarter (temporal) of CEA excluding-heavy-duty energy | Error and interval coverage vs a naive stock-proportional baseline |
| B. Supply | Is charger evidence fusion accurate? | Hand-label 150–200 Telangana records, stratified by confidence band and including the highest band: duplicate and location (maps, imagery), public (site type), current (operator listing); operational only where app status was checked | Precision and recall per field, with method stated |
| C. Decision (headline) | Does the system beat Indian planning baselines? | Same budget for the NITI/WRI grid-cell method (headline baseline), proportional-to-EV, the current deployment pattern and our model | Demand served, population within T, unserved population, cost, duplication of existing capacity; not CEA error, since the NITI method produces no energy estimate |
| D. Policy replay and revealed preference | How does it compare with real plans and real choices? | Replay separately TGREDCO's 116-location Phase-I sanction, its 369-station tender (200 Hyderabad, 169 across five districts) and UPNEDA's 238-station tender; rank actual 2025–26 sites in a candidate ranking trained only on pre-2025 data, within the same eligible candidate pool | Share of actual sites in our top 5 / 10 / 20%, vs NITI and proportional baselines; differences explained, never scored as accuracy |
| E. Confidence ablation | Does evidence fusion change decisions? | Re-run with raw capacity, the effective usable capacity proxy, a conservative variant (only chargers above a confidence threshold), and scores without recency or without source quality; reported as a headline result | Sites added or dropped; capacity previously miscounted |
| F. Data corruption | How fragile is the plan to bad data? | Remove 20% of chargers, duplicate 10%, shift VAHAN ±20%, CEA −15%, costs +30%, uptime −20%; latent-fleet plan switched | Change in objective; number of sites that change |
| G. Scalability | How large a problem is tractable? | Solve on increasing candidate and cell counts | Solve time and MIP gap (table below) |

| Candidates | Demand cells | Solve time | MIP gap |
| --- | --- | --- | --- |
| 500 | 2,000 | To measure | To measure |
| 1,000 | 5,000 | To measure | To measure |
| 5,000 | 20,000 | To measure | To measure |

A sensitivity ranking of all sampled parameters accompanies the tests.

### M8 Assumed or weakly identified

| Item | Status |
| --- | --- |
| Segment public-charging propensity π\_c | Weakly identified; priors dominate |
| Latent fleet λ | Three plans with externally sourced sizes; spreading to RTOs is an assumption |
| Equipment and upstream costs | Ranges until tender data is collected |
| Charger operational status | Confidence score, not probability |
| Spread of demand within an RTO | Assumption; not validated by CEA; tested under three spatial priors |
| Corridor charge-stop probability | Assumption; sensitivity-tested |
| Queueing capacity κ | Approximation with peak factor |
| Site-security uptime multipliers (M5) | Assumption; sensitivity-tested |
| Urban seasonal factor and silent-failure threshold | Assumptions; sensitivity-tested |
| Battery-swapping share | Assumption; dropped if no defensible range |
| Lineage groups of sources | Judgement from source documentation; listed in the ledger |

### M9 Evidence ledger schema

Every number the system shows is backed by ledger records, so any figure in a proposal can be traced back to its sources: site → demand estimate → RTO stock → VAHAN extract → source and date.

| Field | Meaning |
| --- | --- |
| entity\_id | Site, charger, zone, RTO or DISCOM the claim is about |
| claim | What is asserted (value and unit) |
| source, source\_type | Publisher and tier (official, utility-reported, operator, community) |
| source\_date, retrieval\_date | When it was published; when we fetched it |
| spatial\_resolution, temporal\_resolution | E.g. RTO × month, DISCOM × month, point |
| transformation | Steps applied (dedup, spread, calibration) with code version |
| assumption | Any assumption the claim depends on, linked to M8 |
| confidence | Score from M2 where applicable |
| licence | Reuse terms of the source |
| provenance\_hash | Hash of the inputs, so a changed source is detectable |

### M10 Adoption forecasting and policy scenarios (Revision 3)

Monte Carlo sampling is not a forecast; it describes uncertainty around one. The forecast is an S-shaped adoption curve fitted to VAHAN monthly registrations per state and segment, and it must beat simple baselines before it is used.

| Step | Method | Check |
| --- | --- | --- |
| Fit | Logistic or Bass diffusion curve per state × segment on the monthly EV share of registrations; enforcement-driven spikes flagged and smoothed first | Fit diagnostics per curve |
| Backtest | Fit on data to Dec 2024, predict 2025 | Error vs two baselines (last 12 months repeated; linear trend); if the curve does not beat both, the better baseline is used, with bands |
| External forecasts | Official targets and published forecasts used as scenario bounds; how earlier forecasts compared with outcomes is recorded in the ledger | Never used as truth |
| Policy switches | Dated events change growth assumptions within a scenario: e-2W subsidy halved to ₹5,000 (Aug 2026); PM E-DRIVE claims close 31 Dec 2027 and the scheme ends 31 Mar 2028 | Each switch is a named, versioned scenario |
| Uncertainty | Growth rate and saturation level enter the Latin-hypercube sampling (M6) | Decision stability, not a single number |
| Update | New VAHAN months refit the curves automatically; a policy change adds a switch, not a new model | Version diff (M11) |

Operators that win tenders enter only as a reliability prior: an operator's observed uptime on earlier sites sets the starting C\_functional for its new sites. Operator financial analysis is out of scope.

### M11 Data architecture and update pipeline (Revision 3)

Neither one "super table" nor a graph database: three layers, each versioned.

| Layer | Contents | Rule |
| --- | --- | --- |
| Raw | Every source download exactly as received, with retrieval date and hash | Never edited; every number traces back to a file |
| Resolved | One table each for charger sites, zones (H3 cells), RTOs, DISCOMs, candidate sites and tenders, linked by IDs and H3 codes | Built from raw by dedup and matching (M2) |
| Outputs | Demand per cell, gaps, plans, proposal packages, flags | Stamped with data version and method version |

The parts that are graphs live inside these tables: the evidence ledger (which inputs produced which number, M9) and the road network used for travel times.

**Method versioning.** Every weight, threshold and assumption sits in one versioned settings file. Changing a value reruns the affected steps and produces a diff: which sites changed, and which input or parameter caused it. Changes are visible and reversible, and every past proposal stays reproducible with the version that produced it.

**Incremental recompute.** Steps form a dependency chain (source → RTO → zone → DISCOM calibration → state plan). When a source changes, only steps downstream of the changed records rerun, as a spreadsheet recalculates only affected cells. A full state rerun takes minutes and is needed only after method changes; the optimiser runs on request and the 200-sample stability run as a batch.

| Source | Refresh | Note |
| --- | --- | --- |
| VAHAN (dashboard or mirror) | Monthly | Registrations are flows; stock rebuilt for changed RTOs only |
| CEA EVCS report | Monthly | About 5 months behind |
| MoP / Parliament counts | When published | Reconciliation target |
| OSM, OCM | Weekly | Diffed against the previous pull |
| Operator lists | Weekly where terms allow | Licence checked per source |
| UBC / UEI, Delhi OpenEV | Live once access exists | Roadmap for Telangana |
| Tenders and sanction lists | On publication | Feeds the delivery tracker (M12) |

Stack as in Part VIII: Parquet and DuckDB for the layers, PostGIS for serving in the finale.

### M12 Delivery tracker and feedback loop (Revision 3)

A recommendation is only useful if someone can see what happened to it. Each proposed site moves through dated stages; the tracker flags delays and paper-only completions.

| Stage | Evidence | Flag (initial thresholds) |
| --- | --- | --- |
| Recommended | Our proposal package | — |
| Sanctioned | MHI or state sanction list | — |
| Tendered / awarded | Tender documents | Stuck more than 90 days |
| Grid connection applied → connected | Agency or DISCOM dates where published | Past the Rights of Consumers deadline (3 / 7 / 15 / 30 days) for standard connections; network augmentation flagged separately against its stated timeline |
| Commissioned | Agency report | — |
| Working | Status evidence (M2) | Commissioned but "unknown or likely down" |
| Used | CEA energy at DISCOM level now; UBC sessions per site later | Commissioned sites in a DISCOM whose reported energy does not move |

The tracker cannot detect corruption and does not claim to; it makes delay and non-delivery visible, which is the accountability lever available from public data. For the demo it runs on TGREDCO's sanction and tender as far as dates are public (open item).

**Feedback loop.** Predicted demand is compared with observed use and the model recalibrated: at DISCOM level now (CEA), at site level once session data exists. Built sites enter the next plan as existing supply, so earlier errors are absorbed rather than repeated. The limit, stated openly: site-level learning needs site-level usage data, which only operators and UBC hold.

**Fixing errors after deployment.** Because data, method and evidence are versioned (M11), a bug is fixed, the pipeline rerun, and the diff shows exactly which recommendations change and why. Past decisions stay explainable with the version that produced them. Nothing is scrapped.

### M13 Privacy, legal basis and governance (Revision 3)

| Question | Position |
| --- | --- |
| Personal data | None. Inputs are RTO × month counts, public charger locations and published aggregates; charger locations are not personal data. |
| Vehicle data | Public dashboard aggregates only. MoRTH scrapped bulk sale of VAHAN data in 2020 over privacy concerns; the 2025 National Transport Repository data-sharing policy (masking, compliance memoranda, CERT-In-audited applications, purpose limitation under the DPDP Act 2023) is the production path for deeper access. |
| Charger data from apps | Only sources whose terms allow reuse; Google Maps and PlugShare excluded; every licence recorded in the ledger. |
| Session data (future, via UBC) | Aggregated to H3 cell × day, no user identifiers, cells with fewer than 10 sessions suppressed. |
| Why consolidation has not happened | A known coordination and incentive problem, not an undiscovered one: ownership is split across MHI (schemes, UBC), MoP and BEE (guidelines, EV Yatra), MoRTH (VAHAN), MoPNG (OMC chargers), states and DISCOMs; there was no common schema until UEI/UBC; operators gain nothing by reporting failures; MHI told Parliament adequacy and NH data are not centrally maintained. |
| Who validates outputs | Review by exception: the method is reviewed once, published and versioned; automated checks run on every run (M7 tests, pre-merge gates, sanity rules); humans review only fragile sites, low-confidence inputs and large diffs from the previous run. |
| Users and interfaces | One user, the state nodal officer: planner screen and proposal export. No driver app (UBC serves drivers). Roadmap: a read-only public page showing sanctioned sites, delivery stage and status, for accountability. |

## Part I — Problem deconstruction

The PS asks for one of two tracks; both are judged on intelligence, transparency and defensibility, not on access to premium data. That last line is the most important sentence in the PDF for strategy.

### Track 1: EV Infra Map India

| Element | What the PS actually requires |
| --- | --- |
| Core objective | Integrate and map public EV charging nationwide; relate it to VAHAN EV population; find underserved areas; estimate future requirements; support MHI, ICAT and states |
| Data layers | EV registrations (VAHAN, state transport); chargers (apps, networks, open DBs); boundaries; roads and corridors; demographics and economic activity; electricity infrastructure; tourism, logistics, land use |
| Deliverables | Web platform; interactive national GIS map; methodology document; charger requirement estimation + recommendation module (states, districts, cities or corridors); decision-support dashboard; demo video for one geography; scalability roadmap |
| Explicit permission | Public, open, sample or realistic synthetic data allowed if documented |
| Hidden signal | Recognition section promises a pathway into real municipal / ULB charging planning |

### Track 2: Green Auto India

| Element | What the PS actually requires |
| --- | --- |
| Core objective | India-specific automotive LCA database and framework covering materials, components, processes, energy, logistics, use phase, end of life |
| Data layers | Materials (steel, Al, Cu, plastics, composites, recycled); components (body, chassis, powertrain, battery, tyres, electronics); processes (casting to assembly); energy (grid, RE, gas, H2); freight (road, rail, coastal); use phase; EoL; impact indicators |
| Deliverables | Prototype database with defined scope; architecture + data-collection framework; impact calculation engine; web dashboard; methodology document; case study on one product; scalability roadmap |
| Explicit relief | No exhaustive national database expected; a defined subset is fine |

### Judging and timeline

| Round | Criteria and weights | Date |
| --- | --- | --- |
| Registration | — | 15 Oct 2026 |
| Round 1: concept + roadmap | Problem understanding 25, feasibility 25, novelty 20, roadmap 20, data strategy 10 | Submit by 30 Oct 2026; results 7 Nov |
| Round 2: live demo at IIT Bombay | Robustness 25, data quality + integration 20, usability 20, innovation 15, scalability 10, presentation 10 | 16–18 Dec 2026 |

Round 1 is a document only: methodology + step-by-step roadmap with sources, tools and stages. Round 2 must be built in line with that roadmap, and you must explain how it evolved. So the roadmap is a contract; overpromising in Round 1 is penalised in Round 2.

### Rules that constrain strategy

- Rule 5: synthetic data must be clearly identified.
- Rule 6: AI tools, third-party software, datasets and frameworks must be disclosed.
- Rule 9: solutions must not be protected by patents, copyrights or publications. Using a published algorithm is fine; copying a patented method is a risk (see Part XII).
- One track per team; 2–5 members; cross-department teams encouraged.

## Part II — Global SOTA

The global state of the art in charging planning is the US NREL EVI-X suite; we did not identify a publicly documented Indian system combining its breadth of planning functions with the PM E-DRIVE proposal workflow, and its US travel-survey assumptions do not transfer. Academic SOTA for demand forecasting (spatio-temporal graph networks) depends on station-level session data that India does not publish.

### Deployed and reference systems

| System | Owner | What it does | Lesson for us | Reproducible? |
| --- | --- | --- | --- | --- |
| [EVI-X suite](https://nrel.gov/transportation/evi-x.html) (EVI-Pro, EVI-RoadTrip, EVI-Equity, EVI-DiST, EVI-Ratio) | NREL, USA | Network planning, site design and financial tools from regional to national scale | Separate daily-travel demand from road-trip corridor demand; link to grid (DiST) and equity tools | Concepts yes; models depend on US travel surveys and telematics |
| EVI-RoadTrip | NREL | Simulates routes, energy use and charging per minute of trip, then designs the corridor network and gap analysis | Corridor logic for NH-44 / NH-65 class roads | Partly; needs OD flows we must proxy |
| [EVI-OnDemand](https://github.com/NREL/EVI-OnDemand) | NREL | Open-source simulator for ride-hailing fleet charging needs | Relevant to e-3W and fleet demand | Yes, open source |
| [WRI India FACtTool](https://wri-india.org/initiatives/powering-ev-shift-building-indias-charging-ecosystem) + location framework | WRI India | Financial viability of charging sites; top-down geospatial + bottom-up siting applied in Delhi, Mumbai, Hyderabad | Indian precedent the judges may know; cite and extend, do not duplicate | Methodology public, tool partly |
| [NITI / WRI EV charging handbook](https://niti.gov.in/sites/default/files/2023-02/EV_Handbook_Final_14Oct.pdf) | NITI Aayog, MoP, WRI | Grid-cell weighting of demand parameters, energy-demand method | The "default" Indian method; most teams will copy it | Yes |
| [ASCI–NRDC siting manual](https://renewablewatch.in/2024/08/16/strategic-siting-framework-for-setting-up-ev-charging-stations/) | ASCI Hyderabad, NRDC | Site ranking validated with user surveys at 50+ Hyderabad sites | Hyderabad survey evidence to compare against | Method yes |
| [UBC](https://emobilityplus.com/2026/08/14/pulse-energy-integrates-10000-ev-chargers-with-bhim-upi-under-unified-bharat-echarge/) / UEI | MHI-BHEL-NPCI; Beckn alliance | National discovery + payment rail for chargers on the Beckn protocol | The sponsor's own data rail; design ingestion for it | Protocol open; access UNVERIFIED |
| Consumer apps (Statiq, Tata EZ Charge, ChargeIndia OCPI hub, PlugShare) | Private | Driver-facing discovery, booking, payment | Not planners; they show what operators report | No (closed data) |

### Open-source and data projects

| Project | Status | Use for us | Novelty risk |
| --- | --- | --- | --- |
| [Open Charge Map API](https://openchargemap.org/site/develop/api) | Active; mixed licensing per provider; filter `opendata=true` for CC BY-SA content | One charger source among several | Every team will use it |
| OCM "trust layer" and India road-trip planners on [GitHub](https://github.com/topics/open-charge-map) | Small hobby repos; one merges 3 India sources with an LLM copilot; one adds freshness-weighted reliability check-ins | Shows consumer reliability ideas already exist | High for consumer features; low for planning |
| [ST-EVCDP](https://gitee.com/mosskate/ST-EVCDP) (Shenzhen) | Research dataset: 18,061 piles, 5-min occupancy for 30 days, 247-zone graph | Template for the occupancy dataset UBC live status could create in India | None in India yet |
| OSMnx, OSRM, H3, OR-Tools | Mature, permissive licences | Core stack (Part VIII) | Neutral |

### Academic SOTA in one paragraph

Forecasting has moved to spatio-temporal graph networks (TGCN, ASTGRN, hypergraph models) trained on station occupancy or GPS trajectories from Shenzhen, Beijing, Tennessee or Scotland. Siting has moved from deterministic covering models to two-stage and multi-stage stochastic programs that handle adoption uncertainty and phased budgets ([Shen et al. 2024](https://arxiv.org/pdf/2411.01416); [equity-weighted fixed + mobile stations, 2026](https://arxiv.org/abs/2602.02333)). A 2024 review of 84 fast-charger siting studies found 41.7% used conventional optimisation, 33.3% metaheuristics, 22.6% hybrids, and called for real data on demand ([Putra et al.](https://doaj.org/article/263a1cbd16b64e4ba52feb587923e25d)). Indian studies mostly use metaheuristics on single cities (Guwahati, Delhi, Bhubaneswar) with assumed penetration rates.

**Takeaway:** the SOTA gap for India is not algorithms, it is calibrated, India-specific inputs. That is where to compete.

## Part III — India landscape

India has the money, the norms and a new national charger rail, but PM E-DRIVE prescribes no national spatial allocation method and sets no state, district or annual targets, and the MoP guidelines push annual demand mapping onto state nodal agencies.

### Policy and schemes that define the decision

| Instrument | What it says | Why it matters for the build |
| --- | --- | --- |
| [MoP charging guidelines 2024](https://www.mercomindia.com/ministry-of-power-releases-ev-charging-infrastructure-guidelines) | One station per 1 km × 1 km urban grid by 2030; every 20 km both sides of highways; fast charging every 100 km for long-range and heavy vehicles; separate metering; e-bus depots ≥ 240 kW | Testable guideline-alignment checks for the gap engine (guidance, not legal violations) |
| [Annual demand mapping](https://inc42.com/?p=465355) | State nodal agencies and city authorities map potential charging demand at least once a year | Your product is the tool for this duty |
| [PM E-DRIVE charger guidelines](https://www.newsonair.gov.in/centre-issues-guidelines-for-rollout-of-72300-ev-charging-stations-under-pm-e-drive/) | \~72,300 chargers; 100% subsidy at government premises with free public access; 80/70% at transit hubs, OMC outlets, toll plazas; nodal bodies aggregate demand and submit via a portal | Defines the candidate-site categories and subsidy tiers for the optimiser |
| [PM E-DRIVE status](https://www.electrive.com/2026/08/05/india-approves-chargers-awaits-deployment/) | 6,562 sanctioned, 0 installed as of 22 July 2026; no state/district/annual targets; FAME-II delivered 9,583 stations | The unsolved allocation problem |
| [UBC](https://emobilityplus.com/2026/08/14/pulse-energy-integrates-10000-ev-chargers-with-bhim-upi-under-unified-bharat-echarge/) | MHI-backed National Unified Hub; BHEL is implementing agency, NPCI BHIM builds it; announced 12 May 2026 | Sponsor's own discovery rail; design for it |
| [Delhi OpenEV database](https://www.deccanherald.com/india/delhi-govt-launches-open-database-for-ev-charging-battery-swapping-stations-1144788.html) | Mandatory operator reporting; static and real-time data via API key on request | Overlooked source of reliability labels; current status UNVERIFIED |
| [BEE EV Yatra](https://powerline.net.in/2022/12/14/ev-yatra-web-portal-and-mobile-app-launched/) | National online database where CPOs register stations | The official registry behind MoP counts; no bulk download found |

### VAHAN deep dive

| Question | Finding | Tier |
| --- | --- | --- |
| Granularity | RTO × month × fuel × category × class × maker via the public dashboard and mirrors ([India Data Portal](https://ckandev.indiadataportal.com/dataset/vahan-vehicle-registrations/resource/808d2b3c-dcdd-48fc-ae6a-cc99e137ec9c), [Dataful](https://dataful.in/datasets/22379)) | A / C |
| API | No official public API found; dashboard scraping or mirrors | UNVERIFIED that none exists |
| Stock vs flow | Registrations are flows; stock must be built by summing with a retirement assumption | Method |
| Data quality | CSE found 10.4 lakh+ records with no fuel, unknown fuel types, EVs tagged with BS norms ([Down To Earth, 2026](https://www.downtoearth.org.in/air/driving-on-broken-data-why-indias-clean-air-and-ev-push-cannot-outrun-vahans-cracks)) | E citing B-grade analysis |
| Unregistered low-speed e-2W | \~22.4 lakh CKD kits imported Nov 2023–Oct 2025 vs \~25.0 lakh registered high-speed e-2W; North skews low-speed ([EVreporter](https://evreporter.com/the-e-2w-sales-india-doesnt-track-why-should-it-bother-us/)) | E citing customs data |
| Unregistered e-rickshaws | \~4.75 lakh estimated; West Bengal drive caused a Nov 2025–Jan 2026 registration spike ([JMK](https://jmkresearch.com/mandatory-registration-of-all-electric-rickshaws-across-states-in-india/)) | C |
| Location bias | Vehicle registers at owner's RTO, not where it charges; fleet and leasing companies register in hub cities | Known structural bias |
| RTO → district | RTOs do not map 1:1 to districts; a crosswalk must be built | Engineering task |

Compensation without inventing data: model stock by class, apply state-level shadow-fleet multipliers with explicit low/high bands, flag and smooth enforcement-driven spikes, and calibrate total public-charging energy to CEA.

### Charger data sources

| Source | Coverage | Access | Freshness | Key problem |
| --- | --- | --- | --- | --- |
| MoP / PIB state counts | All states (29,277 stations) | Public PDF | Periodic | State level only |
| CEA EVCS power consumption | States with reporting DISCOMs | Public, monthly | Monthly | Missing NE states, HP, Uttarakhand, some UTs |
| UBC / UEI | Participating CPOs; UEI listed 5,386 points early on; Pulse alone connects 10,000+ to UBC | Gateway access UNVERIFIED | Live | Coverage still growing |
| Delhi OpenEV | Delhi only | Registration + API key | Real-time | Access UNVERIFIED |
| Open Charge Map | Global; OCM itself says India data is thin | Open API, mixed licences | Crowd | Sparse, duplicates |
| OpenStreetMap `amenity=charging_station` | Partial | ODbL | Crowd | Uneven by city |
| Operator locators (Tata, Statiq, ChargeZone, OMCs) | Network-specific | Website terms vary | Live | Scraping terms; no common schema |
| Google Maps / PlugShare | Broad | Restricted terms | Live | Cannot legally build a derived database |

Count definitions conflict: MoP says 29,277 stations; industry reports cite 39,500 chargers including semi-public; blogs cite 52,700. Your methodology must define site, charge point and connector, and reconcile to the MoP site count.

### Demo geography fact base: Telangana

Telangana has 2.8 lakh+ registered EVs, 91,572 new EV registrations in FY2025-26, 1,063 operational stations (about 600 in Hyderabad), and a target of 6,000 stations by 2030 ([UNI, May 2026](https://www.uniindia.com/telangana-showcases-ev-charging-success-story-at-national-conference-in-bengaluru/business-economy/news/3840860.html)). TGREDCO holds a PM E-DRIVE Phase-I sanction of ₹10.24 crore for 116 locations and tendered 369 stations in September 2026: 200 in Hyderabad in six clusters with 95% uptime, and 169 across Warangal, Khammam, Karimnagar, Nizamabad and Adilabad ([Telangana Today](https://telanganatoday.com/tg-redco-invites-tenders-for-369-public-ev-charging-stations)). Hyderabad also targets 2,800 e-buses by 2027. These give you real planning decisions to benchmark against.

## Part IV — Social and news intelligence

The dominant real-world failure is not missing chargers but unreliable ones: owners have shifted from range anxiety to "will the charger work when I arrive". Grid connection cost and land are the main supply-side blockers. None of these show up in official counts.

| Failure mode | Evidence | Evidence class | What the platform should do |
| --- | --- | --- | --- |
| Listed chargers not working | 18% of OMC stations non-functional (27,737 installed vs 22,753 operational, OMC stations only, Rajya Sabha Q.3910); BPCL network reported at 60% non-operational ([mmcm.in](https://mmcm.in/blog/ev-charging-infrastructure-in-india/)); an "audit" claiming most chargers are broken traces to IEEFA's 2024 Delhi sample (\~84% of examined chargers not functional) | Official (OMC only) + sampled audit | Confidence score per charger; plan on working capacity, not installed |
| App shows "available" when offline | Owners keep several apps and never trust one app's status ([Team-BHP](https://www.team-bhp.com/news/mobile-apps-locate-check-working-ev-charging-stations)); apps advertise backend cross-checks as a fix | Repeated pattern | Weight live-status sources; decay stale listings |
| Fragmented apps and wallets | Core motivation for UBC and the IEEFA 2026 report on charging experience ([IEEFA](https://ieefa.org/sites/default/files/2026-09/EV%20charging%20experience%20in%20India.pdf)) | Official + C-tier | Interoperability-ready ingestion |
| Grid connection cost and delay | Upstream grid works can be up to 50% of station cost; DISCOM delays named as a key barrier ([IEEFA via EV Infrastructure News](https://www.evinfrastructurenews.com/ev-regulations/india-needs-more-reliable-affordable-ev-charging-to-boost-adoption-ieefa)) | Independently corroborated | Grid-headroom proxy in site scoring |
| Land identification | Land-owning agencies lack tools to estimate a site's revenue potential ([ITDP India](https://india.itdp.org/?p=17754)) | Recognised technical organisation | Candidate sites limited to eligible public land; show expected utilisation |
| Low yields, OMC sites underused | OMCs earn nothing for occupied time; EV charging "government-pushed" ([The Core, May 2026](https://www.thecore.in/business/real-estate-hurdles-low-yields-continue-to-stifle-indias-ev-charging-expansion-863379)) | Reputable journalism | Over-supply detector; avoid stranded subsidy |
| Chargers blocked by parked cars | Videos and posts of ICE and EVs parked at chargers ([Cartoq](https://svb1.cartoq.com/car-life/ev-owners-blocking-charging-stations-growing-problem-india)) | Anecdotal | Mention only; not modelled |
| Grid quality in small towns | Voltage fluctuation, poor earthing, informal connections ([Down To Earth](https://www.downtoearth.org.in/amp/story/energy/indias-ev-charging-push-faces-ground-level-hurdles-home-charging-must-be-seen-as-key-solution)) | Expert panel statements | Reliability prior lower in Tier-3 towns |
| Counts that disagree | MoP 29,277 stations vs IEEFA 52,718 by July 2026 vs 39,500 "chargers" incl. semi-public | Official vs C-tier conflict | Counting standard + reconciliation report |
| Uneven spread | Two-thirds of Karnataka's \~6,000 locations in or around Bengaluru; Delhi = 27.9% of FY26 PCS energy (CEA) | Corroborated (CEA + reporting) | Concentration index per state |

Saturation note: searches for Reddit and X threads mostly returned blogs and consumer apps quoting each other. Reddit evidence is therefore thin and not used for any number. The repeated themes (offline chargers, app fragmentation, grid delay) converge across Team-BHP, industry, think tanks and government, which is why they are treated as real.

## Part V — Competitor landscape

This appears to be the first MHI/ICAT challenge at Techfest: no prior edition, winners or published solutions turned up, so there is no winning template to copy, and judges will compare teams mainly against each other. Past EV hackathons in India and student GitHub projects show a very consistent pattern of consumer apps and dashboards.

### What past entries look like

| Source | Typical build | Lesson |
| --- | --- | --- |
| Hackathon repos (e.g. a [Dotslash smart-city entry](https://github.com/Done-With-Coding)), [Devfolio projects](https://devfolio.co/projects/ev-sathi-709f) | Flutter/React app, PostGIS, Maps API, "find nearest charger + book slot" | Driver-facing apps are the default student instinct; wrong user for this PS |
| Portfolio dashboards ([Maven](https://mavenanalytics.io/project/18217), LinkedIn "VoltVista") | Power BI on VAHAN sales + state charger counts | The "EVs per charger by state" chart is already everywhere |
| Consumer AI launches ([ChargeRoute](https://webmail.hunted.space/dashboard/chargeroute)) | Gemini assistant, multilingual, community voting on status | LLM + charger map is a commodity in 2026 |
| [CMU INCEPTS, MOVE hackathon 2018](https://www.cmu.edu/energy/news-multimedia/2018/global-mobility-hackathon.html) | Physics-based demand density with Ather | Finalist-level work varies charger scale by local power demand, not just distance |
| [iTEC India 2019 hackathon](https://channeldrive.in/applications/itec-india-2019-announces-10-hackathon-finalists/) | Themes: last-mile e-2W/3W, recycling, efficiency | e-2W/3W relevance is recognised by Indian juries |

### Common build patterns and the questions they face

| Build pattern | What a judge will ask |
| --- | --- |
| Charger map + state choropleth | What decision does this support? |
| EVs-per-charger heatmap | Are 2W and 4W lumped together? |
| ML demand forecast | Trained on what target? |
| K-means / GA / PSO siting | Can you explain or reproduce it? |
| LLM chatbot over the map | What does it decide? |
| NITI grid-cell weighting | What is new beyond the handbook? |

We assume competitors will have competent GIS, optimisation and ML implementations; our differentiation does not depend on their being weak. Indian student repos reportedly already implement MCLP/MILP siting, GIS and ML for Hyderabad and Bengaluru, so assume capable competitors.

### Typical builds

- National charger map with clustering and filters.
- EVs-per-charger by state or district.
- A demand forecast with no stated training target.
- "Optimal sites" from k-means or a metaheuristic.
- A chatbot.

### Our differentiators (a combination, not a claim of algorithmic novelty)

- A charger confidence score and an installed-vs-working reconciliation.
- Demand in kWh by vehicle class, calibrated to CEA state energy.
- A shadow-fleet correction with uncertainty bands.
- MoP guideline-alignment scoring (1 km grid, 20 km and 100 km highway guidance).
- Budget-constrained allocation that outputs a PM E-DRIVE-style proposal list with a reason per site.
- A retrospective backtest against chargers actually built.
- An over-supply and stranded-asset detector.
- A benchmark against a real state plan (TGREDCO's 369-station tender).

## Part VI — Research landscape

For Track 1, the right methods are classical and well proven (covering models, flow-refuelling models, stochastic programs); the differentiator is feeding them calibrated Indian inputs and stating uncertainty. For Track 2, the open tooling is mature (Brightway, openLCA), but Indian inventory data is old or missing, which is the real gap.

### Track 1: methods judged against Indian data reality

| Method family | Maturity | Data it needs | Available in India? | Verdict |
| --- | --- | --- | --- | --- |
| Maximal covering location (MCLP), p-median, set cover | Seminal, exact MIP solvers | Demand points + candidate sites + distances | Yes (built from VAHAN, census, OSM) | **Use**: core urban allocation |
| Flow-capturing / flow-refuelling location (FCLM, FRLM) | Mature; continuous versions active ([arXiv 2025](https://arxiv.org/pdf/2509.11441)) | OD flows on corridors | Proxy only (NH traffic counts sparse) | **Use with proxy flows** for NH corridors |
| Two-stage / multi-stage stochastic programs | Active 2024–26 ([Shen et al.](https://arxiv.org/pdf/2411.01416)) | Scenario set for adoption and behaviour | Yes, via scenario generation | **Use light version**: scenario sampling + robustness score |
| Equity-weighted siting | Active ([arXiv 2026](https://arxiv.org/abs/2602.02333)) | Socio-economic index per zone | Census + night-lights proxies | **Use** as a weight, not a headline |
| Metaheuristics (GA, PSO, Walrus, CSO-TLBO) | Saturated; 33% of recent studies | Same as MCLP | — | **Avoid**: exact solvers suffice at our scale and are explainable |
| Spatio-temporal GNNs (TGCN, ASTGRN, hypergraph) | Strong on Chinese/US session data | Station-level occupancy or sessions | No public Indian equivalent | **Roadmap only**: possible once UBC live status is logged |
| Bayesian spatial models (INLA, latent Gaussian) | Recent for EV demand ([Scotland, 2026](https://arxiv.org/pdf/2604.19841)) | Area-level counts over time | Partly (VAHAN by RTO-month) | **Optional**: adoption forecast with intervals |
| Gravity / accessibility indices, travel-time surfaces | Mature | Roads + population | Yes | **Use** for accessibility metrics |
| Peak-hour utilisation sizing (M/M/c-inspired approximation) | Mature | Arrival rate, session time | Assumed from CEA energy + literature | **Use** for plugs-per-site sizing |
| Agent-based / digital twin | Heavy | Trip diaries, behaviour | No | **Avoid** in competition window |

Open problems the literature itself names: real demand data for fast-charger siting; mixed fleets dominated by 2W/3W; and siting under adoption uncertainty with phased budgets. Each maps to a feature in Part X.

### Track 2: LCA state of the art

| Item | Status | India relevance |
| --- | --- | --- |
| [Brightway 2.5](https://github.com/brightway-lca/brightway25) | Open-source Python LCA framework; separated matrix and calculation libraries; large plugin ecosystem | Best engine for a transparent student build |
| [premise](https://pypi.org/project/premise/2.4.9.2/) | Projects ecoinvent into the future using integrated-assessment scenarios | Models India's grid decarbonising over a vehicle's life; needs an ecoinvent licence |
| openLCA 2 | Open-source desktop LCA; imports to Brightway exist ([openlca2bw](https://pypi.org/project/openlca2bw)) | Good for ICAT-style users; less scriptable |
| ecoinvent | Licensed global database; India datasets mainly for electricity and steel from earlier projects | Licence cost and redistribution limits |
| [Indian LCA database (CSIR-NEERI)](https://jurnal.ugm.ac.id/ajse/article/download/101472/41078) | \~1,321 datasets, dated 2016 | Old; useful as seed data if accessible |
| [National LCA database roadmap](https://zenodo.org/records/18509407) | NEERI-led plan for UN Environment with CII | Governance template for the "scalability roadmap" |
| [ITF LCA India Tool v1.0](https://www.itf-oecd.org/sites/default/files/repositories/subrajeet_sengupta.pdf) | IIT (ISM) Dhanbad; vehicle life-cycle stages, city cases | Direct prior art; judges may know it |
| [ICCT review of Indian car LCAs, 2025](https://theicct.org/publication/review-of-ghg-life-cycle-assessments-of-passenger-cars-in-india-jun25/) | Six studies; grid carbon intensity, test-cycle energy and real-world adjustment explain about three-quarters of the variance | Tells you which three parameters matter most |
| [Battery Waste Management Rules 2022](https://www.iea.org/policies/25166) | EPR; EV battery recovery 70% (2024-25) rising to 90% (2026-27); recycled-content minimums from FY2027-28 | End-of-life module can be policy-grounded |

Track 2's whitespace is real: no open, maintained, India-specific automotive inventory exists. But filling it credibly needs primary process data (Indian steel routes, cell imports, state grid mixes) that a student team can only approximate from literature by 30 October.

## Part VII — Data landscape

Every data layer the PS lists can be filled from public sources, but three of the most valuable are obscure: CEA monthly charging-energy reports, IHMCL monthly FASTag counts per toll plaza, and state transmission utilities' substation lists with coordinates and spare capacity.

### Dataset inventory

| Dataset | Owner | Coverage | Resolution | Freshness | Access / licence | Reliability | Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VAHAN dashboard + mirrors | MoRTH / NIC; India Data Portal, Dataful | All states | RTO × month × fuel × class | Monthly | Public; mirrors ODC-BY | Medium (gaps, unregistered fleet) | EV stock by class |
| [CEA EVCS power consumption](https://cea.nic.in/electric-vehicle-charging-reports/?lang=en) | CEA | Reporting DISCOM states | State, monthly | Monthly | Public | High where reported | Calibration + utilisation |
| [MoP state station counts](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/aug/doc202581598101.pdf) | MoP via PIB / Parliament | 36 states/UTs | State | Periodic | Public | High (as a count) | Reconciliation target |
| UBC / UEI discovery | MHI-BHEL-NPCI / Beckn | Participating CPOs | Charger, live | Live | Access UNVERIFIED | High for listed CPOs | Truth layer + live status |
| [Delhi OpenEV](https://www.deccanherald.com/india/delhi-govt-launches-open-database-for-ev-charging-battery-swapping-stations-1144788.html) | GNCTD Transport | Delhi | Charger, real-time | Live | Registration + API key | Mandatory reporting | Reliability labels |
| Open Charge Map | Community | Thin in India | Point | Crowd | Mixed; CC BY-SA subset | Low–medium | Secondary source |
| OSM (roads, chargers, POIs, `power=substation`) | OSM | National | Vector | Continuous | ODbL | Medium; uneven | Road graph, POIs, candidate sites |
| [NHAI toll plazas (TIS scrape)](https://github.com/ajitccdc/toll-plazas-india) | NHAI | \~468 plazas | Point + PCU/day | Monthly scrape | Gov open data intent | Medium | Corridor flow anchors |
| [IHMCL FASTag monthly counts](https://ihmcl.co.in/wp-content/uploads/2026/08/June-2026.pdf) | IHMCL (NHAI) | All FASTag plazas | Plaza × vehicle class × month | Monthly PDF | Public | High | Corridor traffic by class |
| State substation lists, e.g. [MP PM-KUSUM 33 kV list](https://mprenewable.nic.in/uploads/2024/List%20of%20Substations%20November%202024.pdf), [MSETCL spare capacity](https://www.mahatransco.in/uploads/docs/Power%20evacuation%20capacity%20available%20in%20MSETCL%20substations%20as%20on%2003.06.2025.pdf) | State utilities | State-specific | Point + capacity | Irregular | Public PDFs | Indicative only | Grid-headroom proxy |
| Census 2011 + WorldPop / GHSL grids | RGI; academic | National | District; \~100 m | 2011; modelled annual | Open | Medium (old census) | Demand spreading |
| Night-time lights (VIIRS) | NOAA / academic | National | \~500 m | Monthly | Open | Medium | Economic activity proxy |
| Bhuvan LULC | NRSC / ISRO | National | Raster | Periodic | Registration | Medium | Land-use screening |
| State tenders (e.g. TGREDCO 369-station tender) | State nodal agencies | Per state | Site / cluster | Event | Public | High | Benchmark plans |

### Official data vs real-world reality

| Variable | Officially available? | Resolution | Freshness | Reliability | Real-world gap | Legitimate proxy |
| --- | --- | --- | --- | --- | --- | --- |
| EV registrations | Yes (VAHAN) | RTO-month | Monthly | Medium | Unregistered low-speed 2W and e-rickshaws; registration ≠ usage location | Customs / industry estimates as bounded multipliers |
| Charger locations | Partly (EV Yatra, UBC) | Point, not bulk-public | Varies | Medium | Duplicates, stale and private sites | Multi-source fusion + confidence |
| Operational status | No national feed | — | — | Low | OMC only: 82% operational on 1 Mar 2026 | UBC/OpenEV live status; operator priors |
| Utilisation | Yes, aggregated (CEA) | State-month | Monthly | High where reported | No site-level data | kWh per station by state |
| Queueing | No | — | — | — | Lunch-hour peaks reported anecdotally | Peak-hour utilisation sizing approximation from energy and session assumptions |
| Grid capacity | Fragmented PDFs | Substation | Irregular | Indicative | No national feeder headroom data | Substation density + state lists |
| Traffic | Yes on tolled roads (IHMCL) | Plaza-month | Monthly | High | Untolled roads, urban streets | OSM road class + centrality |
| Road quality | Partial | — | — | Low | — | Road class as proxy |
| Land availability | No | — | — | — | Main CPO blocker | PM E-DRIVE eligible-site categories from OSM (bus depots, metro, OMC outlets) |
| Socio-economic demand | Yes (census, lights) | District / grid | Old / monthly | Medium | 2011 census age | Night lights + POI density |

## Part VIII — Framework and stack landscape

A fully open, laptop-runnable stack is enough for one state and scales to national by partitioning on state; no paid solver or API is needed. Licence and maturity notes below are from general knowledge unless linked; confirm licences before Round 1 disclosure (Rule 6).

| Tool | Domain | Best at | Maturity | Licence | Student prototype? | National scale? | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DuckDB + Parquet | Data | Fast local analytics, spatial extension | Mature | MIT | Yes | Yes | **Core store** |
| PostgreSQL + PostGIS | Data / GIS | Multi-user serving, spatial SQL | Mature | PostgreSQL / GPL | Yes | Yes | Finale serving layer |
| Polars | Data | Fast dataframes | Mature | MIT | Yes | Yes | Use for VAHAN wrangling |
| GeoPandas, Shapely, GDAL, Rasterio | GIS | Vector/raster ops | Mature | BSD / MIT | Yes | Yes | **Core** |
| H3 | GIS | Hexagonal indexing, dedup, aggregation | Mature | Apache-2.0 | Yes | Yes | **Core index** (computational index only; MoP 1 km × 1 km alignment is checked on a separate guideline layer) |
| OSMnx + NetworkX | Network | Road graphs, centrality | Mature | MIT / BSD | Yes | Slow nationally | City-scale analysis |
| OSRM | Routing | Fast distance matrices | Mature | BSD-2 | Yes (Docker) | Yes | **Core** for coverage distances |
| Valhalla / GraphHopper / OpenRouteService | Routing | Isochrones, profiles | Mature | MIT / Apache / GPL | Yes | Yes | Isochrones if needed |
| OR-Tools (CP-SAT, MIP) | Optimisation | Exact MCLP / allocation | Mature | Apache-2.0 | Yes | Yes per state | **Core solver** |
| Pyomo + HiGHS | Optimisation | Readable model code | Mature | BSD / MIT | Yes | Yes | Alternative |
| Gurobi / CPLEX | Optimisation | Speed | Mature | Commercial (academic free) | Yes | Yes | Not needed; avoid licence questions |
| pymoo (NSGA-II) | Optimisation | Multi-objective fronts | Mature | Apache-2.0 | Yes | Medium | Optional Pareto view |
| LightGBM / XGBoost | ML | Tabular classification | Mature | MIT / Apache | Yes | Yes | Reliability model, later phase, once status labels exist |
| PyTorch Geometric | ML | Graph neural networks | Mature | MIT | Yes | Yes | Roadmap only (no Indian session data) |
| rapidfuzz / splink | Entity resolution | Fuzzy match, probabilistic linkage | Mature | MIT | Yes | Yes | **Charger dedup** |
| FastAPI | Backend | Typed APIs | Mature | MIT | Yes | Yes | **Core API** |
| MapLibre GL + deck.gl | Frontend | Open vector maps, GPU layers, H3 layers | Mature | BSD / MIT | Yes | Yes | **Core map** |
| Kepler.gl | Frontend | Quick exploratory maps | Mature | MIT | Yes | Demo only | Exploration |
| Mapbox GL | Frontend | Polished tiles | Mature | Proprietary since v2 | Yes | Cost | Avoid |
| QGIS | Desktop GIS | Manual QA | Mature | GPL | Yes | — | Data checking |
| Beckn protocol / UEI sandbox | Integration | Charger discovery over the national rail | Growing | Open spec | Sandbox UNVERIFIED | Yes | **Ingestion adapter** |
| Brightway 2.5 / openLCA | LCA | Track 2 engine | Mature | BSD / MPL | Yes | Yes | Only if Track 2 |
| LLM (any) | Explanation | Turning optimiser output into a plain-language site memo | — | Varies | Yes | Yes | Narrow use only; disclose |

### Where AI genuinely helps

| Task | Best tool | Why |
| --- | --- | --- |
| Distance, coverage, MoP guideline alignment | Deterministic GIS | Exact and auditable |
| Where to put N chargers | MIP optimisation | Provably optimal for the stated objective; explainable |
| EV stock and adoption trend | Statistics (growth curves, Bayesian) | Small data, needs intervals |
| Charger dedup across sources | ML-assisted entity resolution | Messy names and coordinates |
| Probability a charger is offline | Gradient-boosted classifier | Only once enough status labels exist; start with rule-based evidence fusion |
| Charging demand forecast at station level | GNN | Only with occupancy data (not yet) |
| Site justification memo | LLM | Language task over structured facts |
| Chatbot over the map | — | Adds nothing for a planner |

Pitch framing: AI handles messy evidence (entity resolution, evidence fusion, registration-spike and anomaly detection, scenario generation, plain-language explanation); operations research handles constrained decisions. Neither replaces the other.

| Problem | Method | Kind |
| --- | --- | --- |
| Charger entity resolution | ML-assisted fuzzy matching | AI |
| Conflicting charger evidence | Rule-based confidence scoring | Evidence fusion |
| Registration spikes and data anomalies | Statistical change and anomaly detection | Statistics |
| Demand estimation | Calibration against CEA aggregates | Statistics |
| Future uncertainty | Scenario generation (Latin hypercube, latent-fleet plans, spatial priors) | Statistics |
| Site and configuration allocation | Budgeted MIP with ε-constraint frontier | Operations research |
| Corridor placement | Flow-refuelling optimisation | Operations research |
| Explanation | Structured template; an LLM may only reword | AI (narrow) |
| Validation | Holdouts, ablation, baselines, corruption tests | Statistics |

## Part IX — Novelty map and true whitespace

The strongest whitespace is not a new algorithm; it is moving Indian charging research from suitability mapping to executable, auditable PM E-DRIVE proposals. 2026 Indian papers already cover GIS/MCDA siting, AI forecasting with siting and sizing, and equity frameworks, so no single component below is novel on its own.

### Novelty tiers

| Tier | Ideas | Why |
| --- | --- | --- |
| Crowded | Charger map; EVs-per-charger heatmap; ML demand forecast without target; GA/PSO siting; LLM chatbot; trip planner | Dozens of repos, dashboards and consumer apps already do these |
| Moderately differentiated | NITI grid-cell weighting; MCLP with population; highway 20 km gap check; equity index | Published methods; good execution still scores |
| High-value whitespace | PM E-DRIVE proposal package; evidence ledger per site; charger evidence fusion; CEA-constrained demand totals; decision stability; marginal coverage per crore; why-not-here explanations; real-plan replay (TGREDCO, UPNEDA) | We did not identify a publicly documented Indian tool doing these; data exists publicly |
| Research-grade opportunities | Logging UBC live status into India's first station-occupancy dataset; Bayesian district adoption model; multi-stage phased allocation 2026→2030 | Feasible after the finale; strong roadmap material |

### Gaps we did not find publicly documented (within our search scope)

| Gap | Evidence it is a gap | We did not identify a publicly documented Indian example of |
| --- | --- | --- |
| Spatial targets for PM E-DRIVE | MHI says the scheme sets no state, district or annual targets | Any public allocation model for the 72,300 chargers |
| Constraining demand totals with reported charging energy | CEA publishes state energy monthly; Indian siting papers assume penetration rates instead | A planning study using CEA EVCS data as an aggregate constraint |
| Installed-vs-working reconciliation | Count conflicts (29,277 vs 39,500 vs 52,718); official status data exists only for OMC stations (82% operational) | A public reliability-weighted national charger layer |
| Unregistered-fleet-aware demand | Customs data implies a low-speed e-2W channel \~0.9× the registered high-speed channel; \~4.75 lakh unregistered e-rickshaws | Any planning model correcting VAHAN for this |
| Class-specific coverage | Tools treat "EVs" as one class; PM E-DRIVE itself splits \~48,400 chargers for 2W/3W | Planning outputs split by 2W/3W/4W/bus |
| Planning on the national rail | UBC launched May 2026 | Any planning tool consuming Beckn discovery |
| Under-utilisation risk | Karnataka: most stations, about one-fifth of Delhi's energy per station | A tool flagging stranded or under-used subsidised capacity |
| Revenue estimate for land-owning agencies | ITDP: agencies cannot estimate a site's revenue potential | A public site-level viability estimate tied to measured demand |

### India-specific novelty (what a US or EU platform would miss)

- Two- and three-wheelers dominate EV volume, so coverage radius and charger type must vary by class.
- A large unregistered low-speed fleet concentrated in the North and East.
- Registration drives that create artificial adoption spikes in VAHAN.
- DISCOM-fragmented grid data and heavy upstream connection costs.
- Apartment and street parking limits on home charging, raising public 2W/3W demand.
- Seasonal traffic peaks pre-monsoon and pre-festival on tolled corridors, visible in IHMCL data ([NIIF](https://niifindia.in/?p=10289)).
- A government-built digital public infrastructure rail (UBC) that Western markets do not have.

## Part X — Proposed winning architecture

The system turns public data into a ranked, justified list of charger sites; every proposed site carries an evidence trail, and modelled demand totals must stay consistent with CEA's utility-reported energy by state and DISCOM (an aggregate constraint, not proof of where demand sits).

&#91;embedded content: system architecture · 3 source groups, 7 processing stages\]

Data flows top to bottom; the only loop is the calibration refit, which keeps demand totals consistent with reported energy.

### Models and algorithms

| Stage | Method | Inputs | Output |
| --- | --- | --- | --- |
| Truth layer | H3 res-9 bucketing, rapidfuzz/splink matching on name + operator + connector, 50 m merge radius; evidence fusion: confidence scores C\_real, C\_public, C\_current, C\_functional, C\_location from published rules (Formal methods, M2); not probabilities | All charger sources | One record per site with p(real, public, working) |
| Reconciliation | Sum high-confidence sites per state vs MoP count; report the gap | Truth layer + MoP | Coverage-of-official-count per state |
| Stock model | Cumulative registrations minus retirement curve; enforcement-spike detection (step change + known drives) | VAHAN RTO-month by class | EV stock by class per district |
| Shadow fleet | Three plans: registered-only, moderate and high latent fleet (low-speed e-2W, e-rickshaws); report sites that survive all three | Customs-based and industry estimates | Adjusted stock with interval |
| Energy demand | stock × daily km × kWh/km × public-charging propensity per segment, split into local, corridor and fleet/depot demand; swapping share stated as an assumption | Stock + literature parameters | kWh/day per district, then per H3 cell |
| Spatial spread | Dasymetric weighting by population, night lights, POI density, road class | WorldPop, VIIRS, OSM | kWh/day per cell |
| Calibration | Fit public-share parameters so modelled light-duty state totals match CEA's light-duty column (heavy-duty column for the e-bus module); hold out 3–4 states | CEA monthly kWh | Calibrated parameters + error |
| Corridor demand | FASTag counts as a directional traffic anchor (not charging demand) → segment flows with EV share and range assumptions → flow-refuelling candidates | IHMCL, NHAI TIS, OSM NH | Corridor kWh and gap segments |
| Gap engine | Demand vs confidence-weighted capacity (kW × realistic hours); MoP grid and spacing tests; capacity-normalised under-utilisation risk | All above | Gap and guideline-alignment layers |
| Allocation | Budgeted MIP in efficiency, equity and balanced modes, with optional district access floors and a minimum-benefit hurdle, ₹ budget, site-eligibility ladder and segment-specific travel-time coverage; separate flow model for NH; solver gap reported | Gap layer + candidates | Site list with marginal gain per site |
| Sizing | Peak-hour utilisation ceiling ρ ≤ ρ\_max per configuration (Formal methods, M6) | Allocated demand | Plugs and kW per site |
| Robustness | Re-solve over Latin-hypercube samples of documented parameter ranges; selection frequency per site | Scenario sampler | Decision-stability score |
| Source lineage and gates | Lineage groups; pre-merge checks; source reliability from the labelled sample (M2) | All charger sources | Independent-agreement counts; quarantine log |
| Status and silent failure | Signal hierarchy; zero-session test where sessions exist; display labels (M2) | Status feeds, reports, priors | C\_functional and "unknown" labels |
| Resilience | N-1 removal test on corridors with OSRM rerouting (M6) | Corridor plan, road graph | Resilience score; single points of failure |
| Adoption forecast | S-curve per state × segment with backtest and policy switches (M10) | VAHAN monthly | Adoption scenarios with bands |
| Delivery tracker | Dated stage table; energy-after-commissioning check (M12) | Sanctions, tenders, CEA | Delay and non-delivery flags |
| Explanation | Template over structured facts (why here / why not here); an LLM may reword, never decide | Site record | Plain-language reason per site |

### Validation

| Test | How | Pass signal |
| --- | --- | --- |
| Calibration hold-out | Fit on most states, predict CEA energy for held-out states | Error stated with interval |
| Temporal backtest | Fit adoption through 2024, predict 2025 VAHAN by class | MAPE by state |
| Retrospective siting | Run allocation on 2023 data; compare coverage, travel time, equity and cost against actual 2024–26 deployment (overlap is not proof) | Beats "proportional to EVs" baseline |
| Benchmark against a real plan | Replay TGREDCO's 116-location PM E-DRIVE sanction and 369-station tender, and UPNEDA's 238-station tender | Overlap and documented differences |
| Sensitivity | One-at-a-time and Sobol-style ranking of parameters | Top drivers named |
| Baselines | Proportional-to-EVs; MoP grid rule only; k-means | Coverage per crore |

This table is superseded by the four-test validation protocol in Formal methods (M7).

### Scalability

The pipeline runs per state inside a hierarchical frame (national envelope → state → city or corridor → site), with national corridor links so state borders do not create gaps. H3 keeps joins cheap. Solve times are not yet measured, so no scalability claim is made until the benchmark in Formal methods (M7, test G) is run. Production would swap web sources for UBC discovery, CEA DISCOM-level reports and direct VAHAN access under an MoU.

## Part XI — MVP vs grand-finale version

Round 1 should ship a thin but real slice for Telangana with actual outputs; everything else is roadmap. The Round 2 rubric rewards robustness and data integration, so the finale adds the live optimiser, robustness runs and validation, not more map layers.

&#91;embedded content: build timeline · official dates + proposed work blocks\]

The five weeks between results (7 Nov) and the finale (16 Dec) carry most of the engineering, so Round 1 must already have the data plumbing working.

| Capability | Round 1 (by 30 Oct) | Finale (16–18 Dec) |
| --- | --- | --- |
| Charger truth layer | Telangana, 3 sources, confidence v0, reconciliation vs MoP and the state's 1,063 figure | All sources incl. UBC/OpenEV where accessible; reliability classifier |
| Demand | RTO-level demand by segment from VAHAN; latent-fleet plans documented, not yet run | H3 spread; enforcement-spike handling; Bayesian adoption intervals |
| Calibration | CEA aggregate check for Telangana's DISCOMs | Hold-out states; error bars in the dashboard |
| Corridors | Not in Round 1 | IHMCL-based flows, flow-refuelling allocation |
| Resilience | Method described | N-1 check on one or two corridors |
| Delivery tracker | Schema and stage definitions | Telangana sanction and tender tracked with flags |
| Forecast | Method and backtest plan | Backtested S-curves with policy scenarios |
| Allocation | One budgeted run exported as a proposal package, with reasons | Live re-solve on budget change; decision-stability runs |
| Validation | Method described; NITI/WRI baseline comparison on the same budget | Full test suite (Part X) incl. TGREDCO benchmark |
| UI | Screenshots and a short screen recording | Live web app, proposal export, demo script |

### Digital twin: feasible or not?

A lightweight **scenario twin** is feasible: current state + adoption scenarios + budget → re-optimised plan and coverage change, in seconds per state. A true operational twin (live occupancy, grid load, traffic) is not feasible by December, because India has no public session or feeder data; position it as the roadmap enabled by UBC logging and DISCOM data-sharing.

Questions the scenario twin can answer live:

- Where should the next 100 chargers in Telangana go under PM E-DRIVE site rules?
- How does 2W coverage change if the EV share of new registrations doubles by 2030?
- Which districts have gaps relative to the 1 km urban guideline, and what would closing them cost?

### Live demo sequence (about 5 minutes)

1. India view: MoP count beside high-confidence working count, per state.
2. CEA check: reported charging energy vs modelled totals by state and DISCOM.
3. Zoom to Telangana; switch between registered-only, moderate and high latent-fleet plans.
4. Show deserts, gaps relative to MoP guidelines and under-utilisation risk.
5. Enter a ₹ budget and PM E-DRIVE categories; solve live in efficiency and equity modes and show the coverage-per-crore curve.
6. Click a selected and a rejected site: evidence ledger, why here or why not here, decision stability.
7. Raise 2030 adoption; show which sites hold and which drop.
8. Overlay TGREDCO's tender clusters; explain agreements and differences.
9. Run the N-1 check on one corridor; show a single point of failure and its cheapest fix.
10. Open the delivery tracker for sanctioned Telangana sites; show stage dates and flags.
11. Export the PM E-DRIVE proposal package: site, segment, charger type, count and kW, subsidy, grid screen, security class, evidence.

**Demo narrative: the answer changes as evidence improves.** Show one area of Telangana as each layer is added:

1. Listings only: site A looks like an obvious gap.
2. After charger evidence fusion: site A is already served by effective usable capacity that was missing from one source.
3. After the CEA check and spatial priors: site B's demand holds up under all three priors and becomes the priority.
4. After budget optimisation: site C wins on served demand per rupee, and one candidate gets "no investment recommended".
5. After uncertainty runs: site C stays selected across latent-fleet plans, spatial priors and cost scenarios.

## Part XII — Competitive moat and IP landscape

The moat is the combination of India-specific inputs, validation against measured data and a sponsor-aligned output format; no single algorithm is protectable or needs to be.

### Why this beats a team using the same public data

1. **Aggregate calibration.** Demand totals are constrained by CEA's reported energy; theirs are assumed.
2. **Reconciled supply.** You plan on working capacity with confidence scores; they plan on listings.
3. **Class-aware demand.** 2W, 3W, 4W and buses get different energy, radii and charger types; they lump "EVs".
4. **Shadow-fleet correction.** You model vehicles VAHAN cannot see, with stated bands.
5. **Spike handling.** You detect enforcement-driven registration jumps; their forecasts chase them.
6. **Policy-native output.** Sites map to PM E-DRIVE categories and MoP spacing rules; theirs are generic dots.
7. **Exact, explainable optimiser.** Optimal for the stated model with a reported gap, and a reason per site; a GA gives neither.
8. **Robustness, not a point answer.** Each site carries a decision-stability score across documented parameter ranges.
9. **Backtests and a real benchmark.** Retrospective siting and the TGREDCO comparison show it works.
10. **Under-utilisation risk.** A capacity-normalised risk score shows where more subsidy is least likely to be used.
11. **Sponsor's rail.** The ingestion layer speaks Beckn/UBC, MHI's own system.
12. **Corridor flows from FASTag.** Highway demand comes from measured IHMCL counts, not guesses.

### Patent and prior-art landscape

Rule 9 says the solution must not be protected by patents, copyrights or publications. Practical reading: build from textbook methods, cite them, and avoid reproducing a specific claimed pipeline.

| Item | Type | What it claims or describes | Risk to you | How to stay clear |
| --- | --- | --- | --- | --- |
| [IN 202421003182](https://www.quickcompany.in/patents/202421003182-0b6e) (TCS address) | Indian application | Flow-based candidate scoring from daily traffic counts, road network and station constraints | Medium if corridor scoring copies it | Use published flow-refuelling formulations (Hodgson; Kuby–Lim) and cite them |
| [IN 202341076531](https://www.quickcompany.in/patents/202341076531-839c) | Indian application | Ranking merchant sites by yearly yield from demand, dwell time and cost | Low | Your objective is public coverage, not merchant yield |
| [IN 202341055303](https://gmrit.edu.in/PDFs/Patents/2023-44.pdf) | Indian application | DEA-based selection of charger location and capacity | Low | Do not use DEA scoring |
| [US10417723B2](https://patents.google.com/patent/US10417723) | US grant | Aggregating separate demand models from historical demand, POIs and traffic | Low in India; avoid the exact three-model aggregation | Single calibrated energy model |
| [US11775872B1](https://patents.google.com/patent/US11775872) | US grant | Dynamically generating a charger map for site selection | Low | Generic mapping is not the claim; avoid copying its steps |
| [EP4327258A2](https://data.epo.org/gpi/EP4327258A2) | EP application | Charge needs from mobility simulation with probability distributions, then suggested sites | Low–medium if you build a stochastic driver simulation | Use stock × energy demand, not driver simulation |
| [Gopalakrishnan et al., IJCAI 2016](https://www.ijcai.org/Abstract/16/442) | Publication | CCA demand prediction + packing-covering heuristic | Prior art to cite | Different demand basis and exact solver |

Patents are territorial and these notes are not legal advice; the point is to know what is crowded and to cite rather than replicate.

## Part XIII — Judge attack

Every hard question has an answer rooted in a data source or a test; the weakest areas are shadow-fleet multipliers and grid headroom, so those answers must state their uncertainty openly.

### 40 questions with defensible answers

| # | Question | Answer |
| --- | --- | --- |
| 1 | Isn't this just a fancy map? | The map is the output; the product is a PM E-DRIVE proposal package with evidence and a reason per site. |
| 2 | Where does your data come from? | VAHAN, MoP, CEA, OSM, OCM, IHMCL, census, state utility lists; every layer is in a source register with date and licence. |
| 3 | VAHAN is incomplete; why trust this? | We agree and quantify it: shadow-fleet bands, spike detection, and demand totals constrained by CEA's reported energy, not registrations alone. |
| 4 | What is your prediction model trained on? | The core is calibrated to CEA state energy, not trained; charger reliability uses rule-based evidence fusion until enough status labels exist. |
| 5 | What if charger sources disagree? | Each site has a confidence score; plans use confidence-weighted capacity; disagreements are reported. |
| 6 | Why would MHI or ICAT use this? | It produces PM E-DRIVE-style proposals and the annual demand map the MoP guidelines require. |
| 7 | What is genuinely novel? | Not any one algorithm (2026 Indian papers already do GIS/MCDA siting and AI forecasting); it is turning fragmented evidence into an auditable PM E-DRIVE proposal package. |
| 8 | Can it scale nationwide? | Same pipeline per state, 36 runs; H3 and DuckDB keep it laptop-sized per state. |
| 9 | What if your assumptions are wrong? | Each site shows decision stability across documented parameter ranges; fragile picks are flagged. |
| 10 | Why can't Google or OCM do this? | They show chargers to drivers; they do not model unregistered fleets, calibrate to DISCOM energy or optimise a public budget. |
| 11 | How do you know the 18% offline figure? | It covers OMC stations only (Rajya Sabha Q.3910, 27 Mar 2026); we use it as a prior for OMC sites and estimate other networks ourselves. |
| 12 | Why not a genetic algorithm? | A MIP is optimal for the stated model, with a reported gap, and is auditable; GA results vary per run. |
| 13 | How do you handle 2W vs 4W? | Separate energy parameters, coverage radii and charger types; outputs split by class. |
| 14 | What about home charging? | Captured by the public-charging share per class, fitted to CEA totals. |
| 15 | How do you validate without utilisation data? | State-level CEA hold-outs, retrospective siting backtest and a benchmark against TGREDCO's real plan. |
| 16 | CEA misses some states. | We calibrate where reported and transfer parameters with wider bands elsewhere, flagged in the UI. |
| 17 | Is grid capacity considered? | As a headroom proxy from substation lists and density; marked indicative, never a hard guarantee. |
| 18 | Where is land in your model? | Sites move up a ladder: candidate → eligible → land-confirmed → grid-screened → deployable; we only claim the rung reached. |
| 19 | How do you treat highways? | FASTag counts by class feed a flow-refuelling model with 20 km and 100 km MoP spacing checks. |
| 20 | Why H3 hexagons? | Equal-area cells near the 1 km rule, cheap joins and dedup; districts are aggregations of cells. |
| 21 | How do you avoid double counting chargers? | 50 m merge radius plus fuzzy name and operator matching; reconciled to MoP state totals. |
| 22 | What if UBC never gives access? | The open-source truth layer works now; UBC is the production path in the roadmap. |
| 23 | What did you synthesise? | Only queue parameters and any site-level session assumptions, labelled as synthetic per Rule 5. |
| 24 | Where did you use AI tools? | Entity matching, reliability classifier and optional memo text; all disclosed per Rule 6. |
| 25 | How sensitive are results to km/day? | Shown in a sensitivity ranking; calibration absorbs part of the bias at state level. |
| 26 | Isn't this the NITI handbook method? | We extend it with calibration, reliability, class splits and exact optimisation, and cite it. |
| 27 | Does it handle e-buses? | Depot charging per MoP's 240 kW rule as a separate module; Hyderabad's 2,800-bus plan is the test case. |
| 28 | What happens as EV share grows fast? | Scenario sampler re-solves; multi-stage phasing is on the roadmap. |
| 29 | How would a state officer use it? | Pick budget and site categories, solve, export the list, read the reason per site. |
| 30 | How does it evolve from Round 1? | Same pipeline: Round 1 slice, then live optimiser, robustness and validation, shown side by side. |
| 31 | How do you know a charger works right now? | We don't claim to; each charger has a functional score from the best available signal, it decays without fresh evidence, and the map shows "unknown" rather than green. |
| 32 | What if a charger reports "available" but is broken? | Where session data exists, a busy site with no sessions over a window is flagged as a suspected silent failure; quiet sites are never flagged on silence alone. |
| 33 | Who fixes broken chargers? | The operator, under its tender's uptime clause; we track status and delivery and recommend uptime and reporting clauses for new tenders. |
| 34 | What about theft and vandalism? | Operators and hosts handle them; the site-security factor lowers expected uptime at unstaffed sites, which favours staffed hosts with CCTV. |
| 35 | Several sources agree; isn't that proof? | Only if they are independent; copies of one list count once, and stale agreement still decays. |
| 36 | What if a highway is diverted? | The N-1 check removes each site or segment and tests whether the corridor stays passable; single points of failure get a stated fix. |
| 37 | How do policy changes enter the forecast? | As dated scenario switches, such as the e-2W subsidy cut; new VAHAN months refit automatically. |
| 38 | What happens after you recommend a site? | The delivery tracker follows it from sanction to use and flags delays, including grid connections past the legal deadline. |
| 39 | Is any personal data used? | No; only aggregates and public locations. The NTR data-sharing policy is the legal path for deeper VAHAN access. |
| 40 | If you find a bug later, do you start over? | No; data and method are versioned, so we fix, rerun and show which recommendations change and why. |

### Three highest-leverage improvements

1. **Ship the CEA calibration chart in Round 1.** It lifts feasibility, data strategy and novelty at once.
2. **Run the retrospective backtest before the finale.** Robustness is the biggest Round 2 weight, and a backtest is the strongest evidence.
3. **Rehearse the demo with a state officer's workflow.** Usability and presentation together are 30% of Round 2.

## Part XIV — Top 10 features and final recommendation

If our objective is maximising the probability of winning, I would build **an evidence-backed PM E-DRIVE proposal engine for Track 1**, because it fits the scheme's actual proposal workflow and makes every proposed site traceable to public evidence.

### Top 10 features

Each factor is scored 1–5 by judgement; rank = product.

| Rank | Feature | Impact | Novelty | Feasibility | Judge value | Score |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PM E-DRIVE proposal package + evidence ledger | 5 | 5 | 5 | 5 | 625 |
| 2 | Budgeted allocator with modes and coverage per crore | 5 | 4 | 5 | 5 | 500 |
| 3 | Charger evidence fusion | 5 | 4 | 4 | 5 | 400 |
| 4 | Class-specific demand (2W, 3W, 4W, bus) | 5 | 4 | 5 | 4 | 400 |
| 5 | Decision stability across parameter ranges | 4 | 4 | 4 | 5 | 320 |
| 6 | Retrospective backtest + TGREDCO benchmark | 4 | 4 | 4 | 5 | 320 |
| 7 | Latent-fleet scenario plans | 4 | 5 | 4 | 4 | 320 |
| 8 | MoP guideline-alignment check (1 / 20 / 100 km) | 4 | 4 | 5 | 4 | 320 |
| 9 | Under-utilisation risk score | 4 | 5 | 5 | 3 | 300 |
| 10 | IHMCL FASTag corridor flows | 4 | 4 | 3 | 4 | 192 |

Just outside: the UBC/Beckn adapter (high novelty and judge value, low feasibility until access is confirmed) and a reliability classifier (needs labels).

**Revision 3 additions**, scored on the same scale:

| Feature | Impact | Novelty | Feasibility | Judge value | Score |
| --- | --- | --- | --- | --- | --- |
| Delivery tracker with grid-delay flags | 5 | 4 | 4 | 5 | 400 |
| Source-independent confidence and pre-merge gates | 4 | 4 | 5 | 4 | 320 |
| N-1 corridor resilience check | 4 | 5 | 3 | 5 | 300 |
| Site-security factor | 3 | 4 | 5 | 3 | 180 |

The delivery tracker would rank joint third on the main list; the other three strengthen existing features rather than displacing any.

### The recommendation in brief

| Element | Decision |
| --- | --- |
| Architecture | Part X diagram: sources → truth + demand → CEA calibration → gap engine → optimiser + scenarios → dashboard |
| Core algorithms | H3 dedup + fuzzy matching; stock × energy demand; regularised, bounded calibration against CEA; budgeted site/configuration MIP with ε-constraint and flow-refuelling MIP in OR-Tools; peak-hour utilisation sizing approximation; Latin-hypercube decision stability |
| Data sources | VAHAN mirrors, CEA EVCS reports, MoP counts, OSM, OCM, IHMCL, census/WorldPop, VIIRS, state substation lists, TGREDCO tender |
| Novelty | Policy-native proposal output; evidence ledger; CEA aggregate constraint; latent-fleet plans; real-plan replay |
| Demo | Telangana budget run with live re-solve; separate replays of the 116-location Phase-I sanction and the 369-station tender (Part XI) |
| Validation | Hold-out calibration, temporal backtest, retrospective siting, real-plan benchmark, baselines |
| Roadmap | Round 1 slice by 30 Oct; build blocks Nov 8 – Dec 14; finale 16–18 Dec |

### Risks and fallback

| Risk | Likelihood | Effect | Mitigation / fallback |
| --- | --- | --- | --- |
| RTO → district crosswalk takes too long | High | Delays demand model | Start week 1; stay at RTO level; never invent district boundaries |
| Charger dedup quality | Medium | Wrong supply picture | Manual QA on Telangana; report precision on a hand-labelled sample |
| CEA data missing or coarse for some states | Medium | Weaker calibration there | Transfer parameters with wider bands; flag in UI |
| UBC / OpenEV access never granted | High | Loses live-status feature | Keep open truth layer; UBC stays roadmap |
| Shadow-fleet multipliers challenged | Medium | Credibility hit | Show results with and without; bands from two independent sources |
| Scope creep into consumer features | Medium | Dilutes pitch | Single user: the state nodal officer |
| Revision 3 features crowd out the core slice | Medium | Core demo weak | Core slice first; Revision 3 features follow their kill criteria |
| Delivery stage dates not public | High | Thin tracker | Show the schema with whichever dates are public; request data from the nodal agency (roadmap) |
| Operating questions pull scope into maintenance or surveillance | Medium | Dilutes pitch | Scope boundary (Revision 3): consume operating signals, never operate |

**Track 2 fallback:** if the team strongly prefers LCA, build an India-parameterised Brightway model for one e-2W battery pack, with state grid mixes and BWMR end-of-life rules, and use the ICCT finding that grid intensity, test-cycle energy and real-world adjustment drive most variance as the sensitivity backbone.

## Intelligence brief

|  |  |
| --- | --- |
| **The idea** | A proposal engine that produces PM E-DRIVE charger proposals a state nodal agency can submit, defend and audit: sites, segment, charger count and kW, subsidy, grid screen, and an evidence trail for each. |
| **Why it wins** | PM E-DRIVE has a ₹2,000 crore charging envelope, ₹688.84 crore approved for 6,562 chargers and nothing spent, no spatial targets, and nodal agencies must justify every proposed site; MoP requires annual demand mapping. MHI told Parliament in March 2026 it has not assessed charger adequacy against registered EVs. We solve that live decision in the sponsor's own terms. |
| **What everyone else will do** | Charger map, EVs-per-charger heatmap, an untargeted ML forecast, GA/k-means "optimal" sites, a chatbot. |
| **What we will do differently** | Fuse charger evidence; model local, corridor and fleet demand by segment; constrain totals with CEA; test latent-fleet plans; allocate a ₹ budget in efficiency and equity modes; attach an evidence ledger, why-here reasons and a decision-stability score to every site; count only independent sources as agreement; test corridors against single failures; track every recommendation from sanction to use. |
| **Our data advantage** | CEA EVCS energy reports, IHMCL FASTag counts, state substation lists, TGREDCO's real plan, and a UBC-ready ingestion layer. |
| **Our technical advantage** | Budgeted MIP with reported gap, coverage per crore, Latin-hypercube decision stability, evidence fusion, replay against real state plans. |
| **Our India advantage** | 2W/3W-first demand, low-speed and e-rickshaw shadow fleet, registration-drive spikes, MoP 1 / 20 / 100 km rules, PM E-DRIVE site categories. |
| **Our demo** | Telangana: CEA check → latent-fleet plans → gaps and under-utilisation risk → live budget solve with coverage-per-crore curve → why-here / why-not-here cards → TGREDCO replay → export proposal package. |
| **Our biggest risk** | Data plumbing (RTO crosswalk, dedup) eating the five build weeks. |
| **Our fallback** | Open-source truth layer without UBC; RTO-level demand if the district crosswalk slips. |
| **The 3 things to build first** | 1. The proposal-package schema and evidence ledger. 2. Telangana charger evidence fusion plus RTO-level segment demand checked against CEA by DISCOM. 3. One budgeted run in efficiency and equity modes, exported as a proposal package. |

## Sources, saturation and open items

About 35 searches across government, academic, industry, news, GitHub and patent sources; core Track 1 topics reached saturation, while Reddit/X and past Techfest material stayed thin.

### Source register (key claims)

Tiers: A official · B peer-reviewed · C recognised technical organisation · D company documentation · E journalism · F community.

| Claim | Source | Date | Tier | Confidence |
| --- | --- | --- | --- | --- |
| 29,277 public stations by state | [MoP annexure via PIB](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/aug/doc202581598101.pdf) | Aug 2025 | A | High |
| Over 29,000 stations installed | [AIR / Lok Sabha reply](https://www.newsonair.gov.in/over-29000-public-ev-charging-stations-installed-in-india-mos-bhupathiraju-srinivasa-varma) | Feb 2026 | A (reported) | High |
| 52,718 stations by July 2026 | [IEEFA via EV Infrastructure News](https://www.evinfrastructurenews.com/ev-regulations/india-needs-more-reliable-affordable-ev-charging-to-boost-adoption-ieefa) | Sep 2026 | C | Medium (definition unclear) |
| PM E-DRIVE: 6,562 sanctioned, 0 installed, no targets | [electrive citing MHI reply](https://www.electrive.com/2026/08/05/india-approves-chargers-awaits-deployment/) | Aug 2026 | E citing A | High |
| PM E-DRIVE site categories and subsidy tiers | [News On AIR](https://www.newsonair.gov.in/centre-issues-guidelines-for-rollout-of-72300-ev-charging-stations-under-pm-e-drive/) | Sep 2025 | A (reported) | High |
| MoP 1 km / 20 km / 100 km norms | [Mercom](https://www.mercomindia.com/ministry-of-power-releases-ev-charging-infrastructure-guidelines) | Sep 2024 | E citing A | High |
| CEA PCS energy FY26 1,558.69 MU, 69% heavy-duty; state and DISCOM split (primary report linked in the Verification update) | [EFY citing CEA](https://www.electronicsforyou.biz/industry-buzz/electricity-consumption-at-public-charging-stations-increase-72-year-on-year/) | Aug 2026 | E citing A | High |
| UBC launch and structure | [emobilityplus](https://emobilityplus.com/2026/08/14/pulse-energy-integrates-10000-ev-chargers-with-bhim-upi-under-unified-bharat-echarge/), [carhp](https://carhp.in/car-news/unified-bharat-e-charge-ubc-explained-india-s-answer-to-the-ev-charging-app-problem) | May–Aug 2026 | E | High |
| \~18% non-functional | [mmcm.in](https://mmcm.in/blog/ev-charging-infrastructure-in-india/) | 2026 | F | Superseded: primary is Rajya Sabha Q.3910, OMC stations only |
| Low-speed e-2W CKD imports | [EVreporter](https://evreporter.com/the-e-2w-sales-india-doesnt-track-why-should-it-bother-us/) | 2025–26 | E citing customs | Medium |
| \~4.75 lakh unregistered e-rickshaws | [JMK Research](https://jmkresearch.com/mandatory-registration-of-all-electric-rickshaws-across-states-in-india/) | 2026 | C citing industry | Medium |
| VAHAN data-quality gaps | [Down To Earth / CSE](https://www.downtoearth.org.in/air/driving-on-broken-data-why-indias-clean-air-and-ev-push-cannot-outrun-vahans-cracks) | Jun 2026 | C/E | Medium–high |
| Telangana EVs, stations, PM E-DRIVE sites | [UNI](https://www.uniindia.com/telangana-showcases-ev-charging-success-story-at-national-conference-in-bengaluru/business-economy/news/3840860.html) | May 2026 | E citing A | High |
| TGREDCO 369-station tender | [Telangana Today](https://telanganatoday.com/tg-redco-invites-tenders-for-369-public-ev-charging-stations) | Sep 2026 | E | High |
| IHMCL plaza-level FASTag counts | [IHMCL June 2026 PDF](https://ihmcl.co.in/wp-content/uploads/2026/08/June-2026.pdf) | Aug 2026 | A | High |
| Fast-charger siting review (84 studies) | [Putra et al., e-Prime](https://doaj.org/article/263a1cbd16b64e4ba52feb587923e25d) | Dec 2024 | B | High |
| Indian car LCA variance drivers | [ICCT](https://theicct.org/publication/review-of-ghg-life-cycle-assessments-of-passenger-cars-in-india-jun25/) | Jun 2025 | C | High |
| BWMR EV battery recovery targets | [IEA policy database](https://www.iea.org/policies/25166) | — | C citing A | High |
| PM E-DRIVE extension, ₹11,900 crore, component split | [PIB factsheet](https://www.pib.gov.in/FactsheetDetails.aspx?Id=151062) | Oct 2026 | A | High |
| e-2W subsidy halved to ₹5,000 | [Entrepreneur](https://india.entrepreneur.com/business-news/government-extends-pm-e-drive-scheme-till-march-31-2028-e2w-incentive-cut) | Aug 2026 | E | High |
| UBC pilot states | [MHI on X](https://x.com/MHI_GoI/status/2095490089631809683) | Sep 2026 | A | High |
| Grid connection deadlines 3 / 7 / 15 / 30 days | [Business Standard](https://www.business-standard.com/india-news/govt-tweaks-rules-for-speedy-electricity-connection-rooftop-installation-124022300594_1.html) | Feb 2024 | E citing A | High |
| CAG findings on FAME-II chargers | [Down To Earth](https://www.downtoearth.org.in/energy/cag-flags-rs-468-crore-in-fame-incentives-to-ev-makers-violating-localisation-norms) | 2026 | E citing A | High |
| VAHAN bulk data policy scrapped, June 2020 | [IFF / SaveOurPrivacy](https://saveourprivacy.in/blog/bulk-data-sharing-policy-scrapped-is-an-incremental-victory-that-requires-follow-up-action-saveourprivacy) | Jun 2020 | C | High |
| NTR data-sharing policy | [MoRTH PDF](https://morth.nic.in/sites/default/files/circulars_document/Data-Sharing-policy-20082025-merged.pdf), [S.S. Rana summary](https://ssrana.in/articles/digitization-of-transport-data-and-securing-personal-information/) | Aug–Sep 2025 | A / E | High |
| Usage-based placement from 2026 | [Municipality of Voorschoten](https://en.voorschoten.nl/oplaadpalen-elektrische-autos) | 2026 | A | High |
| Utilisation-triggered highway expansion | [China EV Home](https://chinaevhome.com/2026/02/06/china-targets-10000-ev-chargers-at-highway-service-areas-in-2026/) | Feb 2026 | E | Medium |
| California 97% uptime standard | [IEEFA feedback on Delhi EV policy](https://ieefa.org/sites/default/files/2026-05/IEEFA_Feedback%20on%20the%20draft%20Delhi%20Electric%20Vehicle%20%28EV%29%20Policy%202026%20%281%29.pdf) | May 2026 | C | High |

### Saturation by area

| Area | Status |
| --- | --- |
| Government policy and schemes | Saturated; new searches repeated the same documents |
| VAHAN access and quality | Saturated for public access; no official API found |
| Charger data sources | Near saturation; operator APIs not individually checked |
| Academic siting and forecasting | Saturated at review level; India-specific papers sampled, not exhaustive |
| LCA tools | Saturated for open tools; Indian inventory datasets not inspected |
| Patents | Sampled; not a freedom-to-operate search |
| Reddit / X / YouTube | Thin; most results were blogs and apps |
| Past Techfest / ICAT challenge | No prior edition found |

### Still UNVERIFIED (check before Round 1)

- [x] Primary source for 27,737 / 22,753: Rajya Sabha Q.3910, 27 Mar 2026; covers OMC stations only.
- [x] CEA report format: monthly, state and DISCOM, light-duty / heavy-duty / other split, \~5-month lag; 2026 issues carry no station counts.
- [x] UBC access: production hub "yet to be operationalised" (IEEFA, Sep 2026); open UEI spec and Beckn Onix allow a local test network now.
- [ ] Delhi OpenEV API still live and issuing keys (register on the portal to check).
- [ ] Count of Telangana chargers in OSM and OCM today (needs a quick export run outside this sandbox).
- [ ] Licence terms for each operator locator page before scraping.
- [x] 52,718 figure: IEEFA does not define station vs point; treat as unresolved, do not use as a station count.
- [ ] Download older CEA issues (2022–24) that still list station counts per DISCOM, to build a station-count time series.
- [ ] Which Telangana PM E-DRIVE sites have public stage dates (sanction, award, grid connection, commissioning) for the delivery tracker.
- [ ] Whether the UBC pilot reaches Telangana before the finale.
- [ ] Substation spare-capacity data from Telangana's transmission utility or DISCOMs (otherwise grid screening reads "not assessed").
- [ ] Exact VAHAN fuel labels for strong hybrids and plug-in hybrids.
- [ ] Whether research access is possible under the NTR data-sharing policy (roadmap only).
- [ ] A defensible range for battery-swapping share in e-2W/e-3W demand, or drop swapping from the menu.
