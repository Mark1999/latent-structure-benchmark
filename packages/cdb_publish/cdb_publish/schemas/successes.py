"""Publish-layer schema for the per-domain successful-records summary JSON
and per-record detail JSON.

These are dashboard-internal schemas that describe the shape of
apps/dashboard/public/data/records/{slug}.json (summary) and
apps/dashboard/public/data/records/{slug}/detail/{informant_id}.json
(per-record detail). They are NOT part of the cdb_core open-data-bundle
schema contract (which is governed by cdb_core/schemas.py and
docs/DATA_DICTIONARY.md §9-10). Changes here do not trigger CLAUDE.md
R6 or a DATA_DICTIONARY.md co-update for cdb_core; they do require
updating the DATA_DICTIONARY.md §12.6 and §12.7 sections that document
the published successful-records summary and per-record detail JSON shapes.

See docs/status/2026-06-10-collection-records-rework-kickoff.md §4
Task 4 and Task 7, and
docs/status/2026-06-10-collection-records-rework-verdicts.md CR-T4 and
CR-T7 for the CDA SME framing requirements applied to these shapes.

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


# ============================================================================
# Per-record detail JSON schema (CR-T7, 2026-06-10)
# See DATA_DICTIONARY.md §12.7 and
# docs/status/2026-06-10-collection-records-rework-verdicts.md CR-T7.
# ============================================================================


class PublishedStepExchange(BaseModel):
    """Verbatim bytes for one CDA elicitation step.

    Three fields record what the LSB pipeline sent (prompt_verbatim),
    what the provider returned (response_verbatim), and any reasoning
    trace the provider surfaced (thinking_verbatim).

    Per CDA SME N2 disposition (a): the three top-level step fields on
    PublishedRecordDetail (freelist, pile_sort, pile_interview) are
    non-Optional because InformantRecord.{freelist, pile_sort, interview}
    are required fields per cdb_core/schemas.py. The publish path cannot
    emit a detail record where any of these is null.

    thinking_verbatim is typed str (not str | None) but may be the empty
    string when the provider did not surface a reasoning trace. An empty
    string is a first-class state, not a missing record.
    """

    prompt_verbatim: str
    """Verbatim bytes the LSB pipeline sent for this step."""

    response_verbatim: str
    """Verbatim bytes the provider returned for this step."""

    thinking_verbatim: str
    """Reasoning trace the provider surfaced for this step.
    Empty string when the provider did not surface a trace."""

    model_version_returned: str
    """Provider-returned model-version string for this step's API call."""

    prompt_version: str
    """LSB-side prompt-template version string for this step."""


class PublishedRecordProvenance(BaseModel):
    """Provenance and pipeline identifiers for a single collection session.

    These identifiers name the LSB collection session, the prompt-template
    version, and the provider-returned model-version string. They are
    properties of the LSB pipeline run, not of the model's intent.
    """

    provider_request_id: str
    """Provider-assigned request ID. Used for independent audit through
    the provider's logs."""

    model_id: str
    """User-supplied model alias (NOT the same as model_version_returned;
    see CLAUDE.md §9 pitfall #1)."""

    model_version_returned: str
    """Exact version string the provider returned in the API response."""

    provider: str
    """Provider string from the InformantRecord."""

    domain_slug: str
    """Domain slug for this collection session."""

    run_index: int
    """Run index within the (model_id, domain_slug) cohort."""

    collection_date: str
    """ISO-8601 collection date string."""

    sha256_manifest: dict[str, str]
    """SHA256 manifest covering verbatim prompts and responses. Eight
    keys: freelist_prompt, freelist_response, pilesort_prompt,
    pilesort_response, interview_prompt, interview_response,
    request_params, informant_record_total."""


class PublishedRecordDetail(BaseModel):
    """Per-record detail JSON: verbatim bytes for all three CDA steps.

    Emitted to
    apps/dashboard/public/data/records/{slug}/detail/{informant_id}.json.

    The three step fields (freelist, pile_sort, pile_interview) are
    non-Optional per CDA SME N2 disposition (a). InformantRecord requires
    all three fields; the publish path cannot emit a detail record where
    any of these is null.

    The framing_note_detail field carries the CDA SME-bound anti-attribution
    framing text. It is distinct from the per-domain summary framing_note.

    See DATA_DICTIONARY.md §12.7 for the full field contract.
    """

    informant_id: str
    """Unique identifier for this collection session."""

    framing_note_detail: str
    """Anti-attribution framing note. Distinct from the per-domain summary
    framing_note. Byte-identical to the CDA SME bound string in
    .claude/agent-memory/cda_sme/project_cr_t7_sme_bound_strings.md."""

    freelist: PublishedStepExchange
    """Verbatim bytes for the free-list elicitation step (CDA Step 1)."""

    pile_sort: PublishedStepExchange
    """Verbatim bytes for the pile-sort elicitation step (CDA Step 2)."""

    pile_interview: PublishedStepExchange
    """Verbatim bytes for the pile-interview elicitation step (CDA Step 3).
    Note: the field on InformantRecord is named 'interview'; the published
    name is 'pile_interview' per CDA SME N1 binding (avoids confusion with
    the follow-up DeclineInterview record kind)."""

    provenance: PublishedRecordProvenance
    """Provenance and pipeline identifiers for this session."""
