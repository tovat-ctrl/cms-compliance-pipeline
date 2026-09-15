# Case Study: Automated CMS Provider Data Compliance Pipeline

**Role:** Designer and developer (solo project)
**Stack:** Python, requests, GitHub Actions
**Status:** Live — runs weekly on a schedule, fully reproducible from source

## The problem

Hospitals, payers, and consultants rely on publicly reported CMS provider-quality data — Care Compare hospital ratings, readmission and complication measures, infection rates, patient experience scores, nursing home ratings — to benchmark performance and identify quality problems. That data has three characteristics that make it hard to trust casually:

1. **Rolling refresh schedules.** CMS re-publishes datasets on quarterly or semiannual cycles that differ per dataset. A report built in January may silently rely on stale data in July.
2. **Schema drift.** Column names, measure identifiers, and dataset catalog IDs change between releases.
3. **Volume.** Seven core datasets translate to hundreds of thousands of rows — too much to eyeball.

Manual review does not scale, and one-off scripts break silently. What is needed is continuous, audit-ready monitoring with a documented control framework and an immutable evidence trail.

## The solution

This repository implements that monitoring as a scheduled, self-healing pipeline:

- **Metadata-driven extraction.** The pipeline resolves dataset identifiers from the CMS Provider Data Catalog metastore at runtime rather than hardcoding IDs, so catalog re-issues do not break it.
- **Seven audit-style controls per dataset** — availability, freshness, conformity, completeness, uniqueness, validity, and referential integrity — each with documented pass/warn/fail thresholds centralized in a single config file that an auditor can review without reading code.
- **Fail-soft architecture.** A failure in one dataset is recorded as an availability finding and never blocks the others.
- **Automated, versioned reporting.** A weekly GitHub Actions run regenerates the compliance scorecard and archives it immutably by timestamp, producing a longitudinal audit trail.
- **Privacy by design.** Only public aggregate reporting data is processed — no beneficiary-level or claims data, so no PHI exposure risk.

## How the controls map to audit practice

The control set mirrors the dimensions a reviewer examines in a healthcare data-availability review:

| Pipeline control | Audit dimension it demonstrates |
| --- | --- |
| Availability | Data can be obtained when needed |
| Freshness | Data is current for the measurement period |
| Conformity | Data matches the expected specification |
| Completeness | Required fields are populated |
| Uniqueness | Records are not duplicated |
| Validity | Values fall within plausible ranges |
| Referential integrity | Related records reconcile across files |

This is the same logic used to evaluate whether a measure can be trusted for reporting and payment decisions — applied continuously instead of annually.

## Skills demonstrated

- ETL design against a live public API, including pagination and runtime metadata resolution
- Data quality control design with documented, reviewable thresholds
- Data governance documentation: provenance capture, versioned reporting, and audit trail
- CI/CD automation with scheduled execution and auto-commit of artifacts
- Privacy-safe design (public aggregate data only; no PHI)

## How to verify

Anyone can reproduce the result: trigger the workflow from the Actions tab (or run `python -m etl.run_pipeline` locally) and inspect `reports/compliance_report.md` and `reports/archive/`. The pipeline is deterministic against the current CMS catalog.

## Data use

All data originates from the CMS Provider Data Catalog and is subject to CMS public information posting terms. This project is not affiliated with or endorsed by CMS.
