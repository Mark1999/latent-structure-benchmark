---
filed: 2026-05-17
reviewer: CDA SME agent (Opus)
task: Phase 7 T5 — Queue + review CLI
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 7 T5 — CDA SME verdict on the queue + review CLI

**VERDICT: PASS-WITH-NOTES**

T5 is the lightest CDA SME gate of Phase 7 per the kickoff §3 T5 row, and
the architectural design (`cdb_social/queue.py` atomic-move helpers +
`scripts/social_review.py` v1 reviewer CLI per ARCHITECTURE.md §4.6 line
1215) is **methodologically clean at the structural level**. The
queue-state transitions (`pending → approved / failed`, `pending →
pending` on edit-then-validate-failure) honor the §5.3 / §5.11 framing-
check semantics established at T1 and T3, and the CLI does not surface
the schema fields to a public audience (per Mark's
`feedback_ui_polish_scope.md` memory — internal ops ≠ public dashboard).

The CDA SME's review surface is narrow but load-bearing: the prose the
human reviewer sees on stdout while making the y/n/e call is the
**operator-internal §1.5 boundary**. A CLI label that says "Confidence:
0.5" instead of "Drafter self-rating: 0.5" defeats the T1 §5.4 rename;
a "Reason this should be posted" trigger summary undoes the T1 §5.7
prose discipline. The seven methodology questions are addressed below
with **exact-string recommendations** the Coder must apply, collected
in §5 as eleven binding-at-Coder-dispatch notes.

Headline rulings (one per Orchestrator question):

1. **Column-header phrasing.** Six canonical column headers: `Trigger`,
   `Draft text`, `Framing checks`, `Dashboard`, `Suggested posting time`,
   `Drafter self-rating`. **"Confidence" is forbidden** per T1 §5.4.
   See §5.1.

2. **Validator-results enumeration.** Display the four T3 canonical
   `framing_checks` keys (`hypothesis_framing`,
   `cognition_attribution`, `bare_numeric_without_ci`,
   `register_boundary`) **verbatim** as keys with a `PASS`/`FAIL`
   value per key — NOT a single composite PASS/FAIL summary. Plus a
   single-line `forbidden_terms_hit: []` summary (always empty for any
   queued draft; non-empty surfaces a drafter-validator bug). See §5.2.

3. **Reject-reason structure.** Closed enumeration of five codes plus
   an optional free-text note. The five codes:
   `forbidden_vocab`, `register_boundary`, `bare_numeric`,
   `off_topic`, `other`. The reason is persisted as a top-level
   `rejection_reason` + `rejection_note` field on the `SocialDraft`
   JSON in `queue/failed/`. See §5.3. **T1-schema impact:** two new
   optional fields on `SocialDraft` (or a sidecar JSON); see §5.3 for
   the Coder's two implementation choices.

4. **Edit-path editor contents.** Editor opens with **original draft
   text** as the buffer contents, NOT blank. Rationale: the T3-cached
   prompt invested ~1100 tokens in producing methodology-compliant
   framing; an iterative tweak preserves that scaffolding; a blank
   editor invites the human to recompose without the framing. See §5.4.

5. **Edit-then-validate failure path.** The CLI shows the validator
   failure verbatim (the exact matched forbidden term / the bare
   numeric / the failed framing-check key) before the draft re-enters
   `pending/`. **Wording for the failure screen** binds in §5.5 to
   neutral operational language ("Edit did not pass validator:
   `<check_name>` failed because `<reason>`") — NOT "you wrote
   forbidden vocabulary" (which is shaming and confuses the operator
   role with the drafter role).

6. **Quit-while-displaying.** Pressing `q` leaves the displayed draft
   in `pending/` unchanged (the most conservative semantics). No
   "deferred" state. See §5.6.

7. **Trigger-summary strings per TriggerType.** Five canonical summary
   patterns binding in §5.7. Headline wording fixes:
   - `DIVERGENCE` summary uses **"max pairwise distance"**, not
     "pairwise gap" — `gap` overloads the visual metaphor; `max
     pairwise distance` is the canonical Register-2 phrasing matching
     the T2 evidence-schema docstring.
   - `DRIFT` summary uses **"Procrustes distance"** verbatim (the
     Register-3 statistic name); the placeholder caveat ("threshold
     0.15 unvalidated") surfaces on-screen until the kickoff §7.3
     drift-trigger lockout is released.
   - `MONTHLY_ROUNDUP` summary uses **"monthly cross-domain
     categorical-structure roundup"**, applying the T1 §5.7 prose fix
     verbatim — so the CLI does not surface the
     pre-amendment "state of cultural alignment" phrasing even while
     the T7 ARCHITECTURE.md fix is still pending.

Coder dispatch may proceed on T5 with the eleven binding notes in §5
applied. The Reviewer enforces. No Architect re-planning required; one
minor T1-schema-touch surfaces in §5.3 (two optional fields for
`rejection_reason` + `rejection_note`) — the Coder coordinates with the
Architect on whether to add the fields to `SocialDraft` directly or use
a sidecar JSON.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | N/A | T5 is a CLI / queue-mechanics task; no CDA elicitation protocol surface is touched. The CLI consumes already-validated `SocialDraft` JSON; it does not run free-list / pile-sort / pile-interview / decline-interview logic. |
| Analytical validity | N/A | T5 performs no analytical computation. It surfaces already-computed values (the trigger evidence dict, the framing-check pass/fail entries, the drafter-self-rating placeholder). The §5.7 trigger-summary wording references analytical constructs by name (Procrustes distance, max pairwise distance) but does not recompute or interpret them. |
| Claims validity | PASS-WITH-NOTES | The CLI surfaces methodology-loaded fields (`drafter_self_rating`, `framing_checks`, `forbidden_terms_hit`, trigger evidence per `TriggerType`). The §5.1 column-header phrasing and the §5.7 trigger-summary strings are the binding claim-shape constraints. Three load-bearing fixes: (a) "Drafter self-rating" not "Confidence" (T1 §5.4 honored at the display layer); (b) the four canonical `framing_checks` keys surfaced verbatim, not collapsed to a composite PASS/FAIL; (c) the `MONTHLY_ROUNDUP` summary uses the T1 §5.7 §1.5-compliant phrasing, applying the fix at the display layer before the T7 ARCHITECTURE.md amendment lands. |
| Audience translation | PASS-WITH-NOTES | The CLI's audience is exactly one person — Mark — making y/n/e calls under time pressure. The phrasing must be precise (not loose journalist-style framing) AND scan-fast (Mark reads dozens per session). §5.2's per-key `framing_checks` display optimizes for scan speed AND audit precision (operator sees which check failed if a post-edit re-validate fails). §5.5's neutral edit-failure wording optimizes for operator-role preservation (the operator is the reviewer, not the author; the failure is the validator's call, not a shaming message). |

**Register compliance:** **PASS** — the CLI surfaces Register-1 (OCI) and
Register-2 (Romney CCM / max pairwise distance) construct names from the
trigger evidence and the framing-check keys. No Register-1 → Register-2
leakage is introduced at the display layer; the §5.7 `DIVERGENCE`
summary correctly uses Register-2 language ("max pairwise distance");
the §5.7 `DRIFT` summary correctly uses Register-3 language ("Procrustes
distance"). The `register_boundary` framing-check key (per T3 §5.11) is
displayed verbatim — operationally this signals "this check guards
against §1.5.4 rows 7–10 within-model phrasings."

**Vocabulary compliance:** **PASS-WITH-NOTES** — scanned every
LSB-authored string surface in the T5 implementation surface (column
headers, action prompts, trigger summaries, failure-message templates,
the quit-prompt, the edit-failure screen). Full table in §3. The single
§1.5 hazard surfaced and fixed: the §5.7 `MONTHLY_ROUNDUP` summary
applies the T1 §5.7 ARCHITECTURE.md fix at the CLI layer (the CLI must
not reproduce the pre-amendment phrasing even though the
ARCHITECTURE.md fix itself is still pending at T7).

---

## 2. Rationale on the seven methodology questions

### 2.1. Question 1 — Column-header phrasing

The Orchestrator surfaced three sub-questions: header wording for
trigger, validator results, drafter rating.

**Trigger column.** Header: `Trigger`. The body text is the §5.7
per-TriggerType summary string. Header phrasing rejected: "Reason this
should be posted" — it implies an editorial judgment ("should this be
posted") that the CLI is asking the operator to make against the
detector's claim. The operator's call is post-or-not; the detector's
job is "this event happened." Headline label "Trigger" matches the
schema field name (`SocialDraft.trigger`) and is methodology-neutral.

**Validator-results column.** Header: `Framing checks`. The body text
is the §5.2 per-key display (four keys, each with `PASS`/`FAIL`).
Header phrasing rejected: "Validator results" — too generic; "Quality
checks" — implies a quality dimension LSB does not measure (the checks
are §1.5 boundary enforcement, not "quality" in the engagement /
calibration sense). `Framing checks` matches the T1 schema field name
(`framing_checks`) and is methodology-precise.

**Drafter-rating column.** Header: `Drafter self-rating`. Body: the
`drafter_self_rating` float (always `0.5` for v1 per T3 §5.6). Header
phrasing FORBIDDEN: `Confidence`, `Confidence score`, `Quality score`,
`Rating`. The T1 §5.4 rename was specifically to defuse calibration
implication; the CLI display must honor the rename.

**Other column headers** (operational, not methodology-loaded):
`Draft text` (header for the verbatim post body — methodology-neutral);
`Dashboard` (header for the URL — methodology-neutral); `Suggested
posting time` (header for the `suggested_posting_time` datetime —
methodology-neutral per T1 §5.5 docstring).

### 2.2. Question 2 — Validator-results enumeration

The Orchestrator surfaced: enumerate the four canonical keys vs collapse
to single PASS/FAIL.

**Ruling — enumerate.** Three reasons:

1. **Audit precision.** The T3 §5.11 binding-minimum four-key dict
   exists precisely because a single boolean is "necessary but
   insufficient" (T1 §5.3 verdict). The CLI is the primary forensic
   consumer of the `framing_checks` dict; collapsing to a composite
   defeats the rationale.

2. **Post-edit re-validation diagnostic.** When the operator edits a
   draft and the post-edit validator fails, the operator needs to see
   exactly which check failed (per Question 5 / §5.5). Displaying the
   four keys at view-time prepares the operator for what failure mode
   to expect on re-validation.

3. **Audience scan speed is not compromised.** Four lines of
   `<key>: PASS` is fast to read; a green/colorless pass-line vs a
   red-and-bold fail-line is faster than parsing a composite badge.

**Display format:**

```
Framing checks:
  hypothesis_framing       PASS
  cognition_attribution    PASS
  bare_numeric_without_ci  PASS
  register_boundary        PASS

Forbidden terms hit: []
```

The Coder uses verbatim key names from T3 §5.11 (not human-readable
labels like "Hypothesis framing"). Rationale: the keys are the audit
trail; the operator quickly learns the four-key vocabulary; the
operator's grep over `out/social/state/drafter_rejections.jsonl` will
use the same keys. **Coder may add an optional inline tooltip / brief
note** under the framing-checks block (e.g., "(See methodology
docstring on `SocialDraft.framing_checks`.)") but not change the key
names.

`forbidden_terms_hit` is always `[]` for any draft that admitted to
the queue (the T3 validator raised `DrafterRejectedException`
otherwise). Displaying it is a forensic affordance: if the list is
ever non-empty for a queued draft, that signals a drafter-validator
bug, and the CLI must surface it as a `[BUG]` row (Coder uses a
visible-distinct rendering — e.g., bold-red — to flag the
queue-contract violation).

### 2.3. Question 3 — Reject-reason structure

The Orchestrator surfaced: free-text vs closed enumeration.

**Ruling — closed enumeration of five codes + optional free-text
note.** Three reasons:

1. **Auditability.** A closed enum lets the operator (and future post-
   mortem analyses) compute "what fraction of rejections were
   forbidden_vocab vs off_topic." Free-text is not aggregable.

2. **Trend monitoring (T3 §5.8).** The drafter-rejections.jsonl audit
   log records validator-side rejections. The `failed/` queue records
   human-side rejections. If both share enum codes, an analyst can
   distinguish "drafter is leaking" (validator catches before queue)
   from "validator is permissive" (human catches after queue) —
   different fixes.

3. **Operator scan speed.** Closed enum at the prompt is faster than
   typing a free-text reason. The operator hits a single key per code
   (e.g., `1` = forbidden_vocab, `2` = register_boundary, etc.) and
   optionally appends a free-text note.

**The five codes:**

| Code | When to use |
|---|---|
| `forbidden_vocab` | Operator catches §1.5.4 left-column phrasing the drafter validator missed (or a borderline phrase the validator passed but the operator judges as still §1.5.4-loaded). |
| `register_boundary` | Operator catches a Register-1 / Register-2 leak (per §1.5.4 rows 7–10) — e.g., a draft that uses "consensus" without specifying Register-2 context. |
| `bare_numeric` | Operator catches a numeric finding without an adjacent CI that the drafter validator's K=12 window or exemption set let through. |
| `off_topic` | Draft is methodology-clean but doesn't surface a useful finding — e.g., a NEW_MODEL trigger that produces a draft about a model that's not interesting to highlight. |
| `other` | Catch-all; pairs with a free-text note explaining the reason. |

**The optional free-text `rejection_note`** is for the `other` code
and for any code where the operator wants to leave a forensic note
("the gap_delta is real but the model_pair is uninteresting because
both are sub-frontier"). The note is operator-internal and does not
surface on the public dashboard.

**T1-schema impact.** The Coder has two implementation choices:

- **Choice A (preferred):** Add two optional fields to `SocialDraft`
  in `cdb_core/schemas.py`:
  ```python
  rejection_reason: str | None = None  # one of the five codes
  rejection_note: str | None = None    # operator free-text
  ```
  These fields are set only when the draft moves to `failed/`. The
  T1 §13 DATA_DICTIONARY entry updates accordingly.

- **Choice B:** Store the rejection metadata in a sidecar JSON at
  `out/social/queue/failed/{draft_id}.rejection.json` with the two
  fields. Avoids `cdb_core/schemas.py` re-edit.

The CDA SME's preference is Choice A (single artifact per draft;
audit trail is in one place). The Coder coordinates with the
Architect on the schema-edit posture (since T1 schemas are landed
and the kickoff §3 T5 row did not anticipate the fields). Either
choice is methodology-compliant.

### 2.4. Question 4 — Edit-path editor contents

The Orchestrator surfaced: original text vs blank.

**Ruling — original text.** Three reasons:

1. **Methodology preservation.** The T3 cached prompt invested ~1100
   tokens in teaching the LLM to produce §1.5-compliant framing. The
   resulting draft text has the canonical 3-line structure (T3 §5.7)
   with line 2 carrying the corpus-lens framing. An iterative tweak
   preserves that scaffolding; a blank editor invites the operator to
   recompose without it.

2. **Operator-role preservation.** The operator is the reviewer, not
   the author. Asking the operator to write from scratch puts them
   in the drafter role; they must then internalize the §1.5.4 / R10 /
   register-boundary rules themselves. The cached prompt handles
   that for the drafter; asking the operator to handle it manually
   is a workflow regression.

3. **Audit-trail clarity.** When the edit succeeds, `text_history`
   appends the original `text`; when blank-editor diff would be
   misleading (the "edit" is actually a rewrite). With original-text
   start, `text_history` clearly captures "the operator's diff against
   the drafter's output."

**Coder implementation:** the CLI writes `SocialDraft.text` to a
tempfile, invokes `$EDITOR` (with `$VISUAL` fallback, then `vi` as
the last resort), reads the tempfile back on exit. The Coder includes
a brief in-file comment at the top of the tempfile (which `$EDITOR`
displays in the buffer) that reminds the operator of the §1.5.4 /
register-boundary rule — but this comment is **stripped before
re-validation** (per a sentinel marker the Coder defines).

Suggested tempfile preamble (stripped before re-validation):

```
# Editing draft {draft_id} for {platform}.
# §1.5.4 forbidden vocab: no "believes" / "thinks" / "worldview" applied
# to models; no "within-model consensus" or "within-model CCM" phrasings.
# Every numeric finding requires an adjacent CI. Save and quit to validate.
# Lines starting with `#` are stripped before validation.
```

### 2.5. Question 5 — Edit-then-validate failure path

The Orchestrator surfaced: silent-bounce vs surface-the-failure;
methodology-compliant wording for "you wrote forbidden vocabulary."

**Ruling — surface the failure verbatim with neutral operational
language.** The wording avoids operator-shaming framing.

**Display format on edit-failure:**

```
Edit did not pass validator. Draft returned to pending/ with edit history.

Failed checks:
  forbidden_vocab        — matched: "believes"
  hypothesis_framing     — matched: "this proves"
  bare_numeric_without_ci — bare numeric "0.84" without adjacent CI

Edit again? [y/n]
```

**Forbidden wording** at this surface:
- "You wrote forbidden vocabulary" — shaming; conflates operator with
  drafter.
- "Your edit violates LSB methodology" — too heavyweight; the operator
  is testing an edit, not committing a methodology error.
- "Bad edit" — judgmental.

**Approved wording patterns:**
- `Edit did not pass validator.` (neutral; subject is the validator,
  not the operator).
- `Failed checks:` (neutral list).
- `matched: "<phrase>"` (neutral evidence-citation).
- `bare numeric "<value>" without adjacent CI` (neutral; uses R10
  vocabulary the operator has already seen at view-time).

The Coder includes the `Edit again? [y/n]` prompt — `y` reopens the
editor with the failed edit as the buffer (so the operator can fix);
`n` leaves the draft in `pending/` with the unmodified original
`text` plus the failed edit appended to `text_history`.

**Audit trail:** the failed edit is appended to `text_history`. The
`SocialDraft.text` field is NOT overwritten with the failed edit (per
T1 schema's `text_history` docstring lines 735–738). The operator may
revisit later.

### 2.6. Question 6 — Quit-while-displaying

The Orchestrator surfaced: stays in pending vs marked-deferred.

**Ruling — stays in `pending/` unchanged, no special state.**

The most conservative semantics. A `q` press is an operator break,
not a queue-state mutation. The draft is re-shown at the next
review-CLI invocation (the queue lists `pending/` oldest-first).

**No "deferred" state.** Adding one would:
- Bloat the queue-state enum (currently {pending, approved,
  published, failed}).
- Create a hiding place for drafts the operator didn't want to act
  on (the operator should either approve, reject, or come back).
- Add a "draft deferred at YYYY-MM-DD" timestamp the operator must
  later reconcile.

The current 4-state queue is sufficient; `q` is just "exit the loop."

**The CLI prints a confirmation on quit:**

```
Quit. {n} drafts remain in pending/.
```

The `{n}` is the count of remaining unreviewed drafts (informational,
not an enforcement).

### 2.7. Question 7 — Trigger-summary strings per TriggerType

The Orchestrator surfaced: five trigger types, each with structured
evidence; recommend canonical summary strings.

**Ruling — five canonical summaries.** Each is one or two lines,
references the trigger-type by `TriggerType` enum value verbatim, and
uses the canonical Register-{N} construct names where applicable.

**NEW_MODEL:**

```
Trigger: NEW_MODEL
{model_id} added to {domain_slug} domain (first seen in domain).
```

Evidence keys consumed: `model_id` (top-level `SocialTrigger.model_id`),
`domain_slug` (top-level), `evidence.first_seen_in_domain` (per T1
§5.6 docstring lines 692–700).

**NEW_DOMAIN:**

```
Trigger: NEW_DOMAIN
{domain_slug} domain added (n={n_models} models).
```

Evidence keys: `domain_slug`, `evidence.n_models`.

**DIVERGENCE:**

```
Trigger: DIVERGENCE
{domain_slug}: max pairwise distance increased from {old_high:.3f}
to {new_high:.3f} (Δ {gap_delta:+.3f}) between {model_pair[0]} and
{model_pair[1]}.
```

Evidence keys: `domain_slug`, `evidence.model_pair` (list of two
model IDs), `evidence.old_high`, `evidence.new_high`,
`evidence.gap_delta`.

**Wording note: "max pairwise distance" not "pairwise gap."** The
Orchestrator's invocation example uses "pairwise gap"; the canonical
Register-2 phrasing is "max pairwise distance" (matching the T2
`detect_divergence` docstring contract). "Gap" is visually ambiguous
(suggests a discrete categorical separation); "distance" is the
Register-2 statistic name. The Coder uses "max pairwise distance"
verbatim.

**DRIFT:**

```
Trigger: DRIFT
{model_version_returned}: Procrustes distance {procrustes_distance:.3f}
between {date_pair[0]} and {date_pair[1]} (threshold 0.15 placeholder;
drift trigger lockout is engaged per kickoff §7.3 until multi-date
data validates threshold).
```

Evidence keys: `evidence.model_version_returned`,
`evidence.procrustes_distance`, `evidence.date_pair`.

**Wording note: "Procrustes distance" verbatim.** Register-3 statistic
name. The "threshold 0.15 placeholder" caveat is **mandatory** on every
DRIFT display while the kickoff §7.3 lockout is engaged — so the
operator never approves a drift draft without knowing the threshold is
unvalidated. When (if) the lockout is released, the caveat is removed
by a Coder one-line change.

**MONTHLY_ROUNDUP:**

```
Trigger: MONTHLY_ROUNDUP
Monthly cross-domain categorical-structure roundup for {month}.
```

Evidence keys: `evidence.month` (YYYY-MM string).

**Wording note: "monthly cross-domain categorical-structure roundup"
verbatim.** This is the T1 §5.7 binding replacement for the
pre-amendment "state of cultural alignment roundup" phrasing in
ARCHITECTURE.md §4.6 line 1211. The T7 ARCHITECTURE.md fix is still
pending, but the CLI surface must not reproduce the pre-amendment
phrasing at the display layer — applying the §1.5-compliant phrasing
now means the operator never sees the §1.5 hazard, and the T7 fix
becomes a doc-sweep formality rather than a surface-changing edit.

---

## 3. Vocabulary compliance on T5-authored strings

Scanned every LSB-authored string surface implied by the kickoff §3 T5
+ the §5 binding notes:

| String | §1.5.4 reading | Verdict |
|---|---|---|
| Column header `Trigger` | Schema-field identifier | Compliant |
| Column header `Draft text` | Technical descriptor | Compliant |
| Column header `Framing checks` | Schema-field-aligned identifier | Compliant |
| Column header `Dashboard` | Technical descriptor (URL link) | Compliant |
| Column header `Suggested posting time` | Schema-field identifier | Compliant |
| Column header `Drafter self-rating` | Schema-field identifier (T1 §5.4 honored) | Compliant |
| Framing-check key `hypothesis_framing` (displayed verbatim) | §1.5.7-aligned identifier (T3 §5.11) | Compliant |
| Framing-check key `cognition_attribution` (displayed verbatim) | §1.5.4-aligned identifier | Compliant |
| Framing-check key `bare_numeric_without_ci` (displayed verbatim) | R10-aligned identifier | Compliant |
| Framing-check key `register_boundary` (displayed verbatim) | Register-aligned identifier | Compliant |
| Rejection-reason code `forbidden_vocab` | §1.5.4-aligned identifier | Compliant |
| Rejection-reason code `register_boundary` | Register-aligned identifier | Compliant |
| Rejection-reason code `bare_numeric` | R10-aligned identifier | Compliant |
| Rejection-reason code `off_topic` | Operational descriptor | Compliant |
| Rejection-reason code `other` | Catch-all descriptor | Compliant |
| Trigger summary "NEW_MODEL" body wording | Operational descriptor; no §1.5.4 hazard | Compliant |
| Trigger summary "NEW_DOMAIN" body wording | Operational descriptor; no §1.5.4 hazard | Compliant |
| Trigger summary "DIVERGENCE" body using "max pairwise distance" | Register-2 canonical phrasing | Compliant |
| Trigger summary "DRIFT" body using "Procrustes distance" | Register-3 canonical phrasing | Compliant |
| Trigger summary "DRIFT" body's placeholder caveat | Operational disclosure of the §7.3 lockout | Compliant |
| Trigger summary "MONTHLY_ROUNDUP" body using "monthly cross-domain categorical-structure roundup" | T1 §5.7-compliant replacement for the pre-amendment "state of cultural alignment" phrasing | Compliant |
| Action prompt `[y/n/e/s/q]` | Operational descriptor | Compliant |
| Action prompt `Approve? Edit? Reject? Skip? Quit?` (if used as long-form) | Operational descriptor | Compliant |
| Edit-failure header "Edit did not pass validator." | Neutral operational language | Compliant |
| Edit-failure body "Failed checks:" | Neutral operational language | Compliant |
| Edit-failure body `matched: "<phrase>"` | Neutral evidence citation | Compliant |
| Edit-failure body `bare numeric "<value>" without adjacent CI` | R10-aligned diagnostic | Compliant |
| Reject-flow prompt `Rejection reason? [1=forbidden_vocab, 2=register_boundary, 3=bare_numeric, 4=off_topic, 5=other]:` | Operational descriptor | Compliant |
| Reject-flow optional prompt `Optional note:` | Operational descriptor | Compliant |
| Quit confirmation `Quit. {n} drafts remain in pending/.` | Operational descriptor | Compliant |
| Tempfile preamble (per §5.4) `# Editing draft {draft_id} for {platform}. # §1.5.4 forbidden vocab: ...` | Operator-facing reminder; uses §1.5.4 vocabulary as forbidden-set citation, not as forbidden usage | Compliant |
| Bug-surfacing rendering for `forbidden_terms_hit != []` on a queued draft | `[BUG]` annotation is forensic; the underlying matched phrases are quoted, not endorsed | Compliant |

No new §1.5.4 violations introduced. The T1 §5.7 carry-forward
(ARCHITECTURE.md §4.6 line 1211 prose revision pending at T7) is
**partially defused at the display layer** by T5's
`MONTHLY_ROUNDUP` summary using the §1.5-compliant phrasing — but the
doc-level fix is still required at T7.

---

## 4. Cross-references to T1 and T3

The T5 implementation reads the T1 schema (`SocialDraft`,
`SocialTrigger`, `TriggerType`) and the T3 framing-check populating
behavior. No re-edits to either are required by T5 itself, except for
the §5.3 schema-touch (two optional fields on `SocialDraft` for
`rejection_reason` + `rejection_note`) which the Coder may instead
implement as a sidecar JSON.

**Cross-reference table:**

| T5 surface | Reads from | Defined at |
|---|---|---|
| Column header `Drafter self-rating` | `SocialDraft.drafter_self_rating` | T1 §5.4 (rename) + T3 §5.6 (fixed 0.5) |
| Per-key `framing_checks` display | `SocialDraft.framing_checks` (dict) | T1 §5.3 (sibling field) + T3 §5.11 (four canonical keys) |
| `forbidden_terms_hit: []` display | `SocialDraft.forbidden_terms_hit` | T1 §5.2 (queue-acceptance precondition) |
| Trigger summary per TriggerType | `SocialTrigger.evidence` (per-trigger keys) | T1 §5.6 (docstring contract) + T2 (evidence-shape implementation) |
| `MONTHLY_ROUNDUP` summary text | T1 §5.7 binding-replacement phrasing | T1 §5.7 (T7 doc-amendment carry-forward) |
| Edit-failure verbatim matched phrases | T3 `validate_draft()` return values | T3 §5.1/§5.2/§5.3 (three sub-validators) |
| Rejection-reason enum (§5.3 of this verdict) | New T5-introduced enum | This verdict §5.3 + optional T1 schema-touch |

---

## 5. Binding carry-forward notes (apply at Coder dispatch)

These notes are binding on the Coder during T5 implementation. The
Reviewer enforces.

### 5.1. **Column headers: six canonical strings.** [Audience translation, Claims validity]

The CLI displays each `pending/` draft with the following six columns
(or row-labels — the Coder picks the layout, but the header strings are
binding):

- `Trigger` — body is the §5.7 per-TriggerType summary.
- `Draft text` — body is `SocialDraft.text` verbatim.
- `Framing checks` — body is the §5.2 per-key block.
- `Dashboard` — body is `SocialDraft.dashboard_url`.
- `Suggested posting time` — body is `SocialDraft.suggested_posting_time`
  rendered as ISO-8601 or human-readable (Coder picks).
- `Drafter self-rating` — body is `SocialDraft.drafter_self_rating`
  as a float to two decimal places (e.g., `0.50`).

**Forbidden headers:** `Confidence`, `Confidence score`, `Quality score`,
`Rating`, `Reason this should be posted`, `Validator results` (the last
is too generic — use `Framing checks`).

### 5.2. **Validator-results enumeration: four canonical keys verbatim + forbidden_terms_hit summary.** [Claims validity, Audience translation]

Under the `Framing checks` column header, the Coder renders each of the
four T3 §5.11 binding-minimum keys verbatim with a `PASS` / `FAIL`
value:

```
Framing checks:
  hypothesis_framing       PASS
  cognition_attribution    PASS
  bare_numeric_without_ci  PASS
  register_boundary        PASS

Forbidden terms hit: []
```

If `framing_checks` contains additional keys beyond the four, the Coder
renders them after the canonical four (sorted alphabetically). The
display does NOT collapse to a single composite PASS/FAIL.

`forbidden_terms_hit` is rendered verbatim. For any queued draft, this
list is `[]` (per the T1 schema queue-acceptance contract). If the list
is non-empty, the Coder renders a `[BUG]` marker prominently — e.g.:

```
[BUG] Forbidden terms hit: ['believes']
  This draft should not have reached the queue. File an issue.
```

The Coder uses a visible-distinct rendering (bold-red ANSI, or
equivalent) to flag the queue-contract violation.

### 5.3. **Rejection-reason structure: five closed codes + optional free-text note.** [Claims validity]

When the operator presses `n` to reject, the CLI prompts:

```
Rejection reason? [1=forbidden_vocab, 2=register_boundary,
  3=bare_numeric, 4=off_topic, 5=other]: <input>
Optional note: <input>
```

The five codes are binding (no operator-introduced codes; the closed
enumeration is the audit contract). The optional note is free-text.

**Implementation choice for persistence** (Coder picks one;
coordinate with Architect on schema-touch posture):

- **Choice A (preferred):** Add two optional fields to `SocialDraft` in
  `cdb_core/schemas.py`:
  ```python
  rejection_reason: Literal["forbidden_vocab", "register_boundary",
      "bare_numeric", "off_topic", "other"] | None = None
  rejection_note: str | None = None
  ```
  Update `docs/DATA_DICTIONARY.md` §13 in the same PR (Reviewer R7).

- **Choice B:** Sidecar JSON at
  `out/social/queue/failed/{draft_id}.rejection.json` with the two
  fields. Avoids re-edit of T1-landed schemas.

The CDA SME's preference is Choice A; the Coder coordinates with the
Architect on the schema-edit posture.

### 5.4. **Edit-path editor: original draft text as buffer; tempfile preamble; preamble stripped before re-validation.** [Audience translation, Claims validity]

The Coder implements the `e` action as:

1. Write `SocialDraft.text` to a tempfile, prepended by a comment-style
   preamble (sentinel-marked for stripping):

```
# Editing draft {draft_id} for {platform}.
# §1.5.4 forbidden vocab: no "believes" / "thinks" / "worldview" applied
# to models; no "within-model consensus" or "within-model CCM" phrasings.
# Every numeric finding requires an adjacent CI. Save and quit to validate.
# Lines starting with `#` are stripped before validation.
```

2. Invoke `$EDITOR` (with `$VISUAL` fallback, then `vi` as last resort).
3. On exit, read tempfile; strip all lines starting with `#`.
4. Run the T3 `validate_draft()` on the stripped text.
5. On pass: move draft to `approved/` with updated `text` and
   `text_history` appended with the original.
6. On fail: leave draft in `pending/` with `text` unchanged, append
   failed-edit to `text_history`, display the §5.5 failure screen.

### 5.5. **Edit-then-validate failure: surface validator failures verbatim with neutral wording.** [Audience translation]

On post-edit validation failure, the CLI displays:

```
Edit did not pass validator. Draft returned to pending/ with edit history.

Failed checks:
  <check_name_1>  — <evidence_1>
  <check_name_2>  — <evidence_2>
  ...

Edit again? [y/n]
```

**Failure-evidence wording templates:**

- For forbidden-vocab matches:
  `<check_name>  — matched: "<phrase>"`

- For bare-numeric failures:
  `bare_numeric_without_ci  — bare numeric "<value>" without adjacent CI`

- For hypothesis-framing matches:
  `hypothesis_framing  — matched: "<phrase>"`

- For register-boundary matches:
  `register_boundary  — matched: "<phrase>"`

**Forbidden wording at this surface:**
- "You wrote forbidden vocabulary"
- "Your edit violates LSB methodology"
- "Bad edit"
- "Try again"

**Approved wording posture:** subject is the validator; subject is NOT
the operator. Pattern: `Edit did not pass validator.` / `Failed
checks:` / `matched: "<phrase>"`.

`Edit again? [y/n]` — `y` reopens the editor with the failed edit as
buffer; `n` returns the operator to the main review loop (the draft
stays in `pending/` with the failed edit appended to `text_history`).

### 5.6. **Quit-while-displaying: draft stays in pending/ unchanged.** [Claims validity, Audience translation]

The `q` action exits the review loop. The currently-displayed draft
stays in `pending/` unchanged (no state mutation, no "deferred" marker,
no special timestamp).

CLI prints on exit:

```
Quit. {n} drafts remain in pending/.
```

`{n}` is the count of remaining unreviewed drafts (informational).

### 5.7. **Trigger-summary strings: five canonical per-TriggerType patterns.** [Claims validity, Register compliance, Vocabulary compliance]

The Coder implements `format_trigger_summary(trigger: SocialTrigger) ->
str` returning the per-TriggerType canonical pattern:

**`NEW_MODEL`:**

```
Trigger: NEW_MODEL
{model_id} added to {domain_slug} domain (first seen in domain).
```

**`NEW_DOMAIN`:**

```
Trigger: NEW_DOMAIN
{domain_slug} domain added (n={n_models} models).
```

**`DIVERGENCE`:**

```
Trigger: DIVERGENCE
{domain_slug}: max pairwise distance increased from {old_high:.3f}
to {new_high:.3f} (Δ {gap_delta:+.3f}) between {model_pair[0]} and
{model_pair[1]}.
```

**`DRIFT`:**

```
Trigger: DRIFT
{model_version_returned}: Procrustes distance {procrustes_distance:.3f}
between {date_pair[0]} and {date_pair[1]} (threshold 0.15 placeholder;
drift trigger lockout is engaged per kickoff §7.3 until multi-date
data validates threshold).
```

**`MONTHLY_ROUNDUP`:**

```
Trigger: MONTHLY_ROUNDUP
Monthly cross-domain categorical-structure roundup for {month}.
```

**Binding vocabulary** (Reviewer enforces):

- `DIVERGENCE`: `max pairwise distance` (NOT "pairwise gap").
- `DRIFT`: `Procrustes distance` (verbatim).
- `MONTHLY_ROUNDUP`: `monthly cross-domain categorical-structure
  roundup` (verbatim — T1 §5.7-compliant phrasing).

The Coder reads the per-trigger evidence keys per T1 §5.6 docstring
(schemas.py lines 692–700). If a trigger's evidence dict is missing
expected keys (T2 implementation error), the Coder renders a
`{key}=??` placeholder and surfaces a `[WARN]` annotation; this is a
diagnostic affordance, not a methodology hazard.

### 5.8. **Sort order in pending/.** [Operational, advisory]

The CLI lists `pending/` drafts oldest-first by `SocialDraft.created_at`
(per the kickoff §3 T5 acceptance sketch). The Coder may optionally
allow `--sort=self-rating` as a flag for drafter-self-rating-descending
order; this is an operator convenience and is non-binding for
methodology.

### 5.9. **Bug-flag rendering for queue-contract violations.** [Claims validity, advisory]

If a queued `SocialDraft` has any of:
- `forbidden_terms_hit != []`
- `framing_check_passed != True`
- `any value in framing_checks is False`

then the CLI renders a `[BUG]` marker prominently on that draft and
appends a single-line note:

```
[BUG] Queue-contract violation: this draft should not have reached
  pending/. Likely cause: drafter validator bypass. Do not approve;
  reject with reason `other` and document the bypass.
```

The operator is instructed to reject the draft (not approve under
exceptional circumstances) and document the bypass for the v2-prompt-
bump decision (T3 §5.8).

### 5.10. **No real API calls in tests; monkeypatched stdin/stdout.** [Architectural, per CLAUDE.md §6 rule 9]

The Tester's CLI tests use `monkeypatch` on stdin/stdout per the
kickoff §3 T5 test plan. The CLI must NOT invoke any platform API in
any test path (publishing is T6 territory). The Coder ensures
`scripts/social_review.py` only reads/writes the `out/social/queue/`
filesystem state and the `$EDITOR` tempfile; no network calls.

### 5.11. **T1 §5.7 carry-forward defused at display layer; doc-level fix still required at T7.** [Vocabulary compliance, cross-reference]

The §5.7 `MONTHLY_ROUNDUP` summary in this verdict uses the
T1 §5.7-compliant phrasing ("monthly cross-domain categorical-structure
roundup"). This means the CLI surface does not reproduce the
pre-amendment ARCHITECTURE.md §4.6 line 1211 phrasing ("state of
cultural alignment roundup") at the operator's display layer.

**The T7 ARCHITECTURE.md amendment is still required.** T5 does not
discharge T7's doc-level fix; T5 only ensures the CLI does not
propagate the §1.5 hazard at runtime.

---

## 6. Mark-escalation note

**No Mark escalation is required for T5 Coder dispatch.**

Two items Mark should be aware of:

1. **§5.3 schema-touch choice (Choice A vs Choice B).** If the Coder
   picks Choice A (adding two optional fields to `SocialDraft`), the
   PR carries a `cdb_core/schemas.py` edit and a `docs/DATA_DICTIONARY.md`
   §13 update in the same PR. CLAUDE.md §6 rule 6 (Architect sign-off
   for schema changes) applies — the Architect should ratify before
   the Coder lands the change. If the Coder picks Choice B (sidecar
   JSON), no schema edit is required and the Architect ratification
   is not needed.

2. **§5.7 `DRIFT` summary placeholder caveat.** The Coder hard-codes
   the "threshold 0.15 placeholder; drift trigger lockout is engaged
   per kickoff §7.3" caveat. When (if) the lockout is released after
   multi-date data validates the threshold (kickoff §7.3, §8 risk 5),
   the caveat is removed by a one-line Coder edit and a follow-up
   CDA SME review (small scope).

---

## 7. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply at T5 (11 binding notes):**
  - §5.1 (six canonical column headers; "Drafter self-rating" not
    "Confidence")
  - §5.2 (four canonical `framing_checks` keys displayed verbatim +
    `forbidden_terms_hit: []` summary)
  - §5.3 (five closed rejection-reason codes + optional free-text;
    Coder picks Choice A or B for persistence)
  - §5.4 (editor opens with original draft text; tempfile preamble
    stripped before re-validation)
  - §5.5 (edit-failure screen with neutral validator-as-subject
    wording; no operator-shaming language)
  - §5.6 (`q` leaves draft in `pending/` unchanged; no "deferred"
    state)
  - §5.7 (five canonical per-TriggerType summary patterns; binding
    wording: "max pairwise distance," "Procrustes distance,"
    "monthly cross-domain categorical-structure roundup")
  - §5.8 (sort oldest-first by `created_at`; optional self-rating
    sort flag)
  - §5.9 (`[BUG]` rendering on queue-contract violations)
  - §5.10 (no real API calls in tests; monkeypatched stdin/stdout)
  - §5.11 (T1 §5.7 doc-amendment still required at T7; T5 defuses at
    display layer only)
- **`cdb_core/schemas.py` change required:** **Conditional** — only if
  Coder picks §5.3 Choice A (two optional fields on `SocialDraft`).
  Choice B avoids the schema edit.
- **`docs/DATA_DICTIONARY.md` §13 update required:** **Conditional** —
  only if Choice A is picked (Reviewer R7 enforces the same-PR rule).
- **Architect ratification required:** **Conditional** — only if Choice
  A is picked (CLAUDE.md §6 rule 6).
- **T7 doc-sweep carry-forward:** the T1 §5.7 ARCHITECTURE.md §4.6
  line 1211 prose revision remains binding on T7.
- **Mark escalation:** §6 advisory only, non-blocking for T5 Coder
  dispatch.

---

*End of Phase 7 T5 CDA SME verdict.*
