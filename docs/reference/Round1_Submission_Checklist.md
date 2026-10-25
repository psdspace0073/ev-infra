# Round 1 Submission Checklist: EV Infra Map India (Track 1)

Techfest 2026-27 · MHI / ICAT EV Infra & Green Mobility AI Challenge
Source documents: problem statement PDF (MIH_PS_1) and `CHANGELOG_Rev4.md` (latest version)
Round 1 deadline: **30 October 2026** · Results: 7 November 2026 · Grand Finale: 16–18 December 2026
Prepared: 23 October 2026

> **Geography change (25 Oct 2026):** the pilot is now **Karnataka**; Telangana is a future expansion geography (repo: `docs/decisions/ADR-001-geography.md`). All active steps now describe Karnataka. Remaining Telangana references are history (the TGREDCO steps F-060 to F-068, earlier figures) or describe Telangana's future-expansion role. Source IDs in this checklist (S01–S22) are not the same as the IDs in `configs/source_register.csv`.
Language: ASD-STE100 Simplified Technical English (approximately 80%)

---

## 0. How to use this checklist

- Do the steps in each part in sequence.
- Some parts can run at the same time. The schedule table shows which parts.
- When a step is complete, put an "x" in the box.
- After each completed step, write the owner initials and the date. Example: `— AN 24 Oct`.
- If a step fails, go to Part W (contingencies). Do not stop the full plan.
- Each step has an ID (for example, `E-014`). Use the ID in the team chat and in the task sheet.
- "R4-xx" refers to the item with the same number in `CHANGELOG_Rev4.md`.

**Warning, caution and note:**

- **WARNING:** a risk of disqualification or of an invalid submission.
- **CAUTION:** a risk of lost marks, lost work or a false claim.
- **NOTE:** useful information.

### 0.1 Schedule

| Date | Parts | Gate (must be true at end of day) |
| --- | --- | --- |
| 23 Oct (evening) | A, B, C | Team ID found. Owners named. Workspace ready. |
| 24 Oct | D, E, F, G, H | Core files downloaded. First joined table works. |
| 25 Oct | I, J | Definitions frozen. Scope frozen. |
| 26 Oct | K, L | Calibration decision recorded. Reproducible slice works. |
| 27 Oct | M, N, O | Validation design, cost model and roadmap complete. |
| 28 Oct | P, Q (full draft), R | Full draft with all figures. |
| 29 Oct | S, T | Final PDF. Claim audit complete. Go/no-go decision. |
| 30 Oct | U | Submission complete before the target time. |
| 31 Oct – 7 Nov | V | Build continues. Portal and email are monitored. |

### 0.2 Critical path

The steps below control the full schedule. Do these first.

1. A-005: find the Team ID.
2. C-001 to C-005: name the owners.
3. F (VAHAN, chargers, CEA, boundaries): download the core data.
4. H: make the first join.
5. I: freeze the definitions.
6. L: make the reproducible slice.
7. Q: write the submission.
8. U: submit (team leader only).

> **CAUTION:** The changelog has a review freeze. Do not start a new review round. Accept a new item only if it unblocks the build or fixes a factual error.

---

## Part A. Registration, eligibility and the portal (23 Oct, evening)

> **WARNING:** Only the team leader can submit. A submission from a different member is not valid. The team can submit one time only. More than one submission can cause disqualification.

### A.1 Team ID and registration

- [ ] A-001 Open techfest.org in a browser.
- [ ] A-002 Log in with the team leader account.
- [ ] A-003 Find the registration record for the "EV Infra & Green Mobility AI Challenge".
- [ ] A-004 Make sure that the record is for this competition and not for a different Techfest event.
- [ ] A-005 Record the Team ID in the team sheet (00_admin).
- [ ] A-006 Record the team name exactly as registered. Keep the same spelling, capital letters and spaces.
- [ ] A-007 Record the email address of the team leader account.
- [ ] A-008 Record the phone number of the team leader as registered.
- [ ] A-009 If the record shows a track field, make sure that it shows Track 1 (EV Infra Map India).
- [ ] A-010 If you cannot find a Team ID, write a query in the Doubt section of the Techfest Competition Portal immediately.

> **NOTE:** The registration deadline was 15 October 2026. Rule 1 says that each registered team gets a Team ID. Rule 11 says: send all queries through the portal Doubt section. Rule 12 says: queries by email are not accepted.

- [ ] A-011 If you wrote a query, record the date and time of the query.
- [ ] A-012 If you wrote a query, examine the Doubt section two times each day until you get an answer.

### A.2 Team composition and eligibility

- [ ] A-013 Count the team members. Make sure that the count is 2 to 5.
- [ ] A-014 For each member, record the full name.
- [ ] A-015 For each member, record the institution (full official name).
- [ ] A-016 For each member, record the programme (UG or PG), the department and the year.
- [ ] A-017 For each member, record the email address and the phone number.
- [ ] A-018 Make sure that each member is a current undergraduate or postgraduate student.
- [ ] A-019 Make sure that no member is also a member of a different team in this competition.

> **WARNING:** An individual cannot be a member of more than one team.

- [ ] A-020 Make sure that the team submits in Track 1 only.
- [ ] A-021 Make sure that the team leader is the person who will do the submission.
- [ ] A-022 Make sure that the team leader is available on 29 and 30 October.
- [ ] A-023 Make sure that the team leader has a working laptop for 30 October.
- [ ] A-024 Make sure that the team leader has a backup internet connection (for example, a phone hotspot).
- [ ] A-025 Ask each member for permission to show their name and contact details in the submission.
- [ ] A-026 Decide which contact details to show. Minimum: name, institution, email and phone of the team leader.
- [ ] A-027 Ask each member if they can attend the Grand Finale at IIT Bombay on 16–18 December (Rule 7).
- [ ] A-028 If a member cannot attend, record this. Tell the team leader.
- [ ] A-029 If the team is cross-college, record the institution of each member separately.

### A.3 Portal, form and deadline details

- [ ] A-030 Open the Doubt section of the portal.
- [ ] A-031 Read all questions and answers in the Doubt section.
- [ ] A-032 Record each answer that changes the format, the length, the file type, the deadline time or the content.
- [ ] A-033 Find the exact deadline time on 30 October (hour, minute and time zone).
- [ ] A-034 Record the deadline time in the team sheet.
- [ ] A-035 If the portal does not show a deadline time, write a query in the Doubt section.
- [ ] A-036 Until you get an answer, use 30 October, 12:00 IST as the team deadline.
- [ ] A-037 Find the Round 1 submission form.
- [ ] A-038 Record the accepted file types (for example, PDF only).
- [ ] A-039 Record the maximum file size.
- [ ] A-040 Record the number of files that the form accepts.
- [ ] A-041 Record if the form wants one combined file or separate files (team information, methodology, roadmap).
- [ ] A-042 Record all text fields in the form and their character limits.
- [ ] A-043 Record if the form accepts links (GitHub, Google Drive, video).
- [ ] A-044 Take screenshots of all form pages. Save them in 00_admin.
- [ ] A-045 If the form is not open, set a daily reminder to examine it.
- [ ] A-046 Make sure that the team leader can log in from the device that they will use on 30 October.
- [ ] A-047 Record the password-recovery method of the team leader account.
- [ ] A-048 Make sure that the team leader can get the one-time password or recovery email, if the portal uses one.

### A.4 Official communication

- [ ] A-049 Add siddhi@techfest.org to the contacts of the team leader email account.
- [ ] A-050 Make sure that email from techfest.org does not go to the spam folder.
- [ ] A-051 Tell each member to examine the registered email each day until 7 November.
- [ ] A-052 Tell each member to examine techfest.org for updates each day (Rule 10).
- [ ] A-053 Put these dates in the team calendar: 30 Oct (Round 1 deadline), 7 Nov (results), 16–18 Dec (finale), 31 Dec (prize form deadline).

---

## Part B. Workspace and tools (23 Oct, evening)

### B.1 Shared folder

- [ ] B-001 Make one shared team folder. Name: `TF26_EVInfra_R1`.
- [ ] B-002 Make these subfolders: `00_admin`, `01_brief`, `02_plan`, `03_data_raw`, `04_data_resolved`, `05_outputs`, `06_figures`, `07_submission`, `08_archive`.
- [ ] B-003 Put the problem statement PDF in `01_brief`.
- [ ] B-004 Put the Rev 3 plan and `CHANGELOG_Rev4.md` in `02_plan`.
- [ ] B-005 Give edit access to all members.
- [ ] B-006 Agree the file name rule: `YYYYMMDD_source_description_vN.ext`. Example: `20261024_vahan_TG_rto_class_month_v1.xlsx`.
- [ ] B-007 Agree that no member deletes a raw file. Move old files to `08_archive`.

### B.2 Repository

- [ ] B-008 Make a private Git repository. Name: `tf26-evinfra`.
- [ ] B-009 Add all members as collaborators.
- [ ] B-010 Make these folders: `/data/raw`, `/data/resolved`, `/data/outputs`, `/src`, `/notebooks`, `/config`, `/docs`, `/figures`.
- [ ] B-011 Add a `.gitignore` file. Exclude files larger than 50 MB, environment folders and secret keys.

> **CAUTION:** GitHub does not accept single files larger than 100 MB. Keep large raw files in the shared folder. Record their hash in the repository.

- [ ] B-012 Add a `README.md`: project name, track, folder map and run instructions.
- [ ] B-013 Add `/config/settings.yaml`. All parameters and thresholds go in this file (method versioning, M11).
- [ ] B-014 Add `/docs/source_register.csv` (Part E uses it).
- [ ] B-015 Add `/docs/decision_log.md`. Record each frozen decision with the date, the owner and the reason.
- [ ] B-016 Keep the repository private until the Round 1 results.
- [ ] B-017 Never put an API key in the repository. Use a local `.env` file.

### B.3 Software

- [ ] B-018 Install Python 3.11 or a later version on each laptop that runs code.
- [ ] B-019 Make `requirements.txt` with: pandas, geopandas, shapely, pyproj, h3, duckdb, pyarrow, rapidfuzz, requests, matplotlib, folium, openpyxl, pulp (or ortools), pdfplumber.
- [ ] B-020 Make a virtual environment. Install `requirements.txt`.
- [ ] B-021 Make sure that each code owner can run: `python -c "import geopandas, h3, duckdb, rapidfuzz"`.
- [ ] B-022 Record the version of each package (`pip freeze > requirements.lock.txt`).
- [ ] B-023 Install QGIS on minimum one laptop (for visual examination of maps).
- [ ] B-024 Make sure that one laptop can run Docker, if you plan OSRM routing (Part I). If no laptop can run Docker, record this.

### B.4 Logs for the disclosure (Rule 4 and Rule 6)

> **WARNING:** Rule 6: the team must disclose the use of AI tools, third-party software, external datasets and pre-built frameworks.

- [ ] B-025 Make `/docs/ai_use_log.csv`. Columns: date, member, tool, purpose, what output the team used, what the team changed.
- [ ] B-026 Record all AI use since the start of the project (research, planning, reviews, text).
- [ ] B-027 From now, record each AI use on the same day.
- [ ] B-028 Make `/docs/software_log.csv`. Columns: name, version, licence, purpose.
- [ ] B-029 Make `/docs/dataset_log.csv`, or use the source-access matrix (Part E) for datasets.

### B.5 Team process

- [ ] B-030 Make a task sheet. Columns: step ID, task, owner, due date, status, evidence link.
- [ ] B-031 Copy items R4-01 to R4-20 into the task sheet.
- [ ] B-032 Agree a daily 15-minute meeting, 24–30 October. Record the time.
- [ ] B-033 Make a team chat group for urgent problems.
- [ ] B-034 Agree one rule: each member reports a blocker within 1 hour of finding it.

---

## Part C. Owners (23 Oct, evening; blocker for all other parts)

- [ ] C-001 Name one owner for **data**: R4-01, R4-02, R4-03, R4-04, data part of R4-11.
- [ ] C-002 Name one owner for **modelling**: R4-05, R4-15, R4-16, thresholds in R4-19.
- [ ] C-003 Name one owner for **validation**: R4-06, R4-10, R4-18, metrics in R4-19.
- [ ] C-004 Name one owner for **UI, maps and figures**: map and site card in R4-11, R4-17, Part R.
- [ ] C-005 Name one owner for **submission and portal**: R4-08, R4-09, R4-12, R4-13, R4-14, R4-20, Part U.
- [ ] C-006 If the team has fewer than five members, give two roles to some members. Record this.
- [ ] C-007 Write the owner names in the Owner column of `CHANGELOG_Rev4.md`.
- [ ] C-008 Write the owner names in the task sheet.
- [ ] C-009 For each part of this checklist, name one reviewer who is not the owner.
- [ ] C-010 Name a backup person for each owner.
- [ ] C-011 Agree the review freeze (see section 0.2).
- [ ] C-012 Agree the time of the go/no-go meeting on 29 October.
- [ ] C-013 Agree the target submission time on 30 October. Recommended: before 12:00 IST.
- [ ] C-014 Record all decisions from Part C in `/docs/decision_log.md`.

---

## Part D. Read and map the problem statement (24 Oct, morning, all members)

### D.1 Read

- [ ] D-001 Each member reads the full problem statement PDF.
- [ ] D-002 Each member reads `CHANGELOG_Rev4.md`.
- [ ] D-003 Each member reads the summary and the "Revision 3" section of the Rev 3 plan.

### D.2 Map the Track 1 objective to the methodology

- [ ] D-004 List the five Track 1 objective points from the PDF.
- [ ] D-005 Map each point to one methodology section. Use this map:

| PDF objective point | Methodology section |
| --- | --- |
| Integrates and maps existing public charging infrastructure | Charger evidence layer (core stage 1) |
| Uses VAHAN data to assess EV population vs charging | Demand by class at RTO level (core stage 2) |
| Identifies underserved areas and gaps | Gap analysis, capacity adequacy (core stage 3) |
| Estimates future charging requirements | Adoption scenarios (M10), budget-constrained selection (core stage 4) |
| Supports evidence-based planning by MHI, ICAT, states | Proposal export, evidence ledger (core stage 5) |

- [ ] D-006 Make sure that the submission mentions each objective point by name.

### D.3 Map the data layers

- [ ] D-007 List the seven data layers in the PDF.
- [ ] D-008 For each layer, record the source that you use, or the reason that you do not use it in Round 1.

| PDF data layer | Source in this plan | Round 1 status target |
| --- | --- | --- |
| EV population and vehicle registration | VAHAN (dashboard or India Data Portal) | Verified |
| Existing EV charging infrastructure | OSM, Open Charge Map, state or DISCOM list (if verified), MoP and state counts | Verified |
| Geographic and administrative boundaries | DataMeet, LGD codes | Verified |
| Road and mobility network | OSM roads (Geofabrik); IHMCL for corridors | Verified (roads); Planned (IHMCL) |
| Demographic and economic activity | WorldPop; Census 2011 | Verified (WorldPop) |
| Electricity infrastructure | CEA EVCS report; DISCOM areas; substation data | Verified (CEA); Planned (substations) |
| Supporting contextual information | OSM points of interest for candidate sites | Verified or Planned |

- [ ] D-009 Note: the PDF allows public, open-source, sample or synthetic data. The PDF says: document all sources and assumptions.

### D.4 Map the deliverables and the rules

- [ ] D-010 List the seven Track 1 expected deliverables.
- [ ] D-011 Make sure that each deliverable has a row in the R4-20 deliverable map.
- [ ] D-012 List the three Round 1 contents: team information, methodology document, implementation roadmap.
- [ ] D-013 List the four roadmap contents that the PDF names: data sources, tools and technologies, development stages, the path to the final prototype before the finale.
- [ ] D-014 Note: the PDF says the submission "should be concise". Set the target length: 10–12 pages plus an appendix.
- [ ] D-015 Record the Round 1 criteria and weights: problem understanding 25, feasibility 25, innovation 20, roadmap 20, data strategy 10.
- [ ] D-016 Read the Round 2 rules. Note: finalists must build "in line with" the Round 1 roadmap. The roadmap is a commitment.
- [ ] D-017 Note: in Round 2, the team must show how the solution evolved from the Round 1 roadmap. Keep all versions (Part V).
- [ ] D-018 Read the eight items of the "Suggested Solution Approach". Map each item to a submission section (Part Q).
- [ ] D-019 Note the sentence: solutions are judged on intelligence, transparency and defensibility, not on premium data.
- [ ] D-020 Read General Rules 1–12. Make a compliance table: rule number, what the team does, where the evidence is.

| Rule | What the team does | Evidence |
| --- | --- | --- |
| 1 Team ID | Team ID on cover page | A-005 |
| 2 Decisions final | No action | — |
| 3 Original work | Own text, code, figures | Part T |
| 4 Attribution | Source register and references | Part E, Q.13 |
| 5 Synthetic data identified | Data status labels | Part G |
| 6 Disclosure of AI, software, datasets, frameworks | Disclosure section | Q.12 |
| 7 Finale availability | Member confirmation | A-027 |
| 8 Late entries | Submit early | Part U |
| 9 Original, not protected | Cite methods; no copied pipelines | T-010, T-011 |
| 10 Updates on website | Daily examination | A-052 |
| 11 Queries via Doubt section | All queries there | A-010 |
| 12 Official email | Contact saved | A-049 |

- [ ] D-021 Read the recognition section. Note: the "municipal / ULB charging-infrastructure planning" pathway supports the choice of a planning user.


---

## Part E. Source-access matrix (R4-01, 24 Oct)

### E.1 Make the matrix

- [ ] E-001 Make the matrix as a sheet and as `/docs/source_register.csv`.
- [ ] E-002 Add these columns: ID, dataset name, publisher, exact URL, format, geographic level, time period covered, last update date of the source, licence or terms, access method, status (Verified / Planned / Synthetic), date checked, checked by, local file name, row or feature count, file hash (SHA-256), lineage group, fallback, notes.
- [ ] E-003 Add one row for each source in the table in E.2.

### E.2 Sources to enter

| ID | Source | Use | Priority |
| --- | --- | --- | --- |
| S01 | VAHAN dashboard, Karnataka, RTO × class × fuel × month (not verified to exist; repo file is statewide totals only) | EV demand | P0 |
| S02 | India Data Portal VAHAN mirror | Fallback for S01 | P0 |
| S03 | VAHAN state totals by class, CEA-reporting states | National calibration (R4-05) | P1 |
| S04 | CEA EVCS monthly reports (minimum last 12 issues) | Consistency check, calibration | P0 |
| S05 | MoP state station counts (PIB annexure, Aug 2025) | Reconciliation | P0 |
| S06 | Rajya Sabha Q.3910 annexure (OMC stations, 27 Mar 2026) | Reconciliation, OMC prior | P0 |
| S07 | Karnataka figure 6,805 (reported MHI, March 2026; not verified) | Reconciliation | P0 |
| S08 | OpenStreetMap `amenity=charging_station` (Overpass) | Charger records | P0 |
| S09 | Open Charge Map API | Charger records | P0 |
| S10 | BEE EV Yatra | Charger records (if terms allow) | P1 |
| S11 | Karnataka real plan, if verified (reported 1,571 PM E-DRIVE approvals; BESCOM portal). Earlier: TGREDCO tender and sanction | Charger plans, benchmark | P0 |
| S12 | DataMeet district boundaries | Geography | P0 |
| S13 | Local Government Directory (LGD) district codes | Join keys | P1 |
| S14 | Karnataka RTO list (KA codes) and jurisdictions (Transport Department) | RTO crosswalk | P0 |
| S15 | BESCOM, MESCOM, HESCOM, GESCOM and CESC service areas | DISCOM crosswalk | P0 |
| S16 | WorldPop population grid | Population, spreading | P0 |
| S17 | OSM road network (Geofabrik, India southern zone) | Routing, accessibility | P1 |
| S18 | OSM points of interest (fuel, government, bus depot, metro, mall) | Candidate sites | P1 |
| S19 | PM E-DRIVE charging infrastructure guidelines | Site categories, subsidy rates, caps | P0 |
| S20 | MoP EV charging guidelines 2024 | Spacing rules (1 km, 20 km, 100 km) | P0 |
| S21 | Electricity (Rights of Consumers) Amendment Rules 2024 | Connection deadlines (tracker) | P1 |
| S22 | NITI / WRI charging handbook method | Baseline (R4-06) | P0 |
| S23 | IHMCL FASTag monthly counts | Corridors (stretch) | P2 |
| S24 | Substation or spare-capacity data, Karnataka | Grid screening | P2 |
| S25 | UBC / UEI; Delhi OpenEV | Live status | Planned only |

> **NOTE (25 Oct 2026): source IDs.** The IDs above are checklist IDs. The canonical IDs are in `configs/source_register.csv`; data files, code and outputs use them. In repo documents, write a checklist ID as "checklist S08". Crosswalk for sources the repo holds or has checked:
>
> | Checklist ID | Register ID | Status |
> | --- | --- | --- |
> | S01 VAHAN dashboard | S01 | acquired_provenance_incomplete: statewide calendar-year totals only |
> | S02 India Data Portal VAHAN | S14 | verified_but_not_acquired: no download URL, licence not specified |
> | S05 MoP state counts | S03 | verified_and_acquired: PIB annexure, Aug 2025 (Karnataka 6,097) |
> | (none) MHI Lok Sabha reply, 16 Dec 2025 | S17 | verified_and_acquired (Karnataka 6,096) |
> | S08 OSM chargers | S02, S10 (inventory S11, district join S12) | verified_and_acquired |
> | S09 Open Charge Map | S13 | inaccessible: API key required (HTTP 403 without key) |
> | S10 BEE / EV Yatra station list | S15 (staging S16, Karnataka rows S18, sites S19) | verified_and_acquired: BEE location-wise PDF, data till 26 Oct 2025 |
> | S12 DataMeet boundaries | S20 | acquired_provenance_incomplete: download URL and licence not recorded |
> | S13 LGD district codes | S06 | verified_and_acquired |
> | S17 OSM roads | S05; S21 (extract), S23 (layers) | S05 road centre points only; S21 verified_and_acquired (Karnataka PBF); S23 derived roads_major lines |
> | S18 OSM points of interest | S21, S22 (cross-check), S23 | S23 derived: settlements, amenities, parking, fuel, power, charging stations |
> | (none) Census 2011, NFHS, Mission Antyodaya, district table | S04, S07, S08, S09 | S04 acquired_provenance_incomplete; S07, S08 verified_and_acquired; S09 derived |
>
> Status values: verified_and_acquired, acquired_provenance_incomplete (file held, origin not fully recorded), verified_but_not_acquired, inaccessible, derived. Details: `docs/research/DATA_SOURCE_RECOVERY_REPORT.md`.

### E.3 Procedure for each source (do E-004 to E-020 for each row)

- [ ] E-004 Open the exact URL.
- [ ] E-005 Make sure that the page belongs to the publisher (official domain or known mirror).
- [ ] E-006 Record the format (PDF, CSV, XLSX, JSON, GeoJSON, API, raster).
- [ ] E-007 Record the geographic level (point, RTO, district, DISCOM, state, grid cell).
- [ ] E-008 Record the time period that the data covers.
- [ ] E-009 Record the date of the last update shown by the source.
- [ ] E-010 Find the licence or the terms of use. Record them.
- [ ] E-011 If the terms forbid reuse or automated collection, set status to "Not used" and record the reason.
- [ ] E-012 Record the access method (download, API with key, manual copy, PDF table).
- [ ] E-013 Do a test download or a test API call.
- [ ] E-014 If the test works, set status to "Verified" after Part F is complete.
- [ ] E-015 If the test fails, set status to "Planned" and write the error.
- [ ] E-016 Record the date checked and the name of the member.
- [ ] E-017 Write the fallback for this source.
- [ ] E-018 Write the lineage group (where the records come from first). Example: an aggregator that copies EV Yatra goes in the EV Yatra group.
- [ ] E-019 Write any field that is missing or not reliable.
- [ ] E-020 Get a second member to examine the row.

> **CAUTION:** Do not describe a source as available because its documentation exists. "Verified" means: a member downloaded it and opened it.

> **CAUTION:** Do not use Google Maps or PlugShare data. Their terms do not allow a derived database.

---

## Part F. Download the core data (R4-02, 24 Oct)

> **NOTE:** For each file: save it in `03_data_raw` without changes, record the retrieval date, record the row count, and compute the SHA-256 hash. Example command: `sha256sum filename`.

### F.1 VAHAN, Karnataka (S01, S02)

> **CAUTION:** The VAHAN file in the repo (register S01) has statewide calendar-year totals only (2022–2026). It has no RTO, class or month field. Do not claim that an RTO × vehicle class × month export exists until a member downloads and opens one.

- [ ] F-001 Open the VAHAN dashboard (vahan.parivahan.gov.in/vahan4dashboard).
- [ ] F-002 Select state: Karnataka.
- [ ] F-003 Find the RTO filter. Record the list of all Karnataka RTOs that the dashboard shows.
- [ ] F-004 Record the RTO codes (KA-xx). Record any RTO that the dashboard shows with a different or old code.
- [ ] F-005 Select the axes: vehicle class (or vehicle category) and month.
- [ ] F-006 Select the fuel filter. Record the exact names of all electric fuel labels (for example, ELECTRIC(BOV), PURE EV).
- [ ] F-007 Record the exact names of the hybrid labels (strong hybrid, plug-in hybrid). This closes an open item in the plan.
- [ ] F-008 Select the years: minimum January 2023 to the latest complete month.
- [ ] F-009 Download the table for each RTO, or for the state with an RTO split, if the dashboard allows it.
- [ ] F-010 If the dashboard shows a CAPTCHA, do the downloads by hand. Do not use an automated tool against the CAPTCHA.
- [ ] F-011 If the dashboard does not work, download the same data from India Data Portal (S02).
  > **NOTE (25 Oct):** the India Data Portal VAHAN package (register S14) has no download URL in its CKAN record and its licence is not specified. RTO-level data is not obtained yet.
- [ ] F-012 Record which source (S01 or S02) gave each file.
- [ ] F-013 Open each file. Make sure that it has the state, the RTO, the class, the fuel, the month and the count.
- [ ] F-014 Record the total number of rows.
- [ ] F-015 Compute the total EV registrations for Karnataka for one year.
- [ ] F-016 Compare this total with the statewide totals already in the repo (register S01, calendar years 2022–2026). Record the difference. (The Telangana figure 91,572 for FY2025-26 is history only.)
- [ ] F-017 If the difference is large, record the probable reason (period, classes, fuel labels). Do not change the data.
- [ ] F-018 Record the latest month that is complete.

### F.2 VAHAN state totals (S03, for R4-05)

- [ ] F-019 Get the list of states in the latest CEA EVCS report (S04).
- [ ] F-020 For each of these states, download EV registrations by class and month from VAHAN, state level only.
- [ ] F-021 Use the same months as the CEA data.
- [ ] F-022 Record states where class data is missing or not clear.
- [ ] F-023 Stop this task at 18:00 on 25 October if it is not complete. Record the status for the R4-05 decision.

### F.3 CEA EVCS reports (S04)

- [ ] F-024 Open the CEA electric vehicle charging reports page (cea.nic.in).
- [ ] F-025 Download the latest monthly report.
- [ ] F-026 Download the previous 11 monthly reports (12 months minimum).
- [ ] F-027 For each report, record the month that the data covers. Note: the data has an approximate 5-month lag.
- [ ] F-028 Find the Karnataka rows. Record the DISCOM names as the report shows them (BESCOM, MESCOM, HESCOM, GESCOM, CESC).
- [ ] F-029 Record the three energy columns: "excluding heavy duty", "heavy duty PCS", "other than PCS".
- [ ] F-030 Record the unit (MU). Note: 1 MU = 1,000,000 kWh.
- [ ] F-031 Extract the Karnataka rows into a CSV with: month, DISCOM, column name, value, unit, report file name, page number.
- [ ] F-032 Do a check of the extraction: compare 3 values with the PDF by eye.
- [ ] F-033 If you need national calibration, extract the rows for all reporting states in the same way.
- [ ] F-034 Record states and DISCOMs that do not report.

### F.4 Official counts (S05, S06, S07)

- [x] F-035 MoP state count annexure: the Karnataka value 6,097 ("public charging stations installed as per inputs received from Ministry of Power", national total 29,277) is in the repo file S03. The file does not state its date. Find the publication date (reported as PIB, August 2025) and record it. — CC 25 Oct: S03 is byte-identical to static.pib.gov.in/.../2025/aug/doc202581598101.pdf (Last-Modified 1 Aug 2025). Question number and reply date still not identified.
- [x] F-035a MHI Lok Sabha written reply, PIB release 2204635, 16 Dec 2025: Karnataka 6,096 EVCS installed during the last five years (751 fast, 5,345 slow); India 29,151. — CC 25 Oct, register S17
- [ ] F-036 Download the Rajya Sabha Q.3910 annexure. Record the Karnataka OMC installed and operational values. (Not verified yet.)
- [ ] F-037 Find the source of the reported Karnataka figure 6,805 (MHI, March 2026). Record the date, the publisher and the definition. Until found, label it "reported, not verified".
- [ ] F-038 For each count, record: date, stations or charge points, public only or all, installed or operational.
- [ ] F-039 Write one sentence for each count: "This number counts ...".

> **CAUTION:** 6,097 (MoP) and 6,805 (MHI) differ, and the OMC values may use a third definition. Treat each difference as a definition or date difference until you can show otherwise. (Telangana history: 1,173 OMC operational vs 1,063 state.)

### F.5 OpenStreetMap chargers (S08)

- [x] F-040 Open overpass-turbo.eu. — register S02 (overpass-turbo export, 24 Oct)
- [x] F-041 Write a query for `amenity=charging_station` (nodes and ways) in the Karnataka area. — nodes, ways and relations; CC 25 Oct
- [x] F-042 Save the query text in `/src/queries/osm_chargers_ka.overpassql`. — CC 25 Oct
- [x] F-043 Run the query. — register S10 via `src/evinfra/ingestion/fetch_osm_chargers.py`; CC 25 Oct
- [x] F-044 Export the result as GeoJSON. — S02 is GeoJSON; S10 is Overpass JSON with element metadata
- [x] F-045 Record the feature count. — 67 (same 67 elements in S02 and S10)
- [x] F-046 Record which tags are present (operator, capacity, socket types, output, opening_hours, access). — in register S10: no socket or output tags; access on 16 of 67
- [x] F-047 Record the OSM licence (ODbL) and the attribution text. — register S10

### F.6 Open Charge Map (S09)

> **NOTE (25 Oct):** blocked. The API returns HTTP 403 without a key (register S13).

- [ ] F-048 Register for an Open Charge Map API key.
- [ ] F-049 Put the key in `.env`. Do not put it in the repository.
- [ ] F-050 Request all points for country code IN inside a Karnataka bounding box.
- [ ] F-051 Save the raw JSON without changes.
- [ ] F-052 Record the record count.
- [ ] F-053 Record the licence and the data provider of each record. Note: Open Charge Map records can have different licences.
- [ ] F-054 Remove from use any record whose licence does not allow reuse. Keep it in raw, with a flag.

### F.7 EV Yatra (S10)

> **NOTE (25 Oct):** the BEE location-wise list (register S15) is acquired: 39,641 rows for India, 8,246 for Karnataka, with coordinates. Its licence is not stated. EV Yatra portal terms are still unchecked.

- [ ] F-055 Open the EV Yatra portal.
- [ ] F-056 Read the terms of use.
- [ ] F-057 If the terms allow it, record the Karnataka station list or the counts by district.
- [ ] F-058 If no bulk export exists, record only what you can copy legally. Record the method.
- [ ] F-059 If the terms do not allow reuse, set status to "Not used". Record the reason.

### F.8 Real plans (S11): Karnataka

> **NOTE:** No verified Karnataka public site-level plan is established yet. Real-plan agreement is "method only / not evaluated" until one is found and verified. F-060 to F-068 below were written for TGREDCO (Telangana, now a future geography) and are kept for reference.

- [ ] F-060a Investigate the reported 1,571 PM E-DRIVE approvals for Karnataka. Record the source, date, unit (chargers, stations or sites) and whether a site list exists.
- [ ] F-060b Investigate the BESCOM charging portal. Record the URL, terms of use and whether it gives a site-level list or plan.
- [ ] F-060c If neither gives a verified site-level plan, record "no verified Karnataka plan" in the decision log. Do not invent one.

- [ ] F-060 Download the TGREDCO tender documents (369 stations: 200 Hyderabad in 6 clusters, 169 across 5 districts).
- [ ] F-061 Download any document for the PM E-DRIVE Phase-I sanction (116 locations).
- [ ] F-062 Extract the site list: name, address, cluster, district, charger type, count.
- [ ] F-063 Record the uptime requirement in the tender (the plan says 95%).
- [ ] F-064 Record each date in the documents (issue, bid, award). These dates feed the delivery tracker.
- [ ] F-065 Geocode the sites. Record the geocoding method.
- [ ] F-066 Give each geocoded site a geocode confidence: exact, street, locality, district.
- [ ] F-067 Do not call the 116 locations "116 chargers" or "116 sites".
- [ ] F-068 Keep the sanction and the tender as two separate datasets.

### F.9 Boundaries and crosswalks (S12, S13, S14, S15)

- [ ] F-069 Download district boundaries for Karnataka from DataMeet. (Census 2011 boundaries are in the repo.)
- [ ] F-070 Count the districts. Census 2011 has 30 Karnataka districts; current LGD has 31 (Vijayanagar split from Ballari). Record the boundary year and the split rule.
- [ ] F-071 Record the DataMeet licence (CC BY 4.0) and the attribution text.
- [ ] F-072 Download LGD district codes for Karnataka. (In the repo: register S06.)
- [ ] F-073 Get the list of Karnataka RTOs (KA codes) and their jurisdictions from the Karnataka Transport Department.
- [ ] F-074 Get the list of districts (or circles) served by BESCOM, MESCOM, HESCOM, GESCOM and CESC.
- [ ] F-075 Record districts or circles that more than one DISCOM serves.
- [ ] F-076 Record the source and date of each list.

### F.10 Population, roads and points of interest (S16, S17, S18)

- [ ] F-077 Download the WorldPop population grid for India (latest year available, 100 m).
- [ ] F-078 Record the year, the method (constrained or unconstrained) and the licence.
- [ ] F-079 Clip the grid to Karnataka. Save the clip in `04_data_resolved`.
> **NOTE (25 Oct):** a Karnataka-only extract replaces the southern-zone file (register S21, OSM France, data 2026-10-23T02:09:05Z). Layers are in S23. Geofabrik has no state extract.

- [x] F-080 Download the OSM extract for the India southern zone from Geofabrik. — CC 25 Oct: Karnataka extract instead (S21)
- [x] F-081 Record the extract date. — 2026-10-23T02:09:05Z (S21 manifest)
- [ ] F-082 Extract points of interest for candidate sites: `amenity=fuel`, government offices, bus stations, metro stations, malls, parking. — partly done: fuel, parking and all other amenities in S23; malls (shop=mall) not extracted yet
- [x] F-083 Save each category as a separate file. — S23 GeoJSON layers

### F.11 Policy documents (S19, S20, S21, S22)

- [ ] F-084 Download the PM E-DRIVE charging infrastructure guidelines from the MHI website.
- [ ] F-085 Download the MoP EV charging guidelines 2024.
- [ ] F-086 Download the Electricity (Rights of Consumers) Amendment Rules 2024.
- [ ] F-087 Download the NITI / WRI handbook that describes the grid-cell planning method.
- [ ] F-088 Save each document in `03_data_raw/policy`.
- [ ] F-089 Record the title, the date and the URL of each document.

### F.12 After all downloads

- [ ] F-090 Compute the SHA-256 hash of each raw file.
- [ ] F-091 Record each hash in the source register.
- [ ] F-092 Record the row or feature count of each file.
- [ ] F-093 Commit the source register to the repository.
- [ ] F-094 Make a backup copy of `03_data_raw` in a second location.

---

## Part G. Data status labels (R4-04, 24 Oct)

- [ ] G-001 Give each source in the register one status: Verified, Planned, Synthetic or Not used.
- [ ] G-002 Verified means: downloaded, opened and checked by a member.
- [ ] G-003 Planned means: the source exists but the team did not get it yet.
- [ ] G-004 Synthetic means: made by the team for a demonstration. Document how (Rule 5).
- [ ] G-005 Set UBC, UEI and Delhi OpenEV to "Planned".
- [ ] G-006 Set substation capacity data to "Planned" unless a member downloaded it.
- [ ] G-007 Set site-level session data to "Planned" (no source is known for Karnataka).
- [ ] G-008 If the team uses any synthetic value, give it a "SYN-" ID and a description.
- [ ] G-009 Make sure that each number in the submission comes from a source with a status.
- [ ] G-010 Do not describe a "Planned" source as working in any text, figure or slide.

---

## Part H. The first join (R4-03, 24 Oct)

### H.1 RTO crosswalk

- [ ] H-001 Make a table: RTO code, RTO name, district (LGD code), DISCOM.
- [ ] H-002 Fill the table from F-073 to F-075.
- [ ] H-003 Record RTOs that cover more than one district.
- [ ] H-004 Record districts that have more than one RTO.
- [ ] H-005 If an RTO maps to more than one district, keep the RTO as the unit. Do not invent a split.
- [ ] H-006 If an RTO maps to two DISCOMs, record it. Choose a rule and write it in the decision log.
- [ ] H-007 Get a second member to examine the crosswalk.
- [ ] H-008 Save the crosswalk as `/data/resolved/ka_rto_crosswalk_v1.csv`.

> **NOTE:** H.1 needs the KA RTO list (F-073) and the DISCOM lists (F-074). Neither is available yet.

### H.2 Charger records

- [ ] H-009 Load the charger records from S08, S09, S10 (if used) and S11 into one table.
- [ ] H-010 Give each record: source ID, source record ID, lineage group, retrieval date.
- [ ] H-011 Do the pre-merge checks (M2 gate) for each source:
  - [ ] H-011a Coordinates inside India and inside Karnataka. Quarantine the others.
  - [ ] H-011b Duplicates inside one source (same operator and name within 50 m). Collapse them.
  - [ ] H-011c Plausible power, connector and vehicle type. Null a wrong field and flag it.
  - [ ] H-011d Date present. If not, use the oldest plausible date.
  - [ ] H-011e Source total vs the official count. Record the coverage ratio.
- [ ] H-012 Record the number of quarantined records for each source.
- [ ] H-013 Give each record an H3 cell (resolution as in `settings.yaml`).
- [ ] H-014 Match records across sources: distance 50 m or less, plus a name or operator match.
- [ ] H-015 Keep the list of all source records for each merged site (lineage).
- [ ] H-016 Count the lineage groups for each merged site, not the sources.
- [ ] H-017 Record the compatibility state per vehicle type: confirmed, confirmed not, or unknown.
- [ ] H-018 Save the merged table as `/data/resolved/ka_charger_sites_v1.parquet`.
- [ ] H-019 Record the count of merged sites.

### H.3 Join to geography and demand

- [ ] H-020 Join each charger site to its district (spatial join with the DataMeet boundaries).
- [ ] H-021 Join each district to its DISCOM.
- [ ] H-022 Join the VAHAN table to the RTO crosswalk.
- [ ] H-023 Make one table per RTO: RTO, district or districts, DISCOM, EVs by class, charger sites near the RTO area.
- [ ] H-024 Make sure that a single query returns, per RTO: EV count by class, charger count, DISCOM (R4-03 "done when").
- [ ] H-025 Make a screenshot of the query and its output. Save it in `06_figures`.
- [ ] H-026 Commit the code and the output.
- [ ] H-027 Write in the decision log: join complete, date, owner.

> **NOTE:** If the join does not work by the end of 24 October, go to W-001.


---

## Part I. Freeze the definitions (R4-15, R4-16, R4-19, 25 Oct)

> **CAUTION:** Freeze all thresholds and parameter values before you compare methods or look at results. Choosing a threshold after you see results is the easiest attack for a judge. If a frozen value must change later, record the change and the reason in the decision log.

### I.1 Spacing checks (distance-based, R4-19)

- [ ] I-001 Read the MoP 2024 guidelines (S20).
- [ ] I-002 Record the urban rule: one station in each 1 km × 1 km grid cell (by 2030). Record the clause.
- [ ] I-003 Record the highway rule: one station each 20 km on both sides. Record the clause.
- [ ] I-004 Record the fast-charging rule: each 100 km for long-range and heavy vehicles. Record the clause.
- [ ] I-005 Write: "Spacing checks stay in kilometres. We do not convert them to minutes."
- [ ] I-006 Write how the 1 km grid is made (separate from the H3 grid).

### I.2 Accessibility (travel-time, R4-19)

- [ ] I-007 Choose one numeric travel-time threshold for each vehicle type: e-2W, e-3W, e-4W, corridor.
- [ ] I-008 Write the reason for each threshold. Use a published source if possible.
- [ ] I-009 Choose the routing profile for each vehicle type. Write it.
- [ ] I-010 Write the routing engine (OSRM) and the road data date.
- [ ] I-011 Write the rule for cells with no road or no route: report them as "unreachable". Do not delete them.
- [ ] I-012 If OSRM is not ready, write the fallback: network distance with a stated speed, or straight-line distance with a stated factor. Label it as a fallback.

### I.3 Capacity (R4-15)

- [ ] I-013 Choose the derating factor d. Write the value, the source and the range.
- [ ] I-014 Choose usable hours per day H. Write the value, the source and the range.
- [ ] I-015 Write the rule for shared connector power (site power limit S_i).
- [ ] I-016 Write the scenario weights: low (C_functional ≥ 0.7 and C_public ≥ 0.7), central (C_functional × C_public), high (all listed compatible chargers).
- [ ] I-017 Write: "Low, central and high are scenarios, not bounds."
- [ ] I-018 Write: "The central scenario is confidence-weighted. It is a heuristic discount, not a probability."
- [ ] I-019 Write the three-state compatibility rule (confirmed, confirmed not, unknown).
- [ ] I-020 Write: uptime enters only through C_functional. No second uptime multiplier.
- [ ] I-021 Write: the local capacity indicator Q is for display only. It is never summed across zones.
- [ ] I-022 Write: adequacy, unmet demand and totals use allocatable capacity (the allocation variables y).
- [ ] I-023 Write the allocation constraints (charger energy limit, zone demand limit, residual demand ≥ 0).

### I.4 Confidence scores (M2)

- [ ] I-024 Write the source-quality weights.
- [ ] I-025 Write the agreement rule: +0.20 for each additional lineage group, maximum +0.40.
- [ ] I-026 Write the recency half-life: 180 days.
- [ ] I-027 Write the negative-evidence penalty: −0.50 for each explicit closed or faulty report.
- [ ] I-028 Write the display labels: likely working (≥ 0.7), uncertain (0.4–0.7), unknown or likely down (< 0.4).
- [ ] I-029 Write the merge radius: 50 m.
- [ ] I-030 Use the term "heuristic evidence-confidence score (not a probability)" in all text.

### I.5 Validation metric definitions (R4-19)

- [ ] I-031 Write the duplicate distance (a new site near an existing high-confidence compatible charger).
- [ ] I-032 Write the real-plan overlap distance. It is used only if a Karnataka plan is verified; otherwise the metric is "method only / not evaluated".
- [ ] I-033 Write the population-within-reach definition (WorldPop cells within the accessibility threshold of a compatible charger, at low, central and high).
- [ ] I-034 Write: EV registrations are observed RTO totals. We do not claim a count of "EVs within reach".
- [ ] I-035 If you use the EV reach proxy, write its formula and label it "estimated proxy".
- [ ] I-036 Write the capacity-adequacy definition (estimated demand vs allocatable capacity per zone). Keep it separate from accessibility.
- [ ] I-037 Write the fixed budget for all method comparisons (in ₹ crore).
- [ ] I-038 Write the cost metric: public cost per site and per unit of population reached.

### I.6 Other parameters

- [ ] I-039 Write the H3 resolution used for computation.
- [ ] I-040 Write the demand parameters (daily km, kWh per km, public-charging share per class) with source and range. Mark them as priors.
- [ ] I-041 Write the latent-fleet plans (registered only, moderate, high) and their sources.
- [ ] I-042 Write the spatial priors (population-led, mobility-led, activity-led).

### I.7 Lock

- [ ] I-043 Put all values in `/config/settings.yaml`.
- [ ] I-044 Put the same values in a table for the submission appendix.
- [ ] I-045 Make a Git tag: `defs-frozen-2026-10-25`.
- [ ] I-046 Record the freeze in the decision log.
- [ ] I-047 Tell all members that the definitions are frozen.

---

## Part J. Freeze the scope (R4-07, 25 Oct)

### J.1 Core and differentiators

- [ ] J-001 Confirm the six core stages:
  1. Charger evidence layer.
  2. Demand by vehicle class at RTO level.
  3. CEA calibration at its real level, plus gap analysis.
  4. Budget-constrained site selection (efficiency and equity modes).
  5. Proposal export per site.
  6. Validation against baselines (and a real Karnataka plan only if one is verified).
- [ ] J-002 Confirm the two differentiators: source-independent confidence scoring and the delivery tracker.
- [ ] J-003 Confirm the stretch list: N-1 corridor resilience, typed configuration menu (including battery swapping), site-security factor, busy-month sizing, IHMCL corridor model, extra latent-fleet runs, UPNEDA replay.
- [ ] J-004 Confirm the roadmap-only list: UBC ingestion, silent-failure test, reliability ML, Bayesian adoption, public transparency page, operator scorecard.
- [ ] J-005 Write in the submission: stretch items are "if time allows", not promised.

### J.2 Status table

- [ ] J-006 Copy the R4-07 status table into the submission draft.
- [ ] J-007 For each stage, write the target status: Demonstrated, Method only or Finale commitment.
- [ ] J-008 Leave the "Status on 29 Oct" column empty until 29 October.
- [ ] J-009 Write the label definitions under the table.

> **CAUTION:** A box in an architecture diagram is not a working feature. Write "Demonstrated" only if the stage runs on real data and a second member can run it again.

- [ ] J-010 All members agree the scope. Record the agreement in the decision log.

---

## Part K. Calibration decision (R4-05, 26 Oct)

### K.1 Go/no-go inputs

- [ ] K-001 List the states with usable class-level VAHAN totals for the CEA months (from F-022).
- [ ] K-002 Make sure that CEA "excluding heavy duty" energy covers the same charging population as the model.
- [ ] K-003 Write how the model treats missing classes, hybrids and unregistered vehicles.
- [ ] K-004 Count the usable state-month pairs.

### K.2 Run (if inputs are sufficient)

- [ ] K-005 Run the national calibration with state-level data.
- [ ] K-006 Record the fitted public-charging rates per class.
- [ ] K-007 Compute bootstrap intervals for each rate.
- [ ] K-008 Do the leave-one-state-out test: remove each state one time and fit again.
- [ ] K-009 Record how much each rate changes.
- [ ] K-010 If the rates are unstable, report the instability and its size. Do not change the method until it passes.

### K.3 Decision

- [ ] K-011 Decide GO (national calibration) or NO-GO (Karnataka-only aggregate check).
- [ ] K-012 Record the decision, the date and the reason in the decision log.
- [ ] K-013 If NO-GO, write in the methodology: "National calibration is a research objective in the roadmap. Round 1 uses the Karnataka aggregate check with wide bands."
- [ ] K-014 If GO, write the method, the states used and the stability result.
- [ ] K-015 In both cases, label the Karnataka CEA comparison a "consistency check", not validation.

> **NOTE:** Calibration runs at the same time as the other work. It must not delay the join, the map or site selection.

---

## Part L. Reproducible slice (R4-11, 26 Oct)

### L.1 Contents

- [ ] L-001 Make one script or notebook that goes from the raw files to one proposed site.
- [ ] L-002 Make sure that the script reads only from `/data/raw` and `/config/settings.yaml`.
- [ ] L-003 Print the source names, retrieval dates and row counts for each input.
- [ ] L-004 Show one deduplication example: one charger in more than one source, its lineage groups and its merged record.
- [ ] L-005 Show one RTO result joined to its district or DISCOM and its nearby charger evidence.
- [ ] L-006 Show the reconciled Karnataka charger count vs 6,097 (MoP, S03), 6,805 (MHI, March 2026, not verified yet) and the OMC annexure values (not verified yet), with the definition and date of each count.
- [ ] L-007 Show EV registrations per RTO by class (observed totals).
- [ ] L-008 Make one CEA comparison chart. Label it "consistency check".
- [ ] L-009 Show one proposed site with these fields:
  - [ ] L-009a Site ID and coordinates.
  - [ ] L-009b Tier label (model-selected candidate, feasibility-checked or field-verified).
  - [ ] L-009c Vehicle type and charger configuration.
  - [ ] L-009d Estimated demand nearby.
  - [ ] L-009e Estimated compatible capacity nearby (low, central, high).
  - [ ] L-009f Cost split (total, PM E-DRIVE subsidy modelled, other public, public cost, operator share).
  - [ ] L-009g Reason for selection.
  - [ ] L-009h Evidence sources and dates.
- [ ] L-010 Write the list of missing fields and the fallback for each.
- [ ] L-011 Make one map screenshot (Karnataka, merged chargers, one proposed site).

### L.2 Reproducibility test

- [ ] L-012 Give the script to a member who did not write it.
- [ ] L-013 That member runs the script on their own laptop from the raw files.
- [ ] L-014 Compare the two outputs. Make sure that they are the same.
- [ ] L-015 If the outputs are different, find the cause. Fix it. Run the test again.
- [ ] L-016 Record the test result in the decision log.
- [ ] L-017 Make a Git tag: `slice-v1-2026-10-26`.

> **NOTE:** If the slice is not complete by the end of 26 October, go to W-010.

---

## Part M. Validation design (R4-06, R4-10, R4-18, 27 Oct)

### M.1 Methods to compare (same budget for all)

- [ ] M-001 Baseline 1: proportional to registered EVs. Write the exact rule.
- [ ] M-002 Baseline 2: NITI / WRI grid-cell method. Write the exact rule from S22.
- [ ] M-003 Reference: a real Karnataka plan, only if one is verified. Otherwise write "method only / not evaluated".
- [ ] M-004 Our engine.
- [ ] M-005 Write the fixed budget from I-037.

### M.2 Metrics (from Part I)

- [ ] M-006 Population within reach (at low, central, high).
- [ ] M-007 Spacing-rule compliance (1 km, 20 km, 100 km).
- [ ] M-008 Capacity adequacy (separate output).
- [ ] M-009 Duplication of existing chargers.
- [ ] M-010 Agreement with a verified real Karnataka plan (method only / not evaluated until one exists). Write: "agreement with an existing plan, not accuracy".
- [ ] M-011 Public cost per site and per unit of population reached.
- [ ] M-012 Our own "demand served" number, labelled "model-based", reported separately.

### M.3 Leakage control

- [ ] M-013 List the data that the calibration uses.
- [ ] M-014 List the data that the evaluation uses.
- [ ] M-015 Make sure that no evaluation result uses calibration data. If it does, call it a "consistency check".
- [ ] M-016 Write the hold-out plan: 3–4 whole states (or DISCOM groups) and the last quarter of CEA data (M7 test A).

### M.4 With and without CEA (R4-10)

- [ ] M-017 Write the plan: run the allocation with and without calibration. Count the sites that change.
- [ ] M-018 If a run is possible before 29 October, do it. Record the result. If not, write it as a method.

### M.5 Other tests to describe

- [ ] M-019 Test B: hand-label 150–200 Karnataka charger records, stratified by confidence band, including the highest band.
- [ ] M-020 Test E: confidence ablation (raw capacity, confidence-weighted, high-confidence only).
- [ ] M-021 Test F: data corruption (remove 20% of chargers, duplicate 10%, shift VAHAN ±20%, and similar).
- [ ] M-022 Sensitivity of scenario weights and thresholds.

### M.6 Acceptance test (R4-18)

- [ ] M-023 Write the five steps of the acceptance test in the submission.
- [ ] M-024 Write the pass rule: all five steps, one non-team person, no help, about 10 minutes.
- [ ] M-025 Write the plan: run the test in early December.

---

## Part N. Cost and subsidy (R4-16, 27 Oct)

- [ ] N-001 Open the PM E-DRIVE guidelines (S19).
- [ ] N-002 Record each eligible site category.
- [ ] N-003 Record the subsidy rate for upstream (grid) cost in each category. Record the clause.
- [ ] N-004 Record the subsidy rate for equipment cost in each category. Record the clause.
- [ ] N-005 Search the document for a per-charger or per-site cap. Record it with the clause.
- [ ] N-006 If you find no cap, write "no cap identified" and the document title and date.
- [ ] N-007 Record the cost components that are not eligible.
- [ ] N-008 Record the condition for 100% subsidy (government premises with free public access).
- [ ] N-009 Collect equipment cost ranges for each charger type from tenders or operator documents. Record each source.
- [ ] N-010 Collect upstream cost ranges. Record each source.
- [ ] N-011 Record the anchor: ₹688.84 crore approved for 6,562 chargers (about ₹10.5 lakh each). Record the source.
- [ ] N-012 Make the five-row cost table (total, PM E-DRIVE subsidy modelled, other public funding, public cost, operator share).
- [ ] N-013 Write: "Government contribution" is the public-cost row. The subsidy is counted one time only.
- [ ] N-014 Write: "eligible (modelled)" is not "sanctioned". Show sanctioned values only from a published sanction list.
- [ ] N-015 Write which amount the budget constraint uses (public cost, or PM E-DRIVE part only).
- [ ] N-016 Fill the cost table for the example site in L-009f.

---

## Part O. Roadmap with owners (R4-09, 27 Oct)

### O.1 Stage table

- [ ] O-001 Make the roadmap table: stage, owner, depends on, build window, output, cutoff and fallback.
- [ ] O-002 Use the build weeks 8 November to 14 December. The finale is 16–18 December.
- [ ] O-003 Add each of the six core stages.
- [ ] O-004 Add the two differentiators.
- [ ] O-005 Add the stretch items in a separate table with the label "if time allows".
- [ ] O-006 Write each kill criterion from the plan next to its module.
- [ ] O-007 Write the dependency for each stage.
- [ ] O-008 Write the owner name for each stage.

### O.2 Content the PDF requires in the roadmap

- [ ] O-009 Data sources to be used (link to the source-access matrix).
- [ ] O-010 Tools and technologies planned (list with versions where known).
- [ ] O-011 Development stages (the stage table).
- [ ] O-012 How the team arrives at the final prototype before the finale (milestones and demo plan).

### O.3 Milestones and finale preparation

- [ ] O-013 Add a weekly milestone for each build week.
- [ ] O-014 Add a code-freeze date (recommended: 12 December).
- [ ] O-015 Add a demo rehearsal date.
- [ ] O-016 Add the acceptance-test date (early December).
- [ ] O-017 Add the demo video date (deliverable for the finale).
- [ ] O-018 Write the finale demo sequence in short form.
- [ ] O-019 Write how the finale presentation will show the evolution from the Round 1 roadmap.
- [ ] O-020 Write the scalability path: Karnataka, then Telangana, then a state-by-state pipeline, then national.

### O.4 Gantt chart

- [ ] O-021 Make a simple Gantt chart (stages vs weeks).
- [ ] O-022 Show the two buffer days before the finale.
- [ ] O-023 Save the chart in `06_figures`.


---

## Part P. Units, wording and labels (R4-12, R4-13, R4-17, 28 Oct)

### P.1 Units (R4-12)

- [ ] P-001 Give a unit to each symbol in each equation.
- [ ] P-002 Use these units: energy in kWh/day; distance in km; daily distance in km/day; consumption in kWh/km; power in kW; cost in ₹ (lakh or crore, state which); time in minutes; sessions in sessions/hour.
- [ ] P-003 Convert CEA values from MU to kWh where you compare them with the model. Show the conversion.
- [ ] P-004 Use one number format for Indian amounts (lakh and crore). Do not mix with million and billion in the same table.
- [ ] P-005 Move all equations to the appendix. Keep one short plain sentence for each equation in the main text.

### P.2 Wording (R4-13)

- [ ] P-006 Search the draft for "confidence score". Change each one to "heuristic evidence-confidence score" at first use. Add "(not a probability)".
- [ ] P-007 Search for "optimal". Change it to "optimal for the stated objective and constraints". Add the solver gap where known.
- [ ] P-008 Search for "validated". Keep it only for a test that was done. Else write "to be validated by test X".
- [ ] P-009 Search for "ground truth". Change it. CEA is "an aggregate check on totals".
- [ ] P-010 Search for "live" and "real-time". Remove them for any source that is Planned.
- [ ] P-011 Search for "EVs within reach". Remove it, or change it to "estimated proxy".
- [ ] P-012 Search for "capacity". Make sure that it is "estimated compatible charging capacity" where it means kWh/day.
- [ ] P-013 Search for "government contribution". Make sure that it means the public-cost row.
- [ ] P-014 Search for "sanctioned". Use it only for values from a published sanction list.
- [ ] P-015 Search for "first", "only", "novel", "nobody", "unique". Mark each for the claim audit (Part T).
- [ ] P-016 Use the same name for the same thing everywhere (one term list). Put the term list in the appendix.

### P.3 Site tier labels (R4-17)

- [ ] P-017 Make sure that each site on each map has a tier label.
- [ ] P-018 Make sure that each site in each table has a tier label.
- [ ] P-019 Make sure that no text gives a site a stronger claim than its label.
- [ ] P-020 Write the three labels and their meaning in the methodology.

---

## Part Q. Write the submission (R4-08, R4-20; draft 28 Oct, final 29 Oct)

> **NOTE:** Target: 10–12 pages plus an appendix. The full Rev 3 plan is the internal reference. Do not submit the full plan.

### Q.1 Document setup

- [ ] Q-001 Make the document in a shared editor (Google Docs, Word or LaTeX).
- [ ] Q-002 Set A4 paper, margins of 2 cm to 2.5 cm.
- [ ] Q-003 Use one body font, 10.5–11 pt. Use one heading font.
- [ ] Q-004 Add page numbers.
- [ ] Q-005 Add a header or footer on each page: Team ID, team name, "Track 1: EV Infra Map India".
- [ ] Q-006 Make heading styles for sections and subsections.
- [ ] Q-007 Make a short table of contents (optional if 12 pages or fewer).

### Q.2 Cover page and team information (required)

- [ ] Q-008 Write the competition name: Techfest 2026-27, EV Infra & Green Mobility AI Challenge (MHI / ICAT).
- [ ] Q-009 Write: Track 1, EV Infra Map India.
- [ ] Q-010 Write the project title (one line).
- [ ] Q-011 Write the one-sentence tagline. Example from the plan: "Auditable PM E-DRIVE proposals from imperfect Indian data."
- [ ] Q-012 Write the team name (exactly as registered).
- [ ] Q-013 Write the Team ID.
- [ ] Q-014 Write the institution (full official name; each institution if cross-college).
- [ ] Q-015 Write each member name and role. Mark the team leader.
- [ ] Q-016 Write the contact details (minimum: team leader email and phone).
- [ ] Q-017 Write the submission date.

### Q.3 Section 1: Problem (about 1 page; criterion "problem understanding", 25%)

- [ ] Q-018 State the decision problem: PM E-DRIVE has ₹2,000 crore for public charging, with no state or district targets.
- [ ] Q-019 State the evidence gap: MHI told Parliament it has no assessment of chargers vs registered EVs. Cite it.
- [ ] Q-020 State that charger counts conflict across sources (29,277 vs 52,718, different definitions). Cite them.
- [ ] Q-021 State that installed is not the same as working. Use the OMC figure (82% operational) and the IEEFA Delhi sample as examples. Say what each covers.
- [ ] Q-022 State that 2W and 3W vehicles dominate EV volume, and that a large part of the fleet is not registered.
- [ ] Q-023 State that VAHAN gives registrations by RTO, not locations.
- [ ] Q-024 State who the user is: the state nodal agency.
- [ ] Q-025 State the decision the user makes: which sites, which chargers, what subsidy, and why.
- [ ] Q-026 State the study boundary: Karnataka for Round 1 and the finale; Telangana as the next expansion state; national as a state-by-state pipeline.
- [ ] Q-027 State the reason for Karnataka: the core data is downloaded and joined (31 LGD districts), and it has the highest public charger count (6,097) among the 36 states and UTs listed in the inspected MoP annexure (repo file S03, national total 29,277). Do not claim a real-plan comparison: no verified Karnataka site-level plan exists yet (method only / not evaluated).
- [ ] Q-028 Map the five PDF objective points to the solution in one small table (from D-005).

### Q.4 Section 2: Solution overview (about 1 page)

- [ ] Q-029 Describe the product in two sentences: a proposal engine, not a map.
- [ ] Q-030 Write the scope boundary: "We build the planner, not the operator." Name what the system does not do.
- [ ] Q-031 Add the architecture diagram (Part R).
- [ ] Q-032 List the six core stages in one line each.
- [ ] Q-033 List the two differentiators.
- [ ] Q-034 Write what a planner sees at the end: a proposal list for a budget, with reasons and evidence.

### Q.5 Section 3: Methodology (about 3 pages; criterion "feasibility", 25%)

- [ ] Q-035 Stage 1, charger evidence: sources, pre-merge checks, matching rule, lineage groups, confidence scores (heuristic), display labels.
- [ ] Q-036 Stage 1: explain the source-independence rule in one plain example ("five copies of one list count as one").
- [ ] Q-037 Stage 2, demand: VAHAN registrations by RTO and class; stock from registrations; energy per class; public-charging share; latent-fleet plans.
- [ ] Q-038 Stage 2: write that RTO totals are not locations. Write how demand is spread (three spatial priors) and that this is an assumption.
- [ ] Q-039 Stage 2: write how hybrids are treated.
- [ ] Q-040 Stage 3, calibration and gaps: what CEA checks (totals only), the level (DISCOM), the lag (about 5 months), and the calibration decision from Part K.
- [ ] Q-041 Stage 3: the capacity formula in plain words; scenarios low, central, high; allocatable capacity vs local indicator.
- [ ] Q-042 Stage 3: the gap is unmet demand after allocation. Spacing checks are separate.
- [ ] Q-043 Stage 4, site selection: candidate sites from eligible PM E-DRIVE categories; budget constraint on public cost; efficiency and equity modes; minimum-benefit rule; solver.
- [ ] Q-044 Stage 4: write that "optimal" means optimal for the stated objective and constraints.
- [ ] Q-045 Stage 4: write decision stability (re-solve over sampled parameter ranges) as method or stretch, per the status table.
- [ ] Q-046 Stage 5, proposal export: list the fields of each site card (from L-009).
- [ ] Q-047 Stage 5: the three tier labels.
- [ ] Q-048 Stage 5: the evidence ledger (each number traces to a source and date).
- [ ] Q-049 Stage 6, validation: pointer to Section 5.
- [ ] Q-050 Differentiator: delivery tracker (stages, flags, grid-connection deadlines 3 / 7 / 15 / 30 days, "commissioned but no energy" check).
- [ ] Q-051 Future requirements: adoption scenarios (S-curve with backtest, policy switches). Mark the status (method or demonstrated).
- [ ] Q-052 Add the status table (R4-07) at the end of the section.
- [ ] Q-053 Add one figure from the reproducible slice (map or site card).

### Q.6 Section 4: Data strategy (1–2 pages; criterion "data strategy", 10%)

- [ ] Q-054 Add the source-access matrix (short form: source, level, period, status, fallback).
- [ ] Q-055 Mark each source Verified, Planned, Synthetic or Not used.
- [ ] Q-056 Write the integration approach: three layers (raw, resolved, outputs), H3 keys, RTO and DISCOM crosswalks, versioning.
- [ ] Q-057 Write the refresh plan (VAHAN monthly, CEA monthly, OSM weekly, and so on).
- [ ] Q-058 Write the known data problems: count definitions, VAHAN quality gaps, unregistered fleet, CEA lag, no live status.
- [ ] Q-059 Write the privacy position: no personal data; aggregates only.
- [ ] Q-060 Write the legal position: licences recorded; no Google Maps or PlugShare data; the NTR data-sharing policy is the path for deeper VAHAN access.
- [ ] Q-061 Add the real numbers from the slice (row counts, reconciled counts).

### Q.7 Section 5: Validation plan (about 1 page)

- [ ] Q-062 List the methods compared (two baselines, a real Karnataka plan only if verified, our engine) at one fixed budget.
- [ ] Q-063 List the metrics with their frozen definitions (short form; full form in appendix).
- [ ] Q-064 Write the leakage rule (calibration data vs evaluation data).
- [ ] Q-065 Write the hold-out plan.
- [ ] Q-066 Write the with-and-without-CEA test.
- [ ] Q-067 Write the hand-label test and the ablation.
- [ ] Q-068 Write the acceptance test.
- [ ] Q-069 Write the limits: what the team cannot validate (site-level usage, live status, land).

### Q.8 Section 6: Implementation roadmap (about 2 pages; criterion "roadmap", 20%)

- [ ] Q-070 Add the stage table with owners, dependencies, windows, outputs and fallbacks (Part O).
- [ ] Q-071 Add the Gantt chart.
- [ ] Q-072 Add the tools and technologies list.
- [ ] Q-073 Add the kill criteria.
- [ ] Q-074 Add the stretch table with "if time allows".
- [ ] Q-075 Add the roadmap-only list (after the finale).
- [ ] Q-076 Add the scalability path (Karnataka, then Telangana, state pipeline, national).
- [ ] Q-077 Add the finale demo plan in short form.

### Q.9 Section 7: Deliverable map (R4-20, about half a page)

- [ ] Q-078 Add the deliverable map: Track 1 deliverable, Round 1 evidence, finale commitment.
- [ ] Q-079 Make sure that each of the seven PDF deliverables has a row.
- [ ] Q-080 Write under the table: "This is a mapping, not a claim that any deliverable is complete."

### Q.10 Section 8: Innovation summary (about half a page; criterion "innovation", 20%)

- [ ] Q-081 List the differentiators as a combination, not as new algorithms.
- [ ] Q-082 Include: evidence ledger; source-independent confidence; CEA aggregate check; class-specific demand; budgeted proposal output in PM E-DRIVE terms; delivery tracker; comparison with a real state plan.
- [ ] Q-083 Write one sentence: what other teams usually build (map, heatmap, chatbot) and why the planner needs more.
- [ ] Q-084 Do not claim "first" or "only" unless Part T confirms it.

### Q.11 Section 9: Limitations and assumptions

- [ ] Q-085 List the main assumptions (from M8 and Part I).
- [ ] Q-086 List what the system does not do (operate chargers, guarantee land or grid).
- [ ] Q-087 List data that does not exist publicly (site-level sessions, live status for Karnataka).

### Q.12 Disclosure section (required by Rule 6)

- [ ] Q-088 Write the list of AI tools used, with purpose (from `ai_use_log.csv`).
- [ ] Q-089 Write the list of third-party software and libraries with licences (from `software_log.csv`).
- [ ] Q-090 Write the list of external datasets with licences (from the source register).
- [ ] Q-091 Write the list of pre-built frameworks (for example, OSRM, OR-Tools or PuLP).
- [ ] Q-092 Write the list of synthetic data, if any (Rule 5).
- [ ] Q-093 Write a statement: the work is the original work of the team (Rule 3).

### Q.13 References

- [ ] Q-094 List each cited source with title, publisher, date and URL.
- [ ] Q-095 Use one citation style for all entries.
- [ ] Q-096 Make sure that each number in the text has a reference.
- [ ] Q-097 Give attribution text required by licences (OSM: "© OpenStreetMap contributors"; DataMeet: "India boundaries by DataMeet India community").

### Q.14 Appendix

- [ ] Q-098 Appendix A: equations with units.
- [ ] Q-099 Appendix B: frozen parameter and threshold table.
- [ ] Q-100 Appendix C: confidence-score rules.
- [ ] Q-101 Appendix D: full metric definitions.
- [ ] Q-102 Appendix E: full source-access matrix.
- [ ] Q-103 Appendix F: term list.
- [ ] Q-104 Appendix G: compliance table for Rules 1–12 (optional).

### Q.15 Length control

- [ ] Q-105 Count the pages of the main text.
- [ ] Q-106 If the main text is longer than 12 pages, move detail to the appendix.
- [ ] Q-107 If the portal gives a page limit, obey it. The portal limit has priority over this checklist.

---

## Part R. Figures and tables (28 Oct)

### R.1 Required figures

- [ ] R-001 Figure 1: architecture diagram (sources → evidence and demand → calibration → gap → selection → proposal export).
- [ ] R-002 Figure 2: Karnataka map of merged charger sites, coloured by confidence label.
- [ ] R-003 Figure 3: reconciliation chart (our Karnataka count vs 6,097 MoP, 6,805 MHI and the OMC values; show only verified figures, each with its definition and date).
- [ ] R-004 Figure 4: EV registrations by RTO and class (observed totals).
- [ ] R-005 Figure 5: CEA consistency check chart.
- [ ] R-006 Figure 6: one site card from the slice.
- [ ] R-007 Figure 7: roadmap Gantt chart.

### R.2 Rules for each figure

- [ ] R-008 Give each figure a number and a caption.
- [ ] R-009 Write the data source and date in each caption.
- [ ] R-010 Write the data status (Verified, Planned, Synthetic) in the caption if not all data is Verified.
- [ ] R-011 Add the map attribution (OSM, DataMeet) on each map.
- [ ] R-012 Add a legend, a scale and a north arrow on each map.
- [ ] R-013 Use colours that a person with colour blindness can read.
- [ ] R-014 Make sure that each figure is readable in black and white print.
- [ ] R-015 Export each figure at 200 dpi or more.
- [ ] R-016 Refer to each figure in the text.
- [ ] R-017 Save the code that made each figure in `/src/figures`.

### R.3 Tables

- [ ] R-018 Give each table a number and a title.
- [ ] R-019 Put units in the column headers.
- [ ] R-020 Make sure that no table breaks across two pages without a repeated header.

---

## Part S. Final file production (29 Oct, morning)

- [ ] S-001 Read the full draft one time from start to end (submission owner).
- [ ] S-002 Get two other members to read the full draft.
- [ ] S-003 Each reader writes comments in the document.
- [ ] S-004 Fix all comments, or record why not.
- [ ] S-005 Do a spelling and grammar check.
- [ ] S-006 Make sure that the team name and Team ID are the same on each page.
- [ ] S-007 Make sure that the figure and table numbers are in sequence.
- [ ] S-008 Make sure that each cross-reference points to the correct section.
- [ ] S-009 Make sure that each link works. Click each link.
- [ ] S-010 If you include a GitHub link, make sure that the judges can open it (public or shared) or remove it. Decide with the team.
- [ ] S-011 Export the document to PDF (unless the portal asks for a different format).
- [ ] S-012 Make sure that all fonts are embedded in the PDF.
- [ ] S-013 Open the PDF on a laptop. Examine each page.
- [ ] S-014 Open the PDF on a phone. Examine that the text and the figures are readable.
- [ ] S-015 Make sure that the file size is less than the portal limit (A-039).
- [ ] S-016 If the file is too large, compress the images. Examine the figures again.
- [ ] S-017 Name the file. Example: `TeamID_TeamName_Track1_Round1.pdf`. Use no spaces if the portal rejects them.
- [ ] S-018 Set the PDF title and author fields in the document properties.
- [ ] S-019 If the portal wants separate files, make each file and name each file in the same way.
- [ ] S-020 Save the final file in `07_submission`.
- [ ] S-021 Save a copy in a second location (email to the team leader, USB drive or second cloud).
- [ ] S-022 Prepare the text for each form field (A-042) in a plain text file. Obey the character limits.

---

## Part T. Claim audit and go/no-go (R4-14, 29 Oct)

### T.1 Claim audit

- [ ] T-001 List each use of these words: first, only, novel, nobody, unique, live, real-time, operational, ground truth, optimal, validated, proven, guaranteed, eligible, sanctioned.
- [ ] T-002 For each claim, find the evidence.
- [ ] T-003 For "first", "only", "nobody": do a fresh search for a counter-example. If one exists, change the claim.
- [ ] T-004 Change each claim with no evidence to a weaker, true claim. Example: "We did not find a publicly documented Indian tool that ...".
- [ ] T-005 Make sure that each number has a source and a date.
- [ ] T-006 Make sure that each "Planned" item is not described as working.
- [ ] T-007 Make sure that each scheme rule (subsidy rate, cap, eligibility) has a clause reference.
- [ ] T-008 Make sure that no metric reports spatial reach or capacity as an observed fact.
- [ ] T-009 Make sure that the text does not copy sentences from sources. Paraphrase and cite.
- [ ] T-010 Make sure that no figure or text is copied from a patent or a paper without citation (Rule 9).
- [ ] T-011 Make sure that the methods are described as standard published methods, cited where used.

### T.2 Final status table

- [ ] T-012 Fill the "Status on 29 Oct" column of the status table from the real results.
- [ ] T-013 Downgrade each stage that does not run to "Method only".
- [ ] T-014 Update the text so that it agrees with the status table.

### T.3 Go/no-go meeting

- [ ] T-015 Hold the meeting at the agreed time (C-012). All owners attend.
- [ ] T-016 Do a check of each GO condition:
  - [ ] T-016a One real, traceable data path from raw sources to a joined Karnataka result.
  - [ ] T-016b A site-selection example that a second member can run and explain.
  - [ ] T-016c A written fallback for national calibration.
  - [ ] T-016d Validation metrics that claim no more than the data supports.
  - [ ] T-016e Clear separation of working, planned and synthetic items.
  - [ ] T-016f A concise submission that maps to the PDF deliverables.
- [ ] T-017 If all conditions are true, record GO.
- [ ] T-018 If a condition is false, shrink each related claim to the smallest working system. Then record GO with the reduced claims.

> **NOTE:** NO-GO does not mean "do not submit". It means "reduce the claims and submit".

- [ ] T-019 Record the decision in the decision log.
- [ ] T-020 Freeze the PDF. Make a Git tag: `round1-final-2026-10-29`.
- [ ] T-021 After the freeze, change the PDF only to fix a factual error.


---

## Part U. Submission day (30 Oct)

> **WARNING:** Only the team leader submits. Submit one time only. More than one submission can cause disqualification.

### U.1 Before you open the form

- [ ] U-001 Charge the laptop of the team leader to 100%.
- [ ] U-002 Connect to a stable internet connection. Keep the backup hotspot ready.
- [ ] U-003 Open the final PDF from `07_submission`. Make sure that it is the frozen version (T-020).
- [ ] U-004 Make sure that the file name and size are correct.
- [ ] U-005 Open the plain text file with the form field answers (S-022).
- [ ] U-006 Examine the portal Doubt section and techfest.org for last-minute changes.
- [ ] U-007 Examine the team leader email for messages from techfest.org.
- [ ] U-008 Make sure that a second member is available by phone during the submission.

### U.2 Submit

- [ ] U-009 Log in to techfest.org with the team leader account.
- [ ] U-010 Open the Round 1 submission form for this competition.
- [ ] U-011 Make sure that the form is for the EV Infra & Green Mobility AI Challenge, Track 1.
- [ ] U-012 Fill each field. Copy text from the prepared file.
- [ ] U-013 Make sure that the Team ID in the form is correct.
- [ ] U-014 Upload the file (or files).
- [ ] U-015 Make sure that the upload is complete (file name shown, no error).
- [ ] U-016 If the form allows a preview, open the preview. Examine each field.
- [ ] U-017 Take a screenshot of the complete form before you submit.
- [ ] U-018 Click submit one time only. Do not click again if the page is slow.
- [ ] U-019 Wait for the confirmation page.
- [ ] U-020 Take a screenshot of the confirmation page.
- [ ] U-021 Record the date and time of the submission.
- [ ] U-022 Record any confirmation number.

### U.3 After you submit

- [ ] U-023 Examine the email for a confirmation message. Save it.
- [ ] U-024 Save all screenshots in `00_admin`.
- [ ] U-025 Tell all members that the submission is complete.
- [ ] U-026 If the page showed an error, do not submit again immediately. Examine the portal to see if the submission exists.
- [ ] U-027 If you are not sure that the submission exists, write a query in the Doubt section with the screenshots. Do this before the deadline.
- [ ] U-028 Archive the final versions of all files in `08_archive/round1_final`.

---

## Part V. After submission (31 Oct to 7 Nov, and next steps)

### V.1 Monitor

- [ ] V-001 Examine the registered email each day.
- [ ] V-002 Examine techfest.org and the Doubt section each day.
- [ ] V-003 On 7 November, examine the result announcement.

### V.2 Continue the build (do not wait for the result)

- [ ] V-004 Continue with the core stages in the roadmap order.
- [ ] V-005 Start the hand-labelled sample (test B): 150–200 Karnataka records.
- [ ] V-006 Start the baseline comparison runs at the fixed budget.
- [ ] V-007 Keep the decision log and the AI-use log current.
- [ ] V-008 Keep each change from the Round 1 roadmap in a change list. The finale presentation must show how the solution evolved (Round 2 rule).

### V.3 Prepare for the finale (if shortlisted)

- [ ] V-009 Confirm travel and stay for all attending members (16–18 December, IIT Bombay).
- [ ] V-010 Confirm that the demo runs without internet (offline data and map tiles), in case the venue network fails.
- [ ] V-011 Prepare the demo video (deliverable). Keep a copy on a USB drive.
- [ ] V-012 Rehearse the demo and the Q&A. Use the judge questions in the plan (Part XIII, 40 questions).
- [ ] V-013 Run the acceptance test (R4-18) with a non-team person in early December.

### V.4 Prize form (only if a top-3 result)

- [ ] V-014 Note: the prize form is on the website after the final round. The deadline is 31 December 2026.
- [ ] V-015 Note: the form needs the account holder name, account number, bank and branch name, and IFSC code.

---

## Part W. Contingencies

| ID | If this happens | Do this |
| --- | --- | --- |
| W-001 | The join does not work by the end of 24 Oct | Keep RTO as the unit. Join only VAHAN and DISCOM. Join chargers at district level. Record the limit. |
| W-002 | The VAHAN dashboard does not work | Use India Data Portal (S02). Record the mirror and its date. |
| W-003 | Both VAHAN sources fail | Use the latest public state-level totals. Mark RTO detail as Planned. Reduce stage 2 to "Method only". |
| W-004 | The CEA PDF tables do not extract | Copy the Karnataka rows by hand. Do a check by a second member. |
| W-005 | State-level class data for national calibration is not available | Activate the R4-05 fallback (Karnataka-only check). |
| W-006 | Open Charge Map key is late | Use OSM only, plus a state or DISCOM list if one is verified. Mark OCM as Planned. |
| W-007 | Geocoding of real-plan sites is poor (only if a Karnataka plan is verified) | Use the district or cluster level. Label it. Use only the clear sites for overlap. |
| W-008 | OSRM routing does not run | Use the I-012 fallback. Label it as a fallback in the text. |
| W-009 | The RTO list or jurisdiction source is not found | Use the RTO names in VAHAN and the district in the RTO name. Record the method and its risk. |
| W-010 | The reproducible slice is not complete by 26 Oct | Reduce it to: raw files, dedup example, RTO join, one map. Mark site selection as "Method only". |
| W-011 | The optimiser does not run before 29 Oct | Show one site chosen by a simple ranking rule. Label it. Mark stage 4 as "Method only". |
| W-012 | A member becomes unavailable | The backup person (C-010) takes the role. Update the owner table. |
| W-013 | The team leader becomes unavailable on 30 Oct | Write a query in the Doubt section immediately. Do not let a different member submit. |
| W-014 | The portal fails near the deadline | Take screenshots with the time. Write a query in the Doubt section. Keep trying. Do not submit two times. |
| W-015 | The PDF is too large | Compress images. Remove the appendix figures that are not needed. |
| W-016 | A factual error is found after the freeze | Fix only that error. Record it in the decision log. |
| W-017 | A new review or idea arrives | Apply the review freeze. Accept it only if it unblocks the build or fixes a factual error. |

---

## Appendix 1. Templates

### A1.1 Source-access matrix row (example)

| Field | Example |
| --- | --- |
| ID | S08 |
| Dataset | OSM charging stations, Karnataka |
| Publisher | OpenStreetMap contributors |
| URL | overpass-turbo.eu (query in `/src/queries/`) |
| Format | GeoJSON |
| Level | Point |
| Period | Snapshot, retrieval date |
| Licence | ODbL |
| Access | Overpass API |
| Status | Verified |
| Date checked / by | 24 Oct / initials |
| File | `20261024_osm_chargers_TG_v1.geojson` |
| Count | (number) |
| Hash | (SHA-256) |
| Lineage group | OSM |
| Fallback | Open Charge Map |
| Notes | Tags present: ... |

### A1.2 Status table (R4-07)

| Stage | Target status | Status on 29 Oct |
| --- | --- | --- |
| 1. Charger evidence layer | Demonstrated | |
| 2. Demand by class at RTO level | Demonstrated | |
| 3. CEA calibration and gap analysis | Consistency check demonstrated; national method only unless R4-05 passes | |
| 4. Budget-constrained site selection | One example demonstrated; equity mode method only | |
| 5. Proposal export | One site card demonstrated | |
| 6. Validation | Method only | |

### A1.3 Cost table (R4-16)

| Field | Value (₹ lakh) | Source or rule |
| --- | --- | --- |
| Total project cost | | Upstream + equipment |
| PM E-DRIVE subsidy (modelled eligible) | | Clause reference |
| Other public funding | 0 (default) | Planner input |
| Public cost | | Subsidy + other public |
| Operator share | | Total − public cost |

### A1.4 Decision log entry

| Date | Decision | Owner | Reason | Evidence |
| --- | --- | --- | --- | --- |
| 25 Oct | Definitions frozen | (name) | Before any comparison | Git tag `defs-frozen-2026-10-25` |

### A1.5 AI-use log entry

| Date | Member | Tool | Purpose | Output used | Change by team |
| --- | --- | --- | --- | --- | --- |
| 23 Oct | (name) | (tool) | Plan review | Checklist structure | Edited and verified |

### A1.6 Disclosure paragraph (draft, change to match the logs)

"The team used AI assistants for research summaries, plan review and text drafting. The team checked all facts against the cited sources and wrote the final text. The team used these open-source tools: (list with licences). The team used these public datasets: (list with licences and attribution). The team used no proprietary datasets. Synthetic data: (none, or list with IDs)."

---

## Appendix 2. Final count

- Parts: A to W, plus two appendices.
- Numbered steps: 659 primary steps, 19 sub-steps and 17 contingency rules (695 actions).
- Every Round 1 requirement in the PDF maps to a step: team information (Q.2), methodology (Q.3–Q.7), implementation roadmap (Q.8, Part O), conciseness (D-014, Q.15), team-leader submission (Part U), one submission (Part U), disclosure (Q.12), synthetic data (Part G), attribution (Q.13), Team ID (A.1).
- Every R4 item maps to a part: R4-01 E · R4-02 F · R4-03 H · R4-04 G · R4-05 K · R4-06 M · R4-07 J · R4-08 Q · R4-09 O · R4-10 M.4 · R4-11 L · R4-12 P.1 · R4-13 P.2 · R4-14 T · R4-15 I.3 · R4-16 N · R4-17 P.3 · R4-18 M.6 · R4-19 I.5 · R4-20 Q.9.
