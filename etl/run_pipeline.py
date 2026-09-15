"""Pipeline orchestrator. Run with `python -m etl.run_pipeline`."""

import datetime as dt
import json
import logging
import os
from pathlib import Path

from etl.extract import extract_all
from etl.report import render_report
from etl.validate import run_all_checks

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"


def main() -> int:
    run_date = dt.date.today()
    commit = os.environ.get("GITHUB_SHA")
    logging.info("Starting CMS compliance pipeline run for %s", run_date)

    extraction = extract_all()
    results = run_all_checks(extraction, run_date)

    report = render_report(extraction, results, run_date, commit=commit)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "compliance_report.md").write_text(report, encoding="utf-8")
    archive = REPORTS_DIR / "archive"
    archive.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    (archive / f"compliance_report-{stamp}.md").write_text(report, encoding="utf-8")

    machine = {
        "run_date": run_date.isoformat(),
        "commit": commit,
        "datasets": {
            key: {
                "title": (outcome.get("meta") or {}).get("title"),
                "rows": len(outcome.get("rows") or []),
                "error": outcome["error"],
                "checks": results[key],
            }
            for key, outcome in extraction.items()
        },
    }
    (REPORTS_DIR / "run_metadata.json").write_text(json.dumps(machine, indent=2), encoding="utf-8")

    failed = [key for key, checks in results.items() if any(check["status"] == "FAIL" for check in checks)]
    logging.info("Pipeline complete. Datasets with failures: %s", failed or "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
