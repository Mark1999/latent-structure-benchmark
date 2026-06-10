"""Successful-records summary publish layer. See the kickoff at
docs/status/2026-06-10-collection-records-rework-kickoff.md §4 Task 4.

Reads data/raw/informants.jsonl (InformantRecord lines — raw dicts) and
emits one apps/dashboard/public/data/records/{slug}.json per domain.
Each file is a per-domain SUMMARY (counts and per-model aggregates) of
collection sessions for which the LSB pipeline parsed a primary-step
response.

"Successful" is a parser-state property of the LSB pipeline, not a
quality judgment on the model output. The framing_note field in every
emitted JSON file makes this explicit. See DATA_DICTIONARY.md §12.6 and
ARCHITECTURE.md §1.5.4 for the language-guardrails table.

Source files in data/raw/ are read-only. This module MUST NOT write to
any raw data paths (Reviewer R4, append-only invariant). SHA256 of
data/raw/informants.jsonl is byte-identical before and after
build_successes() runs.

All string fields in every published record are passed through
cdb_publish.sanitize.sanitize_record_strings() before write. This applies
the three defensive redaction passes: API-key patterns, Slack webhook URL
patterns, and local-filesystem path patterns. See
SECURITY_AND_HARDENING.md §3.3 and §3.4.

This mirrors the posture of cdb_publish.failures but reads
informants.jsonl instead of failures.jsonl and emits a summary shape
(one row per model_id) rather than a full record list.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from cdb_publish.sanitize import sanitize_record_strings

logger = logging.getLogger(__name__)

# Verbatim framing note text, reviewed against §1.5.4 line-by-line by the
# CDA SME. Do not paraphrase. See
# docs/status/2026-06-10-collection-records-rework-verdicts.md CR-T4.
_FRAMING_NOTE = (
    "These records summarise collection sessions for which the LSB pipeline "
    "parsed a primary-step response. Each row reports the run count, the "
    "QA-pass count, and the provider-returned model-version string for a "
    "single `model_id` in this domain. A row is a property of the LSB "
    "collection pipeline's parsing outcome, not a quality judgment on the "
    "model output. The full per-record bytes are available in the open data "
    "bundle under CC0; the unsuccessful counterpart sessions are surfaced "
    "under `data/failures/{slug}.json`. See the methodology page for the "
    "corpus-lens framing."
)


def _load_informants_jsonl(path: Path) -> list[dict]:
    """Read informants.jsonl and return a list of raw dicts.

    Skips blank lines silently. Read-only access — never writes to path.
    """
    records: list[dict] = []
    if not path.exists():
        logger.warning(
            "informants.jsonl not found at %s — returning empty list", path
        )
        return records
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                logger.warning(
                    "Skipping malformed JSON on line %d of %s: %s",
                    lineno,
                    path,
                    exc,
                )
    return records


def _group_by_domain(
    records: list[dict], domain_slugs: list[str]
) -> dict[str, list[dict]]:
    """Partition informant records by domain_slug.

    Records whose domain_slug is not in domain_slugs are skipped (logged
    at WARNING). Returns a dict with every slug in domain_slugs present.
    """
    grouped: dict[str, list[dict]] = {slug: [] for slug in domain_slugs}
    for rec in records:
        slug = rec.get("domain_slug")
        if not slug:
            logger.warning(
                "Informant record with informant_id=%s has no domain_slug — "
                "cannot join to a domain, not counted",
                rec.get("informant_id", "<unknown>"),
            )
            continue
        if slug not in grouped:
            logger.warning(
                "Informant record domain %r not in manifest domain list — "
                "not counted (informant_id=%s)",
                slug,
                rec.get("informant_id", "<unknown>"),
            )
            continue
        grouped[slug].append(rec)
    return grouped


def _build_by_model_rows(domain_records: list[dict]) -> list[dict]:
    """Build per-model-id summary rows from a list of domain informant records.

    Returns a list of dicts matching PublishedSuccessesByModelRow, sorted
    lexicographically by model_id ascending (deterministic, no implicit
    ranking signal per CDA SME N6 / §8 row-order approval).
    """
    # Accumulate per model_id: n_runs, n_qa_passed, provider strings,
    # model_version_returned strings.
    model_data: dict[str, dict] = {}
    for rec in domain_records:
        mid = rec.get("model_id", "")
        if not mid:
            continue
        if mid not in model_data:
            model_data[mid] = {
                "n_runs": 0,
                "n_qa_passed": 0,
                "providers": set(),
                "versions": set(),
            }
        entry = model_data[mid]
        entry["n_runs"] += 1
        if rec.get("qa_passed") is True:
            entry["n_qa_passed"] += 1
        provider = rec.get("provider", "")
        if provider:
            entry["providers"].add(provider)
        version = rec.get("model_version_returned", "")
        if version:
            entry["versions"].add(version)

    rows: list[dict] = []
    for mid in sorted(model_data.keys()):
        entry = model_data[mid]

        # provider: lex-smallest; WARNING on multi-provider (CDA SME N4).
        providers = entry["providers"]
        if len(providers) > 1:
            # WARNING message must not use anthropomorphic phrasing (N4).
            logger.warning(
                "model_id %r has multiple provider strings in raw informants — "
                "lexicographically smallest selected for summary row; full "
                "per-informant provider strings remain in the open data bundle",
                mid,
            )
        provider = min(providers) if providers else ""

        # model_version_returned: lex-greatest; WARNING + count on multi-version.
        versions = entry["versions"]
        version_count = len(versions)
        if version_count > 1:
            logger.warning(
                "model_id %r has %d distinct model_version_returned strings in "
                "domain — lexicographically greatest selected for summary row; "
                "full per-informant version strings remain in the open data bundle",
                mid,
                version_count,
            )
        model_version = max(versions) if versions else ""

        row: dict = {
            "model_id": mid,
            "provider": provider,
            "n_runs": entry["n_runs"],
            "n_qa_passed": entry["n_qa_passed"],
            "model_version_returned": model_version,
            "model_version_returned_count": max(version_count, 1),
        }

        # Sanitize all string leaves in the row (defense-in-depth per R4;
        # model_id / provider / model_version_returned are not expected to
        # carry secrets, but the pass applies uniformly).
        row = sanitize_record_strings(row)  # type: ignore[assignment]
        rows.append(row)
    return rows


def build_successes(
    raw_informants_path: Path,
    output_dir: Path,
    domain_slugs: list[str],
) -> dict[str, str]:
    """Read raw informants, aggregate by domain and model_id, emit per-domain JSON.

    Emits one apps/dashboard/public/data/records/{slug}.json per domain
    in domain_slugs. Domains with zero records still receive an output
    file with by_model: [] and n_informants: 0 (first-class empty state
    per ARCHITECTURE.md §1.5.5 and CLAUDE.md §9 pitfall #4).

    Returns the records-path dict for the manifest (every slug has a
    non-null entry).

    Source file is read-only — never modified. SHA256 of
    raw_informants_path must be byte-identical before and after this
    function runs (Reviewer R4).

    The ``framing_note`` in every emitted file is the byte-identical CDA
    SME verdict string from
    docs/status/2026-06-10-collection-records-rework-verdicts.md CR-T4.
    Do not paraphrase it.

    Parameters
    ----------
    raw_informants_path:
        Path to data/raw/informants.jsonl (read-only).
    output_dir:
        Directory where per-domain records JSON files will be written.
        Created if it does not exist.
    domain_slugs:
        List of domain slugs from the manifest. Every slug gets an output
        file even if it has zero records.

    Returns
    -------
    dict[str, str]
        Map from domain_slug to published path relative to the dashboard
        public directory root (e.g., ``"data/records/family.json"``).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all informant records (read-only).
    all_records = _load_informants_jsonl(raw_informants_path)

    # Partition by domain.
    by_domain = _group_by_domain(all_records, domain_slugs)

    # Build and emit per-domain files.
    generated_at = datetime.now(tz=UTC).isoformat()
    records_map: dict[str, str] = {}

    for slug in sorted(domain_slugs):
        domain_records = by_domain[slug]
        by_model_rows = _build_by_model_rows(domain_records)

        output_obj: dict = {
            "domain_slug": slug,
            "generated_at": generated_at,
            "n_informants": len(domain_records),
            "by_model": by_model_rows,
            "framing_note": _FRAMING_NOTE,
        }

        out_path = output_dir / f"{slug}.json"
        out_path.write_text(json.dumps(output_obj, indent=2), encoding="utf-8")
        logger.info(
            "Wrote %s (%d informants, %d model rows)",
            out_path,
            len(domain_records),
            len(by_model_rows),
        )

        records_map[slug] = f"data/records/{slug}.json"

    return records_map
