"""Reporting layer: render the audit-ready compliance scorecard."""

import datetime as dt

ICON = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}
SEVERITY = {"PASS": 0, "WARN": 1, "FAIL": 2}
CATEGORIES = ["Availability", "Freshness", "Conformity", "Completeness", "Uniqueness", "Validity", "Integrity"]


def _worst(statuses):
    return max(statuses, key=lambda status: SEVERITY[status])


def _category(checks, prefix):
    matching = [check["status"] for check in checks if check["check"].startswith(prefix)]
    if not matching:
        return "—"
    worst = _worst(matching)
    return f"{ICON[worst]} {worst}"


def render_report(extraction, results, run_date, commit=None) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    dataset_status = {key: _worst([c["status"] for c in checks]) for key, checks in results.items()}
    counts = {s: sum(1 for value in dataset_status.values() if value == s) for s in ("PASS", "WARN", "FAIL")}

    out = []
    out.append("# CMS Provider Data — Compliance Scorecard")
    out.append("")
    out.append("_Automated audit of publicly reported CMS provider-quality data._")
    out.append("")
    out.append(f"**Run (UTC):** {now:%Y-%m-%d %H:%M}  ")
    if commit:
        out.append(f"**Commit:** `{commit[:12]}`  ")
    out.append(f"**Evaluation date:** {run_date:%Y-%m-%d}")
    out.append("")

    out.append("## Executive summary")
    out.append("")
    out.append(f"- Datasets monitored: **{len(results)}**")
    out.append(f"- {ICON['PASS']} Fully compliant: **{counts['PASS']}**")
    out.append(f"- {ICON['WARN']} Compliance exceptions (warnings): **{counts['WARN']}**")
    out.append(f"- {ICON['FAIL']} Control failures: **{counts['FAIL']}**")
    out.append("")

    out.append("## Control matrix")
    out.append("")
    out.append("| Dataset | Overall | " + " | ".join(CATEGORIES) + " |")
    out.append("|" + "---|" * (len(CATEGORIES) + 2))
    for key, checks in results.items():
        spec = extraction[key]["spec"]
        cells = [_category(checks, category) for category in CATEGORIES]
        overall = f"{ICON[dataset_status[key]]} {dataset_status[key]}"
        out.append(f"| {spec.domain} — {key} | {overall} | " + " | ".join(cells) + " |")
    out.append("")

    out.append("## Control detail")
    for key, checks in results.items():
        spec = extraction[key]["spec"]
        out.append("")
        out.append(f"### {spec.domain} — `{key}`")
        out.append("")
        out.append("| Control | Status | Result | Detail |")
        out.append("|---|---|---|---|")
        for check in checks:
            out.append(
                f"| {check['check']} | {ICON[check['status']]} {check['status']} | {check['value']} | {check['detail']} |"
            )
    out.append("")

    out.append("## Data provenance")
    out.append("")
    out.append("| Dataset | CMS title | Last modified | Rows | Source |")
    out.append("|---|---|---|---|---|")
    for key, outcome in extraction.items():
        meta = outcome.get("meta") or {}
        title = meta.get("title") or "—"
        modified = str(meta.get("modified") or "—")[:10]
        rows = len(outcome.get("rows") or [])
        link = meta.get("landing_page") or "https://data.cms.gov/provider-data/"
        out.append(f"| `{key}` | {title} | {modified} | {rows:,} | [CMS]({link}) |")
    out.append("")

    out.append("---")
    out.append(
        "_Generated automatically by the CMS compliance pipeline. "
        "Data source: CMS Provider Data Catalog (public aggregate reporting; no PHI processed)."
    )
    return "\n".join(out) + "\n"
