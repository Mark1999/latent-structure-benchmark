"""Dispatch templates: copy-ready Markdown blocks pre-filled with numeric evidence.

These templates surface QA findings in a format Mark can copy and paste for
follow-up actions (model provider contact, campaign decisions). No dispatch
mechanism is included; the copy affordance is client-side only.

Wording follows the divergence boundary label:
  "persisted = qa_passed at collection time;
   recomputed = current run_record_checks rules"

No LLM imports. No dispatch mechanism. Text only. Rule 14 compliant.
CDA SME reviews this wording per plan section 6 (T7).
"""

from __future__ import annotations

from dataclasses import dataclass

from cdb_social.admin_console.qa.divergence import DivergenceRow
from cdb_social.admin_console.qa.histogram import HistogramRow


@dataclass
class DispatchTemplate:
    """One copy-ready Markdown block for the QA panel."""

    title: str
    content: str  # Markdown text with numeric evidence


def build_templates(
    histogram_rows: list[HistogramRow],
    divergence_rows: list[DivergenceRow],
) -> list[DispatchTemplate]:
    """Build copy-ready Markdown templates from QA data.

    Returns a list of DispatchTemplate objects. Each template has a title
    and a Markdown content block suitable for copy-paste.

    Returns at least one template (the summary block) even when there are
    no failures or divergences.
    """
    templates: list[DispatchTemplate] = []

    templates.append(_build_summary_template(histogram_rows, divergence_rows))

    # Per-model failure templates (only when failures exist).
    models_with_failures = sorted(
        {row.model_id for row in histogram_rows}
    )
    for model_id in models_with_failures:
        model_rows = [r for r in histogram_rows if r.model_id == model_id]
        templates.append(_build_model_failure_template(model_id, model_rows))

    # Divergence template (only when divergence exists).
    if divergence_rows:
        templates.append(_build_divergence_template(divergence_rows))

    return templates


def _build_summary_template(
    histogram_rows: list[HistogramRow],
    divergence_rows: list[DivergenceRow],
) -> DispatchTemplate:
    total_failures = sum(r.count for r in histogram_rows)
    affected_models = len({r.model_id for r in histogram_rows})
    divergence_count = len(divergence_rows)

    lines = [
        "## QA Summary",
        "",
        f"- Total check failures: {total_failures}",
        f"- Models with failures: {affected_models}",
        (
            f"- Records diverging between persisted qa_passed and recomputed: "
            f"{divergence_count}"
        ),
    ]

    if total_failures == 0 and divergence_count == 0:
        lines.append("")
        lines.append("No failures or divergence detected.")

    content = "\n".join(lines)
    return DispatchTemplate(title="QA Summary", content=content)


def _build_model_failure_template(
    model_id: str,
    rows: list[HistogramRow],
) -> DispatchTemplate:
    total = sum(r.count for r in rows)
    by_check = sorted(rows, key=lambda r: r.check_num)

    lines = [
        f"## Check failures: {model_id}",
        "",
        f"Total failures: {total}",
        "",
        "| Check | Count |",
        "|---|---|",
    ]
    for row in by_check:
        lines.append(f"| Check {row.check_num} | {row.count} |")

    content = "\n".join(lines)
    return DispatchTemplate(
        title=f"Failures: {model_id}",
        content=content,
    )


def _build_divergence_template(
    rows: list[DivergenceRow],
) -> DispatchTemplate:
    """Render a Markdown block listing divergent records.

    Boundary label: persisted = qa_passed at collection time;
    recomputed = current run_record_checks rules.
    """
    lines = [
        "## QA Divergence",
        "",
        (
            "Boundary: persisted = qa_passed at collection time; "
            "recomputed = current run_record_checks rules."
        ),
        "",
        f"Records with divergence: {len(rows)}",
        "",
        "| informant_id | model_id | domain | persisted | recomputed checks | error |",
        "|---|---|---|---|---|---|",
    ]

    for row in rows:
        persisted_str = "pass" if row.persisted_passed else "fail"
        checks_str = (
            ", ".join(f"C{n}" for n in sorted(row.recomputed_check_nums))
            if row.recomputed_check_nums
            else "pass"
        )
        error_str = row.error[:60] + "..." if row.error and len(row.error) > 60 else row.error or ""
        lines.append(
            f"| {row.informant_id} | {row.model_id} | {row.domain_slug}"
            f" | {persisted_str} | {checks_str} | {error_str} |"
        )

    content = "\n".join(lines)
    return DispatchTemplate(title="QA Divergence", content=content)
