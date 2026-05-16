---
filed: 2026-05-16
author: Architect agent (Opus)
task: Phase 6 T14 — Documentation sweep
status: AWAITING_CDA_SME_AND_UIUX
predecessor_verdicts:
  - docs/status/2026-05-15-phase6-T13-reviewer-verdict.md (PASS, commit 7f8f977 → bfa62a2 superseding; latest tester PASS on 77feec3)
  - docs/status/2026-05-15-phase6-T13-tester-verdict.md (PASS, commit 77feec3)
  - docs/status/2026-05-15-phase6-T12-reviewer-verdict.md (PASS)
  - docs/status/2026-05-15-phase6-T11-reviewer-verdict.md (PASS)
  - docs/status/2026-05-15-phase6-T6-reviewer-verdict.md (PASS)
  - docs/status/2026-05-12-phase6-T8-reviewer-verdict.md (PASS, plus post-fix PASS addendum)
  - docs/status/2026-05-12-phase6-T10-reviewer-verdict.md (PASS)
  - docs/status/2026-05-12-phase6-T9-reviewer-verdict.md (PASS)
  - docs/status/2026-05-12-phase6-T7-reviewer-verdict.md (PASS)
  - docs/status/2026-05-12-phase6-T5-reviewer-verdict.md (PASS)
  - docs/status/2026-05-12-phase6-T0-reviewer-verdict.md (PASS)
companion_docs_read:
  - ARCHITECTURE.md (v0.7.3, §1.5, §4.5, §5.3 Phase 6 bullet list at lines 1340–1346)
  - CLAUDE.md (v1.0, §7 forbidden vocab, §9 fourteen pitfalls)
  - DESIGN_SYSTEM.md (v0.4.9, §2.3 domain nav, §11 component inventory, §12.8/§12.9, §8.1/§8.2)
  - docs/DATA_DICTIONARY.md (v0.1.14, §12 publish failures shape)
  - docs/SME_REVIEW.md
  - docs/BOOTSTRAP_DESIGN.md
  - docs/status/2026-05-12-phase6-architect-kickoff.md §5 (the matrix of doc updates triggered by each T)
slack_channel: #lsb-cda-sme (CDA SME), #lsb-ui-ux (UI/UX) — both gates required
---

# Phase 6 T14 — Documentation sweep (Architect plan)

## §1. Goal

Reconcile the four canonical doctrine documents (`ARCHITECTURE.md`,
`DESIGN_SYSTEM.md`, `docs/DATA_DICTIONARY.md`, `CLAUDE.md`) with what Phase 6
actually shipped through T0/T5/T6/T7/T8/T9/T10/T11/T12/T13 — and explicitly
preserve as pending the surfaces that did not ship (T1/T2 methodology page;
T3/T4 DriftTracker). T14 is a docs-only sweep: it codifies existing reality
into the canonical references, it does not introduce new conventions, new
components, new tokens, or new prose about methodology. The deliverable is
one commit changing only those four files (plus this plan and the gate
verdicts under `docs/status/`).

## §2. Affected files

Only these four canonical documents are in scope for prose edits. Their
current versions immediately prior to T14:

| File | Current version | In scope |
|---|---|---|
| `ARCHITECTURE.md` | v0.7.3 (2026-05-08 amendment) | §5.3 Phase 6 bullet list; §4.5 verification; new failures-display subsection if not already present; §1.5 framing language verification |
| `DESIGN_SYSTEM.md` | v0.4.9 (T6 plan-level verdict, 2026-05-15) | §11 component inventory; §1.2 token list verification; §12.x current-version stamp; §2.3 domain-nav diagram verification |
| `docs/DATA_DICTIONARY.md` | v0.1.14 | §12 publish-failures field-table verification; domain-parity for `food` |
| `CLAUDE.md` | v1.0 | §9 pitfalls audit; §7 forbidden-vocabulary verification |

Additional non-prose files touched by the commit:
- `docs/status/2026-05-16-phase6-T14-architect-plan.md` (this plan)
- `docs/status/2026-05-16-phase6-T14-cda-sme-verdict.md` (gate)
- `docs/status/2026-05-16-phase6-T14-uiux-plan-verdict.md` (gate)
- `docs/status/2026-05-16-phase6-T14-reviewer-verdict.md` (post-implementation)
- `docs/status/2026-05-16-phase6-T14-tester-verdict.md` (post-implementation)

Nothing else. `git diff --stat` after the Coder's commit MUST show only the
four prose files above and the status files. Any other file touched is an
out-of-scope failure (AC11 below).

## §3. Acceptance criteria

Numbered. Each AC names the specific section being touched (or verified) so
the Coder can be precise and the Reviewer can be mechanical.

### Block A — `ARCHITECTURE.md`

**AC1.** §5.3 Phase 6 bullet list (currently lines 1340–1346) is rewritten
to a deliverable checklist that reflects shipped state. Specifically:
- Mark the following as shipped (with date and commit ranges via reference
  to verdict files, NOT inline commit SHAs):
  - SimilarityHeatmap with cell-level CIs and CI-crosses-null reduced-saturation rule (T5; revised under T6 to 5-stop sequential palette)
  - FreeListCompare with per-term bootstrap inclusion-frequency bars (T7)
  - "Read as table" toggle + ScreenReaderSummary across MDS/Free List/Similarity (T8)
  - Failures-as-findings data layer (T9) and UI surface (T10)
  - Mobile hamburger nav (T11) and mobile model-selector bottom-drawer (T12)
  - Third active domain (`food`) promoted (T13)
  - Operator inspection mode `?inspect=<slug>` (T0)
- Mark the following as **still pending in Phase 6** with the documented blocker:
  - **Methodology page** (T1 + T2): blocked on Mark's routing decision (single
    long-scroll vs. multi-route) and on Mark-authored prose. The
    `methodologyPageUrl` reference in `MethodologySummary` remains `null`.
  - **`DriftTracker` + `DateSlider`** (T3 + T4): deferred until the next
    collection campaign produces multi-date data per `model_version_returned`.
    The 0.2 corpus has at most one collection date per model and therefore
    cannot drive a drift visualization without violating R10.
- Preserve the existing bullets for "First public release of the open data
  bundle to Backblaze B2 + Zenodo DOI" — that work is Phase 8 per the §1
  Phase 8 list and the kickoff §1 out-of-scope statement; T14 does not move
  it into Phase 6.
- Editorial constraint: do not delete the historical bullet wording —
  rewrite is acceptable, but the original phrasing of each Phase 6 line
  should be preserved as much as practical so the diff reads as "marked
  shipped / marked pending" rather than as a wholesale rewrite of Phase 6.

**AC2.** §4.5 (frontend / uncertainty / R10 binding) — verify and note
explicitly in the commit message that **no sharpening is required**. The
R10 binding text already correctly covers T5/T7/T10/T11/T12/T13 as
implemented. The DriftTracker paragraph (current lines 1112, 1120–1125)
remains accurate as a forward-looking spec; do not edit it to reflect
Phase 6 status because the visualization did not ship. If the Coder finds
that §4.5 contains a statement now contradicted by shipped behavior, the
Coder STOPS and surfaces the conflict to the Architect — do not edit
§4.5 without re-routing.

**AC3.** Failures-display documentation. Confirm whether ARCHITECTURE.md
already carries a publish-layer failures-display subsection. If it does
not, add a new short subsection (target: ≤25 lines) at the natural
location — most likely as a new §4.4.x or §4.5.x. The subsection MUST:
- Cross-reference `docs/DATA_DICTIONARY.md` §12 for field tables (do NOT
  duplicate the field tables here).
- State the publish-layer redaction boundary verbatim: sanitization runs
  in `cdb_publish.sanitize.sanitize_for_publication()` before any string
  is written to `apps/dashboard/public/data/failures/{domain}.json`.
- State that the `framing_note` field carries CDA-SME-reviewed §1.5.4
  framing text and that the dashboard renders it adjacent to the records
  per the T9/T10 verdicts.
- State that publication-eligibility uses the failures and decline-interview
  JSONL as source-of-truth and that no edits to `data/raw/*.jsonl` are
  permitted (append-only invariant).
- Cite `SECURITY_AND_HARDENING.md` §3.3 for the sanitization rationale.
- Must NOT include any field descriptions, sanitization regexes, or the
  `framing_note` verbatim text — those live in DATA_DICTIONARY.md §12.

If ARCHITECTURE.md already carries a section that meets these conditions,
the AC is "verify and note no change required" in the commit body.

**AC4.** §1.5 framing language spot-check. Verify that no §1.5 wording was
contradicted by shipped T7/T10/T13 copy (the FreeListCompare empty-state
copy, the FailuresFindingsSection framing, the food-domain lede). No edit
expected — record the verification result in the commit body. If a
contradiction is found, STOP and route to CDA SME before editing.

### Block B — `DESIGN_SYSTEM.md`

**AC5.** §11 Component Inventory — extend the "Phase 6 (full dashboard)"
list to include every shipped Phase 6 component with its file path. The
inventory MUST add (alphabetical by component name where a natural cluster
does not dictate otherwise):

- `FailuresFindingsSection.tsx` — domain-page failures-as-findings entry point (T10). File: `apps/dashboard/src/components/FailuresFindingsSection.tsx`.
- `FailuresInspectView.tsx` — operator inspection variant for failures (T0 + T10). File: `apps/dashboard/src/components/FailuresInspectView.tsx`.
- `FreeListColumn.tsx` (if present as a sibling of FreeListCompare per T7's shipped structure) — note this only if the file exists in `apps/dashboard/src/components/`; otherwise omit. Coder verifies before listing.
- `FreeListTable.tsx` — read-as-table rendering for FreeListCompare (T8). File: `apps/dashboard/src/components/FreeListTable.tsx`.
- `InspectRoot.tsx` — operator inspection-mode root (T0). File: `apps/dashboard/src/components/InspectRoot.tsx`.
- `InspectSection.tsx` — operator inspection-mode section wrapper (T0). File: `apps/dashboard/src/components/InspectSection.tsx`.
- `InspectTable.tsx` — operator inspection-mode tabular rendering (T0). File: `apps/dashboard/src/components/InspectTable.tsx`.
- `MdsTable.tsx` — read-as-table rendering for MDSPlot (T8). File: `apps/dashboard/src/components/MdsTable.tsx`.
- `ReadAsTableToggle.tsx` — toggle component (T8). File: `apps/dashboard/src/components/ReadAsTableToggle.tsx`.
- `ScreenReaderSummary.tsx` — hidden prose chart summaries (T8). File: `apps/dashboard/src/components/ScreenReaderSummary.tsx`.
- `SimilarityTable.tsx` — read-as-table rendering for SimilarityHeatmap (T8). File: `apps/dashboard/src/components/SimilarityTable.tsx`.

Components already listed in §11 under "Phase 6" (FreeListCompare,
SimilarityHeatmap, MobileNav, Header T11 update, MobileModelSelectorDrawer
and its copy/CSS siblings) MUST NOT be duplicated. The Coder reads §11
carefully and only adds entries that are not already there.

The pending entries (`DriftTracker.tsx`, `DateSlider.tsx`,
`ModelDetailPanel.tsx`, `AccessibilityTableToggle.tsx`,
`MethodologyPage.tsx`, `CitationBlock.tsx`, `LimitationCard.tsx`) remain
in §11 unchanged; T14 does not delete pending entries.

Note: `AccessibilityTableToggle.tsx` is the legacy name for what shipped
as `ReadAsTableToggle.tsx` under T8's UI/UX verdict. Do NOT rename or
delete the pending `AccessibilityTableToggle.tsx` line — the T8 verdict
folded the legacy name into `ReadAsTableToggle.tsx` already, and §11's
pending list can carry the legacy name as a historical pointer. If the
UI/UX agent prefers a one-line annotation ("renamed to
`ReadAsTableToggle.tsx` per T8 UI/UX verdict; see §12.9"), apply it.

**AC6.** §12.x version-stamp pass. The current changelog header is
v0.4.9 (T6 plan-level verdict, 2026-05-15). Verify that:
- §12.8 (SimilarityHeatmap cell-text contrast) is internally consistent
  with the v0.4.9 rewrite to 5-stop sequential binning;
- §12.9 (ReadAsTableToggle + ScreenReaderSummary) is internally
  consistent with the v0.4.6 text;
- §8.1 (Mobile hamburger menu) is internally consistent with v0.4.7;
- §8.2 (Mobile bottom-drawer) is internally consistent with v0.4.8.

T14 may bump the version once to v0.4.10 with a changelog entry that
summarizes the T14 sweep verbatim from this plan's AC list. T14 MUST NOT
re-bump for each individual §12.x verification — one bump only.

**AC7.** §1.2 Color Palette and token list — verify that every token
added during Phase 6 is listed. Specifically:
- `--color-scale-seq-0` through `--color-scale-seq-4` (T6, v0.4.9): MUST be present.
- `--color-heatmap-cell-text-dark` (T5, v0.4.5): MUST be present.
- `--color-text-caption` (T10, v0.4.3): MUST be present.
- `--color-model-7` through `--color-model-11` (v0.4 + v0.4.1 correction): MUST be present.

If any token is missing from the canonical token block, add it with the
hex value and one-line annotation copied verbatim from the §1.2 block in
the running file (do not invent new annotations).

Per the kickoff matrix (§5 row "Mobile hamburger spec"), T11 and T12
shipped **with no new tokens** by design. T14 explicitly notes this in
the commit body — confirm by grep that neither §8.1 nor §8.2 introduces
a token name not already in the §1.2 block.

**AC8.** §2.3 Domain Navigation diagram — verify the diagram already
shows `[Family] [Holidays] [Food] [Emotion *] [Justice *]` reflecting
the T13 promotion. (Current file at line 223 shows this — verify and
note in the commit body. No edit required.)

### Block C — `docs/DATA_DICTIONARY.md`

**AC9.** §12 publish-failures field tables — verify that v0.1.14 is the
current version, that every field name in the §12 tables matches what
`packages/cdb_publish/cdb_publish/schemas/failures.py` produces, and
that the `framing_note` description (currently line 1086) is consistent
with the T9 CDA SME verdict text. No edit expected; record the
verification in the commit body. If a mismatch is found, STOP and route
to CDA SME — do not edit DATA_DICTIONARY.md §12 without methodology
review.

**AC10.** Food-domain parity. The current §1.1 (line 61) already lists
`food` as a v1 domain alongside `family` and `holidays`. Verify and
extend any other §-table that enumerates per-domain examples so that
`food` has parity with `family` and `holidays`. Specifically:
- §5 Example queries (line 530+): if any query enumerates `family` and
  `holidays` literally (e.g., `WHERE domain_slug = 'family'`), no edit
  required — example queries are example queries, not exhaustive
  enumerations, and changing them would create unnecessary diff noise.
- The Coder must NOT add new example queries solely to mention food.
  AC10 is a verification AC; edits are permitted only where a field
  description literally enumerates the v1 domain set and that
  enumeration omits `food`.

**AC11.** Drift fields — confirm DATA_DICTIONARY.md adds NO drift-related
fields, NO `data/drift/` file shape, NO new section. This AC is an
explicit non-action — the Coder records "drift not added; T3/T4
deferred" in the commit body.

### Block D — `CLAUDE.md`

**AC12.** §9 common pitfalls audit. Verify entries #1–#14 remain
accurate. Specifically:
- #1 (model_id vs. model_version_returned) — still correct.
- #2 (no LLM in cdb_analyze) — still correct.
- #3/#4/#12 (historical grounding pitfalls) — still correct as historical.
- #6 (inventing visual decisions) — Phase 6 (T6, T8, T11, T12) exercised
  this rule explicitly; still correct.
- #7 (forbidden vocab in generated text) — still correct.
- #8 (point estimates without uncertainty) — still correct; T5/T7
  implementations comply.
- #13 (cross-boundary detector reuse) — still correct.
- #14 (no spend-cap reintroduction) — still correct.

**AC13.** Token-discipline pitfall — Phase 6 T8 surfaced a recurring
class of bug: components referencing CSS custom properties that do not
exist in `tokens.css` (the T8 Reviewer FAIL specifically called out
phantom `--font-family-mono`, `--color-bg-surface`, and
`--color-text-secondary`-at-xs-size cases). This pattern is not yet
codified in §9. T14 adds **one** new pitfall entry to §9 covering this:
- Title: "Referencing a CSS custom property that does not exist in `tokens.css`."
- Body (target: ~5 lines, matching the prose density of existing entries):
  describe the bug class (component uses `var(--token-name)` for a token
  that was never defined or that was renamed; the browser silently
  treats the value as `unset`; the visual result is broken but no test
  fails because there is no compile-time check); reference the T8
  Reviewer FAIL (`docs/status/2026-05-12-phase6-T8-reviewer-verdict.md`
  plus the post-fix addendum) as the originating incident; state the
  fix pattern (grep tokens.css before adding a `var(--...)` reference;
  if the token does not exist, route to UI/UX agent for a design-system
  update).

This is the only addition to §9. T14 does NOT renumber existing entries.
The new entry is appended as #15.

**AC14.** §7 forbidden vocabulary — verify the table is unchanged. No
edit expected; record in commit body. No new forbidden vocabulary has
emerged during Phase 6.

### Block E — cross-cutting

**AC15.** Bibliography / cross-reference integrity. After all edits,
verify that no edited section references a doc section that does not
exist. Specifically:
- Any `§4.5.x` reference added under AC3 must point at a real subsection
  number used in the AC3 edit.
- Any `§12.x` reference added under AC6 changelog entry must match the
  actual section number.
- The DATA_DICTIONARY.md cross-references from AC3 must use the
  `docs/DATA_DICTIONARY.md §12` form.

**AC16.** Forbidden-vocabulary scan across the four edited files
post-edit. Coder runs:

```
git diff master -- ARCHITECTURE.md DESIGN_SYSTEM.md docs/DATA_DICTIONARY.md CLAUDE.md \
  | grep -iE 'worldview|believes|thinks of|cultural bias|what the model understands|how models see|model.*believes|model.*thinks of'
```

Output MUST be empty (excluding the existing §7/§1.5.4 forbidden-vocab
tables themselves, which name the terms in order to forbid them).

**AC17.** `git diff --stat` sanity scope. After all edits, `git diff --stat master`
shows exactly:
- `ARCHITECTURE.md`
- `DESIGN_SYSTEM.md`
- `docs/DATA_DICTIONARY.md`
- `CLAUDE.md`
- `docs/status/2026-05-16-phase6-T14-architect-plan.md` (this plan)
- `docs/status/2026-05-16-phase6-T14-cda-sme-verdict.md`
- `docs/status/2026-05-16-phase6-T14-uiux-plan-verdict.md`
- `docs/status/2026-05-16-phase6-T14-reviewer-verdict.md`
- `docs/status/2026-05-16-phase6-T14-tester-verdict.md`

Any other file in the stat output is an out-of-scope failure.

## §4. Out of scope

T14 is a sweep, not a rewrite. The following are explicitly forbidden:

1. **Methodology page prose.** T1 and T2 remain blocked on Mark's routing
   decision and on Mark-authored content. T14 may note in
   ARCHITECTURE.md §5.3 that the methodology page is pending; T14 must
   NOT generate any prose that would appear on `/methodology`. T14 must
   NOT update DESIGN_SYSTEM.md §6 (methodology page) to reflect a
   structure that has not been ratified.
2. **Drift documentation.** T3 and T4 are deferred. T14 must NOT add
   drift JSON file shapes to DATA_DICTIONARY.md, must NOT add
   DriftTracker/DateSlider component spec sections to DESIGN_SYSTEM.md,
   must NOT mark drift as shipped in ARCHITECTURE.md §5.3.
3. **New components, new tokens, new visual decisions.** T14 documents
   what shipped. If the Coder believes a token or component is missing,
   the right action is to STOP and surface the question — not to invent.
4. **Chart-type changes, color decisions, copy rewrites.** The dashboard
   will be handed to a dedicated AI frontend designer next; T14 does not
   anticipate that work. The UI/UX gating for T14 is the accessibility
   floor + DESIGN_SYSTEM.md fidelity, not new visual decisions.
5. **Schema changes.** `cdb_core/schemas.py` is not touched. No
   InformantRecord, GroundingRef, or DeclineInterview field is modified
   or added. R6 / CLAUDE.md §6 rule 6 is mechanically satisfied by
   non-touch.
6. **Code changes.** No `.py`, `.ts`, `.tsx`, `.css`, or test file is
   edited. T14 is prose-only.
7. **Phase 7 / Phase 8 work.** The social pipeline, open bundle release,
   security headers audit, robots.txt, SECURITY.md — out of scope.
8. **Cost / spend language.** Per CLAUDE.md R14 / R13, T14 introduces no
   cost estimates, no spend caps, no `CDB_MAX_SPEND_USD` language. The
   CI grep check + Reviewer R13 are mechanical safety nets; the plan
   here is the doctrinal safety net. <!-- noqa: spend-gate-check -->

## §5. Gate requirements

### CDA SME review — REQUIRED

Triggers:
- AC3 adds (or verifies the absence of) a failures-display subsection in
  ARCHITECTURE.md. The subsection touches the publish-layer redaction
  boundary which is methodology-adjacent (the `framing_note` field
  carries §1.5.4-binding text).
- AC4 spot-checks §1.5 framing across shipped Phase 6 surfaces.
- AC9 verifies DATA_DICTIONARY.md §12 `framing_note` description matches
  the T9 CDA SME verdict text.
- AC13 adds a §9 pitfall entry; CDA SME confirms the body language does
  not introduce anthropomorphism or hypothesis-testing framing.
- AC16 runs a forbidden-vocabulary scan; CDA SME confirms zero
  violations after the Coder's pass.

CDA SME verdict goes to `docs/status/2026-05-16-phase6-T14-cda-sme-verdict.md`.
Four-axis scorecard. PASS / PASS-WITH-NOTES allows the plan to flow to
the Coder. FAIL bounces to Architect.

### UI/UX review — REQUIRED

Triggers:
- DESIGN_SYSTEM.md is in scope (AC5, AC6, AC7, AC8). The UI/UX agent
  owns this doc.
- AC5 extends the component inventory — UI/UX confirms that every added
  entry names a real file path and that no entry is duplicated.
- AC6 may bump the changelog to v0.4.10 — UI/UX confirms the bump syntax
  matches the existing changelog convention.
- AC7 audits the token block — UI/UX confirms no tokens are missing.

Per the v0.4.6+ UI polish scope memo (`feedback_ui_polish_scope.md`), the
UI/UX gate for T14 reduces to **DESIGN_SYSTEM.md fidelity** + **accessibility
floor preservation** + **R10 verification** — no new visual decisions, no
copy review. UI/UX verdict goes to
`docs/status/2026-05-16-phase6-T14-uiux-plan-verdict.md`.

### Reviewer

Enforces:
- §1.5 framing in all newly written prose (AC3 subsection text, AC13 pitfall body).
- No forbidden vocabulary (CLAUDE.md §7) anywhere in the diff (AC16 scan).
- R6 (no schema changes — pure docs task; mechanically verified by
  `git diff --stat` containing no `cdb_core/` or `data/types.ts` paths).
- R7 / R10 / R13 (point estimates without uncertainty, spend-gate
  language, prompt-template versioning) — N/A for a docs-only task but
  the Reviewer's nine-check table records each as N/A explicitly.
- Plan-verdict references in the commit message.

### Tester

For a docs-only task, the Tester verifies:
- `uv run pytest`, `uv run ruff check .`, `uv run mypy packages/` all
  green (no regressions from doc edits — these should be no-ops, the
  test is that they remain no-ops).
- `cd apps/dashboard && npm run lint && npm run test && npm run build`
  green (same reasoning — the dashboard test suite should not be
  affected by doc edits; the test is that it isn't).
- `git diff --stat master` matches AC17 scope exactly.
- Forbidden-vocabulary grep (AC16) returns empty.
- Cross-reference grep: any `§<number>` reference added by the Coder
  resolves to a real section header in the target doc.

Tester verdict goes to `docs/status/2026-05-16-phase6-T14-tester-verdict.md`.

## §6. Risks

1. **Scope creep into T1/T2 methodology prose.** The strongest risk.
   The Coder reading ARCHITECTURE.md §5.3 may feel that "marking shipped"
   is incomplete without "and here is what the methodology page now
   says." It is not. T1 and T2 are blocked on Mark; T14 documents the
   block, it does not unblock. Mitigation: explicit AC1 sub-bullet
   pinning the methodology page as pending with the documented blocker;
   §4 out-of-scope item #1.

2. **Over-documentation of components the FT designer will rebuild.**
   The dedicated AI frontend designer takes over post-Phase 6. Many of
   the components T14 catalogs in DESIGN_SYSTEM.md §11 will be replaced
   or restyled. T14 still adds them to §11 because §11 documents the
   *current* state of the codebase, not the future state. Mitigation:
   AC5 lists components with file paths only — no implementation notes,
   no styling discussion, no API surface. The FT designer will update
   §11 as they replace components.

3. **Premature drift-doc additions.** A Coder who reads the kickoff §5
   matrix may try to add the drift JSON file shape to DATA_DICTIONARY.md
   or the DriftTracker spec to DESIGN_SYSTEM.md §12. Both are blocked
   on data that does not yet exist (multi-date `model_version_returned`
   observations). Mitigation: explicit AC11 non-action; §4 out-of-scope
   item #2.

4. **Phantom-token reintroduction in the new §9 pitfall body.** AC13
   adds prose about phantom CSS custom properties. The Coder must NOT
   accidentally reference a token name that itself does not exist in
   `tokens.css` while describing the bug. Mitigation: the pitfall body
   names the *pattern*, not specific tokens. The originating-incident
   reference points at the T8 Reviewer FAIL verdict for the specific
   token-name examples.

5. **Version-bump churn.** A Coder may bump DESIGN_SYSTEM.md to v0.5.0
   on the grounds that "Phase 6 is closing." Don't. AC6 caps the bump
   at v0.4.10. Semantic version semantics: the FT designer's takeover
   will be the v0.5 bump.

6. **Cross-reference rot.** AC15 catches dangling §-references after
   edits. The Tester re-runs the grep at verification time.

## §7. Suggested ordering for the Coder

### Read first (in this order)

1. This plan, end to end.
2. `docs/status/2026-05-12-phase6-architect-kickoff.md` §5 (the matrix of
   doc updates triggered by each T) — for context on what was planned vs.
   what shipped.
3. The five T-verdict files for T5/T6/T8/T9/T10 (the methodology-relevant
   ones) — Coder reads these to confirm the framing language they will
   reference in AC3 and AC9.
4. `DESIGN_SYSTEM.md` §11 (current state of component inventory) — Coder
   reads carefully so AC5 does not duplicate existing entries.
5. `CLAUDE.md` §9 (existing 14 pitfalls) — Coder reads so AC13's new
   entry matches the prose density and tone of existing entries.
6. `docs/DATA_DICTIONARY.md` §12 (publish-failures field tables) — Coder
   reads to confirm AC9's verification.

### Edit order

The four docs are mostly independent. The recommended edit order
minimizes context-switch cost:

1. **`docs/DATA_DICTIONARY.md`** first — mostly verification (AC9, AC10,
   AC11), minimal-to-zero prose edits. Closing this AC block confirms
   the failures-publish field tables are the canonical reference for
   AC3.
2. **`ARCHITECTURE.md`** second — the failures-display subsection (AC3)
   cross-references DATA_DICTIONARY.md §12. The §5.3 rewrite (AC1) is
   the largest single prose change in T14.
3. **`DESIGN_SYSTEM.md`** third — component inventory extension (AC5)
   is mechanical once the Coder has the file-path list in front of
   them. Version bump (AC6) is the last edit in this file.
4. **`CLAUDE.md`** last — adds one new §9 pitfall (AC13), verifies the
   rest. Smallest diff of the four docs.

### Version bumps

- `DESIGN_SYSTEM.md`: bump to v0.4.10 ONCE at the top of the file with a
  changelog entry summarizing the T14 sweep. Do not re-bump for each
  AC.
- `docs/DATA_DICTIONARY.md`: NO version bump. T14 is a verification
  pass; v0.1.14 remains current. If AC9 surfaces a real correction, the
  Coder STOPS and routes to CDA SME — and that re-route would produce
  a v0.1.15 bump under a different plan.
- `ARCHITECTURE.md`: NO version bump. T14 is documentation reconciliation
  inside v0.7.3; the §5.3 rewrite is a within-version edit. A v0.7.4
  bump would imply a substantive amendment, which T14 is not.
- `CLAUDE.md`: NO version bump. Adding a §9 pitfall is a within-v1.0
  edit. v1.0 remains current.

## §8. Test plan

For this docs-only task, the test plan is verification, not coverage.

### Local verification commands

From `/opt/lsb-agent/`:

```
uv run pytest
uv run ruff check .
uv run mypy packages/
cd apps/dashboard && npm run lint && npm run test && npm run build
```

All five commands MUST be green. None of them should be affected by doc
edits; the test is that they remain green.

### Forbidden-vocabulary scan (AC16)

```
git diff master -- ARCHITECTURE.md DESIGN_SYSTEM.md docs/DATA_DICTIONARY.md CLAUDE.md \
  | grep -iE 'worldview|believes|thinks of|cultural bias|what the model understands|how models see|model.*believes|model.*thinks of'
```

Expected output: empty (or only the existing §7/§1.5.4 table rows that
literally enumerate the forbidden terms in order to forbid them — those
are not violations).

### Diff-scope sanity (AC17)

```
git diff --stat master
```

Expected output: exactly the nine files listed in AC17. Any extra file
is an out-of-scope failure.

### Cross-reference resolution (AC15)

For each `§<number>` reference added or modified by T14, the Coder runs
a grep against the target doc to confirm the section header exists:

```
grep -nE '^#{1,4} (§4\.5|§4\.4|§12\.|§9 |§11 )' <target-file>
```

The Tester reruns this at verification time.

### No-LLM-in-cdb_analyze static check

```
grep -rE 'import anthropic|import openai|from anthropic|from openai|InferenceClient|google.generativeai' packages/cdb_analyze/
```

Expected output: at most the prohibition-comment in
`packages/cdb_analyze/cdb_analyze/__init__.py` (no live import). N/A
for a docs-only task but the Reviewer table records it.

## §9. Commit message guidance

Scope: `docs` (multiple top-level doctrine files touched).

Conventional Commits one-liner (≤72 chars):

```
docs(docs): Phase 6 T14 — documentation sweep reconciling shipped state
```

Commit body must:
- Reference the task ID (Phase 6 T14).
- Reference the CDA SME verdict file path
  (`docs/status/2026-05-16-phase6-T14-cda-sme-verdict.md`).
- Reference the UI/UX verdict file path
  (`docs/status/2026-05-16-phase6-T14-uiux-plan-verdict.md`).
- Enumerate each AC with PASS / VERIFIED / N/A so the Reviewer can be
  mechanical.
- Record the explicit non-actions (AC2, AC4, AC8, AC11, AC14) so the
  audit trail captures the verification rather than only the edits.
- Contain no forbidden vocabulary, no spend-gate language. <!-- noqa: spend-gate-check -->

## §10. Reading list bundled for the Coder

Per CLAUDE.md §2 + the kickoff §6 reading-list convention, the Coder
reads (on top of the standard ARCHITECTURE.md / CLAUDE.md / DESIGN_SYSTEM.md
set):

- `docs/SME_REVIEW.md` — methodology context for AC3, AC4, AC9.
- `docs/BOOTSTRAP_DESIGN.md` — required reading per agent constitution
  before any plan touching bootstrap-adjacent docs; T14 verifies §4.5
  R10 binding (AC2) which is bootstrap-relevant.
- `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` — for AC3 and
  AC9 (failures-publish framing-note text).
- `docs/status/2026-05-12-phase6-T10-cda-sme-verdict.md` — for AC3
  (failures UI framing).
- `docs/status/2026-05-15-phase6-T13-cda-sme-verdict.md` — for AC4 (food
  lede framing).
- `docs/status/2026-05-12-phase6-T8-reviewer-verdict.md` and the post-fix
  addendum — for AC13 (originating-incident reference for the new §9
  pitfall).
- `docs/status/2026-05-12-phase6-architect-kickoff.md` §5 — the matrix
  of doc updates triggered by each T, as a forward-looking checklist
  against which T14 reconciles.

---

**End of T14 architect plan.**
This plan is dispatched to the CDA SME and the UI/UX agent in parallel.
After both gates issue PASS or PASS-WITH-NOTES, the Coder is dispatched
with the bundle of (plan, CDA SME verdict, UI/UX verdict). Reviewer +
Tester verdict files are produced post-implementation per the standard
sequence.
