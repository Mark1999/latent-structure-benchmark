"""Phase 4a.1 — Note J cross-tab + Note K re-evaluation script (T4).

This script implements the T4 analysis from the Phase 4a.1 decline-interview
backfill, per:

  Amendment 2 §3 T4  — primary view, secondary views A/B, reconciliation table,
                        Note K disposition logic (four-disposition tree)
  Amendment 3 §3.2   — safety_attribution_subtype column, Note K mechanism
                        breakdown sub-section, bipartite mechanism string (D20)

**Inputs (4 files — error clearly if any missing or invalid):**

  data/raw/decline_interviews.jsonl
  data/raw/informants.jsonl
  data/derived/decline_interviews_manual_classification.jsonl
  data/derived/decline_interviews_safety_attribution_subtype.jsonl   (Amendment 3)

**Outputs:**

  Markdown to stdout (and optionally to --output path).
  With --json: structured JSON to stdout (or --json-output path).

**Note K disposition four-tier tree (Amendment 2 §3 T4 bullet 4, D21):**

  CONFIRMED-with-mechanism:
      safety_event_attribution_count + blocked_event_attribution_count >= 5
      AND cross-provider sub-table shows >= 2 distinct providers
  CONFIRMED:
      safety_event_attribution_count + blocked_event_attribution_count >= 5
      but only 1 provider in safety/blocked cohort
  INCONCLUSIVE-SUGGESTIVE:
      2 <= count < 5
  INCONCLUSIVE:
      1 <= count < 2
  NOT CONFIRMED:
      count == 0

Binding notes in force: Amendment 2 §3 T4, Amendment 3 §3.2, B11, B14.
No LLM imports. No real API calls.

References:
  Plan:         docs/status/2026-04-30-phase4a1-architect-plan-amendment-2.md §3 T4
  Amendment 3:  docs/status/2026-04-30-phase4a1-architect-plan-amendment-3.md §3.2
  SME verdict:  docs/status/2026-04-30-phase4a1-amendment-3-cda-sme-verdict.md
  B11 source:   docs/status/2026-04-30-phase4a1-t3c-manual-classification-sme-verdict.md
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter, defaultdict
from typing import Any

from cdb_analyze.manual_classification import (
    DeclineManualClassification,
    load_manual_classifications,
)
from cdb_analyze.safety_subtype import (
    SafetyAttributionSubtype,
    load_safety_attribution_subtypes,
)

# ── Constants ─────────────────────────────────────────────────────────────────

SCRIPT_VERSION = "1.0.0"

# The 7-enum values (Amendment 2 §3 T3C, binding note B1)
ALL_CLASSIFICATION_VALUES = [
    "safety_event_attribution",
    "blocked_event_attribution",
    "technical_glitch_attribution",
    "no_prior_context_acknowledgment",
    "substantive_compliance_with_empty_input",
    "other_substring_false_positive",
    "genuine_recursive_decline",
]

# The outcome_class values used for the primary view (informants.jsonl field)
# Cross-tabbed against model_origin
PRIMARY_OUTCOME_CLASSES = [
    "completed",
    "empty_output",
    "parse_failure",
    "content_error",
    "rate_limit",
    "refused",
    "error",
]

# Note K disposition thresholds (binding note 4, Amendment 2 §3 T4 bullet 4)
NOTE_K_CONFIRMED_THRESHOLD = 5   # safety+blocked count >= 5 for CONFIRMED (any tier)
NOTE_K_MIN_PROVIDERS = 2         # cross-provider sub-table >= 2 distinct providers


# ── Domain extraction from prompt_verbatim ────────────────────────────────────

def _domain_from_prompt(prompt: str) -> str:
    """Heuristic domain extraction from the decline-interview prompt_verbatim.

    The prompt text reliably contains the domain vocabulary because the
    CDA freelist prompt is embedded verbatim in the follow-up prompt.
    """
    prompt_lower = prompt.lower()
    if "family relationship" in prompt_lower or "family member" in prompt_lower:
        return "family"
    if "holiday" in prompt_lower or "religious observance" in prompt_lower:
        return "holidays"
    return "unknown"


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    """Load a JSONL file into a list of dicts. Skips blank lines."""
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at line {lineno} of {path}: {exc}"
                ) from exc
    return rows


def load_all_inputs(
    decline_interviews_path: pathlib.Path,
    informants_path: pathlib.Path,
    manual_classification_path: pathlib.Path,
    subtype_path: pathlib.Path,
) -> tuple[
    list[dict[str, Any]],             # decline_interviews rows
    dict[str, dict[str, Any]],        # informants keyed by informant_id
    dict[str, DeclineManualClassification],   # manual classifications
    dict[str, SafetyAttributionSubtype],      # safety subtypes
]:
    """Load and validate all four input artifacts.

    Errors clearly on missing files, UNCLASSIFIED rows, or validation failures.
    """
    # ── File existence checks ─────────────────────────────────────────────────
    for p in (
        decline_interviews_path,
        informants_path,
        manual_classification_path,
        subtype_path,
    ):
        if not p.exists():
            raise FileNotFoundError(
                f"Required input file not found: {p}\n"
                f"All four input files must be present before running T4."
            )

    # ── Decline interviews ────────────────────────────────────────────────────
    decline_rows = _load_jsonl(decline_interviews_path)
    if not decline_rows:
        raise ValueError(f"No rows found in {decline_interviews_path}")

    # ── Informants ────────────────────────────────────────────────────────────
    informant_rows = _load_jsonl(informants_path)
    informants: dict[str, dict[str, Any]] = {}
    for row in informant_rows:
        iid = row.get("informant_id")
        if iid:
            informants[iid] = row

    # ── Manual classifications ────────────────────────────────────────────────
    # load_manual_classifications raises ValueError on UNCLASSIFIED or invalid rows
    manual_classifications = load_manual_classifications(manual_classification_path)

    # ── Safety attribution subtypes ───────────────────────────────────────────
    # load_safety_attribution_subtypes raises ValueError on:
    # - UNCLASSIFIED rows (naming the offending decline_interview_id)
    # - decline_interview_id not in parent manual classification artifact
    # - parent classification is not safety_event_attribution
    subtypes = load_safety_attribution_subtypes(
        subtype_path, manual_classification_path
    )

    return decline_rows, informants, manual_classifications, subtypes


# ── Enrichment ────────────────────────────────────────────────────────────────

def enrich_decline_rows(
    decline_rows: list[dict[str, Any]],
    informants: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Add derived fields (domain, model_origin) to each decline interview row.

    model_origin: joined from informants.jsonl via originating_informant_id.
    If the originating informant is not present in informants.jsonl (possible
    because Gemini-direct rows may not have an informant record), falls back
    to 'unknown'.

    domain: extracted from prompt_verbatim heuristically (reliable — the CDA
    freelist prompt is embedded verbatim in the follow-up prompt).
    """
    # Build model_id -> origin_country index from informants (takes the first occurrence)
    model_origin_by_id: dict[str, str] = {}
    for inf in informants.values():
        mid = inf.get("model_id", "")
        if mid and mid not in model_origin_by_id:
            model_origin_by_id[mid] = inf.get("origin_country", "unknown")

    enriched = []
    for row in decline_rows:
        enriched_row = dict(row)
        enriched_row["domain"] = _domain_from_prompt(row.get("prompt_verbatim", ""))
        # model_origin: look up by model_id (most reliable available join)
        mid = row.get("model_id", "")
        enriched_row["model_origin"] = model_origin_by_id.get(mid, "unknown")
        enriched.append(enriched_row)

    return enriched


# ── Primary view: outcome_class × model_origin ────────────────────────────────

def build_primary_view(
    enriched_decline_rows: list[dict[str, Any]],
    informants: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Primary view: outcome_class × model_origin over the combined population.

    Population = informants.jsonl + decline_interviews.jsonl joined together.

    For informants: the relevant "outcome_class" is inferred from whether the
    freelist/pile_sort/interview produced output (qa_passed + freelist non-empty
    = completed; empty freelist = empty_output; etc.).
    For decline interviews: originating_outcome_class is the outcome_class.

    Amendment 2 §3 T4 bullet 1: primary view is outcome_class × model_origin,
    baseline = corpus collection-attempt distribution, flag if
    observed >= 3 × expected AND observed >= 2.
    """
    # ── Count decline-interview outcomes by model_origin ─────────────────────
    di_by_origin_and_outcome: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in enriched_decline_rows:
        origin = row.get("model_origin", "unknown")
        outcome = row.get("originating_outcome_class", "unknown")
        di_by_origin_and_outcome[origin][outcome] += 1

    # ── Count informant outcomes by model_origin ──────────────────────────────
    inf_by_origin_and_outcome: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for inf in informants.values():
        origin = inf.get("origin_country", "unknown")
        # Infer outcome from QA status and freelist content
        if not inf.get("qa_passed", True):
            outcome = "error"
        elif not inf.get("freelist"):
            outcome = "empty_output"
        else:
            outcome = "completed"
        inf_by_origin_and_outcome[origin][outcome] += 1

    # ── Combined population counts ────────────────────────────────────────────
    all_origins = sorted(
        set(di_by_origin_and_outcome.keys()) | set(inf_by_origin_and_outcome.keys())
    )
    all_outcomes = sorted(
        set(
            k
            for d in list(di_by_origin_and_outcome.values())
            + list(inf_by_origin_and_outcome.values())
            for k in d
        )
    )

    # Combined matrix
    combined: dict[str, dict[str, int]] = {}
    total_by_outcome: dict[str, int] = Counter()
    total_by_origin: dict[str, int] = Counter()
    grand_total = 0

    for origin in all_origins:
        combined[origin] = {}
        for outcome in all_outcomes:
            di_count = di_by_origin_and_outcome.get(origin, {}).get(outcome, 0)
            inf_count = inf_by_origin_and_outcome.get(origin, {}).get(outcome, 0)
            count = di_count + inf_count
            combined[origin][outcome] = count
            total_by_outcome[outcome] += count
            total_by_origin[origin] += count
            grand_total += count

    # ── Flag cells where observed >= 3× expected AND observed >= 2 ───────────
    flags: list[dict[str, Any]] = []
    if grand_total > 0:
        for origin in all_origins:
            for outcome in all_outcomes:
                observed = combined[origin].get(outcome, 0)
                expected = (
                    total_by_origin[origin] * total_by_outcome[outcome] / grand_total
                )
                if expected > 0 and observed >= 3 * expected and observed >= 2:
                    flags.append(
                        {
                            "model_origin": origin,
                            "outcome_class": outcome,
                            "observed": observed,
                            "expected": round(expected, 2),
                            "ratio": round(observed / expected, 2),
                        }
                    )

    return {
        "origins": all_origins,
        "outcomes": all_outcomes,
        "matrix": combined,
        "total_by_outcome": dict(total_by_outcome),
        "total_by_origin": dict(total_by_origin),
        "grand_total": grand_total,
        "flags": flags,
    }


# ── Secondary view A: manual classification × (provider, model_id, domain) ───

def build_secondary_view_a(
    enriched_decline_rows: list[dict[str, Any]],
    manual_classifications: dict[str, DeclineManualClassification],
    subtypes: dict[str, SafetyAttributionSubtype],
) -> dict[str, Any]:
    """Secondary view A: manual classification × (provider, model_id, domain).

    Rows = 7 enum values.
    Columns = (provider, model_id, domain) triples observed.

    Also produces the cross-provider replication sub-table for safety+blocked
    cohorts, with the safety_attribution_subtype column (Amendment 3 §3.2).

    Returns a dict with:
      - matrix: {classification -> {(provider, model_id, domain) -> count}}
      - triples: sorted list of (provider, model_id, domain)
      - cross_provider_table: safety+blocked rows broken out by provider,
          now including safety_attribution_subtype column per Amendment 3
      - provider_subtype_counts: {provider -> {subtype -> count}}
    """
    # Build lookup of enriched rows by decline_interview_id
    di_by_id: dict[str, dict[str, Any]] = {
        row["decline_interview_id"]: row for row in enriched_decline_rows
    }

    # Count by (classification, provider, model_id, domain)
    matrix: dict[str, dict[tuple[str, str, str], int]] = defaultdict(
        lambda: defaultdict(int)
    )
    # Track (provider, model_id, domain) triples for the safety+blocked sub-table
    safety_blocked_rows: list[dict[str, Any]] = []

    for did, mc in manual_classifications.items():
        row = di_by_id.get(did)
        if row is None:
            continue
        classification = mc.manual_classification
        provider = row.get("provider", "unknown")
        model_id = row.get("model_id", "unknown")
        domain = row.get("domain", "unknown")
        triple = (provider, model_id, domain)
        matrix[classification][triple] += 1

        if classification in ("safety_event_attribution", "blocked_event_attribution"):
            subtype_rec = subtypes.get(did)
            # blocked_event_attribution rows get n/a per D17/Amendment 3 §3.2
            if classification == "blocked_event_attribution":
                subtype_val = "n/a"
            elif subtype_rec is not None:
                subtype_val = subtype_rec.safety_attribution_subtype
            else:
                subtype_val = "n/a"

            safety_blocked_rows.append(
                {
                    "decline_interview_id": did,
                    "classification": classification,
                    "provider": provider,
                    "model_id": model_id,
                    "domain": domain,
                    "safety_attribution_subtype": subtype_val,
                }
            )

    # All (provider, model_id, domain) triples observed
    all_triples = sorted(
        {triple for counts in matrix.values() for triple in counts}
    )

    # Cross-provider replication sub-table for safety+blocked cohort
    # With safety_attribution_subtype column (Amendment 3 §3.2)
    safety_blocked_rows_sorted = sorted(
        safety_blocked_rows,
        key=lambda r: (r["provider"], r["model_id"], r["domain"]),
    )

    # (provider, subtype) counts for the Note K mechanism breakdown sub-section
    provider_subtype_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    for sbr in safety_blocked_rows:
        if sbr["classification"] == "safety_event_attribution":
            provider_subtype_counts[sbr["provider"]][sbr["safety_attribution_subtype"]] += 1

    return {
        "matrix": {k: dict(v) for k, v in matrix.items()},
        "triples": all_triples,
        "cross_provider_table": safety_blocked_rows_sorted,
        "provider_subtype_counts": {k: dict(v) for k, v in provider_subtype_counts.items()},
    }


# ── Secondary view B: manual classification × model_origin ───────────────────

def build_secondary_view_b(
    enriched_decline_rows: list[dict[str, Any]],
    manual_classifications: dict[str, DeclineManualClassification],
) -> dict[str, Any]:
    """Secondary view B: manual classification × model_origin.

    Amendment 2 §3 T4 bullet 3: broken out by model_origin ∈ {us, eu, ca, cn, other}.
    """
    di_by_id: dict[str, dict[str, Any]] = {
        row["decline_interview_id"]: row for row in enriched_decline_rows
    }

    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for did, mc in manual_classifications.items():
        row = di_by_id.get(did)
        if row is None:
            continue
        classification = mc.manual_classification
        origin = row.get("model_origin", "unknown")
        matrix[classification][origin] += 1

    all_origins = sorted({o for counts in matrix.values() for o in counts})

    return {
        "matrix": {k: dict(v) for k, v in matrix.items()},
        "origins": all_origins,
    }


# ── Reconciliation table: detector_flag_v1 × manual_classification ───────────

def build_reconciliation_table(
    manual_classifications: dict[str, DeclineManualClassification],
) -> dict[str, Any]:
    """Reconciliation table: detector_flag_v1 × manual_classification.

    Amendment 2 §3 T4 bullet 5: audit-trail evidence for T5 §8.0.
    """
    matrix: dict[bool, dict[str, int]] = {
        True: defaultdict(int),
        False: defaultdict(int),
    }

    for mc in manual_classifications.values():
        flag = mc.detector_flag_v1
        classification = mc.manual_classification
        matrix[flag][classification] += 1

    return {
        "flagged": dict(matrix[True]),
        "not_flagged": dict(matrix[False]),
        "total_flagged": sum(matrix[True].values()),
        "total_not_flagged": sum(matrix[False].values()),
    }


# ── Note K disposition ────────────────────────────────────────────────────────

def compute_note_k_disposition(
    manual_classifications: dict[str, DeclineManualClassification],
    subtypes: dict[str, SafetyAttributionSubtype],
    secondary_view_a: dict[str, Any],
) -> dict[str, Any]:
    """Compute Note K disposition from manual classification data.

    Disposition four-tier tree (Amendment 2 §3 T4 bullet 4, D21):
    - CONFIRMED-with-mechanism: count >= 5 AND >= 2 distinct providers
    - CONFIRMED: count >= 5 but only 1 provider
    - INCONCLUSIVE-SUGGESTIVE: 2 <= count < 5
    - INCONCLUSIVE: 1 <= count < 2 (i.e. count == 1)
    - NOT CONFIRMED: count == 0

    Amendment 3 D20: bipartite mechanism string added to disposition string.
    Amendment 3 D21: K-frame/K-vocab split does NOT affect disposition arithmetic.
    """
    # Count safety_event_attribution + blocked_event_attribution
    safety_count = sum(
        1
        for mc in manual_classifications.values()
        if mc.manual_classification == "safety_event_attribution"
    )
    blocked_count = sum(
        1
        for mc in manual_classifications.values()
        if mc.manual_classification == "blocked_event_attribution"
    )
    total_safety_blocked = safety_count + blocked_count

    # Distinct providers in safety+blocked cohort
    cross_provider_table = secondary_view_a.get("cross_provider_table", [])
    distinct_providers = {row["provider"] for row in cross_provider_table}
    n_providers = len(distinct_providers)

    # Determine disposition tier
    if total_safety_blocked == 0:
        disposition = "NOT CONFIRMED"
    elif total_safety_blocked == 1:
        disposition = "INCONCLUSIVE"
    elif total_safety_blocked < NOTE_K_CONFIRMED_THRESHOLD:
        disposition = "INCONCLUSIVE-SUGGESTIVE"
    elif n_providers >= NOTE_K_MIN_PROVIDERS:
        disposition = "CONFIRMED-with-mechanism"
    else:
        disposition = "CONFIRMED"

    # Count subtypes from the actual artifact (Amendment 3 D20 — do not hardcode)
    k_frame_count = sum(
        1
        for rec in subtypes.values()
        if rec.safety_attribution_subtype == "k_frame"
    )
    k_vocab_count = sum(
        1
        for rec in subtypes.values()
        if rec.safety_attribution_subtype == "k_vocab_without_k_frame"
    )

    # Domain names (from cross_provider_table)
    domains_in_safety = sorted({row["domain"] for row in cross_provider_table})
    domain_str = " and ".join(domains_in_safety) if domains_in_safety else "unknown"

    # Mechanism string per D20 — N values are computed from the actual artifact
    # This string is the canonical D20 wording with actual counts substituted
    mechanism_string = (
        f"provider-safety-layer activation with two co-present trigger patterns "
        f"— (a) AI-vs-human-research-subject framing (K-frame; N={k_frame_count}), "
        f"(b) list-comprehensiveness/sensitivity vocabulary without K-frame "
        f"(K-vocab; N={k_vocab_count}) "
        f"— cross-provider replication on the {domain_str} domains"
    )

    # Disposition string (headline) per D20
    # For CONFIRMED-with-mechanism: mechanism string is the headline
    # For other tiers: disposition tier is the headline (mechanism string in notes)
    if disposition == "CONFIRMED-with-mechanism":
        disposition_string = f"Note K: {disposition} — {mechanism_string}"
    else:
        disposition_string = f"Note K: {disposition}"

    # Supporting numerics line (per Amendment 3 §3.2)
    supporting_numerics = (
        f"Safety attribution count: {total_safety_blocked} "
        f"(safety_event_attribution={safety_count}, "
        f"blocked_event_attribution={blocked_count}); "
        f"K-frame N={k_frame_count}, K-vocab N={k_vocab_count}; "
        f"distinct providers in safety/blocked cohort: {n_providers} "
        f"({', '.join(sorted(distinct_providers)) if distinct_providers else 'none'})"
    )

    return {
        "disposition": disposition,
        "disposition_string": disposition_string,
        "supporting_numerics": supporting_numerics,
        "mechanism_string": mechanism_string,
        "safety_event_attribution_count": safety_count,
        "blocked_event_attribution_count": blocked_count,
        "total_safety_blocked": total_safety_blocked,
        "distinct_providers": sorted(distinct_providers),
        "n_providers": n_providers,
        "k_frame_count": k_frame_count,
        "k_vocab_count": k_vocab_count,
        "domains": domains_in_safety,
    }


# ── Markdown rendering ────────────────────────────────────────────────────────

def render_markdown(
    primary_view: dict[str, Any],
    secondary_view_a: dict[str, Any],
    secondary_view_b: dict[str, Any],
    reconciliation: dict[str, Any],
    note_k: dict[str, Any],
    decline_count: int,
    informant_count: int,
) -> str:
    """Render all cross-tab views and Note K disposition as Markdown.

    Format is designed to be cited verbatim in T5 §8.1 and §8.2.
    B14 (binding): supporting numerics live here; interpretation in Note K section.
    """
    lines: list[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        "# Phase 4a.1 T4: Note J Cross-Tab + Note K Re-Evaluation",
        "",
        f"**Script:** `scripts/phase4a1_note_j_crosstab.py` v{SCRIPT_VERSION}",
        f"**Population:** {informant_count} informants + {decline_count} decline interviews",
        "",
        "---",
        "",
    ]

    # ── Primary view ─────────────────────────────────────────────────────────
    lines += [
        "## Primary View: outcome_class × model_origin",
        "",
        "Cross-tab over the combined informants + decline-interview population.",
        "Flagged cells: `observed >= 3 × expected AND observed >= 2`.",
        "",
    ]

    origins = primary_view["origins"]
    outcomes = primary_view["outcomes"]
    matrix = primary_view["matrix"]
    total_by_origin = primary_view["total_by_origin"]
    total_by_outcome = primary_view["total_by_outcome"]

    if origins and outcomes:
        # Header row
        header = "| outcome_class | " + " | ".join(origins) + " | **Total** |"
        sep = "| --- | " + " | ".join("---" for _ in origins) + " | --- |"
        lines += [header, sep]
        for outcome in sorted(outcomes):
            cells = [str(matrix.get(origin, {}).get(outcome, 0)) for origin in origins]
            row_total = total_by_outcome.get(outcome, 0)
            lines.append(f"| {outcome} | " + " | ".join(cells) + f" | {row_total} |")
        totals = [str(total_by_origin.get(o, 0)) for o in origins]
        grand = primary_view["grand_total"]
        lines.append("| **Total** | " + " | ".join(totals) + f" | {grand} |")
        lines.append("")

        flags = primary_view.get("flags", [])
        if flags:
            lines += ["**Flagged cells (observed >= 3x expected, observed >= 2):**", ""]
            for f in flags:
                lines.append(
                    f"- `{f['model_origin']}` × `{f['outcome_class']}`: "
                    f"observed={f['observed']}, expected={f['expected']}, "
                    f"ratio={f['ratio']}"
                )
            lines.append("")
        else:
            lines += ["*No cells meet the flag criteria.*", ""]
    else:
        lines += ["*No data.*", ""]

    lines += ["---", ""]

    # ── Secondary view A ──────────────────────────────────────────────────────
    lines += [
        "## Secondary View A: Manual Classification × (provider, model_id, domain)",
        "",
        "Cross-tab over the 27 decline-interview records joined to the manual",
        "classification artifact. Rows = 7-enum values; columns = observed triples.",
        "",
    ]

    sv_a_matrix = secondary_view_a["matrix"]
    triples = secondary_view_a["triples"]

    if triples:
        triple_headers = [f"{p}/{m}/{d}" for p, m, d in triples]
        header = "| classification | " + " | ".join(triple_headers) + " | **Total** |"
        sep = "| --- | " + " | ".join("---" for _ in triples) + " | --- |"
        lines += [header, sep]
        for cls in ALL_CLASSIFICATION_VALUES:
            counts = sv_a_matrix.get(cls, {})
            cells = [str(counts.get(triple, 0)) for triple in triples]
            row_total = sum(counts.values())
            lines.append(f"| {cls} | " + " | ".join(cells) + f" | {row_total} |")
        lines.append("")
    else:
        lines += ["*No data.*", ""]

    # ── Cross-provider replication sub-table (Amendment 3 §3.2 addition) ─────
    lines += [
        "### Cross-provider Replication Sub-table (safety + blocked cohort)",
        "",
        "Safety and blocked attribution rows broken out by provider.",
        "Column `safety_attribution_subtype` per Amendment 3 §3.2: `k_frame` or",
        "`k_vocab_without_k_frame` for `safety_event_attribution` rows; `n/a` for",
        "`blocked_event_attribution` rows (per D17 — blocked rows are not subtyped).",
        "",
    ]

    cp_table = secondary_view_a["cross_provider_table"]
    if cp_table:
        lines += [
            "| decline_interview_id | classification | provider | model_id"
            " | domain | safety_attribution_subtype |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for row in cp_table:
            lines.append(
                f"| {row['decline_interview_id']} "
                f"| {row['classification']} "
                f"| {row['provider']} "
                f"| {row['model_id']} "
                f"| {row['domain']} "
                f"| {row['safety_attribution_subtype']} |"
            )
        lines.append("")
    else:
        lines += ["*No safety or blocked attribution rows.*", ""]

    # ── Note K mechanism breakdown (Amendment 3 §3.2 addition) ───────────────
    lines += [
        "### Note K Mechanism Breakdown (safety cohort, by provider + subtype)",
        "",
        "Counts reported by `(provider, subtype)` for the `safety_event_attribution`",
        "cohort. (Blocked rows are absent per B9; `n/a` subtype is excluded from",
        "this breakdown.)",
        "",
    ]

    provider_subtype = secondary_view_a["provider_subtype_counts"]
    if provider_subtype:
        providers = sorted(provider_subtype.keys())
        lines += [
            "| subtype | " + " | ".join(providers) + " | **Total** |",
            "| --- | " + " | ".join("---" for _ in providers) + " | --- |",
        ]
        for subtype_val in ["k_frame", "k_vocab_without_k_frame"]:
            cells = [
                str(provider_subtype.get(p, {}).get(subtype_val, 0)) for p in providers
            ]
            row_total = sum(
                provider_subtype.get(p, {}).get(subtype_val, 0) for p in providers
            )
            lines.append(
                f"| {subtype_val} | " + " | ".join(cells) + f" | {row_total} |"
            )
        lines.append("")
    else:
        lines += ["*No safety attribution rows with subtype data.*", ""]

    lines += ["---", ""]

    # ── Secondary view B ──────────────────────────────────────────────────────
    lines += [
        "## Secondary View B: Manual Classification × model_origin",
        "",
        "Cross-tab broken out by model_origin ∈ {us, eu, ca, cn, other, unknown}.",
        "",
    ]

    sv_b_matrix = secondary_view_b["matrix"]
    b_origins = secondary_view_b["origins"]

    if b_origins:
        header = "| classification | " + " | ".join(b_origins) + " | **Total** |"
        sep = "| --- | " + " | ".join("---" for _ in b_origins) + " | --- |"
        lines += [header, sep]
        for cls in ALL_CLASSIFICATION_VALUES:
            counts = sv_b_matrix.get(cls, {})
            cells = [str(counts.get(o, 0)) for o in b_origins]
            row_total = sum(counts.values())
            lines.append(f"| {cls} | " + " | ".join(cells) + f" | {row_total} |")
        lines.append("")
    else:
        lines += ["*No data.*", ""]

    lines += ["---", ""]

    # ── Reconciliation table ──────────────────────────────────────────────────
    lines += [
        "## Detector Flag v1 × Manual Classification Reconciliation Table",
        "",
        "Audit-trail evidence for T5 §8.0 (Amendment 2 §3 T4 bullet 5).",
        "The stored flag values are preserved as the audit record of v1 behavior.",
        "Manual classification replaces the flag values for analytic purposes.",
        "",
    ]

    flagged = reconciliation["flagged"]
    not_flagged = reconciliation["not_flagged"]
    all_cls_in_recon = sorted(
        set(flagged.keys()) | set(not_flagged.keys())
    )

    if all_cls_in_recon:
        lines += [
            "| manual_classification | detector_flag=True | detector_flag=False | Total |",
            "| --- | --- | --- | --- |",
        ]
        for cls in ALL_CLASSIFICATION_VALUES:
            f = flagged.get(cls, 0)
            nf = not_flagged.get(cls, 0)
            lines.append(f"| {cls} | {f} | {nf} | {f + nf} |")
        tf = reconciliation["total_flagged"]
        tnf = reconciliation["total_not_flagged"]
        lines.append(f"| **Total** | {tf} | {tnf} | {tf + tnf} |")
        lines.append("")
    else:
        lines += ["*No data.*", ""]

    lines += ["---", ""]

    # ── Note K disposition ────────────────────────────────────────────────────
    lines += [
        "## Note K Re-Evaluation and Disposition",
        "",
        "### Disposition (headline)",
        "",
        f"**{note_k['disposition_string']}**",
        "",
        "### Supporting numerics",
        "",
        note_k["supporting_numerics"],
        "",
    ]

    if note_k["disposition"] == "CONFIRMED-with-mechanism":
        lines += [
            "### Mechanism description",
            "",
            "> " + note_k["mechanism_string"],
            "",
            "The framing above describes **what the model's output attributes the",
            "safety event to** — a mechanism description, not a claim about the",
            "model's internal state (per Amendment 3 §3.3 and Ruling 3",
            "public-copy guardrails).",
            "",
        ]
    else:
        lines += [
            "### Mechanism description",
            "",
            "Mechanism description: " + note_k["mechanism_string"],
            "",
            f"Note: disposition is `{note_k['disposition']}` (not",
            "CONFIRMED-with-mechanism) because the cross-provider replication",
            f"threshold ({NOTE_K_MIN_PROVIDERS} distinct providers) is not met.",
            (
                f"Distinct providers in safety/blocked cohort: "
                f"{note_k['n_providers']} "
                + (
                    "(none)."
                    if not note_k["distinct_providers"]
                    else f"({', '.join(note_k['distinct_providers'])})."
                )
            ),
            "",
        ]

    threshold_met = (
        "MET" if note_k["total_safety_blocked"] >= NOTE_K_CONFIRMED_THRESHOLD else "NOT MET"
    )
    xprovider_met = (
        "MET" if note_k["n_providers"] >= NOTE_K_MIN_PROVIDERS else "NOT MET"
    )
    lines += [
        "### Disposition arithmetic",
        "",
        f"- `safety_event_attribution` count: {note_k['safety_event_attribution_count']}",
        f"- `blocked_event_attribution` count: {note_k['blocked_event_attribution_count']}",
        f"- Combined (Note K input): {note_k['total_safety_blocked']}",
        f"- CONFIRMED threshold: >= {NOTE_K_CONFIRMED_THRESHOLD}",
        f"  (threshold {threshold_met})",
        f"- Distinct providers in safety/blocked cohort: {note_k['n_providers']}",
        f"  (cross-provider threshold >= {NOTE_K_MIN_PROVIDERS}: {xprovider_met})",
        (
            f"- K-frame count: {note_k['k_frame_count']}"
            " (descriptive, not a disposition input per D21)"
        ),
        (
            f"- K-vocab count: {note_k['k_vocab_count']}"
            " (descriptive, not a disposition input per D21)"
        ),
        "",
    ]

    lines += ["---", ""]

    return "\n".join(lines)


# ── JSON output ───────────────────────────────────────────────────────────────

def build_json_output(
    primary_view: dict[str, Any],
    secondary_view_a: dict[str, Any],
    secondary_view_b: dict[str, Any],
    reconciliation: dict[str, Any],
    note_k: dict[str, Any],
    decline_count: int,
    informant_count: int,
) -> dict[str, Any]:
    """Build a structured JSON representation of all outputs."""

    def _serialize_triple_matrix(m: dict[str, dict[Any, int]]) -> dict[str, dict[str, int]]:
        """Convert triple-keyed matrix to JSON-serializable form."""
        return {
            cls: {
                f"{p}/{mid}/{d}": count for (p, mid, d), count in counts.items()
            }
            for cls, counts in m.items()
        }

    return {
        "script_version": SCRIPT_VERSION,
        "population": {
            "decline_interviews": decline_count,
            "informants": informant_count,
        },
        "primary_view": {
            "origins": primary_view["origins"],
            "outcomes": primary_view["outcomes"],
            "matrix": primary_view["matrix"],
            "total_by_outcome": primary_view["total_by_outcome"],
            "total_by_origin": primary_view["total_by_origin"],
            "grand_total": primary_view["grand_total"],
            "flags": primary_view["flags"],
        },
        "secondary_view_a": {
            "matrix": _serialize_triple_matrix(secondary_view_a["matrix"]),
            "triples": [f"{p}/{m}/{d}" for p, m, d in secondary_view_a["triples"]],
            "cross_provider_table": secondary_view_a["cross_provider_table"],
            "provider_subtype_counts": secondary_view_a["provider_subtype_counts"],
        },
        "secondary_view_b": secondary_view_b,
        "reconciliation": reconciliation,
        "note_k": note_k,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 4a.1 T4: Note J cross-tab + Note K re-evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--decline-interviews",
        type=pathlib.Path,
        default=pathlib.Path("data/raw/decline_interviews.jsonl"),
        help="Path to data/raw/decline_interviews.jsonl",
    )
    parser.add_argument(
        "--informants",
        type=pathlib.Path,
        default=pathlib.Path("data/raw/informants.jsonl"),
        help="Path to data/raw/informants.jsonl",
    )
    parser.add_argument(
        "--manual-classification",
        type=pathlib.Path,
        default=pathlib.Path(
            "data/derived/decline_interviews_manual_classification.jsonl"
        ),
        help="Path to data/derived/decline_interviews_manual_classification.jsonl",
    )
    parser.add_argument(
        "--subtype",
        type=pathlib.Path,
        default=pathlib.Path(
            "data/derived/decline_interviews_safety_attribution_subtype.jsonl"
        ),
        help=(
            "Path to data/derived/decline_interviews_safety_attribution_subtype.jsonl "
            "(Amendment 3 addition)"
        ),
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=None,
        help="Write Markdown output to this file (default: stdout)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Emit structured JSON instead of Markdown",
    )
    parser.add_argument(
        "--json-output",
        type=pathlib.Path,
        default=None,
        help="Write JSON output to this file (default: stdout when --json is set)",
    )
    return parser.parse_args(argv)


def run(
    decline_interviews_path: pathlib.Path,
    informants_path: pathlib.Path,
    manual_classification_path: pathlib.Path,
    subtype_path: pathlib.Path,
) -> tuple[str, dict[str, Any]]:
    """Run the full T4 analysis and return (markdown, json_dict).

    This is the main entry point for both CLI and test use.
    Raises FileNotFoundError or ValueError on bad inputs.
    """
    # ── Load inputs ───────────────────────────────────────────────────────────
    decline_rows, informants, manual_classifications, subtypes = load_all_inputs(
        decline_interviews_path,
        informants_path,
        manual_classification_path,
        subtype_path,
    )

    # ── Enrich decline rows with domain and model_origin ──────────────────────
    enriched = enrich_decline_rows(decline_rows, informants)

    # ── Build views ───────────────────────────────────────────────────────────
    primary_view = build_primary_view(enriched, informants)
    secondary_view_a = build_secondary_view_a(enriched, manual_classifications, subtypes)
    secondary_view_b = build_secondary_view_b(enriched, manual_classifications)
    reconciliation = build_reconciliation_table(manual_classifications)
    note_k = compute_note_k_disposition(manual_classifications, subtypes, secondary_view_a)

    # ── Render outputs ────────────────────────────────────────────────────────
    md = render_markdown(
        primary_view,
        secondary_view_a,
        secondary_view_b,
        reconciliation,
        note_k,
        decline_count=len(decline_rows),
        informant_count=len(informants),
    )
    json_out = build_json_output(
        primary_view,
        secondary_view_a,
        secondary_view_b,
        reconciliation,
        note_k,
        decline_count=len(decline_rows),
        informant_count=len(informants),
    )

    return md, json_out


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    args = _parse_args(argv)

    try:
        md, json_dict = run(
            decline_interviews_path=args.decline_interviews,
            informants_path=args.informants,
            manual_classification_path=args.manual_classification,
            subtype_path=args.subtype,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        json_str = json.dumps(json_dict, indent=2, ensure_ascii=False)
        if args.json_output:
            args.json_output.write_text(json_str, encoding="utf-8")
        else:
            print(json_str)
    else:
        if args.output:
            args.output.write_text(md, encoding="utf-8")
        else:
            print(md)

    return 0


if __name__ == "__main__":
    sys.exit(main())
