# CMS Provider Data Compliance Pipeline

An automated data pipeline that extracts CMS public-use provider quality files,
runs them through a named control suite, loads what passes into an analytical
warehouse, and publishes a signed audit trail and compliance report on every run.

The point is not that it moves data. The point is that it can prove what it
moved, where it came from, and what it refused to accept.

**Latest run:** 11 datasets · 904,235 rows · 109 controls · 0 blocking failures

---

## Why this exists

Most public-health data work fails quietly. An upstream file gets republished
with a renamed column, a measure gets retired, a state stops reporting, and the
dashboard keeps rendering — just wrong. Nobody finds out until someone asks a
question the numbers can't answer.

This pipeline is built on the assumption that silent failure is the actual risk.
Every dataset is gated before it reaches the warehouse, every gate is named and
severity-tagged, and every run leaves an append-only record that a reviewer can
reconstruct without rerunning anything.

---

## Architecture

```
  CMS Provider Data Catalog  (data.cms.gov — public use files)
            │
            │  dataset_id ──► live distribution_id
            ▼
   ┌──────────────────┐
   │  catalog.py      │  resolves stable IDs to current distributions,
   │                  │  captures modified / released / next-update dates
   └────────┬─────────┘
            ▼
   ┌──────────────────┐
   │  extract.py      │  concurrent pagination, retry w/ backoff,
   │                  │  SHA-256 payload hash, Parquet snapshot
   └────────┬─────────┘
            │
            ├──────────────►  data/raw/dataset=<key>/ingest_date=<date>/
            ▼
   ┌──────────────────┐
   │  validate.py     │  9 named controls, severity-tagged
   │                  │
   │   blocking ──────┼──►  dataset NOT promoted · exit code 1
   │   advisory ──────┼──►  logged, scored, surfaced on report
   └────────┬─────────┘
            ▼  (passing datasets only)
   ┌──────────────────┐
   │  warehouse.py    │  raw_<key> per source
   │   DuckDB         │  dim_facility · fact_quality_measure
   │                  │  vw_compliance_summary · vw_measure_coverage
   └────────┬─────────┘
            ▼
   ┌──────────────────┐      ┌──────────────────┐
   │  audit.py        │      │  scorecard.py    │
   │  runs.jsonl      │─────►│  weighted grade  │
   │  manifest_<id>   │      └────────┬─────────┘
   └──────────────────┘               ▼
                            ┌──────────────────┐
                            │  report.py       │  self-contained HTML
                            └──────────────────┘
```

---

## The control suite

Each control is a named test with an observed value and a threshold — the same
shape a control-testing workpaper takes, so results drop straight into a review
package.

| ID | Control | Severity | What it catches |
|---|---|---|---|
| SCHEMA-01 | Required columns present | Blocking | Upstream renames or drops a column |
| KEY-01 | Primary key columns present | Blocking | Grain cannot be established |
| KEY-02 | Primary key unique | Advisory | Misunderstood grain, or upstream fan-out |
| FRESH-01 | Published within expected cadence | Advisory | File has gone stale |
| FRESH-02 | CMS next-update date not passed | Advisory | CMS missed its own schedule |
| VOL-01 | Row count within drift tolerance | Advisory | Partial load, or a reporting collapse |
| NULL-01 | Null rate on required columns | Advisory | A column silently stopped populating |
| TYPE-01 | Numeric measures parse cleanly | Advisory | Measure became fully suppressed |
| PHI-01 | No direct-identifier columns | Blocking | A non-public file entered a public pipeline |

**Blocking** stops the dataset from being promoted to the warehouse and returns
exit code 1, so CI treats a data-quality regression the same way it treats a
broken build. **Advisory** is logged, scored, and reported but does not halt the
run. Datasets marked `criticality: low` have their blocking controls downgraded
automatically.

### PHI-01 is deliberately paranoid

Every source here is a CMS public-use file, so PHI-01 should never fire. That is
exactly why it is a blocking control rather than a comment in the README. It
screens every ingested schema for direct-identifier column patterns — SSN, MBI,
HICN, MRN, beneficiary ID, date of birth, patient name, member ID — and blocks
promotion on any match. A control that only matters when something has already
gone badly wrong is worth the eleven lines it costs.

---

## The controls found real defects

A validation layer that only ever passes proves nothing. Three findings from the
first full run, all genuine:

**Maternal Health flagged 74% duplicate keys.** The file is published at
facility × measure grain — four maternal measures per hospital (PC_02, PC_07a,
PC_07b, SM_7) — not one row per facility. The registry had the grain wrong.
Fixed by correcting the primary key to `[facility_id, measure_id]`.

**Maternal Health flagged 0% numeric parse.** Those measures are categorical:
`Yes`, `No`, `Not Applicable (our hospital does not provide inpatient
labor/delivery care)`. Fixed by adding a `numeric_measure: false` flag to the
registry rather than lowering the threshold, so the control keeps its teeth
everywhere else.

**The clinician file flagged 8% duplicate keys.** A clinician can be enrolled at
many practice addresses under a single group PAC ID, so the address key is part
of the grain. Fixed by extending the key to `[npi, org_pac_id, adrs_id]`.

---

## A finding in the data itself

CMS suppresses small-cell measure values to protect patient privacy, and the
pipeline preserves that as a distinct state (`is_suppressed`) rather than
collapsing it into null. The rates are high and uneven:

| Domain | Rows | Suppressed |
|---|---:|---:|
| Quality | 491,320 | 52.3% |
| Experience | 325,720 | 41.1% |
| Cost | 4,626 | 37.9% |

State-level variation is wider still — Texas quality measures run 57.3%
suppressed against California's 43.0%. Any downstream analysis treating these as
missing-at-random will be biased toward larger facilities in larger states,
because suppression correlates with volume. Keeping suppression distinguishable
from absence is a modelling decision, not a formatting one.

---

## Quick start

```bash
pip install -r requirements.txt

python -m pipeline.cli run                              # full portfolio
python -m pipeline.cli run --only hospital_general      # single dataset
python -m pipeline.cli catalog --search "nursing home"  # browse CMS catalog
python -m pipeline.cli report                           # rebuild HTML only

python -m pytest tests/ -q                              # 32 tests, offline
```

A full run takes roughly 5–7 minutes and writes:

```
data/raw/dataset=<key>/ingest_date=<date>/data.parquet   immutable snapshots
data/warehouse/cms.duckdb                                queryable warehouse
data/audit/runs.jsonl                                    append-only ledger
data/audit/manifest_<run_id>.json                        full run record
data/audit/scorecard.json                                graded assessment
data/reports/compliance_report.html                      control report
```

---

## Querying the warehouse

```python
import duckdb
con = duckdb.connect("data/warehouse/cms.duckdb")

con.execute("""
    SELECT state, domain, facilities, suppression_pct, avg_score
    FROM vw_compliance_summary
    ORDER BY measure_rows DESC
    LIMIT 10
""").df()
```

Conformed model:

- `dim_facility` — 32,569 providers across hospitals, SNFs, and home health
  agencies, with ownership, type, and overall rating
- `fact_quality_measure` — 821,666 rows at facility × measure grain, spanning
  quality, experience, and cost domains, with `score_numeric`, `score_raw`, and
  `is_suppressed` kept separate
- `vw_compliance_summary` — state × domain rollup
- `vw_measure_coverage` — per-measure reporting participation

Every table carries `_dataset_key`, `_cms_modified`, and `_ingested_at`, so any
row can be traced back to the run and the upstream file version that produced it.

---

## Reproducibility

Each run writes a content hash taken over the extracted payload before any
transformation. An unchanged hash across two runs is proof the upstream file did
not move; a changed hash on a dataset CMS claims it did not modify is a finding
worth chasing.

Paired with the date-partitioned Parquet snapshots, any prior state of the
warehouse can be rebuilt and diffed against the current one without re-querying
CMS. The audit ledger is append-only and never rewritten.

---

## Automation

`.github/workflows/pipeline.yml` runs the suite weekly, restores the prior audit
ledger so drift controls have a baseline, retains the report and warehouse as
build artifacts for 90 and 30 days, publishes the report to GitHub Pages, and
writes a graded summary table to the run page. A blocking control failure fails
the job.

---

## Adding a dataset

Datasets are registered declaratively in `config/datasets.yml`. The pipeline
covers 11 of the 237 datasets in the CMS catalog; adding another is a config
change, not a code change:

```yaml
  - key: dialysis_facilities
    dataset_id: 23ew-n7w9
    title: Dialysis Facility Quality
    domain: quality
    grain: facility_measure
    criticality: high
    expected_cadence_days: 120
    primary_key: [facility_id, measure_id]
    required_columns: [facility_id, measure_id]
```

Use `python -m pipeline.cli catalog --search "dialysis"` to find the identifier.

---

## Scoring

Deliberately transparent — a weighted deduction model rather than an index,
because a compliance score nobody can reconstruct by hand is a score nobody will
trust in a review.

```
dataset score = 100 − (25 × blocking failures) − (6 × advisory failures)
portfolio     = criticality-weighted mean (high ×3, medium ×2, low ×1)

A ≥ 90   B ≥ 80   C ≥ 70   D ≥ 60   F < 60
```

---

## Data handling

All sources are CMS public-use files. No PHI, no beneficiary-level records, and
no direct identifiers are ingested, stored, or emitted. The attestation is
carried in every run manifest and enforced by control PHI-01.

Source: Centers for Medicare & Medicaid Services Provider Data Catalog,
`https://data.cms.gov/provider-data/`.
