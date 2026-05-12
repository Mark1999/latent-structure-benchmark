# Phase 6 T10 — `FailuresFindingsSection` (UI Surface for Failures-as-Findings) — Architect Plan

**Save to:** `/opt/lsb-agent/docs/status/2026-05-12-phase6-T10-architect-plan.md`

**Date:** 2026-05-12
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T10 only (defined in `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T10 as the "public-facing failures-as-findings display. Per ARCHITECTURE.md §1.5.6, first-class evidence — not a debug log").
**Status:** Awaiting CDA SME dispatch (REQUIRED — see §6); then UI/UX light-touch (§6); then Coder dispatch on PASS.

T10 is the **UI consumer of the T9 data layer** (shipped 2026-05-12, commit `e3ade52`). The published JSON shape is at `apps/dashboard/public/data/failures/{slug}.json` and is the binding data contract.

---

## §0. Reading list (mandatory before Coder dispatch)

1. `/opt/lsb-agent/CLAUDE.md` §6 (binding rules — especially **R10** for general UI hygiene, **R12** §1.5.4 forbidden vocabulary, R13 design-system gating), §7 (forbidden vocabulary table — **applies to every LSB-authored string T10 introduces**), §9 (pitfalls **#4** "failures are findings, not defects/placeholders," #5 schema-touch co-update — not triggered by T10 but cited as posture, #7 forbidden vocabulary in any model-facing string, #8 — N/A here since failure records carry no point estimate).
2. `/opt/lsb-agent/ARCHITECTURE.md` §1.5 (binding on every text artifact), **§1.5.4 forbidden vocabulary**, **§1.5.5 first-class-state framing** (empty-records case), **§1.5.6 failures-as-findings framing** (binding on the entire T10 surface), §4.4 publish layer (T9 is the producer).
3. `/opt/lsb-agent/DESIGN_SYSTEM.md` v0.4.5 in full — specifically §1 tokens, §2 page architecture, §7 accessibility floor, §12.1 reveal cascade, §12.7 MethodologySummary (T10 attaches as the **structural sibling below** it).
4. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T9-architect-plan.md` — full data contract: §2.2 published shape, §2.4 field-coverage table per record_type, §2.5 empty-state convention, §2.7 manifest extension.
5. **`/opt/lsb-agent/docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md`** — **binding**. The §5.1 `framing_note` field MUST be rendered verbatim by T10. The §3 enum-§1.5.4-compliance table tells T10 it can surface the seven `originating_outcome_class` values without rewording. The §5.5 "Note on quotation" advisory is duplicated in `DATA_DICTIONARY.md` and is the audience-translation backstop.
6. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T0-architect-plan.md`, `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-architect-plan.md`, `/opt/lsb-agent/docs/status/2026-05-12-phase6-T7-architect-plan.md` — plan format precedents; the §4 "cast through unknown" pattern and the §5 "out of scope" discipline.
7. `/opt/lsb-agent/apps/dashboard/public/data/failures/family.json` and `holidays.json` — actual T9-emitted JSON shape; treat the files as authoritative when they disagree with `data/types.ts` (which is untouched in T10).
8. `/opt/lsb-agent/apps/dashboard/public/data/manifest.json` — confirms the `failures: { "family": "data/failures/family.json", "holidays": "data/failures/holidays.json" }` map is present.
9. `/opt/lsb-agent/apps/dashboard/src/App.tsx` — the attachment point (T10 inserts below `MethodologySummary`).
10. `/opt/lsb-agent/apps/dashboard/src/components/MethodologySummary.tsx` — structural sibling pattern; same `<section aria-labelledby>` posture.
11. `/opt/lsb-agent/apps/dashboard/src/components/InspectRoot.tsx` — T0 did **not** add a failures inspect mode (grep confirms zero references). T10 makes a binding decision in §2.8 about whether to extend InspectRoot.
12. `/opt/lsb-agent/apps/dashboard/src/api/client.ts` — extend with `fetchFailures(slug)`.
13. `/opt/lsb-agent/apps/dashboard/src/data/types.ts` — **do not touch** (T14 doc-sweep concern); cast through `unknown` at the fetch boundary (precedent: `DataExplorer.tsx` lines 152/192/229, `InspectRoot.tsx`).
14. `/opt/lsb-agent/apps/dashboard/src/styles/app.css` lines 70–76 (cascade nth-child delays — T10 extends).
15. Memory: `project_failures_are_findings.md` (2026-04-23 binding directive — "dashboard must expose failures with raw logs"), `feedback_ui_polish_scope.md` (Phase 6 minimum-viable functional surface; UI/UX gating reduced to accessibility floor + R10 + tokens + WCAG AA), `feedback_visual_inspection.md` (visual rendering of records that Mark cannot evaluate as raw JSON).

---

## §1. Mark's binding directives + Phase 6 framing

1. **"Failures are findings" — 2026-04-23 directive.** T10 is the public-facing rendering of this directive. The records are first-class evidence, not a debug log, not a placeholder, not a pending state.
2. **`framing_note` field is consumed verbatim from T9's JSON** (CDA SME §5.1 binding). T10 may NOT paraphrase. Renders as the section's introductory paragraph. Empty-string or missing field is a defensive error state — see §2.4.
3. **Phase 6 minimum-viable functional surface** (memory `feedback_ui_polish_scope.md`). Plain `<details>`/`<summary>` accordions, default tokens, no animation, no microcopy work, no aesthetic blocking by UI/UX.
4. **Forbidden vocabulary (§1.5.4) applies to every LSB-authored string in T10** — section heading, accordion labels, no-records caption, error-state caption, ARIA labels. **Verbatim model output inside `response_verbatim` / `prompt_verbatim` / `thinking_verbatim` / `error_message` is exempt** (model-authored data, not LSB prose). The `framing_note` is exempt from re-review (CDA SME approved at T9).
5. **No software-side spend gates (R14).** N/A to a frontend rendering task, restated for closure.
6. **No new dependencies.** Plain React + TSX + token-driven CSS. Native `<details>`/`<summary>` for keyboard accessibility — see §2.6.
7. **`?inspect=...` operator surface (T0) is touched** at the Architect's discretion per §2.8. Default decision: extend with `?inspect=failures-<slug>` mode for parity with the published shape.
8. **Bundle budget: T10 adds ≤ 8 KB gzipped** against post-T9 baseline. T9 was backend, no bundle change — so the post-T9 baseline equals the post-T7 baseline (~85 KB). Phase 6 cumulative cap is 400 KB.

---

## §2. Decisions (Architect's call, documented for the record)

### §2.1. Placement — **per-domain `FailuresFindingsSection` below `MethodologySummary` in `App.tsx`** (Mark's option (a)).

The orchestrator's binding proposal: option (a). T10 honors it.

**Rationale:**
1. Follows the `MethodologySummary` placement precedent from T13 (DESIGN_SYSTEM.md §12.7).
2. Keeps failures contextually tied to the domain being explored — the reader is already in a "this domain, these models" mental frame; the failures are the same domain's first-class observations.
3. No routing decision required. T1 (kickoff Open Question 1) is unresolved; option (b) would foreclose it.
4. Memory `project_failures_are_findings.md` framing — "allow the website viewer to review the reasons why and the raw logs" — is satisfied by an in-flow section with expandable details, without forcing a route change.

**Concrete change in `App.tsx`:** insert `<FailuresFindingsSection>` immediately below the existing `<MethodologySummary>` block (after the `methodologyPageUrl={null}` MethodologySummary cascade item, before the `<Footer>` cascade item). The new section is wrapped in `<div className="reveal-cascade-item">` at App.tsx level, matching the MethodologySummary precedent (DESIGN_SYSTEM.md §12.7 binding "wrapper at App.tsx level, not inside the component").

**Excluded in embed mode** (per DESIGN_SYSTEM.md §12.5 — embed mode renders only `DataExplorer`). T10 adds an `!embedMode &&` guard parallel to the existing `MethodologySummary` guard at `App.tsx:339`.

### §2.2. Reveal cascade slot — **7th position, 360ms delay** (extends §12.1 by one slot).

Current cascade (`app.css` lines 70–76):
- 1: 0ms (Header)
- 2: 80ms (ArticleHeader)
- 3: 160ms (DomainPicker)
- 4: 240ms (KeyFinding + DataExplorer wrapper, capped at 320ms per §12.1)
- 5: 320ms (MethodologySummary)
- 6: 320ms (Footer)

**T10 inserts at index 6 (FailuresFindingsSection at 360ms); Footer moves to index 7 (also 360ms).** The §12.1 total-cap of 600ms is preserved — the cascade ends well before the cap.

`app.css` edits (Coder surgical):
```css
.reveal-cascade-item:nth-child(6) { animation-delay: 360ms; }  /* was 320ms (Footer); now FailuresFindingsSection */
.reveal-cascade-item:nth-child(7) { animation-delay: 360ms; }  /* new: Footer moves here */
```

Coder verifies cascade order at mount: Header → ArticleHeader → DomainPicker → KeyFinding → DataExplorer → MethodologySummary → **FailuresFindingsSection** → Footer.

### §2.3. Heading hierarchy — **`<h2>` sibling of MethodologySummary's `<h2>`.**

`MethodologySummary` uses `<h2 id="methodology-summary-heading">About this measurement</h2>` (T13 binding). T10 uses `<h2 id="failures-findings-heading">` as a sibling H2 in the article-bottom area.

**Rationale for H2 over H3-under-methodology:**
- The failures section is **not** semantically nested under MethodologySummary's "About this measurement" content — it is a parallel article-bottom block presenting a different category of evidence (verbatim collection records vs. methodology summary prose).
- The §1.5.6 framing posture is that failures are **first-class** observations, parallel to (not subordinate to) the methodology note.
- Article structure: page `<h1>` (Header) → article `<h2>` (KeyFinding lead is typographically primary but does not use H2 in current implementation; visualizations are wrapped in a region — TSX inspection confirms no competing H2 in MDSPlot's region) → MethodologySummary `<h2>` "About this measurement" → **FailuresFindingsSection `<h2>` "Collection records and follow-up interviews"** (heading text per §2.5 below; CDA SME may revise).

**Section markup:**
```tsx
<section
  className="failures-findings"
  aria-labelledby="failures-findings-heading"
>
  <h2 id="failures-findings-heading" className="failures-findings__heading">
    {SECTION_HEADING}
  </h2>
  <p className="failures-findings__framing">{failuresData.framing_note}</p>
  <p className="failures-findings__counts" aria-live="polite">
    {countsCaption}
  </p>
  {records.length === 0
    ? <p className="failures-findings__empty">{EMPTY_CAPTION}</p>
    : <ol className="failures-findings__list">{records.map(...)}</ol>
  }
</section>
```

The `aria-live="polite"` on the counts caption is conservative — it announces the count once on first load and on domain switch; not on every accordion expand/collapse.

### §2.4. Three rendering levels per record + `framing_note` consumption + empty-state.

**`framing_note` consumption (binding):**
- Rendered verbatim as `<p className="failures-findings__framing">{failuresData.framing_note}</p>`.
- Coder MUST NOT paraphrase, abbreviate, line-break in mid-sentence, or split into multiple paragraphs.
- Coder writes a regression assertion: the rendered `<p>` text content equals `failuresData.framing_note` byte-for-byte after React's text-node escape (the verbatim string has no HTML — confirmed against the live `family.json` at line 7).
- **Defensive missing-field handling:** if `framing_note` is missing, empty, or not a string, T10 renders an error caption: `"Collection records are unavailable for this domain. (failures.{slug}.json is malformed.)"` in `--color-text-secondary` and suppresses the records list. This should never happen in production (T9 always emits the field with the binding string); it is defense-in-depth.

**Summary row (always visible) per record:** rendered as a `<details>` element with a `<summary>` child. The summary contains, in a single horizontal row:
1. A small badge identifying `record_type` (text: `"Collection failure"` for `"failure"`; `"Decline follow-up"` for `"decline_interview"`). Token-styled chip, no color encoding beyond `--color-surface` background + `--color-border` border.
2. The `model_id` in `--font-family-mono`.
3. The `collection_date` truncated to date-only (slice the first 10 characters of the ISO string).
4. The `originating_outcome_class` enum value verbatim (e.g., `empty_output`, `refusal_string_match`) in `--font-family-mono` — for `"failure"` records this is `null` (per T9 §2.4); the field is suppressed for null values.
5. A short truncated preview: the first 120 characters of `response_verbatim` (for decline_interview) or `error_message` (for failure), with ellipsis if longer. Plain text — no HTML, no markdown, no syntax highlighting. **The truncated preview is for at-a-glance scanning only.** The full text is in the expanded view.

**Expanded view (on `<details>` open):** native browser-rendered expansion of the `<details>` content. Renders, in this order, each in a labeled `<div>` block:

| Block label (LSB-authored) | Field | Notes |
|---|---|---|
| "Model" | `model_id` | already in summary; expanded for screen reader continuity |
| "Model version returned" | `model_version_returned` (decline_interview only; absent on failure records per T9 §2.4) | CLAUDE.md §9 pitfall #1 — distinct from `model_id` |
| "Provider" | `provider` (decline_interview only) | |
| "Collected at" | `collection_date` (full ISO timestamp; not truncated in expanded view) | |
| "Prompt version" | `prompt_version` (decline_interview only) | |
| "Originating step" | `originating_step` (decline_interview only) | |
| "Outcome class" | `originating_outcome_class` (decline_interview only) | |
| "Error type" | `error_type` (failure only) | |
| "Run index" | `run_index` (failure only) | |
| "Error message" | `error_message` (failure only) | full text, may be long; `<pre>` block with `white-space: pre-wrap; word-break: break-word` |
| "Follow-up prompt LSB sent" | `prompt_verbatim` (decline_interview; optional on failure per T9 §2.4) | `<pre>` block; verbatim sanitized model-facing text |
| "Model response" | `response_verbatim` (decline_interview; optional on failure) | `<pre>` block; verbatim sanitized output |
| "Reasoning trace (when provider surfaced it)" | `thinking_verbatim` (decline_interview; optional on failure) | `<pre>` block; rendered only when non-empty per T9 §2.4 |
| "Partial session" | `partial_session` (failure only, when present) | `<pre>` block, `JSON.stringify(value, null, 2)` |
| "Retry attempts" | `retry_attempts` (failure only, list, may be `[]`) | `<pre>` block of `JSON.stringify(value, null, 2)` when non-empty; suppressed when `[]` |

**No `data/raw/`-path internal IDs** are rendered. T9's §2.3 sanitization redacts these at publish time. T10 does not introduce any path-shaped rendering. Records carry `decline_interview_id`, `originating_informant_id`, `originating_failure_id`, `sha256_manifest` — these are opaque IDs and a SHA hash, not paths. They are surfaced in a small "Provenance IDs" sub-block at the bottom of the expanded view, in `--font-family-mono` with `--font-size-xs`, for researcher reproducibility (the SHA chain enables byte-identity verification per the open data bundle contract). LSB-authored block label "Provenance IDs."

**Block label text is LSB-authored prose and §1.5.4-bound.** The labels above are §1.5.4-compliant: descriptive, technical, no psychological attribution. CDA SME may revise wording.

**Empty-state handling** per T9 §2.5: the file is **always emitted** with `records: []` even for domains with zero records. T10 renders:
- The section heading.
- The `framing_note` paragraph verbatim.
- The counts caption: `"0 records published for this domain."`
- A no-records caption: `"No collection failures or follow-up interviews are published for this domain in this analysis version."` — §1.5.4-compliant, no defect framing, no "pending" / "missing" / "yet" / "placeholder" / "interim" language (CLAUDE.md §9 pitfalls #4 and #5).
- No `<ol>` is rendered. Skipping the empty list is intentional — an empty `<ol>` would announce as "list, 0 items" in some screen readers, which is noisier than the explicit caption.

**Defensive: failures.{slug}.json fetch failure.** If the fetch returns non-OK, T10 renders the section heading + a caption `"Collection records could not be loaded for this domain."` in `--color-text-secondary`. The `framing_note` is not rendered (T10 has no string to render — `framing_note` is not LSB-authored and there is no fallback string the Coder can invent). The section remains keyboard-focusable and screen-reader-accessible.

### §2.5. LSB-authored prose surface — exhaustive list for §1.5.4 review.

CDA SME reviews these strings. The Coder MUST place them in a single `apps/dashboard/src/copy/failures_findings.ts` file (precedent: `apps/dashboard/src/copy/methodology_summary.ts` from T13). One source of truth.

| Variable | Value | §1.5.4 reading |
|---|---|---|
| `SECTION_HEADING` | `"Collection records and follow-up interviews"` | Descriptive, technical, parallel to MethodologySummary's "About this measurement." No "failures," no "refusals," no defect framing. CDA SME may revise. |
| `RECORD_TYPE_LABEL.failure` | `"Collection failure"` | Naming the LSB-pipeline outcome, not the model. T9 verdict §4 confirmed `"failure"` is a positively reclaimed term in this project per the 2026-04-23 directive. CDA SME may revise. |
| `RECORD_TYPE_LABEL.decline_interview` | `"Decline follow-up"` | Naming the LSB-side workflow (a follow-up interview after a decline), not a model state-of-mind claim. CDA SME may revise. |
| `COUNTS_CAPTION_TEMPLATE` | `"{n_records} records published for this domain — {n_failure_records} collection failures and {n_decline_interview_records} follow-up interviews."` | Counts; technical. |
| `EMPTY_CAPTION` | `"No collection failures or follow-up interviews are published for this domain in this analysis version."` | First-class state per CLAUDE.md §9 pitfall #4. |
| `ERROR_FRAMING_MISSING` | `"Collection records are unavailable for this domain."` | Defensive error caption. |
| `ERROR_FETCH_FAILED` | `"Collection records could not be loaded for this domain."` | Defensive error caption. |
| `EXPAND_PROMPT_AT_REST` | (None — `<details>` summary holds the affordance; native browser disclosure triangle is the visual cue. No explicit "click to expand" string.) | — |
| Block labels in expanded view | "Model," "Model version returned," "Provider," "Collected at," "Prompt version," "Originating step," "Outcome class," "Error type," "Run index," "Error message," "Follow-up prompt LSB sent," "Model response," "Reasoning trace (when provider surfaced it)," "Partial session," "Retry attempts," "Provenance IDs" | Descriptive, technical. CDA SME may revise. |
| `framing_note` | Consumed verbatim from T9; not authored at T10. | — |

**Forbidden vocabulary spot-check the Coder applies before commit:** the strings `"worldview"`, `"believes"`, `"thinks"` (applied to models), `"How models see"`, `"What the model understands"`, `"cultural bias"` (standalone), `"refuses"` / `"refused"` (in any LSB-authored caption — model output is exempt), `"intends"`, `"intended to"`, `"missing"`, `"placeholder"`, `"no data yet"`, `"pending"`, `"yet to be"` MUST NOT appear in any T10 LSB-authored source string. The Reviewer's spot check enforces.

### §2.6. Accordion mechanism — **native `<details>`/`<summary>`** (not custom `aria-expanded` button).

**Decision: native `<details>`/`<summary>`.**

**Rationale:**
1. Native `<details>` is keyboard-accessible by default (Enter and Space toggle, focus styles inherit from `<summary>`).
2. Native screen-reader semantics: `<details>` announces as "disclosure widget" or similar; `<summary>` announces as the disclosure label; `aria-expanded` state is managed by the browser.
3. No custom click handler, no state management for open/closed, no `aria-expanded` attribute to sync — eliminates a class of bugs.
4. The Phase 6 functional-surface posture (memory `feedback_ui_polish_scope.md`) explicitly prefers native controls over hand-rolled accessibility plumbing.
5. The T0 InspectRoot scope constraint comment says "Do NOT add `<details>` collapse anywhere" — but that constraint is **scoped to InspectRoot only** (every row of every InspectTable renders inline so Mark can scan as flat tables). The constraint does NOT apply to the public dashboard. T10 explicitly uses `<details>` per this plan; the Reviewer should not conflate the T0 constraint with T10 scope.

**Styling restrictions:**
- The default browser disclosure triangle is acceptable; if visual consistency requires, the Coder may suppress it (`summary::-webkit-details-marker { display: none; }` + a custom inline glyph) — but this is a design polish concern that requires UI/UX explicit approval. **Default: keep the native triangle.**
- `<summary>` must satisfy WCAG 2.5.5 touch target (min 44×44px at `<768px` viewport widths). Padding tokens applied.
- `<details>` open state should NOT trigger any animation. The Phase 5 §12.1 reveal cascade is for page-load only; subsequent interactions do not animate (memory `feedback_ui_polish_scope.md`).

**Keyboard interaction inherited from native `<details>`:** Tab to focus the `<summary>`; Enter or Space to toggle. No additional keybindings.

### §2.7. Touch targets + mobile posture.

- `<summary>` elements: `min-height: 44px`, padding `var(--space-3) var(--space-4)` to satisfy WCAG 2.5.5 (Target Size — Minimum) at `<768px`.
- Container: flexbox or stack layout. No horizontal scroll. Long `<pre>` content uses `white-space: pre-wrap; word-break: break-word` to fit narrow viewports.
- Tested at 320px viewport width (the narrowest WCAG-supported mobile target).
- No mobile-specific layout treatment beyond the touch target floor and the `<pre>` wrapping — Phase 6 functional-surface posture.

### §2.8. InspectRoot integration — **extend with a `?inspect=failures-<slug>` mode.**

T0 (`?inspect=family|holidays|manifest`) did **not** cover failures. Grep confirms zero references to "failures" in `InspectRoot.tsx`. T10 adds a third inspect mode shape.

**Concrete change to `InspectRoot.tsx`:**
- The `InspectNav` array gains two entries: `{ slug: "failures-family", label: "Family failures" }` and `{ slug: "failures-holidays", label: "Holidays failures"}`. Generated dynamically from the manifest's `failures` map for forward compatibility.
- A new `FailuresInspectView` component renders the failures JSON as a flat `<InspectTable>` per the existing T0 precedent — every field, every record, no `<details>` collapse (per T0's scope constraint).
- The `?inspect=failures-family` mode reuses `fetchFailures(slug)` (the new API client function) — single source of truth for fetch.

**Rationale:** Mark's `feedback_inspection.md` memory says "Mark prefers direct inspection over Claude-mediated reads." Without an inspect mode, the only way to see all fields of every failure record is to drop to raw JSON; the inspect mode is the operator equivalent. Adding it now is small marginal work (one new component, one new InspectNav entry per failures-domain) and keeps T0's "every published field surfaces somewhere flat" promise honored after T9 added a new published file.

**Bundle cost:** approximately +0.5–1 KB gzipped. Counted toward T10's 8 KB cap.

The Coder writes a single `FailuresInspectView` that is shared between the public-facing section's optional "view as table" affordance (Phase 6 T8 territory — out of scope here) and the inspect mode. T10 uses it only for inspect mode; T8 may reuse the component when the table-toggle ships.

---

## §3. Acceptance criteria

The task is done when ALL of the following are true:

1. `cd apps/dashboard && npm run build && npm run test && npm run lint` passes locally.
2. Loading `<dev-server>/` on the `family` domain renders `<FailuresFindingsSection>` below `<MethodologySummary>` and above `<Footer>` with no console errors.
3. The `framing_note` paragraph renders **byte-identical** to `failuresData.framing_note`. The Coder writes a regression test asserting `<p>.textContent === framingNote`.
4. Both `record_type` values (`"failure"` and `"decline_interview"`) render correctly: the failure record's summary shows model_id + collection_date (truncated) + error_message preview; the decline_interview record's summary shows model_id + collection_date (truncated) + originating_outcome_class + response_verbatim preview.
5. Expanding any `<details>` shows the §2.4 block list for that record_type with all relevant fields, suppressing fields that are absent or `null` per T9 §2.4 (e.g., `originating_outcome_class` is suppressed on failure records where it is null; `partial_session` and `retry_attempts` are suppressed when absent or empty).
6. The empty-state case (a synthetic domain JSON with `records: []`) renders the section heading + `framing_note` + counts caption (`"0 records published…"`) + the no-records caption, and no `<ol>`. Tester covers via a synthetic fixture.
7. Each `<details>` element passes keyboard accessibility: Tab focuses the `<summary>`, Enter or Space toggles open/closed, and the focus indicator is visible at WCAG AA 3:1 contrast.
8. WCAG AA contrast: every LSB-authored text string in the section (heading, framing_note paragraph, captions, block labels, badge text) meets 4.5:1 against its background. Verbatim model output in `<pre>` blocks uses `--color-text-primary` on `--color-surface` (or equivalent existing token combination already verified at WCAG AA).
9. Touch targets: every `<summary>` element has computed `min-height: 44px` at `<768px` viewport width.
10. Mobile usable at 320px viewport width: no horizontal scroll; long `<pre>` content wraps; no layout breakage.
11. No forbidden vocabulary (CLAUDE.md §7; ARCHITECTURE.md §1.5.4) in any T10 LSB-authored source string. The `failures_findings.ts` copy module passes a Reviewer grep against the §2.5 forbidden list. Field names from the data and verbatim model output are exempt.
12. The Coder uses cast-through-unknown at the fetch boundary in `fetchFailures(slug)`. **The Coder does NOT touch `apps/dashboard/src/data/types.ts`** — T14 doc-sweep concern; Reviewer rejects T10 commits that modify it.
13. The Coder does NOT touch `cdb_core/schemas.py` (CLAUDE.md R6 not triggered).
14. The Coder does NOT touch `MDSPlot.tsx`, `FreeListCompare.tsx`, `SimilarityHeatmap.tsx` (does not yet exist post-T5 but the principle stands), `ModelSelector.tsx`, `KeyFinding.tsx`, `Header.tsx`, `Footer.tsx`, `DataExplorer.tsx`, `VizSwitcher.tsx`, `ArticleHeader.tsx`, `DomainPicker.tsx`, `MethodologySummary.tsx`.
15. The Coder DOES touch (surgical): `App.tsx` (insert FailuresFindingsSection + `!embedMode` guard), `app.css` (cascade nth-child(6/7) adjustment per §2.2), `api/client.ts` (add `fetchFailures`), `InspectRoot.tsx` (add failures-{slug} mode per §2.8), `InspectRoot`'s navigation array.
16. Reveal cascade: T10 renders at cascade slot 6 with 360ms delay; Footer moves to slot 7 (also 360ms). The §12.1 600ms total cap is preserved. Coder verifies via DOM inspection that the `nth-child` selector resolves correctly under the new ordering.
17. `?inspect=failures-family` and `?inspect=failures-holidays` render a flat table of every failure record's every field, mirroring the T0 precedent. The `?inspect=manifest` mode renders the existing manifest content unchanged; T10's `failures` map entry surfaces in the "Other top-level fields" safety net OR as a new dedicated InspectSection (Coder's call — both are acceptable).
18. Bundle delta ≤ 8 KB gzipped against the post-T7 baseline (T9 added zero bundle delta — backend only). Coder reports the measured delta in the commit body. Reviewer rejects if > 8 KB.
19. No new dependencies in `package.json`. No `react-router-dom`, no chart libraries, no markdown libraries (verbatim text is rendered as plain text — `<pre>` is the only special element).
20. The defensive missing-`framing_note` case renders the §2.5 `ERROR_FRAMING_MISSING` caption and suppresses the records list. Tester covers via a synthetic fixture omitting `framing_note`.
21. The defensive fetch-failed case (HTTP 404 / network error) renders the section heading + `ERROR_FETCH_FAILED` caption without crashing the page. Tester covers via a `fetchFailures` mock that rejects.
22. Reviewer rule R6 (`SECURITY_AND_HARDENING.md` §9) is not triggered — no `cdb_core/schemas.py` change; no `DATA_DICTIONARY.md` co-update required (T9 already documented the failures shape per its acceptance criterion 14).
23. CSP compliance: T10 introduces no `eval`, no inline `<script>`, no `dangerouslySetInnerHTML`. All verbatim text is rendered via React text nodes; `<pre>` content is set via `{string}` children, not via `dangerouslySetInnerHTML`. Reviewer R2 spot-check passes.

---

## §4. Known shape disagreements (Coder note, not a blocker)

The published `failures/{slug}.json` shape is documented in T9 §2.2 and §2.4. The Coder defines a local narrow interface in `FailuresFindingsSection.tsx` matching the live JSON, without touching `data/types.ts`:

```ts
// Local interfaces — NOT data/types.ts (T14 doc-sweep concern)
interface FailuresPublishedFile {
  domain_slug: string;
  generated_at: string;
  n_records: number;
  n_failure_records: number;
  n_decline_interview_records: number;
  framing_note: string;
  records: FailureRecord[];
}

interface FailureRecord {
  record_type: "failure" | "decline_interview";
  collection_date: string;
  model_id: string;
  domain_slug: string;
  originating_outcome_class: string | null;
  // Failure-only:
  error_type?: string;
  error_message?: string;
  run_index?: number;
  retry_attempts?: unknown[];
  partial_session?: Record<string, unknown>;
  // Decline-interview-only:
  decline_interview_id?: string;
  originating_informant_id?: string | null;
  originating_failure_id?: string | null;
  originating_step?: string;
  detection_rule_version?: string;
  model_version_returned?: string;
  provider?: string;
  api_endpoint?: string;
  prompt_version?: string;
  sha256_manifest?: string;
  prompt_verbatim?: string;
  response_verbatim?: string;
  thinking_verbatim?: string;
  input_tokens?: number;
  output_tokens?: number;
  latency_ms?: number;
  stop_reason?: string;
  qa_notes?: string;
  version_drift_flag?: boolean;
}
```

Cast through unknown at `fetchFailures`:
```ts
return (await response.json()) as unknown as FailuresPublishedFile;
```

**Forward compatibility:** if T9's published shape gains a new field in a future build (e.g., a `cost_usd` field — currently out of scope per T9 §5), the local interface remains intact (its field list is non-exhaustive). The Coder MUST NOT exhaustively narrow the type to forbid future fields. The "Other top-level fields" rendering safety net from T0's domain mode does NOT apply to T10's public-facing section (it is appropriate for operator surface; the public surface shows only the §2.4 known fields).

---

## §5. Out of scope for T10

Explicitly excluded; do not partially address:

- **A `/failures` standalone route** (Mark's option (b)). Foreclosed by the option (a) decision; not implemented.
- **Inline MDS marker annotations on failed/declined models** (Mark's option (c)). Most design-intensive of the three options; not selected. May resurface in Phase 7+ as a polish enhancement.
- **A "Read as table" toggle** for the failures section. T8 territory (DESIGN_SYSTEM.md §7 "Read as table" toggle). The `FailuresInspectView` component built in §2.8 may be reused by T8 when it ships; T10 does not wire that integration.
- **Client-side filter / search / sort** within the records list. Plain list only. Mark's `feedback_inspection.md` memory: inspect mode is the filter-and-search territory if needed; the public section is a contextual reader.
- **Pagination** within the section. Records render inline. If a future domain produces >200 records, a follow-up commit may add `<details>`-style grouping by `record_type` or `model_id`; out of scope now.
- **Hyperlinking the methodology page** from the section. Methodology page does not exist yet (T1/T2). T14 doc-sweep may wire the link when T1 ships.
- **Animation on `<details>` open/close.** Phase 6 functional-surface posture.
- **CSV / JSON export of the failures data.** The `?inspect=failures-{slug}` view + the raw JSON at `/data/failures/{slug}.json` are the export paths.
- **Touching `data/types.ts`.** T14 doc-sweep concern.
- **Touching `MDSPlot.tsx`, `FreeListCompare.tsx`, `ModelSelector.tsx`, or any other existing component beyond the surgical edits enumerated in acceptance criterion 15.**
- **Cost or token aggregation** (CLAUDE.md R14). T10 surfaces `input_tokens` / `output_tokens` / `latency_ms` per record in the expanded view (these are present on decline_interview records per T9 §2.4) but does NOT aggregate, sum, average, or display cost-derived statistics. The Reviewer's R13 check rejects any T10 PR that introduces aggregation.
- **A custom emoji or color encoding for `record_type`.** Plain text label + token-styled chip per §2.4.
- **Phase 8 launch hardening** — robots, CSP audit, security headers. Phase 8 territory.
- **A second Vite entry.** Single-entry SPA preserved.
- **`react-router-dom` or any router framework.** Phase 6 T1 owns that decision; T10 uses the existing query-param scheme (`?inspect=…`) unchanged.
- **Modifying the `<meta name="robots">` injection from T0.** Inspect mode keeps its `noindex` meta tag; the public-facing section is indexed normally (it lives on the canonical URL).

---

## §6. Gate routing

- **Architect:** this plan. On Mark's acceptance, the orchestrator dispatches the gates below.

- **CDA SME: REQUIRED.** Rationale: T10 introduces LSB-authored prose framing the verbatim model output — the section heading, the per-record-type label vocabulary, the empty-state caption, the error-state captions, the expanded-view block labels. The CDA SME's binding scope:
  1. **§2.5 LSB-authored prose surface** — all strings in `apps/dashboard/src/copy/failures_findings.ts`. Per-string §1.5.4 review. PASS / PASS-WITH-NOTES / FAIL per string or globally.
  2. **§2.4 `framing_note` consumption posture** — verify T10's verbatim consumption (no paraphrase, no abbreviation) honors the §5.1 binding from the T9 verdict.
  3. **§2.3 heading hierarchy** — H2 sibling vs. H3 nested. The CDA SME may prefer a single H2 ("About this measurement") with H3 children ("Methodology summary" + "Collection records and follow-up interviews") if it concludes the two sections are semantically subordinate to a unified methodology-frame block.
  4. **§2.4 truncated preview policy** — 120 characters of `response_verbatim` / `error_message` in the summary row. The CDA SME may flag this as risk of out-of-context partial quotes (a journalist reading the summary row without expanding the `<details>` could quote the truncated preview). Mitigation if flagged: lengthen, shorten, or remove the truncated preview; or require the summary row to disclose only the field name + length (`"response_verbatim, 312 chars"`).
  5. **§2.4 record_type label vocabulary** — `"Collection failure"` / `"Decline follow-up"`. CDA SME may revise.
  6. **§2.4 expanded-view block label vocabulary** — the 16 block labels (Model, Error type, etc.). CDA SME may revise.
  7. **§2.4 ERROR_FRAMING_MISSING and ERROR_FETCH_FAILED captions** — defensive error strings.
  - Four-axis verdict format per T5/T7/T9 precedent.
  - PASS → Coder dispatches after UI/UX PASS.
  - PASS-WITH-NOTES → notes apply at Coder dispatch; verdict saved to `docs/status/2026-05-12-phase6-T10-cda-sme-verdict.md`.
  - FAIL → re-plan.

- **UI/UX agent: light-touch only — accessibility floor + token consistency + WCAG AA contrast + mobile/touch.** Per `feedback_ui_polish_scope.md` memory. The UI/UX agent reviews:
  1. `<section>` has `aria-labelledby` pointing to the `<h2>` id.
  2. Heading order is correct (page `<h1>` → article-region content → MethodologySummary `<h2>` → FailuresFindingsSection `<h2>` as a sibling; no skipped levels within FailuresFindingsSection).
  3. Each `<details>` is keyboard-toggleable with visible focus indicator at ≥ 3:1 contrast.
  4. Touch targets on every `<summary>` are ≥ 44×44px at `<768px`.
  5. WCAG AA contrast: every LSB-authored text string meets 4.5:1 against its background. Verbatim text in `<pre>` blocks meets 4.5:1.
  6. Tokens only: no hardcoded colors, fonts, or spacings; everything via `var(--color-…)` / `var(--space-…)` / `var(--font-…)`.
  7. Mobile posture: usable at 320px viewport width; no horizontal scroll on the section container; `<pre>` content wraps.
  8. R10 concern: **N/A here** — failure records do not carry point estimates with paired uncertainty. The R10 binding is silent on this surface. (The orchestrator's plan prompt explicitly noted "no R10 concern here — failures don't have CI"; this is concurred.)
  - UI/UX issues PASS / PASS-WITH-NOTES / FAIL on these eight checks alone. **No design critique beyond them.** No "the page feels cluttered" verdict permitted.

- **Coder:** implements after CDA SME PASS (or PASS-WITH-NOTES with applied notes) AND UI/UX PASS (or PASS-WITH-NOTES with applied notes).

- **Reviewer:** standard nine-check sweep. Specific attention to:
  - R6: no `cdb_core/schemas.py` change; no `data/types.ts` change.
  - R10: §6 axis 8 above — confirmed N/A; do not reject for missing CI rendering on failure records.
  - R12 (§1.5.4 forbidden vocabulary): grep the §2.5 copy module against the forbidden list. Spot-check the rendered DOM via the vitest snapshot.
  - R13 (no spend-cap framing): grep the new files for `cost`, `$`, `usd`, `spend`, `budget`, `max_tokens`, `rate_limit` — and reject any aggregation or framing reintroducing the spend-cap posture. Verbatim model output containing dollar signs (a model explaining "an API key like $XXX") is exempt; LSB-authored aggregation is not.
  - R2: no `dangerouslySetInnerHTML`; all verbatim text rendered as React text nodes / `<pre>` children.
  - The `framing_note` byte-identity regression test passes.
  - Reviewer rejects any commit that touches `data/types.ts` or any of the 12 components enumerated in acceptance criterion 14.

- **Tester:** standard vitest. T10's testable surface:
  - `fetchFailures(slug)` happy path against a fixture file.
  - `fetchFailures(slug)` 404 path.
  - `FailuresFindingsSection` renders with mixed `record_type` records.
  - `FailuresFindingsSection` renders the empty-state case.
  - `FailuresFindingsSection` renders the missing-`framing_note` defensive case.
  - `FailuresFindingsSection` renders the fetch-failed defensive case.
  - The `framing_note` byte-identity assertion against the live `family.json` value (or a fixture matching it verbatim).
  - Keyboard interaction on `<details>` (Tab to focus, Enter / Space to toggle).
  - The `?inspect=failures-family` mode renders the flat table.
  - No real network fetches; fixtures only (CLAUDE.md R9).

---

## §7. Schema impact

| Touch point | Touched? | Co-update required? | Architect sign-off? |
|---|---|---|---|
| `cdb_core/schemas.py` | **No** | No | Not triggered |
| `apps/dashboard/src/data/types.ts` | **No** (T14 doc-sweep concern) | No | Not triggered |
| `docs/DATA_DICTIONARY.md` | No (T9 already documented the failures shape) | No | Not triggered |
| `ARCHITECTURE.md` | No (T14 doc sweep updates §1.5.6 if needed) | No | Not triggered |
| `DESIGN_SYSTEM.md` | No (T14 adds §12.x for FailuresFindingsSection codification; T10 does not pre-codify) | No | Not triggered |
| `apps/dashboard/src/App.tsx` | Yes — surgical insertion of FailuresFindingsSection + `!embedMode` guard | N/A | Not triggered |
| `apps/dashboard/src/styles/app.css` | Yes — cascade nth-child(6/7) adjustment | N/A | Not triggered |
| `apps/dashboard/src/api/client.ts` | Yes — add `fetchFailures(slug)` | N/A | Not triggered |
| `apps/dashboard/src/components/InspectRoot.tsx` | Yes — add failures-{slug} mode + nav entry | N/A | Not triggered |
| `apps/dashboard/src/components/FailuresFindingsSection.tsx` | New file | N/A | Not triggered |
| `apps/dashboard/src/components/FailureRecord.tsx` | New file (or fold into root — Coder's call per §2.3) | N/A | Not triggered |
| `apps/dashboard/src/components/FailuresInspectView.tsx` | New file (per §2.8) | N/A | Not triggered |
| `apps/dashboard/src/copy/failures_findings.ts` | New file (single source for LSB-authored strings) | N/A | Not triggered |
| `apps/dashboard/src/styles/failures-findings.css` | New file (token-only) | N/A | Not triggered |

**Architect sign-off needed for schema change: none** — T10 is schema-quiet.

---

## §8. Bundle budget watch

Post-T7 baseline: ~85 KB gzipped (T0 +4.16 KB + T7 estimated +5–7 KB). T9 added zero bundle delta (backend Python only).

T10 estimate:
- `FailuresFindingsSection.tsx` + `FailureRecord.tsx`: ~3–4 KB gzipped of TSX after tree-shaking.
- `FailuresInspectView.tsx` (per §2.8): ~1 KB gzipped.
- `failures_findings.ts` copy module: ~0.5 KB gzipped (strings only).
- `failures-findings.css`: ~1–2 KB gzipped.
- `App.tsx` edits: ~0.1 KB.
- `app.css` edits: ~0.05 KB.
- `api/client.ts` edits: ~0.2 KB.
- `InspectRoot.tsx` edits: ~0.3 KB (nav entry + dispatch case).
- No new dependency in `package.json` — zero bundle cost on the dep side.

**Expected delta: ~6–8 KB gzipped.** At the 8 KB ceiling Mark set for T10.

Phase 6 cumulative budget: 400 KB cap. Post-T10: ~91–93 KB total, ~23% of cap. Headroom preserved for T4/T5/T8/T11/T12/T13.

The Coder reports the measured delta in the commit body. Reviewer rejects if > 8 KB delta vs. post-T7 baseline.

---

## §9. Dependency order

**Upstream of T10:**
- **T9 (failures-as-findings data layer) — HARD DEPENDENCY.** T10 cannot dispatch until T9's JSON shape is published and `manifest.json` contains the `failures` map. **T9 shipped 2026-05-12 (commit `e3ade52`)** — dependency satisfied.
- T0 (operator inspection mode) — soft dependency for §2.8 InspectRoot extension. T0 shipped 2026-05-12 — satisfied.

**Downstream of T10:**
- T8 (`AccessibilityTableToggle.tsx` + `ScreenReaderSummary.tsx`) — may reuse `FailuresInspectView` as the table-format alternative for the public section.
- T14 (documentation sweep) — updates `ARCHITECTURE.md` §1.5.6 (the failures-as-findings UI surface), `DESIGN_SYSTEM.md` §11 component inventory (add `FailuresFindingsSection.tsx`), and adds a new §12.x subsection codifying T10's visual decisions.
- T1/T2 (methodology page) — when the methodology page ships, T14 wires a link from FailuresFindingsSection to the "How we handle refusals and declines" section.

**Parallel with T10:**
- T1 (methodology page skeleton), T2 (methodology page prose), T3 (drift data layer), T4 (DriftTracker), T5 (SimilarityHeatmap), T7 (FreeListCompare — in flight), T11 (mobile hamburger), T12 (mobile bottom-drawer). All independent of T10.

---

## §10. Risks and watch-items

1. **CDA SME revises section heading or block labels.** Probability: moderate. The §2.5 strings are Architect-proposed; the CDA SME may prefer different wording (e.g., heading "Records the LSB pipeline could not parse" or similar). All copy strings live in a single `failures_findings.ts` module so a verdict-driven revision is a one-file edit.

2. **CDA SME flags the truncated preview as a quote-out-of-context risk.** Probability: moderate. A 120-character preview of `response_verbatim` shown without expansion could be quoted as if it were the full response. Mitigation if flagged: lengthen to first sentence boundary (and add ellipsis at sentence boundary), or remove the preview entirely (summary row shows only `record_type` + `model_id` + `collection_date` + `originating_outcome_class`). The Coder defers to CDA SME notes.

3. **`framing_note` field drift between T9 and T10.** Low probability — T9's verdict §5.1 specifies the exact verbatim text and acceptance criterion 14 in T9's plan requires DATA_DICTIONARY.md documentation. The byte-identity regression test in T10 acceptance criterion 3 is the protection. If a future `cdb_publish` build changes the field's text without coordinated CDA SME re-review, the regression test fails and the Reviewer catches.

4. **The `<details>` native styling varies across browsers.** Safari, Firefox, and Chromium have slightly different default disclosure-triangle styles. Acceptable for Phase 6 minimum-viable; if UI/UX flags it, the Coder may suppress the marker with a `summary::-webkit-details-marker { display: none; }` rule and add an inline glyph — but that's a UI/UX-gated polish concern, not a default.

5. **Cascade re-indexing risk.** The §2.2 nth-child renumbering depends on the exact child count of `.reveal-cascade-item` instances in `App.tsx`. If a future task adds or removes a cascade item, the delays drift. Coder adds a comment in `app.css` near the nth-child block enumerating the current cascade order so future authors don't break it.

6. **InspectRoot scope-constraint comment** at `InspectRoot.tsx` lines 9–13 says "Do NOT add `<details>` collapse anywhere — all rows render inline." This applies to **InspectRoot only** (the operator surface; flat-tables-everywhere is Mark's binding directive). T10's `<details>` use in `FailuresFindingsSection` is NOT a violation. The Coder must not extend the InspectRoot constraint to FailuresFindingsSection. Coder adds a comment at the top of `FailuresFindingsSection.tsx` noting "this is the public surface; `<details>` is the chosen accordion mechanism per the T10 plan §2.6, distinct from InspectRoot's flat-table posture."

7. **Bundle creep from "just one more affordance."** The Coder MUST resist adding: per-record copy-to-clipboard buttons, JSON download buttons, search inputs, filter selects, sort controls, dark mode, custom transitions on `<details>`. T10 is a reader, not a tool. If T8's table-toggle pattern is desirable here, it ships at T8, not T10.

8. **Per-record key for React reconciliation.** The Coder uses a stable key per record. For decline_interview records: `decline_interview_id`. For failure records: the T9 deterministic identifier from `cdb_collect/decline_detection.py:_failure_id` is NOT exposed in the published JSON (T9 surfaces `originating_failure_id` only on decline_interview records). The Coder constructs a stable composite key for failure records: `` `failure|${model_id}|${run_index}|${collection_date}` ``. This mirrors the upstream identifier scheme without re-implementing it. If two failure records share that key (should not happen in practice; the source `failures.jsonl` uses timestamp-disambiguation), React will warn — Coder handles with `(model_id, run_index, collection_date, array_index)` as ultimate fallback.

9. **Empty-string `framing_note` vs. missing field.** Defensive handling treats both as the error case (renders `ERROR_FRAMING_MISSING`). The CDA SME may prefer different handling for the "empty string" case specifically; out-of-band clarification if requested.

10. **Mobile expanded view with long `thinking_verbatim` (multi-KB strings).** The `<pre>` blocks wrap; long content scrolls vertically within the section. Acceptable per the functional-surface posture. If performance becomes a concern with very long traces (>10 KB), a future commit may add lazy-rendering inside `<details>` — out of scope now.

---

*End of T10 plan.*

---

# Report back to Mark

**One-paragraph summary.**
T10 is the failures-as-findings UI surface, the public-facing consumer of T9's published JSON at `apps/dashboard/public/data/failures/{slug}.json`. A new `<FailuresFindingsSection>` component renders below `<MethodologySummary>` in `App.tsx` (option (a) — the orchestrator's binding proposal), one per active domain, consuming `failuresData.framing_note` verbatim (CDA SME §5.1 binding from T9) as the section's introductory paragraph. Each record is rendered as a native `<details>`/`<summary>` accordion with a summary row (`record_type` chip + model_id + truncated collection_date + truncated 120-char preview) and an expanded view containing every relevant field per T9 §2.4 (16 block-labeled sub-blocks), with verbatim model output in `<pre>` blocks. Empty-state case renders `framing_note` + a §1.5.5-compliant no-records caption. The `?inspect=failures-{slug}` operator mode is added to `InspectRoot` per Mark's `feedback_inspection.md` posture. Bundle budget ≤ 8 KB; no `data/types.ts` touch (cast through unknown); no `cdb_core` touch; no R10 concern (failure records carry no point estimate). CDA SME REQUIRED for the LSB-authored copy strings; UI/UX light-touch for accessibility + tokens + mobile.

**Entry-point decision rationale.**
Option (a) — per-domain `FailuresFindingsSection` below MethodologySummary — is selected as proposed. It follows the T13 MethodologySummary structural precedent (sibling H2 in the article-bottom area), keeps failures contextually attached to the domain the reader is exploring, requires no routing decision (avoids forcing T1 closure), and honors the `project_failures_are_findings.md` directive that failures be reviewable with raw logs in-context. The cascade slot extends to slot 6 (FailuresFindingsSection, 360ms) with Footer moving to slot 7 (also 360ms); §12.1's 600ms total cap is preserved.

**Component breakdown.**
- New: `/opt/lsb-agent/apps/dashboard/src/components/FailuresFindingsSection.tsx` (root component, fetches via `fetchFailures`)
- New: `/opt/lsb-agent/apps/dashboard/src/components/FailureRecord.tsx` (per-record `<details>` block — or folded into root if simpler; Coder's call)
- New: `/opt/lsb-agent/apps/dashboard/src/components/FailuresInspectView.tsx` (flat-table inspect view, shared with §2.8 inspect mode)
- New: `/opt/lsb-agent/apps/dashboard/src/copy/failures_findings.ts` (single source for LSB-authored strings; CDA SME reviews this file)
- New: `/opt/lsb-agent/apps/dashboard/src/styles/failures-findings.css` (token-only)
- Edited: `/opt/lsb-agent/apps/dashboard/src/App.tsx` (insert FailuresFindingsSection + `!embedMode` guard)
- Edited: `/opt/lsb-agent/apps/dashboard/src/styles/app.css` (cascade nth-child(6/7) renumber)
- Edited: `/opt/lsb-agent/apps/dashboard/src/api/client.ts` (add `fetchFailures(slug)`)
- Edited: `/opt/lsb-agent/apps/dashboard/src/components/InspectRoot.tsx` (add failures-{slug} dispatch case + nav entry)

Untouched: `cdb_core/schemas.py`, `apps/dashboard/src/data/types.ts`, `MDSPlot.tsx`, `FreeListCompare.tsx`, `ModelSelector.tsx`, `MethodologySummary.tsx`, `DataExplorer.tsx`, `VizSwitcher.tsx`, `KeyFinding.tsx`, `Header.tsx`, `Footer.tsx`, `ArticleHeader.tsx`, `DomainPicker.tsx`.

**Concerns needing Mark's attention.**

1. **§2.4 truncated preview policy.** The Architect chose 120 characters of `response_verbatim` / `error_message` in the summary row. This is a real CDA-SME-flag candidate (CDA SME §6 axis 4 of T10's review): a journalist reading the summary row without expanding could quote an out-of-context partial response. The plan documents three mitigation options (lengthen to sentence boundary, replace with field-name + length, remove entirely); CDA SME notes will land on one. **Not blocking dispatch** — the plan accommodates any of the three outcomes via the copy-module pattern.

2. **§2.3 heading hierarchy choice.** Architect chose H2 sibling of MethodologySummary's H2 — the failures section is parallel to (not subordinate to) the method note. If CDA SME prefers H3 nested under "About this measurement," the change is a 2-line edit in `FailuresFindingsSection.tsx` and a heading-text rewording. **Not blocking dispatch** — surfaced for CDA SME review at axis 3.

3. **§2.8 InspectRoot extension.** Architect chose to extend `?inspect=` with failures modes (`?inspect=failures-family`, etc.) for parity with T0's "every published field surfaces somewhere flat" promise. This is a soft Architect-decision; if Mark prefers to defer the inspect extension to a follow-up commit and ship T10 as public-section-only, that's a one-section deletion from the plan. **Not blocking dispatch** — surfaced here per the orchestrator's "verify whether T0 covers this; if not, T10 may add to InspectRoot too" note.

4. **The plan diverges from the orchestrator's "FailureRecord.tsx" component split** by offering Coder discretion to fold into the root component if simpler. The orchestrator's prompt said "or fold into root if simpler — Architect decides"; Architect's call is to let the Coder choose, since the split is a code-organization concern with no architectural significance. If Mark prefers an explicit binding split, that's a one-line plan amendment.

No other concerns. The T9 data contract is firm, the `framing_note` verbatim consumption is unambiguous, the §1.5.4 forbidden-vocabulary discipline carries forward from T7 and T9, and the bundle budget has headroom.