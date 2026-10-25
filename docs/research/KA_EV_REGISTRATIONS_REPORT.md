# Karnataka EV Registrations: Sources, Validation and Geographic Limits

Date: 25 October 2026 · Branch: `feature/ka-ev-registrations` · Register: S01, S14, S24–S28

## 1. Sources

| Source | Register | What it gives | Access | Status |
| --- | --- | --- | --- | --- |
| India Data Portal "Vehicle Registrations": Registrations by Fuel Type | S24 | Monthly new registrations by state, RTO and fuel type (VAHAN compilation) | Direct CSV, no login; ODC-BY | Acquired |
| India Data Portal "Vehicle Registrations": Registrations by Vehicle Class | S27 | Same registrations by RTO and vehicle class (all fuels) | Direct CSV, no login; ODC-BY | Acquired (consistency check only) |
| Karnataka Transport Department, monthly vehicle statements | S25 | State and Bengaluru totals by vehicle category: stock and new registrations. No fuel, no RTO | PDF, no login | Two months acquired |
| VAHAN dashboard (vahan.parivahan.gov.in/vahan4dashboard) | S01 (earlier statewide export) | The primary source; can show RTO x class x fuel x month on screen | TCP connection to port 443 fails from the project machine (25 Oct, twice); parivahan.gov.in answers | Not reachable here |
| India Data Portal norm and maker tables | – | Same one-attribute layout (norm, maker) | Checked headers only | Not needed |
| data.gov.in "KAxx ... Vehicle Newly Registered In The Year 2021-2022" | – | One file per RTO, 2021-22, all fuels (about 1.7 KB each) | Download returns HTTP 403 without the portal's download form or API key; GODL-India | Not acquired |
| Dataful (dataful.in) VAHAN-derived sets | – | Third-party paid copies | Custom licence | Not used |

Links: [IDP package API](https://ckandev.indiadataportal.com/api/3/action/package_show?id=vehicle-registrations) · [Transport Department monthly statistics](https://transport.karnataka.gov.in/50/Monthwise%20Vehicle%20Statistics%20Report/en)

**No accessible source publishes RTO x month x vehicle class x fuel.** Every IDP table is a single attribute by RTO and month. S24 and S27 must not be combined to estimate EVs by class.

## 2. Data and definitions

- **Coverage:** S24 Karnataka has 36,198 rows covering 67 VAHAN RTOs over 57 months (January 2022 to September 2026). Counts are **new registrations per month** (flows); the `date` column is month end.
- **Battery EVs:** BEV = `Electric(BOV)` + `Pure EV`. "Pure EV" first appears in March 2024 and takes over from "Electric(BOV)" over the following months, while their sum stays continuous. This is consistent with a relabelling of the same battery-electric category.
- **Hybrids:** `Strong Hybrid EV` (from March 2024) and `Plug-in Hybrid EV` (5 Karnataka rows) are kept separate.
- **Zero counts:** the source never publishes a zero (minimum 1). An absent RTO, month and fuel combination is therefore zero or unreported; it stays blank and is never set to 0.

## 3. Validation findings

| Check | Result |
| --- | --- |
| Duplicates, invalid or negative counts, RTO code-name conflicts | None (S24 and S27) |
| S24 BEV vs S01 VAHAN dashboard export, calendar years | 2022 +1 · 2023 −3 · 2024 +5 · 2025 −68 (−0.03%). 2026 not comparable (S01 cut-off unknown) |
| S24 vs S27 totals per RTO-month | Equal in 3,785 of 3,786. KA16 (Chitradurga) April 2026 is absent from S27; S24 has 3,560, in line with March (4,019) and May (3,227). The gap is in S27, not S24 |
| 33 RTO-months without rows (KA45 9, KA46 7, KA57 17) | Absent identically in S24 and S27, so this is not a fuel-table defect. Whether these months were genuine zeros or unreported cannot be determined. KA57 (STU and Autorikshaw, Shanthinagar) is a specialised office, so zero months are plausible but unproven |
| S24 all-fuel vs official statement (S25), Sep 2026 | 184,194 vs 181,753 (+2,441, +1.3%). By S27 class: non-transport +2,366 (160,062 vs 157,696), transport +75 (24,132 vs 24,057). The gap is almost all non-transport |
| S24 all-fuel vs official statement, Dec 2025 | 130,751 vs 130,313 from the stock difference (+438, +0.3%) |

**Unresolved:**
- **2025 BEV gap (−68):** the S01 export's filter settings and date were not recorded, and VAHAN figures can be revised after the month. The gap cannot be located without a fresh dashboard export.
- **Sep 2026 official gap (+1.3%):** the official statement and the VAHAN dashboard may use different cut-off dates or category rules. This is not determined.

No total was adjusted to match.

## 4. Trends (S28)

| Year | BEV | All fuels | BEV share | Hybrids |
| --- | --- | --- | --- | --- |
| 2022 | 95,770 | 1,532,362 | 6.2% | 0 |
| 2023 | 152,711 (+59.5%) | 1,746,740 | 8.7% | 0 |
| 2024 | 179,230 (+17.4%) | 1,888,157 | 9.5% | 6,293 |
| 2025 | 203,625 (+13.6%) | 1,911,489 | 10.7% | 11,228 |
| 2026 (Jan–Sep) | 231,645 | 1,665,579 | 13.9% | 9,662 |

- **Peak month:** July 2026, with 29,665 BEV registrations.
- **2025 RTO concentration:** the largest RTOs by BEV registrations are KA5 Bengaluru South (11.0% of the state), KA2 Bengaluru West (6.9%), KA3 Bengaluru East (6.7%), KA1 Bengaluru Central (6.6%) and KA51 Electronic City (6.0%).
- **These are RTO figures, not district figures.** Registrations are counted where vehicles are registered, not where they are used or charged.

## 5. RTO-to-district crosswalk

`configs/ka_rto_district_crosswalk.csv` lists all 67 VAHAN RTO codes. **All rows are `unresolved`.** A row can become `verified_official` only with an LGD district code, a jurisdiction basis, a source URL and a retrieval date; the S28 build enforces this.

Sources tried (25 Oct 2026):
- **Transport Department site:** there is no office-jurisdiction page, and the contact page has no list.
- **Parivahan state page:** returns 404.
- **Transport Department annual reports:** the 2018-19 and 2021-22 mirrors on data.opencity.in now return 404, and the dataset is gone.
- **Government of Karnataka contact directory:** rendered client-side, with no transport offices exposed.
- **Web search:** returned only insurance and aggregator pages, which contradict each other (for example KA-29 and KA-41).

None of these were used. Office names (for example "Hunsur ARTO") are **not** treated as jurisdiction evidence. Jurisdictions follow taluks and can change, for example with the creation of Vijayanagara district in 2021 or new ARTOs such as KA70 and KA71.

## 6. Method for joining registrations to charging infrastructure

1. **Statewide:** compare S28 statewide BEV flows with the charger inventory (S15/S18, BEE stations; S11/S23, OSM). This is valid now.
2. **RTO level:** registrations stay at RTO. A charger can be related to an RTO only through a verified jurisdiction polygon or list. None exists yet, so no charger-per-RTO ratio is produced.
3. **District level:** allowed only for RTOs whose crosswalk row is `verified_official`. A district total is reported only if **every** RTO serving that district is verified; otherwise it is "not computable". Several VAHAN RTO names refer to Bengaluru or nearby places (for example KA1–KA5 "Bengaluru ...", KA41 Jnanabharathi, KA51 Electronic City). Their district membership is not verified, so they are not grouped into any district or metro total.
4. **Never:** split RTO or state totals by population, roads or names. Never treat registrations as vehicle locations (R4-19). Never use S24/S27 to infer an EV vehicle-class mix.

## 7. Manual VAHAN export (needs a network that can reach the dashboard)

> The control names below follow the dashboard's usual layout. They could **not** be checked from the project machine (the site is unreachable), so adjust them to what the page actually shows and record the real labels.

1. Open https://vahan.parivahan.gov.in/vahan4dashboard/ and go to the report view.
2. Set the type to "Actual Value", the state to "Karnataka", the RTO to one office (repeat for each), the Y-axis to "Vehicle Class", the X-axis to "Month Wise", and the year to the calendar year (repeat for 2022 to 2026).
3. Under the fuel filter, select only ELECTRIC(BOV) and PURE EV. Record the exact labels shown. Export hybrids separately.
4. Click Refresh, then download the Excel file. If a CAPTCHA appears, solve it by hand; do not automate it.
5. Save each file unchanged as `data/raw/S29_vahan_ka_<RTO>_<year>_class_month_bev.xlsx` and record the export time and filter settings.
6. Check whether each export's class totals per month sum to S24's BEV for that RTO and month.

## 8. Next priority

1. **Manual VAHAN export (section 7)** to get BEV by vehicle class at RTO level.
2. **Official RTO jurisdiction list:** request it from the Transport Department, for example through its contact or RTI channel, or find the gazette notifications that created each RTO and ARTO. Then fill `verified_official` rows with sources.
