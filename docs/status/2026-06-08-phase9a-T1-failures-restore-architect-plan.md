# Phase 9a T1 — Restore the failures-as-findings surface — Architect plan (2026-06-08)

**Task:** Phase 9a T1 (kickoff §6.5 recommended first move). Restore the failures-as-findings
surface dropped by the 2026-05-25 frontend rebuild (commit `5df1f32`).
**Gate path:** Architect → **CDA SME** (framing + classification-display) → **UI/UX** (surface, a11y)
→ Coder → Reviewer → Tester.

## 1. Confirmed regression
`grep -ri failure apps/dashboard/src/` = zero; `failures/*.json` fetched nowhere; data orphaned
(family 36 records, holidays some, food 0). Violates the binding "failures are findings" directive
(ARCHITECTURE §1.5.6, CLAUDE §9 pitfall #4). Data + the CDA-SME-approved `framing_note` already
exist; only the component is missing.

## 2. ADAPT, not verbatim-revert
The rebuilt frontend is NOT the old OWID article-with-explorer scaffold the `389993f` component
assumed (no MethodologySummary sibling, no cascade slots, no embed/inspect modes). Reverting it
verbatim would not compile or fit. **Rebuild the component fresh to the current architecture; carry
the binding T9/T10 framing constraints over verbatim.** `git show 389993f:...FailuresFindingsSection.tsx`
is a content reference only.

## 3. Integration point — SEPARATE TOP-LEVEL NAV TAB (Mark directive 2026-06-08)
**Mark overrode the Architect's Focus-3-viz-tab proposal: failures gets its own top-level NavBar
tab** (sibling to Explore / Methodology / Data), for now. This is no longer an "invented nav
structure" (pitfall #6) because Mark explicitly directed it; it IS a design-system change, so the
UI/UX agent must add the nav tab to DESIGN_SYSTEM (the nav-tab pattern) as part of its gate. Concrete
shape:
- `NavBar.tsx` / `App.tsx`: add a top-level route/tab `Failures` alongside Explore / Methodology /
  Data. It is domain-aware: the tab shows a domain selector (reuse the existing domain picker) and
  renders `<FailuresFindings domainSlug={selectedDomain} />` for the chosen domain. (Failures are
  per-domain; the tab needs a domain selector since it is no longer inside the per-domain Explore
  view.)
- `FailuresFindings` self-fetches `/data/failures/{slug}.json` on mount + on domain change.
- No chart-lede involved (this is its own page, not a viz tab under the Explore lede), so the
  Smith's-S-suppression concern from the prior draft is moot; the page renders its own `<h1>`/`<h2>`
  + verbatim framing_note + the records list / empty state.
- UI/UX decides: does the Failures tab default to the same domain currently selected in Explore, or
  its own selector defaulting to family? Reuse the existing domain-picker component either way.
**The rest of this plan (types §4, per-record display, framing §5, ACs, tests) is unchanged by the
placement; only the mount point moves from a Focus-3 viz tab to a top-level tab + domain selector.**
The UI/UX gate now additionally covers: the new nav-tab DESIGN_SYSTEM addition, the domain-selector
reuse on the tab, and where the tab sits in the nav order.

## 4. Data wiring + types (add to `data/types.ts`)
`FailureOutcomeClass` (7-enum: empty_output, refusal_string_match, single_degenerate_pile,
parse_failure, http_error, timeout, other); `FailureRecord` (record_type:"failure"; model_id,
error_type, error_message, run_index, originating_outcome_class, ...); `DeclineInterviewRecord`
(record_type:"decline_interview"; the full provenance set incl. prompt_verbatim, response_verbatim,
thinking_verbatim, sha256_manifest, model_version_returned, provider, tokens, latency, stop_reason);
`FailuresRecord` union; `FailuresFile` wrapper ({domain_slug, generated_at, n_records,
n_failure_records, n_decline_interview_records, framing_note, records[]}). **Live `failures/family.json`
is the source of truth for field names** — if the Coder's types disagree with the JSON, pause + surface.
Fetch boundary: useEffect fetch, cast through unknown, first-class loading/fetch-failed/malformed
states (NO "missing"/"pending"/"placeholder").

### Per-record display
- **Summary row (no verbatim bytes — T10 S1 binding):** badge ("Failure" red / "Follow-up interview"
  neutral; badge text drives the accessible name), model_id (mono), collection_date (YYYY-MM-DD);
  failure → error_type + "error_message: N chars"; decline → "originating_outcome_class: <code>{enum}</code>".
- **Expanded `<details>` (verbatim bytes behind native disclosure):** failures → full error_message
  in `<pre>`, run_index, outcome_class. declines → "Originating context" / "Prompt LSB sent" /
  "Model output to the follow-up prompt" (block label, T10 S4b) / "Reasoning trace" (if non-empty) /
  "Provenance" (model_version_returned, provider, api_endpoint, sha256_manifest mono, tokens, latency,
  stop_reason). All `<pre>`: pre-wrap + break-word + `--font-mono` + `--font-size-xs`, max-height scroll.
- **Empty state (food, n_records=0) — FIRST-CLASS, not a defect:** verbatim T10 §S2 caption "This
  domain's collection run produced no failure records. The absence is itself an observation about how
  this set of models responded to this domain's elicitation prompts." No error icon/greyout/skeleton.

## 5. CDA SME points (re-affirm under the new placement, do NOT re-litigate T9/T10)
- **framing_note rendered verbatim** as the intro `<p>` below the `<h2>` (byte-identity vitest assertion).
- **Classification-display (pitfall #13):** `originating_outcome_class` enum shown verbatim in `<code>`
  mono, no LSB-authored human-readable expansion (`refusal_string_match` reads as an LSB detection-rule
  name, not model intent; the framing_note carries the anti-attribution framing). Badge labels
  "Failure"/"Follow-up interview" are LSB-side pipeline-state categories, not model-state. Re-affirm.
- **New in this re-issue:** placement in a Focus 3 viz tab (vs old article-bottom) — SME confirms it
  does not change the §1.5.6 first-class-evidence posture (tab-strip is the primary horizontal nav,
  parallel-with-other-viz-tabs ≈ parallel-with-MethodologySummary). Chart-lede suppression — SME confirms
  a Smith's-S lede over failures is a category error. Binding strings carried from T10:
  SECTION_HEADING="Collection records and follow-up interviews", the empty caption, badge labels, block
  labels. SME re-affirms or revises; Architect's call is no revision needed.

## 6. Gates + empty-state
Architect → CDA SME (verdict `docs/status/2026-06-08-phase9a-T1-failures-restore-cda-sme-verdict.md`,
four-axis) → UI/UX (verdict `…-uiux-verdict.md`; Focus3 tab integration, empty-state, `<details>`/
`<summary>` keyboard a11y, `<pre>` overflow, badge color tokens — if a needed token is absent the UI/UX
agent updates DESIGN_SYSTEM first per pitfall #15) → Coder (only on both PASS) → Reviewer → Tester.
Empty-state is first-class (pitfall #4): no error/greyout/"coming soon".

## 7. Acceptance criteria (one commit)
AC1 union+FOCUS3_TABS include `failures`. AC2 ContentArea branch + chart-lede suppressed. AC3 five
Failures types in types.ts. AC4 self-fetch on mount + domainSlug change w/ cancellation. AC5
framing_note verbatim first `<p>` + byte-identity test. AC6 each record a `<details>`/`<summary>` whose
accessible name has no verbatim model bytes before open. AC7 outcome_class enum in `<code>`, no
translation. AC8 exact block labels. AC9 empty-state verbatim caption + no records list (food fixture).
AC10 first-class loading/fetch-failed strings. AC11 all CSS via tokens.css, every var(--…) resolves
(pitfall #15); missing token → pause to UI/UX. AC12 build+test+lint green. AC13 no forbidden vocab in
LSB-authored strings (model verbatim bytes exempt per T10 §1). AC14 one commit referencing plan + SME +
UI/UX verdicts.

## 8. Test plan (Tester) — new `__tests__/FailuresFindings.test.tsx`
Fixtures = the live `failures/family.json` + `food.json` (production JSON IS the fixture; no synthesized
records). Cases: (1) heading present; (2) framing_note byte-identity; (3) `<details>` count ===
n_records; (4) summary rows contain NO verbatim response bytes (S1); (5) outcome_class in `<code>`;
(6) click-to-expand exposes full response_verbatim in `<pre>`; (7) provenance exposes sha256_manifest;
(8) empty-state (food) = verbatim caption + zero `<details>`; (9) forbidden-vocab scan over LSB chrome
only (exclude verbatim model bytes); (10) domain switch re-fetches. No real API (fetch via vi.fn()).
Dashboard vitest is not in CI (T-CI-vitest) — Tester runs locally, saves output to verdict; Reviewer
accepts local pass.

## 9. Scope / schema
NO `cdb_core/schemas.py` change (R7 not triggered); the types.ts addition mirrors an already-published
shape. Files: NEW FailuresFindings.tsx + copy/failures_findings.ts + styles/failures-findings.css +
__tests__/FailuresFindings.test.tsx; EDIT data/types.ts + ContentArea.tsx + VizTabs.tsx. **Working-tree
hygiene: the Coder stages ONLY its own files; Mark has uncommitted edits to
`docs/proposed/2026-06-08-methodology-page-scaffold.md` (leave alone) + an unpushed kickoff commit. No
`git add -A`, no `git add docs/` blanket — targeted paths only.**

## 10. Binding precedent (read)
`.claude/agent-memory/cda_sme/project_phase6_T9_failures_publish_verdict.md` +
`…_T10_failures_ui_verdict.md`; `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` (framing_note §5.1)
+ `…-T10-cda-sme-verdict.md` (S1–S7). The seven binding strings + S1–S7 notes remain in force.
