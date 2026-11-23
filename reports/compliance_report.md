# CMS Provider Data — Compliance Scorecard

_Automated audit of publicly reported CMS provider-quality data._

**Run (UTC):** 2026-11-23 20:42  
**Commit:** `8a5837a41ae1`  
**Evaluation date:** 2026-11-23

## Executive summary

- Datasets monitored: **7**
- ✅ Fully compliant: **0**
- ⚠️ Compliance exceptions (warnings): **0**
- ❌ Control failures: **7**

## Control matrix

| Dataset | Overall | Availability | Freshness | Conformity | Completeness | Uniqueness | Validity | Integrity |
|---|---|---|---|---|---|---|---|---|
| Facility master — hospital_general_info | ❌ FAIL | ❌ FAIL | ✅ PASS | ❌ FAIL | — | — | — | — |
| Process quality — timely_effective_care | ❌ FAIL | ❌ FAIL | ✅ PASS | ❌ FAIL | — | — | — | — |
| Outcome quality — readmissions_deaths | ❌ FAIL | ❌ FAIL | ❌ FAIL | ❌ FAIL | — | — | — | — |
| Outcome quality — unplanned_visits | ❌ FAIL | ❌ FAIL | ✅ PASS | ❌ FAIL | — | — | — | — |
| Patient safety — healthcare_associated_infections | ❌ FAIL | ❌ FAIL | ✅ PASS | ❌ FAIL | — | — | — | — |
| Patient experience — hcahps | ❌ FAIL | ❌ FAIL | ✅ PASS | ❌ FAIL | — | — | — | — |
| Long-term care — nursing_home_provider_info | ❌ FAIL | ❌ FAIL | ❌ FAIL | ❌ FAIL | — | — | — | — |

## Control detail

### Facility master — `hospital_general_info`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/af9369a8-f9c7-53d6-8d77-dbd4bdfef5ab/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 28 days | CMS last published 2026-10-26 |
| Conformity | ❌ FAIL | missing: Facility ID, Facility Name, State, Hospital Type, Hospital overall rating | Schema drift detected |

### Process quality — `timely_effective_care`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/795adeaf-97bc-5104-86d6-297851391af2/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 35 days | CMS last published 2026-10-19 |
| Conformity | ❌ FAIL | missing: Facility ID, Measure ID, Measure Name, Score | Schema drift detected |

### Outcome quality — `readmissions_deaths`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | No metastore match for keywords: ('readmissions complications and deaths',) |
| Freshness | ❌ FAIL | unknown | CMS published no modified date |
| Conformity | ❌ FAIL | missing: Facility ID, Measure ID, Measure Name, Score | Schema drift detected |

### Outcome quality — `unplanned_visits`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/9fbe0bf5-0433-51b9-a827-0f41883c56fa/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 35 days | CMS last published 2026-10-19 |
| Conformity | ❌ FAIL | missing: Facility ID, Measure ID, Measure Name, Rate | Schema drift detected |

### Patient safety — `healthcare_associated_infections`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/6dfb9217-4d69-5e58-9833-6f693c83c7c7/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 35 days | CMS last published 2026-10-19 |
| Conformity | ❌ FAIL | missing: Facility ID, Measure ID, Measure Name, Score | Schema drift detected |

### Patient experience — `hcahps`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/29ef905d-e864-5e59-8455-f94f5a68fa21/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 35 days | CMS last published 2026-10-19 |
| Conformity | ❌ FAIL | missing: Facility ID, Measure ID, Measure Name, Patient Survey Star Rating | Schema drift detected |

### Long-term care — `nursing_home_provider_info`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | No metastore match for keywords: ('nursing home', 'provider information') |
| Freshness | ❌ FAIL | unknown | CMS published no modified date |
| Conformity | ❌ FAIL | missing: Federal Provider Number, Provider Name, State, Overall Rating | Schema drift detected |

## Data provenance

| Dataset | CMS title | Last modified | Rows | Source |
|---|---|---|---|---|
| `hospital_general_info` | Hospital General Information | 2026-10-26 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/xubh-q36u) |
| `timely_effective_care` | Timely and Effective Care - Hospital | 2026-10-19 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/yv7e-xc69) |
| `readmissions_deaths` | — | — | 0 | [CMS](https://data.cms.gov/provider-data/) |
| `unplanned_visits` | Complications and Unplanned Hospital Visits - PPS-Exempt Cancer Hospital - Hospital | 2026-10-19 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/z8ax-x9j1) |
| `healthcare_associated_infections` | Healthcare Associated Infections - Hospital | 2026-10-19 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/77hc-ibv8) |
| `hcahps` | Patient survey (HCAHPS) - Hospital | 2026-10-19 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/dgck-syfz) |
| `nursing_home_provider_info` | — | — | 0 | [CMS](https://data.cms.gov/provider-data/) |

---
_Generated automatically by the CMS compliance pipeline. Data source: CMS Provider Data Catalog (public aggregate reporting; no PHI processed).
