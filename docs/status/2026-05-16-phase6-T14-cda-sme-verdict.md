---
filed: 2026-05-16
reviewer: CDA SME agent (Opus)
task: Phase 6 T14 — Documentation sweep
plan_reviewed: docs/status/2026-05-16-phase6-T14-architect-plan.md
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# CDA SME verdict — Phase 6 T14 (documentation sweep)

## VERDICT: PASS-WITH-NOTES

T14 is a docs-only reconciliation sweep across four canonical
doctrine files (`ARCHITECTURE.md`, `DESIGN_SYSTEM.md`,
`docs/DATA_DICTIONARY.md`, `CLAUDE.md`). The plan correctly scopes the
work as a verification-and-codification pass, not a methodology
rewrite. The five methodology-adjacent ACs (AC3, AC4, AC9, AC13, AC16)
are scoped tightly enough that no new methodology surface is being
created — the binding-text references already exist downstream
(T9 verdict §5.1 `framing_note`; T10 verdict UI rendering contract;
DATA_DICTIONARY.md §12 v0.1.14 row at line 1086). T14 is reconciling
them upward into the doctrine files, not authoring fresh framing.

The plan's escalation discipline is correct on every methodology-touch
point: AC4, AC9, and the §4.5 verification in AC2 all carry an
explicit STOP-and-route-to-CDA-SME clause on mismatch detection. That
is the right posture — the Coder must not self-correct §1.5 contradictions or
DATA_DICTIONARY.md §12 mismatches without methodology review. The AC3
new-subsection language is methodologically sound; the AC13 phantom-
token pitfall stays in technical/CSS territory with zero
anthropomorphism drift. The plan's prose contains no §1.5.4 forbidden
vocabulary (one false-positive in the AC16-grep set at plan line 331
"the Coder believes a token... is missing" is general-purpose English
applied to an agent role, not model-facing — CLAUDE.md §7 exempts this
explicitly).

Six binding notes follow under §5, each downstream-tracked. None
blocks Coder dispatch.

---

## Four-axis scorecard

| Axis | Verdict | One-sentence rationale |
|---|---|---|
| 1. Protocol validity | PASS | T14 documents what shipped; AC1 explicitly preserves T1/T2 methodology page and T3/T4 DriftTracker as pending, so no CDA elicitation protocol surface is being modified or claimed. |
| 2. Analytical validity | PASS | The §4.5 R10 uncertainty binding is verified, not edited (AC2 STOP-on-conflict); AC11 correctly bars drift-field additions on the doctrinal ground that the 0.2 corpus has at most one collection date per `model_version_returned`. |
| 3. Claims validity | PASS-WITH-NOTES | The AC3 failures-display subsection touches the publish-layer redaction boundary and references the T9-emitted `framing_note` — the binding text per T9 verdict §5.1 must be referenced, not re-authored, and the AC3 ≤25-line cap is the right ceiling to prevent re-authoring; see §5 notes 1–3. |
| 4. Audience translation | PASS-WITH-NOTES | The AC13 pitfall body stays in CSS/token-discipline register; AC4's §1.5 spot-check posture (stop-on-contradiction, no self-correction) is the right gate for shipped Phase 6 copy; see §5 note 4. |

Register compliance: **PASS** — T14 surfaces no Register 1/2/3
analytical changes; it documents the existing publish-layer artifacts
(failures, decline interviews) which are atomic elicitation-result
records, not consensus or concentration statistics. No OCI, Romney
CCM, or Procrustes interpretation is added or modified.

Vocabulary compliance: **PASS** — scanned the full plan prose. The
single token-match at plan line 331 ("If the Coder believes a token
or component is missing") refers to a human/agent role, not a model;
CLAUDE.md §7 paragraph beginning "The forbidden vocabulary applies
to text *about* the models that LSB measures..." exempts this
general-purpose English usage. No other forbidden-vocabulary
candidates appear in the plan.

---

## 1. AC3 subsection scope review (failures-display in ARCHITECTURE.md)

The AC3 specification is methodologically sound. The proposed
subsection (≤25 lines, added at §4.4.x or §4.5.x) MUST:

- Cross-reference DATA_DICTIONARY.md §12 for field tables (do NOT
  duplicate the tables). **Concur** — DATA_DICTIONARY.md §12 is the
  canonical reference; duplication would create rot risk.
- State the publish-layer redaction boundary verbatim:
  `cdb_publish.sanitize.sanitize_for_publication()` runs before
  any string is written to `apps/dashboard/public/data/failures/{domain}.json`.
  **Concur** — this is the boundary established in T9 verdict §2.1
  and the SECURITY_AND_HARDENING.md §3.3 cross-reference is correct.
- State that `framing_note` carries CDA-SME-reviewed §1.5.4
  framing text and that the dashboard renders it adjacent to the
  records per T9/T10 verdicts. **Concur** — this is the cross-link
  from publish-layer JSON to UI rendering contract.
- State the append-only invariant on `data/raw/*.jsonl`. **Concur**
  — this is the open-data-bundle reproducibility guarantee
  (ARCHITECTURE.md §1 commitment 9 / pitfall #10).
- Cite SECURITY_AND_HARDENING.md §3.3 for sanitization rationale.
  **Concur** — the rationale doc is the right home for the
  sanitization spec; ARCHITECTURE.md only needs the pointer.
- MUST NOT include field descriptions, sanitization regexes, or the
  `framing_note` verbatim text. **Concur, and binding** — the
  `framing_note` text is governed by T9 verdict §5.1 byte-identity.
  Re-typing it in ARCHITECTURE.md creates two copies that can drift.
  See §5 note 1 below.

**Redaction-boundary language judgment:** the AC3 wording "publish-layer
redaction boundary" is correct. The boundary is descriptive-technical
(string-pattern replacement with visible markers), not psychological-
attribution language. The AC3 spec correctly names sanitization
as defense-in-depth rather than content policy, which preserves the
T9 §1.5 stance (verbatim publication IS the §1.5 stance, with
sanitization scoped narrowly to secrets/paths).

**Conditional-edit posture is correct.** If ARCHITECTURE.md already
carries a section that meets these conditions, the AC9 disposition
is "verify and note no change required" — that is the right
verification gate. I confirmed via grep that no
failures-display subsection currently exists (only two passing
references to `failures.jsonl` at lines 751 and 1004), so the
Coder will land a new subsection. Recommended location: a new
§4.4.x near the existing publish-layer documentation in §4.4, or
a new §4.5.x adjacent to the R10 uncertainty binding. The Coder
selects the natural insertion point; either placement is
methodologically defensible.

## 2. AC4 verification posture review (§1.5 spot-check)

**The AC4 stop-on-contradiction posture is correct.** The Coder must
NOT self-correct any §1.5 contradiction found during the spot-check.
Three shipped surfaces are in scope:

- FreeListCompare empty-state copy (T7)
- FailuresFindingsSection framing (T10)
- Food-domain lede (T13)

All three have been through CDA SME content review (T7 R10 verdict;
T10 verdict; T13 AC10 verbatim review). The spot-check is therefore
expected to PASS without notes. If the Coder finds a contradiction,
it is either (a) a new copy surface that did not pass through CDA
SME review — which is itself a process violation — or (b) a regression
in a previously-cleared surface. Either case warrants STOP +
CDA SME re-routing rather than self-correction.

**Spot-check vs. before/after diff judgment:** spot-check is the
correct gate for T14. A before/after diff would imply that T14 is
expected to produce framing edits, which it is not. AC4's "no edit
expected; record verification in commit body" is the right
disposition.

## 3. AC9 verification posture review (DATA_DICTIONARY.md §12)

**The AC9 stop-on-mismatch posture is correct.** I confirmed by
direct read that DATA_DICTIONARY.md §12 line 1086 carries the
`framing_note` description:

> "LSB-authored corpus-lens framing note. Verbatim text from
> `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` §5.1. T10
> is contracted to render this field adjacent to the records.
> See §12.5 below."

This is consistent with T9 verdict §5.1. AC9's verification gate
("no edit expected; record verification in commit body") is correct.
If the Coder finds a mismatch (e.g., a field name in §12 that does
not match `packages/cdb_publish/cdb_publish/schemas/failures.py`),
that is a doc-vs-code drift that the Coder must NOT silently fix
under T14 — drift-fix is a separate task and requires methodology
review of any wording change to the `framing_note` description.

## 4. AC13 phantom-token pitfall body language review

**The proposed pitfall body language stays cleanly in technical/CSS
territory.** Reading the AC13 specification line by line:

- Title: "Referencing a CSS custom property that does not exist in
  `tokens.css`." — Descriptive-technical. No model attribution.
- Body summary: bug class names (`var(--token-name)` for an
  undefined or renamed token), browser silently treats as `unset`,
  no compile-time check, visual breakage without test failure —
  all CSS/browser-behavior language. No hypothesis-testing framing.
- Originating-incident reference: T8 Reviewer FAIL
  (`docs/status/2026-05-12-phase6-T8-reviewer-verdict.md` + post-fix
  addendum). Reference is a verdict file, not a methodology claim.
- Fix pattern: "grep tokens.css before adding a `var(--...)`
  reference; if the token does not exist, route to UI/UX agent
  for a design-system update." — Operational, no methodology
  surface.

**Risk vector check:** the §6 risk #4 in the plan explicitly anticipates
the failure mode (a Coder accidentally introducing a phantom token
name *while describing the bug*). Mitigation is that the pitfall
body names the *pattern*, not specific tokens, and points to the T8
verdict file for specific token-name examples. This is the right
mitigation — concur.

**No anthropomorphism or hypothesis-testing framing is introduced.**
The pitfall is structurally parallel to pitfalls #8 (point estimates
without uncertainty), #9 (real API calls in tests), #10 (editing
append-only files), #11 (webhook URLs in repo) — all operational/
technical pitfalls about codebase discipline, not methodology
claims. AC13 fits the §9 conventions cleanly.

## 5. AC16 forbidden-vocabulary gate position review

**The gate position is correct.** The Coder runs the grep
post-edit, before commit. The grep covers the §1.5.4 forbidden
phrases (`worldview`, `believes`, `thinks of`, `cultural bias`,
`what the model understands`, `how models see`, `model.*believes`,
`model.*thinks of`).

**One refinement to the grep itself, advisory:** the current pattern
list omits `thinks` (bare, without "of") which appears in the §1.5.4
table as a forbidden generic ("`thinks` when applied to models").
The bare token is too broad to grep mechanically without high
false-positive rate (every "I think this loop terminates" code
comment would trip), so the AC16 grep correctly anchors on
`thinks of` which is the specific anthropomorphism phrase. This is
the right tradeoff for a mechanical scan. Spot-check by the Reviewer
covers the bare `thinks`-applied-to-models case.

**Exclusion clause is correct:** the AC16 spec correctly notes that
the existing §7/§1.5.4 tables themselves enumerate the forbidden
terms in order to forbid them — those tables are not violations of
the rule they articulate. Concur.

## 6. AC11 non-action discipline review (drift fields)

**The doctrinal reasoning is correctly stated.** AC11 explicitly
bars adding any drift-related fields, file shape, or section to
DATA_DICTIONARY.md. The plan §4 out-of-scope item #2 reinforces this.

The methodological basis: ARCHITECTURE.md §4.5 lines 1118–1125 spec
DriftTracker as requiring `model_version_returned × collection_date`
as the unit of analysis, with Procrustes distance across consecutive
collection dates as the change metric. The 0.2 corpus has at most
one collection date per `model_version_returned` (the project has
not yet re-collected on a previously-collected model version),
which means a Procrustes drift score cannot be computed —
distance-to-self is trivially zero, and there are no two consecutive
collection dates to compare. Publishing a drift JSON shape now
would either (a) require a single-date placeholder that violates
R10 (uncertainty cannot be expressed on a single observation) or
(b) require a synthetic second observation, which is fabrication.

Both outcomes are methodologically incoherent. **AC11's non-action
is correct.** The Coder records "drift not added; T3/T4 deferred"
in the commit body per the plan; this preserves the audit trail
for when the next collection campaign produces multi-date
observations and T3/T4 can ship.

The plan §4 out-of-scope item #2 ("Drift documentation") and the
§6 risk #3 ("Premature drift-doc additions") provide the same
guardrail at the prose level. Concur on all three.

## 7. Out-of-scope discipline review

The plan §4 enumerates eight out-of-scope categories. From the CDA
SME viewpoint, the methodology-adjacent ones are:

1. **Methodology page prose** (§4 item 1) — correctly out of scope.
   T1/T2 remain blocked on Mark's routing decision and Mark-authored
   content. T14 may note pending status; T14 must NOT generate
   `/methodology` prose. Concur with the plan §6 risk #1 mitigation
   (explicit AC1 sub-bullet pinning methodology page as pending).
2. **Drift documentation** (§4 item 2) — already reviewed under §6
   above; concur.
3. **New components, new tokens, new visual decisions** (§4 item 3)
   — correctly out of scope. The phantom-token pitfall body
   (§4 of this verdict) must not introduce a new token reference
   while describing the bug class.
4. **Schema changes** (§4 item 5) — correctly out of scope.
   `cdb_core/schemas.py` is not touched; pitfall #5 (DATA_DICTIONARY
   .md co-update required for schema changes) is mechanically
   satisfied by non-touch.

These scope boundaries are clear enough that the Coder cannot drift
across them without explicit AC violation. **Concur.**

---

## 5. Binding carry-forward notes (apply at Coder dispatch)

These are binding on the Coder during T14 implementation. The
Reviewer enforces. They do not require re-planning by the Architect.

### 5.1. **AC3 subsection must not duplicate the `framing_note` verbatim text.** [Claims validity]

The AC3 subsection in ARCHITECTURE.md MUST reference the
`framing_note` field by name and cross-reference DATA_DICTIONARY.md
§12 (which carries the field description, currently at line 1086)
and the T9 CDA SME verdict (§5.1) as the source-of-truth for the
verbatim text. The AC3 subsection MUST NOT re-type the full
`framing_note` string in ARCHITECTURE.md, because:

1. Two copies of the verbatim text create drift risk — if the
   methodology page eventually expands the framing language,
   the verdict file + DATA_DICTIONARY.md will be the canonical
   sources of update, and an ARCHITECTURE.md copy will lag.
2. The verdict file is the methodology-review trail. Surfacing
   the verbatim text in ARCHITECTURE.md without the surrounding
   review context (the T9 verdict's §5.1 rationale paragraph)
   risks the reader treating it as an architectural decision
   rather than a methodology-reviewed framing artifact.

**Binding wording for the AC3 subsection's framing_note reference:**
the subsection may say (paraphrase, not verbatim):

> "Each published failures JSON carries an LSB-authored
> `framing_note` top-level field whose verbatim text is governed
> by `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` §5.1
> and documented in `docs/DATA_DICTIONARY.md` §12. The dashboard
> renders this field adjacent to the records per the T9/T10
> rendering contract."

The Coder may paraphrase but must preserve the byte-identity
chain (verdict file → DATA_DICTIONARY.md → JSON output → UI).

### 5.2. **AC3 redaction-boundary language must not characterize model intent.** [Audience translation]

The AC3 spec correctly names sanitization as "publish-layer
redaction boundary" (descriptive-technical). The Coder MUST NOT,
when writing the subsection prose, drift into language that
characterizes what the model "intended" by emitting a string
that matched a redaction pattern. This is the same constraint
the T9 verdict §5.3 placed on `sanitize.py`'s docstring; T14's
AC3 subsection inherits that constraint.

**Concretely forbidden phrasings in the AC3 subsection:**

- "Strings the model thought were... [paths/keys/etc.]" — attributes
  intent.
- "When the model believes it should reveal a credential..." — same.
- "Sanitization removes content the model would expose..." — same.

**Correct phrasings:**

- "Sanitization replaces strings matching defensive regex patterns
  with visible markers before publication."
- "The redaction-marker strings (`[redacted: secret pattern]`,
  `[redacted: local path]`) preserve the signal that a match occurred."

### 5.3. **AC3 cross-references must use canonical section forms.** [Bibliography/cross-reference integrity]

When the Coder cross-references DATA_DICTIONARY.md §12 from the new
AC3 subsection, the form MUST be `docs/DATA_DICTIONARY.md §12`
(matching plan AC15). Similarly for `SECURITY_AND_HARDENING.md §3.3`
(plan AC3 sub-bullet). AC15 catches dangling references at
implementation time; this note pre-emptively names the canonical
forms so the Coder does not improvise abbreviations.

### 5.4. **AC4 verification log must enumerate the three surfaces by name.** [Claims validity, Audience translation]

When the Coder records the AC4 verification result in the commit
body, the log MUST enumerate the three surfaces by name:

- FreeListCompare empty-state copy (T7) — verified §1.5 compliant
- FailuresFindingsSection framing (T10) — verified §1.5 compliant
- Food-domain lede (T13) — verified §1.5 compliant

This is binding because a generic "AC4 verified, no contradictions
found" log entry would not be auditable. A future reader cannot
confirm that the spot-check actually touched all three surfaces
without the enumeration.

### 5.5. **AC13 pitfall body must not name specific phantom tokens.** [Claims validity]

The §6 risk #4 mitigation in the plan is binding. The new §9
pitfall body MUST describe the *pattern* (referencing a CSS custom
property that does not exist) and reference the T8 Reviewer FAIL
verdict for specific examples. The body MUST NOT enumerate
`--font-family-mono`, `--color-bg-surface`, or `--color-text-secondary`
verbatim in the pitfall prose — that creates a residual risk of
the reader treating these as canonical token names rather than
the originating-incident artifacts they are.

### 5.6. **Out-of-scope drift documentation MUST be a non-action with a single-sentence commit-body annotation.** [Analytical validity]

AC11's "drift not added; T3/T4 deferred" record in the commit
body MUST include the doctrinal reasoning in one short sentence:
"the 0.2 corpus has at most one collection date per
`model_version_returned`, so a Procrustes drift score cannot be
computed without a second observation, which does not yet exist."
This preserves the methodology audit trail and pre-emptively
answers a future reviewer asking "why was drift documentation
deferred at T14 if `data/drift/` was planned for Phase 6?"

---

## 6. Notes for downstream agents

### UI/UX agent

The UI/UX gate for T14 is DESIGN_SYSTEM.md fidelity + accessibility
floor + R10 verification — no new visual decisions. From the CDA
SME viewpoint, the relevant UI/UX checks are:

- AC5 component-inventory extension names real file paths; no
  invented names.
- AC6 version bump to v0.4.10 captures the T14 sweep without
  re-bumping per AC.
- AC7 token-block audit lists no new tokens; the §1.2 block is
  verified-complete only.

No CDA SME concerns at the UI/UX gate.

### Reviewer

Enforces the six §5 binding notes above plus the plan's stated
gates (forbidden-vocabulary scan AC16, diff-stat scope AC17,
cross-reference integrity AC15). The Reviewer's nine-check table
records R7/R10/R13 as N/A explicitly per the plan §5 Reviewer block.

### Tester

For a docs-only task, the Tester verifies:

- `uv run pytest && uv run ruff check . && uv run mypy packages/`
  green (no regression).
- `cd apps/dashboard && npm run lint && npm run test && npm run build`
  green (same).
- `git diff --stat master` matches AC17 (nine files exactly).
- AC16 forbidden-vocabulary grep returns empty (excluding the
  §7/§1.5.4 tables themselves).
- Cross-reference grep (AC15) confirms every `§<number>`
  reference added resolves to a real section header in the
  target doc.

---

## 7. Carry-forward to Phase 6.5 / methodology page (downstream-tracked)

The following are not blockers for T14 but should land before the
methodology page closes:

- The methodology page should reference the failures-as-findings
  framing (the `framing_note` source-of-truth text from T9 §5.1)
  so that an open-data-bundle reader who lands on `/methodology`
  sees the corpus-lens framing for failure records. (T1/T2 concern.)
- The methodology page should name the four-link corpus lens
  (corpus → training → alignment → decoding → output distribution)
  and explicitly note that failures are observations of the output-
  distribution link, not claims about model intent. (T2 concern.)
- The drift documentation (DATA_DICTIONARY.md `data/drift/` shape,
  DriftTracker spec in DESIGN_SYSTEM.md §12) lands when the next
  collection campaign produces multi-date `model_version_returned`
  observations. (T3/T4 concern.)

These are advisory to the Architect on Phase 6.5/T1/T2/T3/T4; they
do not gate T14.

---

## 8. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply:** §5.1 (AC3 must reference, not re-type, framing_note), §5.2 (AC3 redaction-boundary language stays technical), §5.3 (canonical cross-reference forms), §5.4 (AC4 verification log enumerates three surfaces), §5.5 (AC13 pitfall body names pattern not specific tokens), §5.6 (AC11 non-action carries doctrinal-reasoning annotation in commit body)
- **Architect must update:** No re-plan required.
- **`cdb_core/schemas.py` change required:** No.
- **T1/T2 methodology-page carry-forwards raised:** Yes — failures-as-findings methodology section + corpus-lens chain naming (advisory, downstream-tracked).
- **Mark escalation:** None.

T14 proceeds to Coder dispatch once the UI/UX gate also clears.

---

*End of Phase 6 T14 CDA SME verdict.*
