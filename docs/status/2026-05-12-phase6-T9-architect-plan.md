# Phase 6 T9 — Failures-as-Findings Data Layer — Architect Plan

**Save to:** `/opt/lsb-agent/docs/status/2026-05-12-phase6-T9-architect-plan.md`

**Date:** 2026-05-12
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T9 only (defined in `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T9 as "extend `cdb_publish/build.py` to emit `apps/dashboard/public/data/failures/{domain_slug}.json` from `data/raw/failures.jsonl` and `data/raw/decline_interviews.jsonl`, joined by `domain_slug`, with the §1.5 framing applied; surface refusal `response_verbatim`, follow-up `prompt_verbatim` + `response_verbatim`, and `originating_outcome_class`; sanitization wrapper per `SECURITY_AND_HARDENING.md` §3.3").
**Status:** Awaiting CDA SME dispatch (REQUIRED — see §6). No UI/UX gate (T9 is backend-only; T10 is the UI surface and will engage UI/UX separately). Coder dispatch on CDA SME PASS / PASS-WITH-NOTES.

---

## §0. Reading list (mandatory before Coder dispatch)

Common to T9:

1. `/opt/lsb-agent/CLAUDE.md` §6 binding rules (especially **R6 schema-touch + DATA_DICTIONARY co-update**, R8 keys, R9 fixtures, **R12 §1.5.4 language guardrails — binding on every LSB-authored category label and caption in the failures JSON**), §7 forbidden vocabulary, §9 pitfalls (**#4** "model X declined" framing as first-class state, **#5** schema-touch co-update, **#11** webhook URLs as secrets, **#13** detector / marker-list role boundaries — the `originating_outcome_class` enum already classifies output-side records; do not introduce input-side detector tokens at publish time).
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (binding on every LSB-authored text artifact published from this layer — captions, category labels, manifest entry strings; raw record content from the models is verbatim data, not LSB-authored prose, and is exempt per §2.6 below), **§1.5.4 forbidden vocabulary table**, §3.2 `InformantRecord` / `DeclineInterview` schemas, §4.1 collection pipeline (where `data/raw/failures.jsonl` is produced — see `packages/cdb_collect/cdb_collect/jsonl.py:append_failure`), §4.4 publish layer.
3. `/opt/lsb-agent/SECURITY_AND_HARDENING.md` §3.3 LLM-output sanitization (the publish-layer redaction boundary; T9 reuses the existing convention — no new redaction tooling), §8.3 "no secret in any error message," §9 Reviewer rules table (especially R2 sanitization, R4 append-only invariant — read-only access to `data/raw/`, R10 webhook secret pattern).
4. `/opt/lsb-agent/docs/DATA_DICTIONARY.md` (T9 adds a new published-JSON shape entry; field semantics for `Failure` and `DeclineInterview` are documented as the open data bundle contract).
5. `/opt/lsb-agent/packages/cdb_core/cdb_core/schemas.py` — `DeclineInterview` Pydantic schema (lines 555–639), `InformantRecord` (lines 456–547 — needed for the decline-interview → domain join; see §2.4 below).
6. `/opt/lsb-agent/packages/cdb_collect/cdb_collect/jsonl.py` (lines 45–124, `append_failure()` — defines the *de facto* failure-record shape; **there is no Pydantic `Failure` schema** — failures are written as raw dicts per §2.4 below), `/opt/lsb-agent/packages/cdb_collect/cdb_collect/exceptions.py` (PartialSessionError carries the verbatim fields written into failures.jsonl).
7. `/opt/lsb-agent/packages/cdb_publish/cdb_publish/build.py` (extension point — T9 adds `build_failures()` and wires into the main `build()` flow), `/opt/lsb-agent/packages/cdb_publish/cdb_publish/schemas/manifest.py` (Manifest schema — T9 extends per §2.7 below).
8. `/opt/lsb-agent/data/raw/failures.jsonl` and `/opt/lsb-agent/data/raw/decline_interviews.jsonl` — actual record shapes peeked during planning; **verbatim content includes provider error URLs, model refusal text, and full thinking traces**.
9. Memory: `project_failures_are_findings.md` (2026-04-23 binding directive — "all failed / refused / partial runs preserved verbatim; dashboard must expose failures with raw logs"), `feedback_visual_inspection.md` (failures must be renderable, T10 territory), `feedback_ui_polish_scope.md` (Phase 6 minimum-viable functional surface).
10. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T7-architect-plan.md`, `T7-cda-sme-verdict.md`, `T5-architect-plan.md`, `T5-cda-sme-verdict.md` — plan structure precedent and CDA SME verdict format precedent.

---

## §1. Mark's binding directives + Phase 6 framing

1. **"Failures are findings" — 2026-04-23 directive (memory `project_failures_are_findings.md`).** Every failed / refused / partial run is preserved verbatim. Refusals already trigger follow-up "why did you decline" interviews (the existing `cdb_collect/run_decline_interview.py` workflow produces `decline_interviews.jsonl`). T9's job is the publish-layer half: emit per-domain JSON files that surface those raw records to the dashboard so T10 (the UI surface) can render them. The mismatch between "successful response" and "no parseable output" is the finding — not a defect, not a placeholder, not a pending state.
2. **§1.5 framing is binding on all LSB-authored text in the published JSON.** That includes: any category-label string LSB invents (none under §2.6 below — we surface the schema's `originating_outcome_class` enum verbatim), any caption emitted by the publish layer (none under §2.6), and the manifest entry string. **It does NOT apply to the verbatim model output preserved in `response_verbatim`, `prompt_verbatim`, `thinking_verbatim`, or `error_message`** — that text is the data, not LSB's prose. Publishing verbatim text without editing IS the §1.5 stance: LSB does not paraphrase the model's output into a framed claim, it surfaces the bytes and the §1.5 framing lives in T10's surrounding UI copy and the methodology page.
3. **Phase 6 minimum-viable functional surface (memory `feedback_ui_polish_scope.md`).** T9 is a backend data layer; the contract is "emit the JSON shape T10 needs to render." No microcopy work, no rich-text decoration, no aesthetic decisions. The published JSON is purely data.
4. **Publication safety: publish-layer §3.3 sanitization wrapper is the redaction boundary.** See §2.1 below for the binding default proposal that the CDA SME approves or refines. The Architect's strong recommendation is publish-all-records-verbatim, gated only by the existing §3.3 sanitization (no new redaction logic).
5. **No software-side spend gates (CLAUDE.md R14).** N/A to a publish-layer extension that reads existing JSONL; restated for closure.
6. **No new dependencies.** Implement using Python stdlib + existing `pydantic` for `DeclineInterview` parsing + existing `cdb_core` schemas. No new packages.
7. **Read-only access to `data/raw/`.** The append-only invariant (Reviewer R4) is preserved: T9 reads `data/raw/failures.jsonl` and `data/raw/decline_interviews.jsonl`; it does not modify them, ever. Source-file SHA256s must be byte-identical before and after `build()` runs.

---

## §2. Decisions (Architect's call, documented for the record)

### §2.1. Publication-safety default proposal — **publish ALL records verbatim, gated by existing §3.3 sanitization.** (CDA SME REQUIRED — owns binding decision.)

**The proposal.** Every record currently in `data/raw/failures.jsonl` and `data/raw/decline_interviews.jsonl` is eligible for publication to `apps/dashboard/public/data/failures/{domain_slug}.json`, in raw verbatim form, with two non-negotiable conditions:

1. **The existing `SECURITY_AND_HARDENING.md` §3.3 boundary applies** — every byte that reaches the dashboard's React render path eventually flows through the `SanitizedLLMText` wrapper (T10 enforces at the UI layer; T9 emits JSON whose string fields are plain text and therefore safe to render through that wrapper). T9 emits no HTML, no markdown, no embedded URLs as hyperlinks — strings only.
2. **One defensive sanitization pass at the publish layer** strips three categories of strings from `error_message`, `response_verbatim`, `prompt_verbatim`, `thinking_verbatim`, and any string in `partial_session` / `retry_attempts` before they land in the published JSON:
   - **Local filesystem paths** matching `data/raw/`, `data/results/`, `data/processed/`, `/opt/lsb-agent/`, `/home/lsb/`, `/home/markd/` — these should not appear in model output, but defense-in-depth (one of the failure records has a provider error URL in plain English, which is fine; a local path leaking through would be a privacy concern).
   - **Anthropic / OpenRouter / HuggingFace / Backblaze API-key patterns** matching the `gitleaks` patterns in `SECURITY_AND_HARDENING.md` §3.4 (`sk-ant-…`, `sk-or-v1-…`, `hf_…`, `K…` for B2). Defensive only; these should never appear in model output, but a single accidental leak is one too many.
   - **Slack webhook URL patterns** matching `https://hooks.slack.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+` (Reviewer R10). Defensive.

   Match → replace with the literal string `"[redacted: secret pattern]"` (no information leak about which pattern matched). A `data/raw/`-style path → `"[redacted: local path]"`. Same redaction marker style as `gitleaks --redact`.

**The Architect's rationale (CDA SME may override):**

- **The publish layer is already the redaction boundary** — `data/raw/` was always developer-facing; `apps/dashboard/public/` is reader-facing. T9 codifies this boundary explicitly for the failures case, mirroring how the `DomainResult` publish flow already handles it implicitly (a domain result's strings — model IDs, free-list items, ledes — are also developer-originated content that the dashboard surfaces).
- **Verbatim model output IS the finding.** Redacting model refusal language ("I'm sorry, I can't help with that") or model thinking trace would defeat the purpose of the 2026-04-23 directive. The whole point is to surface what the model actually said.
- **The §1.5 framing protects against the "models embarrassing themselves" framing** — at the T10 UI layer. T9's job is to emit the data; the framing wrapper around the data ("the model's output produced no parseable response," not "the model refused to think about X") lives on T10's failures section heading and the methodology page (T1/T2). T9 does not paraphrase or edit the verbatim text.
- **Provider T&C compliance is a Phase 8 legal-review concern, not T9.** The dashboard does not go public-launch until Phase 8; T9 emits the JSON, T10 builds the UI, and the legal-review pass at Phase 8 either confirms publication is safe or specifies a redaction policy that T9/T10 then implement. The default-public-with-sanitization posture is reversible if legal review at Phase 8 says otherwise. Defaulting to redacted-and-conservative now would create UI affordances ("[redacted]" placeholders) that would need to be unwound later, which is more work than the reverse.
- **The §3.3 sanitization wrapper exists precisely for this — model-generated text rendered in the dashboard.** T10 will use it. T9 ensures the JSON the wrapper consumes is plain text, not HTML or markdown.

**CDA SME's binding scope on this question:**

1. **PASS** → publish all records, default sanitization passes (paths, API keys, webhook URLs), no per-record redaction beyond that. T9 proceeds.
2. **PASS-WITH-NOTES** → publish all records BUT with additional sanitization or category-label adjustments (e.g., redact `originating_failure_id` if it leaks operational info; rewrite the `originating_outcome_class` enum surface; gate `thinking_verbatim` behind an opt-in flag). Notes apply at the Coder dispatch.
3. **FAIL** → publication-safety posture rejected. CDA SME specifies what redaction is required. T9 re-planned to apply that policy. (Architect's expectation: PASS or PASS-WITH-NOTES.)

The CDA SME reviews against the **four-axis framework** with explicit attention to:

- **Protocol validity:** is publishing the raw output of a failed elicitation a valid representation of the CDA protocol's output? (The Architect's reading: yes — failed elicitations are part of the protocol's output distribution. The protocol does not assume every elicitation succeeds.)
- **Analytical validity:** does the published JSON allow a reader to reproduce the "failures-as-findings" claim? (Yes if the verbatim bytes are present; no if they're redacted.)
- **Claims validity:** does publishing verbatim model output overclaim? (The §1.5 framing in T10's surrounding UI is what guards against overclaim; the data itself is the data.)
- **Audience translation:** will a journalist or AI engineer reading the published JSON understand it without inadvertently quoting a model in a way that embarrasses the provider? (T10's framing is the protection; T9's JSON has no narrative element.)

### §2.2. Published JSON shape — flat record list, one file per domain.

Each domain produces `apps/dashboard/public/data/failures/{domain_slug}.json`:

```json
{
  "domain_slug": "family",
  "generated_at": "2026-05-12T18:30:00Z",
  "n_records": 47,
  "n_failure_records": 32,
  "n_decline_interview_records": 15,
  "records": [
    { "record_type": "failure", … },
    { "record_type": "decline_interview", … },
    …
  ]
}
```

**Top-level fields:**

| Field | Type | Source / semantics |
|---|---|---|
| `domain_slug` | `str` | The domain slug, mirroring the same field in the per-domain `DomainResult` JSON. |
| `generated_at` | `str` (ISO-8601 UTC) | Build-time wallclock when the JSON was emitted. Mirrors the existing `Manifest.built_at` semantic. |
| `n_records` | `int` | Total record count in this file (`n_failure_records + n_decline_interview_records`). |
| `n_failure_records` | `int` | Subtotal of `record_type === "failure"`. |
| `n_decline_interview_records` | `int` | Subtotal of `record_type === "decline_interview"`. |
| `records` | `list[FailuresPublishedRecord]` | The records themselves, ordered by `collection_date` ascending (then by `record_type`, then by stable identifier). |

**Sort order (stable, deterministic):** primary key `collection_date` (or `timestamp` / `detection_timestamp` — see field-coverage table for which timestamp each record_type uses; mapped to a single `collection_date` field on the published record per §2.4). Secondary: `record_type` ascending lexicographic (`"decline_interview"` before `"failure"`). Tertiary: the record's unique identifier (`originating_informant_id` for failures' best-available stand-in; `decline_interview_id` for decline_interviews). The Coder uses a single sort key tuple — no special-casing.

**`record_type` discriminator:** `"failure"` or `"decline_interview"`. Required, always present. Determines which fields are populated; see §2.4.

**Empty domain case (no records):** see §2.7. The file is **still emitted** for the domain (with `records: []`) so the dashboard can render the section uniformly across all domains. The manifest entry (§2.5) is also still emitted (pointing at the empty file). This is the §1.5.5 first-class-state stance for the cross-domain case — "zero failures" is a normal observation, not a fallback.

### §2.3. Sanitization wrapper — reuse `SECURITY_AND_HARDENING.md` §3.3 plus a publish-layer defensive pass.

**At the dashboard render layer (T10's concern, not T9's):** every string field in this JSON eventually flows through `SanitizedLLMText` (per §3.3). T9 ensures the JSON contains only plain strings — no markdown, no HTML fragments, no embedded URLs as hyperlinks. The Coder writes strings as-is (after the publish-layer defensive pass below); React's text-node auto-escaping at the T10 render time is the XSS prevention.

**At the publish layer (T9's concern):** a single Python function in a new module `packages/cdb_publish/cdb_publish/sanitize.py` runs the three defensive passes (paths, API keys, webhook URLs) over every string field of every published record. Specifically:

```python
# packages/cdb_publish/cdb_publish/sanitize.py
import re

# Patterns mirror SECURITY_AND_HARDENING.md §3.4 gitleaks rules.
_API_KEY_PATTERNS = [
    re.compile(r"sk-ant-[a-zA-Z0-9_-]{50,}"),
    re.compile(r"sk-or-v1-[a-zA-Z0-9]{60,}"),
    re.compile(r"hf_[a-zA-Z0-9]{30,}"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # generic OpenAI/Anthropic shape; defensive
]
_WEBHOOK_PATTERN = re.compile(
    r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+"
)
_LOCAL_PATH_PATTERNS = [
    re.compile(r"/opt/lsb-agent/[^\s\"']*"),
    re.compile(r"/home/(lsb|markd)/[^\s\"']*"),
    re.compile(r"\bdata/raw/[^\s\"']*"),
    re.compile(r"\bdata/results/[^\s\"']*"),
    re.compile(r"\bdata/processed/[^\s\"']*"),
]

def sanitize_for_publication(s: str) -> str:
    """Redact secret-shaped strings and local-filesystem paths from
    a model-generated or pipeline-generated string before publishing
    it to apps/dashboard/public/. See SECURITY_AND_HARDENING.md §3.3
    and §3.4.
    """
    for pat in _API_KEY_PATTERNS:
        s = pat.sub("[redacted: secret pattern]", s)
    s = _WEBHOOK_PATTERN.sub("[redacted: secret pattern]", s)
    for pat in _LOCAL_PATH_PATTERNS:
        s = pat.sub("[redacted: local path]", s)
    return s
```

**Applied to every string in every record's published shape** — `error_message`, `response_verbatim`, `prompt_verbatim`, `thinking_verbatim`, `stop_reason`, `qa_notes`, and recursively into `partial_session` and `retry_attempts` nested dicts. The Coder writes a small `_sanitize_record_strings()` walker that traverses the dict and applies `sanitize_for_publication()` to every `str` leaf.

**Test fixture required (Tester):** at least one synthetic record per pattern category to confirm redaction fires; the Reviewer can spot-check that the function does not match on benign strings (e.g., `"openrouter.ai"` appearing in an error URL is not a secret).

**The §3.3 wrapper itself is unchanged.** T9 does NOT modify `apps/dashboard/src/lib/sanitizeLLMText.tsx`. The publish-layer pass is additive defense, not a replacement for `SanitizedLLMText`.

### §2.4. Field-coverage table — every `Failure` and `DeclineInterview` field → published shape.

**Important note on the `Failure` shape:** there is **no Pydantic `Failure` schema** in `cdb_core/schemas.py`. Failure records are written as raw dicts by `cdb_collect.jsonl.append_failure()` (`packages/cdb_collect/cdb_collect/jsonl.py:45`). The de facto shape (verified against actual `data/raw/failures.jsonl` content) is documented in `append_failure()`'s docstring. T9 reads these as plain dicts — no Pydantic parsing on the failure side.

**Failure records — dict shape from `append_failure()`:**

| Source field (in `failures.jsonl` dict) | Type | Published as | Notes |
|---|---|---|---|
| `timestamp` | `str` (ISO-8601) | `collection_date: str` | Renamed for symmetry with `decline_interview` records. Used as primary sort key. |
| `error_type` | `str` | `error_type: str` | Pass-through. |
| `error_message` | `str` | `error_message: str` (sanitized) | §2.3 sanitization applied. |
| `context.model_id` | `str` | `model_id: str` | Pass-through. |
| `context.domain` | `str` | `domain_slug: str` (top-level group key) | The **domain join key** for failures. Note: the source field is `context.domain`, NOT `context.domain_slug` — defensive map at read time. Records whose `context.domain` is missing or null are filtered out (cannot be joined to a domain) and not published; the Coder logs a warning per filtered record. |
| `context.run_index` | `int` | `run_index: int` | Pass-through. |
| `prompt_verbatim` | `str?` | `prompt_verbatim: str?` (sanitized) | Optional; the field is omitted entirely from the published record when absent (matching the source-record convention — see `append_failure()`'s "Field order" docstring). |
| `response_verbatim` | `str?` | `response_verbatim: str?` (sanitized) | Optional, same rule. |
| `thinking_verbatim` | `str?` | `thinking_verbatim: str?` (sanitized) | Optional, same rule. |
| `stop_reason` | `str?` | `stop_reason: str?` | Optional, same rule. |
| `thoughts_token_count` | `int?` | `thoughts_token_count: int?` | Optional, same rule. |
| `partial_session` | `dict?` | `partial_session: dict?` (recursively sanitized) | Optional; structure is `{freelist?: {...}, pile_sort?: {...}, interview?: {...}}` per `append_failure()` docstring. Passed through with §2.3 sanitization applied to every string leaf. |
| `retry_attempts` | `list[dict]` | `retry_attempts: list[dict]` (recursively sanitized) | Always present (defaults to `[]`); each entry has `attempt_index`, `response_verbatim`, `thinking_verbatim`, `stop_reason`, `input_tokens`, `output_tokens`, `latency_ms`, `parse_error_message`. Strings sanitized. |
| — (derived) | — | `record_type: "failure"` | Constant for this record type. |
| — (derived) | — | `originating_outcome_class: null` | Failures do not carry this field (only DeclineInterviews do). Always `null` for `record_type === "failure"` so T10's render code can treat the field uniformly. |

**`DeclineInterview` records — Pydantic schema from `cdb_core/schemas.py:555`:**

| Source field (`DeclineInterview`) | Type | Published as | Notes |
|---|---|---|---|
| `decline_interview_id` | `str` | `decline_interview_id: str` | Pass-through (stable identifier). |
| `originating_informant_id` | `str?` | `originating_informant_id: str?` | One of two xor-paired join keys; see "domain join" below. |
| `originating_failure_id` | `str?` | `originating_failure_id: str?` | The other xor-paired key. |
| `originating_step` | `Literal["freelist", "pile_sort", "interview", "pre_session"]` | `originating_step: str` | Pass-through. |
| `originating_outcome_class` | `Literal[...]` (7 values) | `originating_outcome_class: str` | **Pass-through verbatim from the schema enum.** See §2.6 — no LSB-authored rewording. |
| `detection_rule_version` | `str` | `detection_rule_version: str` | Pass-through. |
| `detection_timestamp` | `datetime` | (not published; used internally for sort fallback only) | The user-visible timestamp is `followup_timestamp`. The internal sort uses `collection_date` (mapped from `followup_timestamp` for this record type) for cross-record-type consistency. |
| `followup_timestamp` | `datetime` | `collection_date: str` (ISO-8601) | Renamed for symmetry with failure records. Primary sort key. |
| `model_id` | `str` | `model_id: str` | Pass-through. |
| `model_version_returned` | `str` | `model_version_returned: str` | Pass-through (CLAUDE.md §9 pitfall #1: this is the distinct field from `model_id`). |
| `provider` | `str` | `provider: str` | Pass-through. |
| `api_endpoint` | `str` | `api_endpoint: str` (sanitized) | Sanitized; should not contain secrets but defensive. |
| `prompt_version` | `str` | `prompt_version: str` | Pass-through (e.g., `"decline_v1"`). |
| `sha256_manifest` | `str` | `sha256_manifest: str` | Pass-through (provenance — researchers can verify the verbatim bytes match this hash). |
| `prompt_verbatim` | `str` | `prompt_verbatim: str` (sanitized) | The follow-up prompt LSB sent to the model ("In your own words, please describe what happened in that exchange"). |
| `response_verbatim` | `str` | `response_verbatim: str` (sanitized) | The model's reply to the follow-up — the substantive content of the decline interview. |
| `thinking_verbatim` | `str` | `thinking_verbatim: str` (sanitized) | The follow-up call's reasoning trace, if surfaced by the provider. Empty string when not surfaced. Per schema docstring, this is the follow-up's trace, not the originating session's. |
| `input_tokens` | `int` | `input_tokens: int` | Pass-through. |
| `output_tokens` | `int` | `output_tokens: int` | Pass-through. |
| `latency_ms` | `int` | `latency_ms: int` | Pass-through. |
| `stop_reason` | `str` | `stop_reason: str` | Pass-through. |
| `qa_notes` | `str` | `qa_notes: str` (sanitized) | Pass-through. |
| `version_drift_flag` | `bool` | `version_drift_flag: bool` | Pass-through — flags when the provider rolled a snapshot between original collection and decline-interview pass (see SME Note F 2026-04-23). |
| — (derived) | — | `record_type: "decline_interview"` | Constant for this record type. |
| — (derived via join — see below) | — | `domain_slug: str` (top-level group key) | The decline-interview record itself does NOT carry `domain_slug`. T9 joins via `originating_informant_id` or `originating_failure_id`. |
| — (derived from `latency_ms`, `input_tokens`, `output_tokens`, etc.) | — | (no further derived fields in v1; cost_usd is intentionally NOT published — see §2.6) | |

**Domain join — the central data-integration challenge:**

`DeclineInterview.domain_slug` does not exist on the schema. T9 must compute it via the xor-paired originator:

1. If `originating_informant_id is not None`: look up the informant in `data/raw/informants.jsonl` and read `domain_slug` from there.
2. If `originating_failure_id is not None`: look up the failure entry in `data/raw/failures.jsonl` and read `context.domain` from there. **Failure-record identifier:** failures.jsonl entries do not have a stable explicit ID field. The `cdb_collect/decline_detection.py` module computes a deterministic identifier at decline-trigger time (see `decline_detection.py:105` per Grep `"Build a deterministic identifier for a failures.jsonl entry"`). The Coder reads the existing identifier-derivation function from `cdb_collect/decline_detection.py` (importing it into `cdb_publish`); this is the canonical join function. **The Coder MUST NOT reimplement the identifier scheme** — that would create a drift hazard with the collection layer.

If neither join succeeds (orphaned record — both originator IDs reference unknown records), the decline-interview record is filtered out and logged. This should not happen in practice (the xor invariant + the deterministic-identifier function guarantee join), but defensive.

### §2.5. Empty-state handling per domain — **emit the file with `records: []`, emit the manifest entry pointing at it.**

Three cases:

**Case A — domain has both failures and decline-interviews.** Normal case. Emit `failures/{slug}.json` with mixed records. Manifest entry: `"failures": { "family": "data/failures/family.json", … }`.

**Case B — domain has failures but no decline-interviews (or vice versa).** Normal case. Emit `failures/{slug}.json` with whichever records exist. Manifest entry as above.

**Case C — domain has zero failures AND zero decline-interviews.** **Still emit `failures/{slug}.json` with `records: []`.** Still emit the manifest entry. Architect's reasoning: T10's render code needs a uniform contract — every domain has a failures section, even if empty. The dashboard's framing of "zero failures observed for this domain" is a first-class state per CLAUDE.md §9 pitfall #4 and ARCHITECTURE.md §1.5.5 ("the empty case is a normal first-class state, not a fallback"). The T10 UI surfaces this as "No collection failures or declines observed for this domain in this analysis version." (T10's copy, not T9's.) T9 emits `records: []` and lets T10 frame.

**Manifest entry is always present for every domain in the manifest's `domains` list**, even if `records: []`. The path is always `data/failures/{slug}.json`; never `null`. (Kickoff §2 T9 proposed `null` for empty; Architect overrides: emit empty file + non-null path for uniform contract.)

### §2.6. Forbidden-vocabulary handling for LSB-authored labels — **none required; surface schema enums verbatim.**

**Architect's call:** T9 emits NO new LSB-authored category labels or captions. Every label in the published JSON comes from one of three sources:

1. **Schema enum values** (`originating_outcome_class` — already a `Literal[...]` in `cdb_core.schemas.DeclineInterview`; `originating_step` ditto; `record_type` is a publish-layer literal, not a label).
2. **Field names** (`prompt_verbatim`, `response_verbatim`, etc.) — data identifiers, not prose.
3. **Verbatim model output** (the strings inside `response_verbatim`, `thinking_verbatim`, etc.) — model-authored, not LSB-authored. Exempt from §1.5.4 per kickoff §2 T9 and per the spirit of the "failures are findings" directive (the model's words are the finding).

This means **T9 introduces no new vocabulary surface for the CDA SME to police at the publish layer.** The §1.5.4 forbidden vocabulary review for the failures display happens at T10 (the UI layer authors the section heading, the per-record framing label, and the methodology link copy), not at T9.

**However** — the CDA SME's binding scope at T9 includes:

- Approving the schema enum values as-is for public surfacing (or specifying that one or more enum values needs renaming before publication). The values are: `empty_output`, `refusal_string_match`, `single_degenerate_pile`, `parse_failure`, `http_error`, `timeout`, `other`. The Architect's reading: these are descriptive technical terms, none of which carry psychological-attribution baggage. `refusal_string_match` is the only one with any framing weight; it describes the detection rule (a string match against a list of refusal patterns), not a claim about the model's intent. CDA SME confirms or requests rewording.
- Approving the manifest key `"failures"` (vs. e.g., `"refusals_and_failures"` or `"non_responsive_records"` or `"unparseable_outputs"`). The Architect's recommendation: `"failures"` is shortest, descriptively accurate (the data IS the set of failed elicitations), and aligned with the source file name `data/raw/failures.jsonl`. The §1.5 framing concern is real — "failure" implies a defect, and the 2026-04-23 directive specifically says "failures are findings, not defects" — but renaming the manifest key adds friction without changing the data. CDA SME confirms or recommends an alternative. (If alternative: the Coder applies it consistently across the manifest entry, the directory name `apps/dashboard/public/data/failures/`, the published JSON file names, and the function name `build_failures()`.)

If CDA SME approves both as-is → no LSB-authored prose surface in T9. If CDA SME requests rewording of any enum value → the schema is touched (CLAUDE.md R6 — Architect sign-off required + DATA_DICTIONARY.md co-update), which expands T9's scope; in that case the Architect re-plans rather than the Coder absorbing scope creep.

### §2.7. Manifest extension — add `failures: dict[str, str]` to the `Manifest` schema.

The existing `Manifest` schema (`packages/cdb_publish/cdb_publish/schemas/manifest.py`) currently has:

```python
class Manifest(BaseModel):
    built_at: datetime
    domains: list[ManifestDomain]
    oci_low_concentration_threshold: float = OCI_LOW_CONCENTRATION_THRESHOLD
```

T9 extends `Manifest` with:

```python
    failures: dict[str, str] = {}
    """Map from domain_slug to the published failures JSON path,
    relative to apps/dashboard/public/. Always present and always
    non-null for every domain in `domains` — empty-domain files
    are emitted with `records: []`. See
    docs/status/2026-05-12-phase6-T9-architect-plan.md §2.5
    and docs/DATA_DICTIONARY.md.
    """
```

This is a **publish-layer schema** (`cdb_publish/schemas/`), NOT a `cdb_core` schema, so **no Architect sign-off is required under CLAUDE.md R6.** The schema lives under `cdb_publish/` and is not part of the open data contract (the `cdb_core` schemas are; the publish-layer manifest is a dashboard-internal index). The Coder edits `manifest.py` directly without invoking R6.

**Cost framing constraint:** the publish-layer manifest must not introduce any cost-estimate or spend-cap field (CLAUDE.md R14; CI grep check enforces). The `failures` dict is a path map, no cost-adjacent semantics.

**Empty-failures convention (binding decision per §2.5 override of kickoff):** every domain in `domains` has an entry in `failures`. No `null` values. No omission. T10's render code can rely on `manifest.failures[slug]` always being a valid path.

### §2.8. Build flow integration — extend `build()` in `packages/cdb_publish/cdb_publish/build.py`.

Two new module-level functions in a new file `packages/cdb_publish/cdb_publish/failures.py` (separation of concerns — keeps `build.py` from growing past comfortable size):

```python
# packages/cdb_publish/cdb_publish/failures.py
"""Failures-as-findings publish layer. See ARCHITECTURE.md §4.4 and
docs/status/2026-05-12-phase6-T9-architect-plan.md."""

def build_failures(
    raw_failures_path: Path,
    raw_decline_interviews_path: Path,
    raw_informants_path: Path,
    output_dir: Path,
    domain_slugs: list[str],
) -> dict[str, str]:
    """Read raw failures and decline interviews, join to domains, emit
    one apps/dashboard/public/data/failures/{slug}.json per domain.

    Returns the failures-path dict for the manifest.

    Empty-domain case: every slug in `domain_slugs` gets an output
    file (with `records: []` if no records); the returned dict has
    an entry for every slug.
    """
    ...
```

And:

```python
def _join_decline_interview_to_domain(
    di: DeclineInterview,
    informants_by_id: dict[str, str],  # informant_id → domain_slug
    failures_by_id: dict[str, str],    # deterministic failure_id → domain_slug
) -> str | None:
    """Compute domain_slug for a DeclineInterview via its xor-paired
    originator. Returns None for orphaned records (which the caller
    filters out and logs)."""
    ...
```

**Wiring into `build()`:** at the end of the existing `build()` function in `build.py`, after the per-domain loop completes:

```python
    # After existing manifest_domains assembly:
    domain_slugs = [d.slug for d in manifest_domains]
    failures_map = build_failures(
        raw_failures_path=Path("data/raw/failures.jsonl"),
        raw_decline_interviews_path=Path("data/raw/decline_interviews.jsonl"),
        raw_informants_path=Path("data/raw/informants.jsonl"),
        output_dir=output_dir / "failures",
        domain_slugs=domain_slugs,
    )

    manifest = Manifest(
        built_at=datetime.now(tz=UTC),
        domains=manifest_domains,
        failures=failures_map,
    )
```

The `data/raw/` paths are passed as parameters (not hard-coded), so the Tester can drive `build_failures()` against fixtures. The default values for production are wired from `scripts/publish.py` (which already passes `results_dir` and `output_dir` — the new raw-data paths are added there).

**`scripts/publish.py` edit:** the entry-point script gains three CLI args (with sensible defaults pointing at `data/raw/{failures,decline_interviews,informants}.jsonl`) and passes them through to `build()`. **Surgical edit** — no refactoring of the script beyond the three new args.

---

## §3. Acceptance criteria

The task is done when ALL of the following are true:

1. `uv run pytest packages/cdb_publish/ -v && uv run ruff check . && uv run mypy packages/cdb_publish/` passes locally.
2. Running `uv run python scripts/publish.py` (or the equivalent entry point) on the existing `data/results/` + `data/raw/{failures,decline_interviews,informants}.jsonl` produces:
   - `apps/dashboard/public/data/failures/family.json` with the §2.2 shape
   - `apps/dashboard/public/data/failures/holidays.json` with the §2.2 shape
   - `apps/dashboard/public/data/manifest.json` extended with the `failures` map per §2.7
3. The two published failure files validate against an inline `pydantic` model the Coder defines in `cdb_publish/schemas/failures.py` (`PublishedFailuresFile`, `PublishedFailureRecord` with `record_type: Literal["failure", "decline_interview"]`). Schema lives in publish-layer, NOT in `cdb_core` (no R6 trigger).
4. Every record in every emitted file carries `record_type` ∈ `{"failure", "decline_interview"}`.
5. For every record in `data/raw/failures.jsonl` whose `context.domain` is set and maps to a domain in the manifest, a corresponding record appears in the published file for that domain. Failed-to-join records (no `context.domain`) are logged at WARN level and not published. Test coverage for the filter case via a synthetic fixture.
6. For every record in `data/raw/decline_interviews.jsonl` whose xor-paired originator resolves to a known domain, a corresponding record appears in the published file for that domain. Orphaned records (no resolvable originator) are logged at WARN level and not published. Test coverage for both join paths (via `originating_informant_id` and via `originating_failure_id`).
7. The `decline_detection.py:_failure_id` function (or equivalent — the Coder identifies the exact function during implementation) is **imported** into `cdb_publish.failures`, NOT reimplemented. If the function name or signature has drifted, the Coder pauses and surfaces the question rather than fork-reimplementing.
8. The sanitization function `sanitize_for_publication()` in `packages/cdb_publish/cdb_publish/sanitize.py` is applied to every string leaf in every record before write. Tester verifies via synthetic-fixture records seeded with each of the three secret/path categories that the published output contains `"[redacted: …]"` markers in place of the seeded patterns.
9. Domain with zero failures and zero decline-interviews emits an output file with `records: []`, `n_records: 0`, and is listed in the manifest's `failures` map. Tester covers this via a synthetic empty-domain fixture.
10. The build is **deterministic** within a fixed wallclock window: given the same input files, the output files are byte-identical (except for `generated_at` / `built_at` timestamps which reflect wallclock at build). Tester verifies via a same-fixture-rebuild test that compares non-timestamp content.
11. Source files in `data/raw/` are not modified by the build. Reviewer R4 (append-only invariant) holds. Tester verifies via SHA256 before/after on the three `data/raw/*.jsonl` files.
12. Records in each per-domain file are sorted per §2.2: by `collection_date` ascending, then `record_type` ascending, then by stable identifier.
13. The `Manifest` schema in `packages/cdb_publish/cdb_publish/schemas/manifest.py` carries the new `failures: dict[str, str]` field with the docstring per §2.7. Field default is `{}` (preserves backward compatibility for build invocations that predate T9; the value at runtime is always populated).
14. `docs/DATA_DICTIONARY.md` is updated **in the same commit** with a new section documenting the published failures JSON shape — top-level structure, per-record-type field tables (mirroring §2.4), the sanitization policy reference, and the empty-state convention. The CLAUDE.md R6 co-update is not strictly required (no `cdb_core` schema touched) but the Architect requires DATA_DICTIONARY.md update on principle (the open data bundle's contract extends to failure records under the 2026-04-23 directive). See §4.
15. No forbidden vocabulary (CLAUDE.md §7; ARCHITECTURE.md §1.5.4) anywhere in T9-authored prose: function docstrings, the DATA_DICTIONARY.md addition, log messages, error messages, the new `sanitize.py` module's redaction marker strings. Field names (`originating_outcome_class`, etc.) are exempt as data identifiers. Verbatim text inside `response_verbatim` / `prompt_verbatim` / etc. is exempt (model-authored, not LSB-authored).
16. The schema enum `originating_outcome_class` is surfaced **verbatim** from `cdb_core.DeclineInterview` (no per-value LSB-authored rewording), unless the CDA SME's verdict specifies otherwise. (Architect expectation: PASS.)
17. The Coder does NOT touch `cdb_core/schemas.py`. (Architect sign-off would be required if they did; T9 explicitly does not touch core.) Reviewer R6 not triggered.
18. The Coder does NOT touch `apps/dashboard/` source files. (T10 territory.)
19. The Coder does NOT touch `data/raw/*.jsonl`. (Reviewer R4.)
20. The Coder does NOT touch the existing `cdb_publish.build()` flow beyond the surgical wiring described in §2.8 — `_compute_display`, `_select_latest_version`, `generate_lede`, and the existing per-domain JSON write logic are unchanged.
21. Bundle budget: N/A — T9 is backend Python, no dashboard bundle delta.
22. Tester writes pytest test cases (no real network, no real `data/raw/` access in tests — uses `tmp_path` + synthetic JSONL fixtures): join via informant, join via failure, orphaned decline-interview, missing-domain failure, sanitization fires on each pattern category, empty-domain file emitted, sort order correct, build is deterministic on fixture inputs.

---

## §4. Schema impact

| Touch point | Touched? | Co-update required? | Architect sign-off? |
|---|---|---|---|
| `cdb_core/schemas.py` | **No** | No | Not triggered |
| `packages/cdb_publish/cdb_publish/schemas/manifest.py` | **Yes** — adds `failures` field | No (publish-layer schema, not open-data-contract schema) | Architect call: this is approved within the T9 plan |
| `packages/cdb_publish/cdb_publish/schemas/failures.py` | **New file** — defines `PublishedFailuresFile`, `PublishedFailureRecord` | Yes — DATA_DICTIONARY.md documents the published shape per §2 acceptance criterion 14 | Not triggered (publish-layer schema) |
| `packages/cdb_publish/cdb_publish/failures.py` | **New file** — the build logic | N/A (not a schema file) | Not triggered |
| `packages/cdb_publish/cdb_publish/sanitize.py` | **New file** — the redaction passes | N/A | Not triggered |
| `packages/cdb_publish/cdb_publish/build.py` | **Yes** — adds the `build_failures` wiring at the end of `build()` | N/A | Not triggered |
| `scripts/publish.py` | **Yes** — adds three new CLI args for the raw-data paths | N/A | Not triggered |
| `docs/DATA_DICTIONARY.md` | **Yes** — new section per §2 acceptance criterion 14 | Co-update is the same commit by definition | Not triggered |
| `ARCHITECTURE.md` | **No** (the §1.5.6 failures-as-findings text and the §4.4 publish-layer text are sharpened in T14 documentation sweep, not in T9) | No | Not triggered |
| `DESIGN_SYSTEM.md` | No (T10 owns design-system updates for the failures display) | No | Not triggered |

**CLAUDE.md R6 binding interpretation:** R6 ("InformantRecord and GroundingRef schema changes co-update `docs/DATA_DICTIONARY.md`") is **not strictly triggered** because T9 does not touch `cdb_core/schemas.py`. However, the Architect requires the DATA_DICTIONARY.md update in the same commit because:

1. The published failures JSON is part of the open data contract under the 2026-04-23 directive (failures are first-class data, surfaced to readers; researchers using the dashboard's JSON expect a stable contract).
2. The Reviewer's spot check for "schema-touch without dictionary update" generalizes naturally to "published-shape-introduction without dictionary update."
3. Same-commit co-update is the project's general posture for data contracts; deferring docs is the path to drift.

The Architect signs off on the publish-layer manifest extension at plan-acceptance time; the Reviewer enforces the DATA_DICTIONARY co-update at PR review.

---

## §5. Out of scope for T9

Explicitly excluded; do not partially address:

- **T10 (FailuresAsFindings.tsx + dashboard entry point).** Strictly the UI layer; T9 emits the data, T10 consumes it. The dashboard-entry-point options (per-domain section / standalone route / inline MDS marker annotations) are T10 territory and require UI/UX gate engagement that T9 does not.
- **Methodology page link / framing copy.** T1/T2 own the methodology page. T10 (not T9) wires the link from the failures display to the methodology page's "How we handle refusals and declines" section.
- **Per-record redaction beyond §3.3 + §2.3 defensive passes.** If the CDA SME's verdict requires richer redaction (e.g., a per-record `publish_allowed` boolean, an allowlist of provider/model combos that may be published), that becomes a follow-up task with its own plan cycle. T9 implements the §2.1 default proposal as-is on CDA SME PASS.
- **Schema changes to `DeclineInterview` or `InformantRecord`.** Adding a `domain_slug` field directly to `DeclineInterview` would simplify T9's join logic — but it's a `cdb_core` change requiring Architect sign-off + same-commit DATA_DICTIONARY.md co-update + Reviewer R6 enforcement, which expands scope. T9 joins via the existing xor-paired originator pattern instead.
- **Schema for the `Failure` record.** There is currently no `Failure` Pydantic schema in `cdb_core` (failures are dicts produced by `append_failure()`). Promoting failures to a typed `cdb_core` schema is a defensible improvement but expands scope and triggers R6; T9 reads failures as dicts and casts at the boundary.
- **Cost / token aggregation across failures.** Per CLAUDE.md R14 ("no software-side spend gates") and R12, T9 emits `input_tokens`, `output_tokens`, `latency_ms` per record but does NOT aggregate cost across records, does NOT compute total spend on failed elicitations, does NOT emit a `total_cost_usd` field. The `cost_usd` field that exists on individual decline-interview records in `data/raw/decline_interviews.jsonl` is NOT published in v1 (per CLAUDE.md R14 spirit — cost framing on individual records would invite aggregation downstream). The Architect's call: omit `cost_usd` from the published shape; CDA SME can override if desired.
- **Drift integration.** The `version_drift_flag` on DeclineInterviews is surfaced verbatim, but T9 does not cross-link to T3's drift data (which doesn't exist yet) or aggregate drift-affected records across the failures set.
- **A retry endpoint that re-runs a failed elicitation from the dashboard.** Phase 7+ territory; the publish layer is read-only by definition.
- **Filtering published records by date range, by model, or by outcome class.** T9 emits all records; T10 may add client-side filters.
- **Compression of the published JSON.** Cloudflare Pages gzips static files at serve time per `HOSTING_AND_DEV_OPS.md`; no T9 compression work.
- **An API surface or query interface.** Static JSON files per ARCHITECTURE.md §4.4 binding.

---

## §6. Gate routing

- **Architect:** this plan. On Mark's acceptance, the orchestrator dispatches the CDA SME gate.
- **CDA SME: REQUIRED.** Rationale: T9 introduces the failures-as-findings publish-layer surface for the first time. The CDA SME's binding scope:
  1. **Publication-safety binding decision (§2.1).** PASS = publish all records with default §2.3 sanitization. PASS-WITH-NOTES = publish with additional sanitization / category rewording / per-field gating; notes apply at Coder dispatch. FAIL = re-plan with a redaction policy.
  2. **§1.5 framing review on LSB-authored strings (§2.6).** The schema enum values (`originating_outcome_class`: `empty_output`, `refusal_string_match`, `single_degenerate_pile`, `parse_failure`, `http_error`, `timeout`, `other`; `originating_step`: `freelist`, `pile_sort`, `interview`, `pre_session`) are surfaced verbatim — CDA SME confirms each value is §1.5.4-compliant for public surfacing, or specifies rewordings (which would expand scope to `cdb_core` schema change).
  3. **Manifest key naming (`"failures"` vs alternative).** CDA SME confirms or recommends an alternative.
  4. **Forbidden-vocabulary scan on Architect-authored text in this plan + the binding caption/redaction marker strings** (`"[redacted: secret pattern]"`, `"[redacted: local path]"`).
  5. **§1.5.6 binding interpretation on the verbatim-publication posture.** Does publishing raw model refusal text + raw model thinking trace honor the §1.5 framing, or does it risk overclaiming the model's state-of-mind? The Architect's reading: the framing wrapper at T10 + the methodology page is the protection; the data itself is the data. CDA SME confirms or specifies a stronger guard.
  - Four-axis verdict format per the T5/T7 precedents.
  - PASS → Coder dispatches.
  - PASS-WITH-NOTES → notes apply at Coder dispatch; verdict saved to `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md`.
  - FAIL → re-plan.

- **UI/UX agent: NOT REQUIRED for T9.** T9 is a backend Python publish-layer extension; no `apps/dashboard/` source touched. T10 (the UI surface) engages UI/UX separately on its own plan cycle.

- **Coder:** implements after CDA SME PASS (or PASS-WITH-NOTES with applied notes).

- **Reviewer:** standard nine-check sweep, with specific attention to:
  - R1 / R10: no secrets committed; spot-check the sanitization function and the redaction markers for any leak vector
  - R2: no `dangerouslySetInnerHTML` (N/A — T9 doesn't touch `apps/dashboard/`)
  - R4: append-only invariant on `data/raw/` (SHA256 before/after verified by Tester; Reviewer cross-checks)
  - R6: no `cdb_core` schema change; DATA_DICTIONARY.md co-update present in the same commit per acceptance criterion 14 (Architect-required even though strict R6 letter is not triggered)
  - R12: §1.5.4 forbidden vocabulary spot check on Architect/Coder prose; verbatim model output exempt
  - R13: no cost-estimate or spend-cap framing in the new code, the new schema, the docstring, or the DATA_DICTIONARY.md addition

- **Tester:** standard pytest. Per CLAUDE.md §6 R9 (no real model calls in tests; use fixtures). T9's testable surface includes the join logic (both paths + orphans), the sanitization passes (all three categories), the sort order, the empty-domain case, the deterministic-build invariant, the manifest extension, and the source-file SHA256 stability. Fixtures live under `tests/fixtures/failures/` (new directory) with synthetic JSONL files mirroring the real shapes. No reading from `data/raw/` in tests.

---

## §7. Bundle budget watch

**N/A.** T9 is a backend Python `cdb_publish` extension. No dashboard bundle delta. The published JSON files themselves are static assets served by Cloudflare Pages; their on-disk size adds to the public/data/ asset footprint but does not enter the JS bundle. Rough estimate: ~50–200 KB per domain failures JSON (depending on record count and verbatim content size); negligible for static-asset serving.

The dashboard bundle delta for the failures UI lives in T10, not T9.

---

## §8. Dependency order

**Upstream of T9:**
- None strict. T9 reads existing `data/raw/{failures,decline_interviews,informants}.jsonl` files that have been accumulating since Phase 4. No T0/T5/T7-style backend prerequisites.

**Downstream of T9:**
- **T10 — FailuresAsFindings.tsx + dashboard entry point.** Hard dependency: T10 cannot dispatch until T9's JSON shape is published and the manifest is extended. T10's plan-for-review will reference §2.2 of this plan as the data contract.
- **T14 — Documentation sweep.** Updates ARCHITECTURE.md §1.5.6 (the failures-as-findings binding section) and §4.4 (the publish layer's failures sub-section) to match T9's implementation. DESIGN_SYSTEM.md §11 component inventory adds the FailuresAsFindings entry (T10 may codify; T14 confirms).

**Parallel with T9:**
- T1 (methodology page skeleton), T2 (methodology page prose), T3 (drift data layer), T4 (DriftTracker), T5 (SimilarityHeatmap — in flight at this time per the T5 plan), T7 (FreeListCompare — in flight), T11 (mobile hamburger), T12 (mobile bottom-drawer). All independent of T9.

---

## §9. Risks and watch-items

1. **CDA SME requires per-record redaction beyond §2.1 defaults.** Probability: moderate. The verbatim publication of model thinking traces (especially provider-specific reasoning content) is the riskiest aspect of the §2.1 proposal — model thinking traces can contain idiosyncratic content that a provider might consider private. If CDA SME flags this, the most plausible compromise is gating `thinking_verbatim` behind a manifest-level `include_thinking: bool` toggle (default true, can be flipped at publish-time without re-running the build); T9 plan supports the toggle as a follow-up if requested.

2. **Provider T&C compliance is deferred to Phase 8 legal review.** This is a known unresolved concern. The §2.1 proposal is conservative-in-defaults (`SECURITY_AND_HARDENING.md` §3.3 sanitization is the floor) and reversible: at Phase 8, a legal review verdict to redact more is implementable by extending the sanitization passes and re-running the build. The dashboard at Phase 6 close is not yet public-launch-ready (Phase 8 is the launch); failure records being visible on a not-yet-launched dashboard is a development affordance, not a publication.

3. **Refusal text from a model may embarrass the provider.** The §1.5 framing at T10 is the protection — "the model's output produced no parseable response" is the framing, not "the model refused to think about X." If T10's framing turns out to be insufficient at PR review or post-launch, the redaction-via-publish-flag path is the unwind mechanism. Documented for T10's plan.

4. **The `_failure_id` deterministic-identifier function in `cdb_collect/decline_detection.py` may have drifted since the join was originally specified.** The Coder confirms the function's name, signature, and invariant at implementation time. If it has drifted, the Coder pauses and surfaces (CLAUDE.md §8 stop condition — schema/contract drift). The Architect would then re-plan the join semantics rather than the Coder fork-reimplementing.

5. **`context.domain` (not `context.domain_slug`) on failure records.** Defensive coding required at the read boundary; documented in §2.4. The Coder must not "fix" the source records to standardize the field name (CLAUDE.md §10 pitfall #10 / R4 append-only).

6. **Empty `partial_session` and missing-key handling in failure records.** `append_failure()` writes a sparse-dict shape (only present-and-non-None fields are written). The Coder must handle missing keys gracefully in the dict-walker (`KeyError` would be a bug). Tester covers via a minimal failure-record fixture.

7. **The DATA_DICTIONARY.md section may grow large** if the field-coverage table from §2.4 is reproduced verbatim. Coder may abbreviate by referencing this plan; the Reviewer's spot-check criterion is "every published field is documented somewhere reachable from DATA_DICTIONARY.md." Verbose-and-self-contained is preferred; cross-reference acceptable.

8. **The `originating_outcome_class` enum surface includes `refusal_string_match`** — the only value with any framing weight (it describes a detection rule, not a model intent, but a careless reader could misread). CDA SME's §6.2 review will specifically address this. If CDA SME requires rewording, that's a `cdb_core` schema change (`Literal[...]` values change) → R6 trigger → Architect sign-off → expanded scope. Architect expectation: PASS, enum kept verbatim, T10's per-record label copy is where the framing happens.

9. **The `cost_usd` field present on `decline_interviews.jsonl` records is intentionally NOT published** per §5 (out of scope). The Reviewer's R13 check would flag any reintroduction. If the CDA SME requests publishing `cost_usd` for transparency, the Architect re-evaluates per CLAUDE.md R14.

10. **Bundle creep from "just one more derived field."** The Coder must resist adding derived statistics ("total failures per model," "median latency on failed runs," "most common error type"). T9 is a flat-record-list publisher. Aggregations live downstream — either client-side at T10 or in a separate Phase-7+ task.

---

*End of T9 plan. CDA SME dispatch is the next action; verdict goes to `#lsb-cda-sme` and is saved to `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` per the T5/T7 precedent.*

---

# Report back

**One-paragraph summary.**
T9 is the failures-as-findings publish-layer data extension. It reads `data/raw/failures.jsonl` (raw-dict shape from `cdb_collect.jsonl.append_failure()`; no Pydantic schema exists) and `data/raw/decline_interviews.jsonl` (`DeclineInterview` Pydantic records), joins each record to a domain (failures via `context.domain`; decline-interviews via the xor-paired originator → informants.jsonl `domain_slug` OR failures.jsonl `context.domain` using the existing `cdb_collect/decline_detection.py:_failure_id` deterministic identifier function), and emits one `apps/dashboard/public/data/failures/{slug}.json` file per domain with every relevant field surfaced verbatim. The `Manifest` schema (publish-layer, not `cdb_core`) gains a `failures: dict[str, str]` map. A new `cdb_publish/sanitize.py` module applies three defensive redaction passes (API-key patterns, webhook-URL patterns, local-filesystem paths) to every string leaf before write. No `cdb_core/schemas.py` change, no Architect R6 trigger, no dashboard bundle delta. Same-commit `DATA_DICTIONARY.md` update is Architect-required even though strict R6 letter is not engaged. T10 (UI surface) is downstream and engages UI/UX separately.

**Publication-safety proposal (2-3 sentences).**
Publish ALL records currently in `data/raw/failures.jsonl` and `data/raw/decline_interviews.jsonl` verbatim, gated only by the existing `SECURITY_AND_HARDENING.md` §3.3 sanitization (`SanitizedLLMText` at T10) plus a publish-layer defensive pass that redacts API-key patterns, Slack webhook URLs, and local filesystem paths from every string leaf before write. The publish layer is the existing redaction boundary; verbatim model output IS the finding (redacting refusal text would defeat the 2026-04-23 "failures are findings" directive); the §1.5 framing protection lives in T10's surrounding UI copy and the methodology page (T1/T2), not in editing the data itself. Provider T&C compliance is a Phase 8 legal-review concern, reversible (sanitization can be extended at any time and the build re-run), and not a T9 blocker. CDA SME owns the binding PASS/PASS-WITH-NOTES/FAIL decision.

**File / component breakdown.**

New files:
- `/opt/lsb-agent/packages/cdb_publish/cdb_publish/failures.py` — `build_failures()` + `_join_decline_interview_to_domain()` helper
- `/opt/lsb-agent/packages/cdb_publish/cdb_publish/sanitize.py` — `sanitize_for_publication()` + the three regex pattern lists (API keys, webhook URLs, local paths)
- `/opt/lsb-agent/packages/cdb_publish/cdb_publish/schemas/failures.py` — `PublishedFailuresFile` + `PublishedFailureRecord` Pydantic models (publish-layer schema, not `cdb_core`)
- `/opt/lsb-agent/tests/fixtures/failures/` — synthetic JSONL fixtures (new directory)
- `/opt/lsb-agent/docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` — CDA SME verdict, filed after dispatch
- Generated runtime output: `/opt/lsb-agent/apps/dashboard/public/data/failures/family.json`, `holidays.json` (one per domain in the manifest)

Edited files:
- `/opt/lsb-agent/packages/cdb_publish/cdb_publish/build.py` — surgical wiring at end of `build()`
- `/opt/lsb-agent/packages/cdb_publish/cdb_publish/schemas/manifest.py` — add `failures: dict[str, str] = {}` field with docstring
- `/opt/lsb-agent/scripts/publish.py` — three new CLI args for the raw-data paths, passed through to `build()`
- `/opt/lsb-agent/docs/DATA_DICTIONARY.md` — new section documenting the published failures JSON shape (same-commit per acceptance criterion 14)
- `/opt/lsb-agent/apps/dashboard/public/data/manifest.json` — regenerated at build time with the new `failures` map

Untouched (per acceptance criteria):
- `cdb_core/schemas.py`, `apps/dashboard/src/**/*`, `data/raw/*.jsonl`, all existing `cdb_publish` modules except `build.py` and `schemas/manifest.py`.

**Concerns needing Mark's attention before plan review.**

None blocking. The two publication-safety concerns Mark deferred at the kickoff (provider T&C compliance; refusal-text potential to embarrass providers) are correctly routed to the CDA SME under §6 — the four-axis review owns the binding decision and PASS/PASS-WITH-NOTES/FAIL verdict gives the proper escalation path. If the CDA SME's verdict requires a posture Mark explicitly opposes (e.g., aggressive redaction that materially neuters the failures-as-findings directive), the CDA SME's notes will surface that and the Architect will escalate at that point rather than now. The Architect's reading of the 2026-04-23 directive is that verbatim publication is the binding intent; the only question the CDA SME can change is *how* the verbatim text reaches readers (raw, sanitized, gated-behind-toggle), not *whether* failures are surfaced.

One Architect override of the kickoff worth flagging: the kickoff's §2 T9 description left open "render empty `records: []` array or omit the manifest entry"; the Architect chose **emit empty file + non-null manifest path** for every domain (§2.5), to give T10 a uniform render contract. If Mark prefers the omit-when-empty posture, that's a one-line override that propagates through §2.5, §2.7, and acceptance criterion 9.