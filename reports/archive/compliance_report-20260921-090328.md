# CMS Provider Data — Compliance Scorecard

_Automated audit of publicly reported CMS provider-quality data._

**Run (UTC):** 2026-09-21 09:03  
**Commit:** `45766e775ee0`  
**Evaluation date:** 2026-09-21

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
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/90fa4cdf-f49d-556d-8790-d32fbbec40c6/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 61 days | CMS last published 2026-07-22 |
| Conformity | ❌ FAIL | missing: Facility ID, Facility Name, State, Hospital Type, Hospital overall rating | Schema drift detected |

### Process quality — `timely_effective_care`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/c99ae75e-0a7d-5db4-99ed-3ba2b7324baf/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 61 days | CMS last published 2026-07-22 |
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
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/9bcf37d7-d942-538a-a7e7-0362cfd86dda/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 61 days | CMS last published 2026-07-22 |
| Conformity | ❌ FAIL | missing: Facility ID, Measure ID, Measure Name, Rate | Schema drift detected |

### Patient safety — `healthcare_associated_infections`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/e0d50f03-1d75-57ac-a6a9-60bf9cdb9407/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 61 days | CMS last published 2026-07-22 |
| Conformity | ❌ FAIL | missing: Facility ID, Measure ID, Measure Name, Score | Schema drift detected |

### Patient experience — `hcahps`

| Control | Status | Result | Detail |
|---|---|---|---|
| Availability | ❌ FAIL | extraction error | Extraction failed: 404 Client Error: Not Found for url: https://data.cms.gov/provider-data/api/1/datastore/query/b42ae2a7-5512-5cb4-b429-d3eaaab212d7/0?limit=5000&offset=0 |
| Freshness | ✅ PASS | 61 days | CMS last published 2026-07-22 |
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
| `hospital_general_info` | Hospital General Information | 2026-07-22 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/xubh-q36u) |
| `timely_effective_care` | Timely and Effective Care - Hospital | 2026-07-22 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/yv7e-xc69) |
| `readmissions_deaths` | — | — | 0 | [CMS](https://data.cms.gov/provider-data/) |
| `unplanned_visits` | Complications and Unplanned Hospital Visits - PPS-Exempt Cancer Hospital - Hospital | 2026-07-22 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/z8ax-x9j1) |
| `healthcare_associated_infections` | Healthcare Associated Infections - Hospital | 2026-07-22 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/77hc-ibv8) |
| `hcahps` | Patient survey (HCAHPS) - Hospital | 2026-07-22 | 0 | [CMS](https://data.cms.gov/provider-data/dataset/dgck-syfz) |
| `nursing_home_provider_info` | — | — | 0 | [CMS](https://data.cms.gov/provider-data/) |

---
_Generated automatically by the CMS compliance pipeline. Data source: CMS Provider Data Catalog (public aggregate reporting; no PHI processed).
