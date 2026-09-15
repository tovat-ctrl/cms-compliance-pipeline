"""Configuration and dataset registry for the CMS compliance pipeline.

Datasets are matched against the CMS Provider Data Catalog metastore at
runtime by title keywords, so the pipeline keeps working when CMS re-issues
or renames catalog entries.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

PDC_BASE = "https://data.cms.gov/provider-data/api/1"
METASTORE_URL = f"{PDC_BASE}/metastore/schemas/dataset/items?show-reference-ids=true"
DATASTORE_URL = f"{PDC_BASE}/datastore/query/{{distribution_id}}/0"

PAGE_SIZE = 5000
REQUEST_TIMEOUT = 60

# Audit thresholds (data quality control limits)
STALENESS_WARN_DAYS = 95    # CMS refreshes most Care Compare data quarterly
STALENESS_FAIL_DAYS = 190
COMPLETENESS_PASS = 0.005
COMPLETENESS_WARN = 0.05
UNIQUENESS_WARN = 0.01
VALIDITY_PASS = 0.98
VALIDITY_WARN = 0.95
INTEGRITY_PASS = 0.99
INTEGRITY_WARN = 0.98

MASTER_KEY = "hospital_general_info"


@dataclass
class DatasetSpec:
    key: str
    title_keywords: Tuple[str, ...]
    domain: str
    required_columns: Tuple[str, ...]
    unique_columns: Tuple[str, ...] = ()
    range_checks: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    references_master: bool = False


DATASETS: List[DatasetSpec] = [
    DatasetSpec(
        key=MASTER_KEY,
        title_keywords=("hospital general information",),
        domain="Facility master",
        required_columns=("Facility ID", "Facility Name", "State", "Hospital Type", "Hospital overall rating"),
        unique_columns=("Facility ID",),
        range_checks={"Hospital overall rating": (1, 5)},
    ),
    DatasetSpec(
        key="timely_effective_care",
        title_keywords=("timely and effective care", "hospital"),
        domain="Process quality",
        required_columns=("Facility ID", "Measure ID", "Measure Name", "Score"),
        unique_columns=("Facility ID", "Measure ID"),
        range_checks={"Score": (0, 100)},
        references_master=True,
    ),
    DatasetSpec(
        key="readmissions_deaths",
        title_keywords=("readmissions complications and deaths",),
        domain="Outcome quality",
        required_columns=("Facility ID", "Measure ID", "Measure Name", "Score"),
        unique_columns=("Facility ID", "Measure ID"),
        range_checks={"Score": (0, 100)},
        references_master=True,
    ),
    DatasetSpec(
        key="unplanned_visits",
        title_keywords=("unplanned hospital visits",),
        domain="Outcome quality",
        required_columns=("Facility ID", "Measure ID", "Measure Name", "Rate"),
        unique_columns=("Facility ID", "Measure ID"),
        range_checks={"Rate": (0, 100)},
        references_master=True,
    ),
    DatasetSpec(
        key="healthcare_associated_infections",
        title_keywords=("healthcare associated infections",),
        domain="Patient safety",
        required_columns=("Facility ID", "Measure ID", "Measure Name", "Score"),
        unique_columns=("Facility ID", "Measure ID"),
        range_checks={"Score": (0, 100)},
        references_master=True,
    ),
    DatasetSpec(
        key="hcahps",
        title_keywords=("patient survey", "hospital"),
        domain="Patient experience",
        required_columns=("Facility ID", "Measure ID", "Measure Name", "Patient Survey Star Rating"),
        unique_columns=("Facility ID", "Measure ID"),
        range_checks={"Patient Survey Star Rating": (1, 5)},
        references_master=True,
    ),
    DatasetSpec(
        key="nursing_home_provider_info",
        title_keywords=("nursing home", "provider information"),
        domain="Long-term care",
        required_columns=("Federal Provider Number", "Provider Name", "State", "Overall Rating"),
        unique_columns=("Federal Provider Number",),
        range_checks={"Overall Rating": (1, 5)},
    ),
]
