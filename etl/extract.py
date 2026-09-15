"""Extraction layer: pull datasets from the CMS Provider Data Catalog API."""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

import requests

from etl.config import (
    DATASETS,
    DATASTORE_URL,
    METASTORE_URL,
    PAGE_SIZE,
    REQUEST_TIMEOUT,
    DatasetSpec,
)

logger = logging.getLogger(__name__)
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch_metastore() -> List[dict]:
    """Return dataset metadata items from the CMS Provider Data Catalog metastore."""
    logger.info("Fetching CMS Provider Data Catalog metastore")
    response = requests.get(METASTORE_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def resolve_distribution(metastore: List[dict], spec: DatasetSpec) -> Optional[dict]:
    """Match a dataset spec to a metastore item by title keywords."""
    for item in metastore:
        title = (item.get("title") or "").lower()
        if all(keyword in title for keyword in spec.title_keywords):
            distributions = item.get("distribution", [])
            if distributions:
                return {
                    "title": item.get("title"),
                    "modified": item.get("modified"),
                    "landing_page": item.get("landingPage"),
                    "distribution_id": distributions[0].get("identifier"),
                }
    return None


def fetch_rows(distribution_id: str) -> List[dict]:
    """Paginate through the datastore query endpoint for a distribution."""
    rows: List[dict] = []
    offset = 0
    while True:
        response = requests.get(
            DATASTORE_URL.format(distribution_id=distribution_id),
            params={"limit": PAGE_SIZE, "offset": offset},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        batch = payload.get("results", [])
        rows.extend(batch)
        total = payload.get("count", len(rows))
        offset += PAGE_SIZE
        if not batch or offset >= total:
            break
    return rows


def save_csv(key: str, rows: List[dict]) -> Path:
    """Persist a raw snapshot (gitignored; regenerated every run)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{key}.csv"
    if rows:
        fieldnames = list(dict.fromkeys(column for row in rows for column in row))
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        path.write_text("", encoding="utf-8")
    return path


def extract_all() -> Dict[str, dict]:
    """Extract every registered dataset; one failure never blocks the others."""
    metastore = fetch_metastore()
    outcomes: Dict[str, dict] = {}
    for spec in DATASETS:
        outcome = {"spec": spec, "meta": None, "rows": [], "error": None}
        try:
            meta = resolve_distribution(metastore, spec)
            if meta is None or not meta.get("distribution_id"):
                outcome["error"] = f"No metastore match for keywords: {spec.title_keywords}"
            else:
                outcome["meta"] = meta
                logger.info("Fetching %s — %s", spec.key, meta.get("title"))
                outcome["rows"] = fetch_rows(meta["distribution_id"])
                logger.info("Fetched %d rows for %s", len(outcome["rows"]), spec.key)
                save_csv(spec.key, outcome["rows"])
        except requests.RequestException as exc:
            outcome["error"] = f"Extraction failed: {exc}"
            logger.error("%s: %s", spec.key, outcome["error"])
        outcomes[spec.key] = outcome
    return outcomes
