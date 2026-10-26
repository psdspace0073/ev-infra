# ADR-001: Pilot geography is Karnataka; Telangana is a future expansion geography

- Status: Accepted
- Date: 2026-10-25
- Supersedes: the "Telangana as proof-of-work geography" choice in `PROJECT_RULES.md`,
  `CHANGELOG_Rev4` (R4-02, R4-03, R4-06, R4-11, R4-20) and the Round 1 submission checklist.

## Context

Rev 3 of the deep-scan report and the Rev 4 changelog chose Telangana as the demo
geography, mainly because a real site-level plan (TGREDCO tender and PM E-DRIVE
sanction) existed to compare against. The data actually downloaded into this
repository on 24 Oct 2026 is for Karnataka (sources S01–S09 in
`configs/source_register.csv`, and the derived district table S09).

## Decision

- Karnataka is the active pilot and demo geography for Round 1 and the finale.
- Telangana is a future expansion geography in the state-by-state roadmap.
- The demand model, confidence scoring, optimiser, validation design and
  architecture do not change. Only the geography-specific inputs change.

## Karnataka-specific inputs

| Topic | Telangana (previous) | Karnataka (now) | Status |
| --- | --- | --- | --- |
| RTO codes | TS / TG prefixes | KA-xx codes | RTO list and jurisdictions not yet obtained |
| DISCOMs (CEA rows, crosswalk) | TGSPDCL, TGNPDCL | BESCOM, MESCOM, HESCOM, GESCOM, CESC | Names only; DISCOM-to-district lists not yet obtained |
| Districts | 33 | 31 current LGD districts vs 30 Census 2011 districts (Vijayanagar split from Ballari) | Verified in S06 and S09 |
| VAHAN registrations | RTO × class × month (planned) | S01 holds statewide calendar-year totals only (2022–2026), no RTO, class or month | Verified as statewide-only; an RTO × class × month export is **not** verified to exist |
| Official charger counts | 1,063 (state), 1,173 (OMC) | 6,097 public EVCS installed (MoP annexure, file S03); 6,805 reported by MHI (March 2026); Rajya Sabha OMC annexure | 6,097 present in local S03 (publication date not stated in the file). 6,805 and the OMC values: **reported, not verified** |
| Real plan for comparison | TGREDCO tender (369) and sanction (116) | Reported 1,571 PM E-DRIVE approvals; BESCOM charging portal | **Not verified.** No verified Karnataka public site-level plan is established |

## Consequences

- Real-plan agreement (R4-06 method 3, R4-19 overlap metric) is labelled
  **"method only / not evaluated"** until a Karnataka site-level plan is found
  and verified. Validation uses the other non-circular metrics.
- RTO-level demand (R4-03, R4-11) is blocked until an RTO-level VAHAN export is
  obtained. Until then only statewide totals are observed; no RTO split is invented.
- Five DISCOMs give the CEA consistency check five monthly totals instead of two.
  This does not change the R4-05 national-calibration design.
- Conflicting charger counts (6,097 vs 6,805 vs OMC values) are recorded with
  their definitions and dates, not reconciled silently.
- Historical Telangana findings in the Rev 3 report stay unchanged as reference.

## Open items

1. Obtain the Karnataka RTO list (KA codes, jurisdictions) and an RTO × class × month VAHAN export, or record that none is available.
2. Obtain DISCOM-to-district lists for BESCOM, MESCOM, HESCOM, GESCOM and CESC.
3. Find and verify the sources for 6,805 (MHI, March 2026), the Rajya Sabha OMC annexure (Karnataka rows) and the S03 publication date.
4. Investigate the reported 1,571 PM E-DRIVE approvals and the BESCOM portal as a possible real plan. Do not use either until verified.

## Amendment (2026-10-27)

- Karnataka is the project geography: all collected data, the Round 1 evidence and the
  finale demo.
- The official problem statement (`docs/reference/MIH_PS_1_compressed (1).pdf`) names no
  state. It asks for "selected states, districts, cities, or transport corridors" and a
  demonstration "for at least one representative geography". Telangana is therefore no
  longer named as the next expansion state. The roadmap expands state by state, in an
  order set by data availability.
- Open item 1 is closed (S29, S30, S31, S35; `docs/research/GAP_CLOSURE_REPORT.md`).
  Item 2 is not required for Round 1. Items 3 and 4 stay open.
- The Telangana column in the table above is history.
