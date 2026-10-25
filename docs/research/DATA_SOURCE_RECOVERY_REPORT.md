# Data Source Recovery Report: Karnataka EV charging infrastructure

Date: 25 October 2026 · Register: `configs/source_register.csv` · Geography: Karnataka (ADR-001)

## 1. Outcome

The official location-level list was found, downloaded and fully extracted.

| Item | Value |
| --- | --- |
| Source | Bureau of Energy Efficiency (BEE), "EV Public Charging Stations Data till 26th October 2025 (Click to view the detailed list)" |
| Listing page | https://www.beeindia.gov.in/show_content.php?lang=1&level=2&lid=67&ls_id=345 |
| File URL | https://www.beeindia.gov.in/WriteReadData/RTF1984/EV_PCS_Data_29277.pdf |
| Local file (register S15) | `data/raw/S15_bee_ev_public_charging_stations_29277_2026-10-25.pdf` (+ `.manifest.json`) |
| SHA-256 | `f519218fa96a04f57b3c56e919a8045133e7df1307a77710cca0076ab25b6882` |
| Size | 7,942,286 bytes; 1,159 pages |
| Retrieved | 2026-10-25T14:12:21Z (scripted, no login) |
| Dates | Data "till 26th October 2025" (link text). PDF created 2026-02-17 from Microsoft Excel. HTTP Last-Modified 22 Apr 2026 |
| Licence | **Not stated** on the page or in the file. Confirm reuse terms before redistributing |

Fields (12): CPO Name, Govt/Private, State, District, City/Village, Location, Latitude, Longitude, Types of Chargers Installed/Connector, Charger Rating, Connector Rating, No. of Connector. The source has no operating status, no per-record date and no unit for ratings.

Third-party copy: Dataful dataset 23369 states BEE as its source, sells downloads under a custom licence, and says it removed some records. It is not equivalent to the original and was not used.

## 2. Unit of the source

One table row is one **charger entry** (type, rating, connector count) at a location. It is not a station:

- India: 39,641 rows. The file name says 29,277. The number of distinct (state, location, coordinates) combinations is 29,376.
- So the published "station" count is close to the number of distinct locations, not to the number of rows. This is an inference from the counts; BEE does not define the unit.

## 3. Karnataka counts (S18 rows, S19 sites)

| Measure | Count |
| --- | --- |
| Raw rows, all states (S16 staging) | 39,641 |
| Karnataka rows (State field = "Karnataka"; no other spelling exists) | 8,246 |
| Connectors (sum of "No. of Connector") | 8,512 |
| Rows with valid coordinates (numeric, latitude ≠ longitude, inside a Karnataka 2011 district polygon) | 8,232 |
| Rows flagged: latitude = longitude | 6 (all IOCL) |
| Rows flagged: outside Karnataka polygons | 8 (for example longitude 7.5 for Bengaluru, a point at 30.12 N 96.12 E, and coastal or border points) |
| Derived station groupings (no official definition; depends on the key) | 6,069–6,150: coordinates only 6,069 · CPO + coordinates 6,077 · location + coordinates 6,146 · CPO + location + coordinates 6,150 (`station_key`; 6,137 with valid coordinates only) |
| Candidate physical sites (identical coordinates) | 6,056 |
| Site clusters within 25 m (lower bound) | 4,636 |
| Exact duplicate rows (all 12 fields identical) | 456 groups; 1,921 surplus rows. Kept: these may be identical chargers at one station (one group has 141 rows) |
| Nearby distinct sites within 25 m | 8,005 pairs, mostly UJOY light-EV points metres apart in the same complex |
| Rows with known operating status | 0 |
| Rows confirmed operational | 0 |
| Rows with a numeric charger rating | 8,246 (unit not stated) |
| Rows with the stated district matched to an LGD code | 8,246 (all 31 districts; 4 explicit aliases) |
| Rows with a district from point-in-polygon | 8,232 |
| Stated district vs point district | agree 7,966 · agree, pre-split Ballari/Vijayanagar 19 · disagree 247 · not assessable 14 |
| Govt. / Private (as stated) | 1,958 / 6,288 |

- **Concentration:** Bengaluru Urban holds 6,541 rows (79%) and 4,564 station keys. Every district has at least 11 station keys.
- **Largest operators:** UJOY (3,965 rows), Reliance BP (1,056), IOCL (667) and BESCOM (559).
- **District disagreements:** most are rows stated as "Bengaluru Urban" whose points fall in neighbouring districts; 110 of them are BESCOM rows. They are flagged, not corrected.

## 4. Official totals

| Figure | Source (register) | Date | Definition | Karnataka | India |
| --- | --- | --- | --- | --- | --- |
| 6,097 | PIB annexure, "as per inputs received from Ministry of Power" (S03) | Last-Modified 1 Aug 2025 | Public charging stations installed | 6,097 | 29,277 |
| 6,096 | PIB release 2204635: Lok Sabha written reply, MoS Heavy Industries (S17) | 16 Dec 2025 | EVCS installed during the last five years (751 fast, 5,345 slow) | 6,096 | 29,151 |
| BEE list | S15 | Data till 26 Oct 2025 | Charger rows at locations | 8,246 rows; derived station groupings 6,069–6,150 | 39,641 rows; 29,376 distinct locations |

- **S03 provenance:** S03 is byte-identical to the PIB annexure at `https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/aug/doc202581598101.pdf`. The parliamentary question number and reply date are not in the file.
- **Comparison:** the official counts (6,096–6,097) fall inside the derived grouping range (6,069–6,150). Neither BEE nor the ministries define a "station", so no single derived count is the match, and no difference from the official figures is claimed. The official figures count stations, not chargers or connectors, so the 8,246 rows must not be compared with them.
- **Possible same snapshot:** the BEE file name carries the same national total (29,277) as the August 2025 annexure. The list may therefore be the same reporting snapshot, extended or re-exported later. This is not confirmed.
- **Remaining gap:** the small difference (about 50 stations) is consistent with date and key-definition differences, such as one station listed under two location spellings. It is not resolved, and no rows were added or removed to match.

## 5. Coverage versus the OSM baseline (S11, 67 records)

- 17 of 67 OSM records lie within 100 m of a BEE site, and 21 BEE sites have an OSM record within 100 m. This is proximity only, not an identity match.
- The other 50 OSM records add locations not in the BEE list:
  - access tag: unknown 41, restricted 5, public 4
  - 9 are battery-swapping points (7 Honda e:swap)
  - others include Bolt Earth, BESCOM, Shell and ChargePoint
- The BEE list adds about 6,000 locations that OSM lacks. OSM remains a supplementary source.
- No cross-source merge was made. Each source keeps its own IDs (S11 `inventory_id`, S18 `source_row_id`).

## 6. Other sources checked

| Source | Result |
| --- | --- |
| Open Charge Map API (S13) | Inaccessible: HTTP 403 without an API key |
| India Data Portal VAHAN (S14) | Verified but not acquired: the CKAN resource has no URL and the licence is "notspecified" |
| Dataful 23369 | Third-party, paid, modified. Not used |
| MHI 6,805 (March/July 2026) and the Rajya Sabha OMC annexure | Not verified in this sprint |
| PM E-DRIVE approvals (1,571 reported), BESCOM and ESCOM portals | Not checked in this sprint. Approved or sanctioned sites must never be counted as installed |

## 7. Register repair

- **New rows:** S01–S05 and S20 (district boundaries) are now registered, alongside the new S15–S19.
- **Status vocabulary:**
  - `verified_and_acquired`: file held and verified
  - `acquired_provenance_incomplete`: file held, but its origin is not fully recorded
  - `verified_but_not_acquired`
  - `inaccessible`
  - `derived`
- **Changes to existing rows:**
  - The old `verified` status became `verified_and_acquired`.
  - S13 became `inaccessible`.
  - S14 became `verified_but_not_acquired`.
  - Other fields of existing rows are unchanged, except notes on S10 and S13.
- **Missing provenance:**
  - S01 (VAHAN export), S04 (Census A-1) and S20 (DataMeet) still lack their exact download URL and retrieval time. S20's licence is also unverified.
  - S01 and S04 terms were not checked.
  - These gaps are recorded, not invented.

## 8. Gaps the model must not fill by inference

| Gap | Status |
| --- | --- |
| EV registrations by RTO × class × year | Not available. S01 is statewide only; S14 not acquired. Do not split state totals |
| RTO jurisdictions and RTO-to-district crosswalk | Not obtained |
| ESCOM service areas (BESCOM, MESCOM, HESCOM, GESCOM, CESC) | Not obtained. The BEE "Bescom" CPO rows are stations, not service-area evidence |
| Grid capacity, transformer or substation data | None. Do not infer from proximity |
| Charger operating status | None in BEE or OSM |
| Connector compatibility and rated power | BEE gives connector type and a rating with no unit. OSM has no power tags |
| District boundaries | Census 2011 polygons (30) vs 31 current LGD districts; Vijayanagar is inside 2011 Ballari. No current boundary file |

The demand model, confidence scoring, optimiser and validation design are unchanged.

## 9. Manual actions, smallest first

1. Confirm BEE reuse terms for the S15 list, by email to BEE or from the site's terms page, before redistributing any derived file.
2. Register an Open Charge Map API key and put it in `.env`.
3. Download RTO-wise EV registrations from the VAHAN dashboard by hand (it has a CAPTCHA).
4. Record the download URLs for S01, S04 and S20 and check the DataMeet licence.
5. Find the Lok Sabha question number behind S03 (Aug 2025).

## 10. Reproduce

```
python -m pip install -e ".[dev,pdf]"          # pdf extra = pdfplumber 0.11.7 (S16 only)
python src/evinfra/ingestion/fetch_bee_pcs.py  # S15 (new dated file; never overwrites)
python src/evinfra/ingestion/extract_bee_pcs.py   # S16, about 8 minutes
python src/evinfra/analysis/build_bee_inventory.py   # S18, S19, dictionary, summary
```

The raw and processed files are gitignored. The hashes in the register identify the exact files used here.

## 11. Tests and checks

- **Tests:** `python -m pytest`: 84 passed. 22 of these are new: `test_extract_bee_pcs.py` (8) and `test_build_bee_inventory.py` (14). They cover schema, Karnataka filtering, coordinate and boundary flags, exact and nearby duplicates, missing-value preservation, station versus site versus connector counts, district assignment, lineage, and determinism.
- **Lint:** `python -m ruff check src tests`: all checks passed.
- **Reproducibility:**
  - Re-running S09, S11/S12 and S18/S19 reported every output unchanged.
  - Re-extracting S16 from the PDF gave the same SHA-256 (`91d13b52…ab9a`).
