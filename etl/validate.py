"""Validation layer: audit-style data quality controls.

Controls are modeled on healthcare data-availability audit logic
(completeness, accuracy, timeliness, uniqueness, referential integrity),
adapted for publicly reported CMS provider data.
"""

import datetime as dt
from typing import Dict, List, Optional, Set

from etl.config import (
    COMPLETENESS_PASS,
    COMPLETENESS_WARN,
    INTEGRITY_PASS,
    INTEGRITY_WARN,
    MASTER_KEY,
    STALENESS_FAIL_DAYS,
    STALENESS_WARN_DAYS,
    UNIQUENESS_WARN,
    VALIDITY_PASS,
    VALIDITY_WARN,
)

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
MISSING_MARKERS = ("", "Not Available", "N/A", "None")


def _is_missing(value) -> bool:
    return value is None or str(value).strip() in MISSING_MARKERS


def _result(check: str, status: str, value, detail: str) -> dict:
    return {"check": check, "status": status, "value": value, "detail": detail}


def check_availability(outcome: dict) -> dict:
    if outcome["error"]:
        return _result("Availability", FAIL, "extraction error", outcome["error"])
    n_rows = len(outcome.get("rows") or [])
    status = PASS if n_rows > 0 else FAIL
    return _result("Availability", status, f"{n_rows:,} rows", "Dataset extracted from CMS API")


def check_freshness(outcome: dict, run_date: dt.date) -> dict:
    modified = (outcome.get("meta") or {}).get("modified")
    if not modified:
        return _result("Freshness", FAIL, "unknown", "CMS published no modified date")
    last_modified = dt.date.fromisoformat(str(modified)[:10])
    age = (run_date - last_modified).days
    if age <= STALENESS_WARN_DAYS:
        status = PASS
    elif age <= STALENESS_FAIL_DAYS:
        status = WARN
    else:
        status = FAIL
    return _result("Freshness", status, f"{age} days", f"CMS last published {last_modified.isoformat()}")


def check_conformity(outcome: dict) -> dict:
    rows = outcome.get("rows") or []
    spec = outcome["spec"]
    columns = set().union(*(row.keys() for row in rows)) if rows else set()
    missing = [column for column in spec.required_columns if column not in columns]
    if not missing:
        return _result("Conformity", PASS, "all required columns present", "Schema conforms to registry")
    return _result("Conformity", FAIL, f"missing: {', '.join(missing)}", "Schema drift detected")


def check_completeness(outcome: dict) -> List[dict]:
    rows = outcome.get("rows") or []
    spec = outcome["spec"]
    results = []
    if not rows:
        return results
    for column in spec.required_columns:
        if column not in rows[0]:
            continue
        missing = sum(1 for row in rows if _is_missing(row.get(column)))
        rate = missing / len(rows)
        if rate <= COMPLETENESS_PASS:
            status = PASS
        elif rate <= COMPLETENESS_WARN:
            status = WARN
        else:
            status = FAIL
        results.append(
            _result(
                f"Completeness [{column}]",
                status,
                f"{1 - rate:.1%} populated",
                f"{missing:,} missing of {len(rows):,}",
            )
        )
    return results


def check_uniqueness(outcome: dict) -> List[dict]:
    rows = outcome.get("rows") or []
    spec = outcome["spec"]
    if not spec.unique_columns or not rows:
        return []
    if not all(column in rows[0] for column in spec.unique_columns):
        return []
    seen = set()
    duplicates = 0
    for row in rows:
        key = tuple(str(row.get(column)) for column in spec.unique_columns)
        if key in seen:
            duplicates += 1
        seen.add(key)
    rate = duplicates / len(rows)
    status = PASS if rate == 0 else (WARN if rate <= UNIQUENESS_WARN else FAIL)
    label = " + ".join(spec.unique_columns)
    return [
        _result(
            f"Uniqueness [{label}]",
            status,
            f"{rate:.2%} duplicate keys",
            f"{duplicates:,} duplicate rows of {len(rows):,}",
        )
    ]


def check_validity(outcome: dict) -> List[dict]:
    rows = outcome.get("rows") or []
    spec = outcome["spec"]
    results = []
    if not rows:
        return results
    for column, (low, high) in spec.range_checks.items():
        if column not in rows[0]:
            continue
        values = [row.get(column) for row in rows if not _is_missing(row.get(column))]
        if not values:
            continue
        in_range = 0
        for value in values:
            try:
                in_range += low <= float(value) <= high
            except (TypeError, ValueError):
                pass
        rate = in_range / len(values)
        if rate >= VALIDITY_PASS:
            status = PASS
        elif rate >= VALIDITY_WARN:
            status = WARN
        else:
            status = FAIL
        results.append(
            _result(
                f"Validity [{column}]",
                status,
                f"{rate:.1%} in range",
                f"Expected values between {low:g} and {high:g}",
            )
        )
    return results


def check_integrity(outcome: dict, master_ids: Optional[Set[str]]) -> List[dict]:
    spec = outcome["spec"]
    if not spec.references_master or master_ids is None:
        return []
    rows = outcome.get("rows") or []
    if not rows:
        return []
    total = orphan = 0
    for row in rows:
        facility = row.get("Facility ID")
        if _is_missing(facility):
            continue
        total += 1
        if str(facility) not in master_ids:
            orphan += 1
    if total == 0:
        return []
    rate = 1 - orphan / total
    if rate >= INTEGRITY_PASS:
        status = PASS
    elif rate >= INTEGRITY_WARN:
        status = WARN
    else:
        status = FAIL
    return [
        _result(
            "Referential integrity",
            status,
            f"{rate:.2%} match facility master",
            f"{orphan:,} facility IDs not in Hospital General Information of {total:,}",
        )
    ]


def run_all_checks(extraction: Dict[str, dict], run_date: dt.date) -> Dict[str, List[dict]]:
    master = extraction.get(MASTER_KEY, {})
    master_ids = None
    if master.get("rows"):
        master_ids = {
            str(row.get("Facility ID"))
            for row in master["rows"]
            if not _is_missing(row.get("Facility ID"))
        }
    results: Dict[str, List[dict]] = {}
    for key, outcome in extraction.items():
        checks = [
            check_availability(outcome),
            check_freshness(outcome, run_date),
            check_conformity(outcome),
        ]
        checks += check_completeness(outcome)
        checks += check_uniqueness(outcome)
        checks += check_validity(outcome)
        checks += check_integrity(outcome, master_ids)
        results[key] = checks
    return results
