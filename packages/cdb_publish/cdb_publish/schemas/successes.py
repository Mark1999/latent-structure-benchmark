"""Publish-layer schema for the per-domain successful-records summary JSON.

These are dashboard-internal schemas that describe the shape of
apps/dashboard/public/data/records/{slug}.json. They are NOT part of
the cdb_core open-data-bundle schema contract (which is governed by
cdb_core/schemas.py and docs/DATA_DICTIONARY.md §9-10). Changes here
do not trigger CLAUDE.md R6 or a DATA_DICTIONARY.md co-update for
cdb_core; they do require updating the DATA_DICTIONARY.md §12.6 section
that documents the published successful-records summary JSON shape.

See docs/status/2026-06-10-collection-records-rework-kickoff.md §4
Task 4, and docs/status/2026-06-10-collection-records-rework-verdicts.md
CR-T4 for the CDA SME framing requirements applied to this shape.

"Successful" here means the LSB pipeline parsed a primary-step response.
It is NOT a quality judgment on the model output. See the framing_note
field on PublishedSuccessesFile and DATA_DICTIONARY.md §12.6.
"""

from __future__ import annotations

from pydantic import BaseModel


class PublishedSuccessesByModelRow(BaseModel):
    """Per-model-id summary row in the published per-domain records JSON.

    Each row aggregates all InformantRecord lines for a single model_id
    within this domain. ``n_runs`` counts every line (including
    ``qa_passed=False``); ``n_qa_passed`` counts the QA-passed subset.
    The gap between the two is itself a finding under the
    failures-are-findings directive.

    ``model_version_returned`` carries the lexicographically greatest
    distinct version string observed for this model_id in this domain.
    When multiple distinct strings are present (provider rolled a snapshot
    mid-cohort per CLAUDE.md §9 pitfall #1), ``model_version_returned_count``
    records how many distinct strings were observed; the Coder logs a
    WARNING in that case. The full per-informant version strings remain
    in the open data bundle.
    """

    model_id: str
    """User-supplied API alias, e.g. ``claude-opus-4-6``. NOT the same
    as ``model_version_returned`` (see CLAUDE.md §9 pitfall #1)."""

    provider: str
    """Literal provider string from InformantRecord. Populated from the
    lexicographically smallest provider string observed for this model_id
    in this domain (should always be one unique value; WARNING is logged
    if multiple are found)."""

    n_runs: int
    """Count of InformantRecord lines for this model_id in this domain,
    including records with ``qa_passed=False``."""

    n_qa_passed: int
    """Count of InformantRecord lines for this model_id in this domain
    where ``qa_passed=True``."""

    model_version_returned: str
    """The lexicographically greatest ``model_version_returned`` string
    observed for this model_id in this domain. See
    ``model_version_returned_count`` when the provider rolled a snapshot
    mid-cohort."""

    model_version_returned_count: int = 1
    """Count of distinct ``model_version_returned`` strings observed for
    this model_id in this domain. Value is 1 in the normal case. When
    greater than 1 the provider rolled a snapshot mid-cohort (CLAUDE.md
    §9 pitfall #1); the lexicographically greatest string is reported in
    ``model_version_returned`` and a WARNING is logged by ``build_successes()``."""


class PublishedSuccessesFile(BaseModel):
    """Top-level shape of apps/dashboard/public/data/records/{slug}.json.

    See docs/status/2026-06-10-collection-records-rework-kickoff.md §4
    Task 4 and docs/DATA_DICTIONARY.md §12.6.

    "Successful" here means the LSB pipeline parsed a primary-step
    response. It is NOT a quality judgment on the model output.
    """

    domain_slug: str
    generated_at: str
    """ISO-8601 UTC wallclock at build time."""

    n_informants: int
    """Total count of InformantRecord lines in this domain, including
    records with ``qa_passed=False``. This is the full run count, not
    a QA-filtered subset."""

    by_model: list[PublishedSuccessesByModelRow]
    """Per-model-id summary rows, sorted lexicographically by model_id
    ascending. Empty list for a domain with zero informant records
    (first-class empty state per ARCHITECTURE.md §1.5.5)."""

    framing_note: str
    """LSB-authored corpus-lens framing attached to the data so that
    readers who download this JSON outside the dashboard UI still receive
    the §1.5 context. T5 is contracted to render this field adjacent to
    the summary. See docs/status/2026-06-10-collection-records-rework-verdicts.md
    CR-T4 CDA SME verdict."""
