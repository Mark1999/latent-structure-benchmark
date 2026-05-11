---
filed: 2026-05-11
reviewer: CDA SME agent (Opus)
task: Phase 5 T13 — methodology summary prose
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 5 T13 — CDA SME verdict on the MethodologySummary prose

**VERDICT: PASS-WITH-NOTES**

The verbatim prose below is binding source text for `apps/dashboard/src/copy/methodology_summary.ts`. The Coder ports it without paraphrase. The PASS is conditional on the carry-forward notes in §5 being honored (tagline imported, not re-typed; footnote rendered conditionally; caption-token contrast for the footnote per T10 precedent).

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS | Names the three CDA elicitation steps (free-list, pile-sort, rating) without dumping acronyms. "Comparison-by-protocol" framing is implicit in "applied to each model on identical prompts." Does not overclaim what the protocols recover from a non-human informant. |
| Analytical validity | PASS | The MDS plot is described as a positional summary of categorical-divergence distances between models; bootstrap ellipses are named as measurement uncertainty (R10). Romney CCM small-n caveat is not asserted as a finding because the prose is at the methodology-summary level, not the per-domain analytical-layer level (the n<15 caveat surfaces on the analytical-layer copy in T2/T6, not here). This is the correct level of abstraction for the summary block. |
| Claims validity | PASS | No model-belief, model-cognition, or worldview language. The corpus-lens five-link chain (corpus → training → alignment → decoding → output distribution per §1.5.1) is named accurately and compressed into one sentence. No cross-domain generalization claim. Affirmative framing: states what the dashboard does measure, not what it does not. |
| Audience translation | PASS | A journalist skimming for 30 seconds gets: (a) what is measured, (b) why model-to-model, (c) that uncertainty is shown. A researcher considering citation gets: (a) the elicitation protocols by name, (b) the corpus-lens construct, (c) the exploratory posture per §1.5.7, (d) a path to the full methodology page in Phase 6. OWID-tone present-tense plainspoken prose; no marketing intensifiers. |

Register compliance: PASS. Vocabulary compliance: PASS (scan in §4 below).

## 2. The verbatim prose (FOR CODER IMPORT)

```typescript
// apps/dashboard/src/copy/methodology_summary.ts
//
// Single source of truth for the methodology summary block (T13).
// SME-approved on 2026-05-11; do not edit without CDA SME re-review.
// See docs/status/2026-05-11-phase5-T13-cda-sme-verdict.md.

import { TAGLINE } from "./framing";

/**
 * Methodology summary prose — rendered below the data explorer per
 * DESIGN_SYSTEM.md §2.1. Max-width 680px. Present-tense, OWID-style.
 *
 * Sources: ARCHITECTURE.md §1.5.1 (corpus-lens five-link chain),
 * §1.5.4 (language guardrails), §1.5.7 (exploratory framing),
 * §4.2.6 / §4.5 (bootstrap uncertainty).
 */
export const methodologySummary = `Cultural Domain Analysis (CDA) is a family of elicitation protocols developed in cognitive anthropology to recover how informants organize the items in a domain. LSB applies three of those protocols — free-list (what items belong in a domain), pile-sort (which items group together), and rating (how items rank on a given dimension) — to large language models, on identical prompts, as if each model were an informant. What this surfaces is the corpus lens: the categorical structure of the model's training data, refracted through training, alignment, decoding, and the output distribution that the model samples from. The map below positions each model by how its outputs categorize the domain relative to every other model in the slate; closer points indicate more similar categorical structure, and the shaded ellipses show the measurement uncertainty around each position from bootstrap resampling. Comparisons are model-to-model by design — every domain in v1 is a comparison across the model slate, not against a human reference — and the protocol is held fixed so differences in the map reflect differences between models rather than differences in how each was asked. The originating question is exploratory: what comes out when you give a large language model a CDA elicitation? LSB answers that question precisely, reproducibly, and at scale across models and time, and releases the verbatim prompts, the verbatim responses, and the analytical code so others can interpret the results on their own terms.`;

/**
 * Footnote — placeholder for the (Phase 6) full methodology page link.
 * Render conditionally: if the Phase 6 page URL is not yet live,
 * render the "coming in Phase 6" form; once the URL is set in
 * site config, swap to a live link. Use caption-token contrast
 * (--color-text-caption) per T10 precedent.
 */
export const methodologyFootnote = `A full methodology page — covering the CDA protocols in detail, the measures shown on the dashboard (Smith's S, Romney CCM, MDS, Procrustes, OCI), the bootstrap procedure, and academic credit to Romney, D'Andrade, Weller, Borgatti, and Batchelder — is coming in Phase 6.`;

/**
 * The verbatim tagline, re-exported here for inline placement at the
 * head of the methodology summary block. The canonical value lives in
 * copy/framing.ts; this re-export exists only so MethodologySummary.tsx
 * can import a single object. The Coder MUST verify at build time that
 * this string equals framing.TAGLINE (a unit test asserting equality
 * keeps the single-source-of-truth invariant honest).
 */
export const taglineQuote = TAGLINE;
```

Sentence count of `methodologySummary`: 6 sentences (within the 5–7 budget).

## 3. Rationale + sources (per sentence)

**Sentence 1** — "Cultural Domain Analysis (CDA) is a family of elicitation protocols developed in cognitive anthropology to recover how informants organize the items in a domain."
*Source:* `ARCHITECTURE.md` §4.1 (CDA pipeline overview) and §1.5.1 (the methodology is imported from cognitive anthropology). Anchors the discipline of origin and names the construct ("organize the items in a domain") without claiming the model has cognition. "Recover how informants organize" is standard CDA phrasing.

**Sentence 2** — "LSB applies three of those protocols — free-list (what items belong in a domain), pile-sort (which items group together), and rating (how items rank on a given dimension) — to large language models, on identical prompts, as if each model were an informant."
*Source:* `ARCHITECTURE.md` §4.1.1 (three-step CDA elicitation; the LSB textual pile sort and the comparison-by-protocol method). The parenthetical glosses keep the prose intelligible to a journalist without dropping the protocol names. "As if each model were an informant" reproduces the load-bearing "as-if" from §1.5.1 explicitly.

**Sentence 3** — "What this surfaces is the corpus lens: the categorical structure of the model's training data, refracted through training, alignment, decoding, and the output distribution that the model samples from."
*Source:* `ARCHITECTURE.md` §1.5.1 corpus-lens five-link chain (corpus → training → alignment → decoding → output distribution). All five links are named in order. "Corpus lens" is introduced as the plain-language term, then immediately unpacked, satisfying the §1.5.1 binding rule that the methodology context use the long form (or define the short form on first use).

**Sentence 4** — "The map below positions each model by how its outputs categorize the domain relative to every other model in the slate; closer points indicate more similar categorical structure, and the shaded ellipses show the measurement uncertainty around each position from bootstrap resampling."
*Source:* `ARCHITECTURE.md` §4.2.6 (bootstrap procedure) and §4.5 (no point estimates without uncertainty in any visualization; R10 binding). Names the MDS plot as a positional summary, names the ellipses as measurement uncertainty, names bootstrap resampling as the source. Avoids "consensus" framing entirely at this level (correctly: the dashboard's MDS plot is the Register 2 between-model positional summary, and the ellipses are bootstrap-derived).

**Sentence 5** — "Comparisons are model-to-model by design — every domain in v1 is a comparison across the model slate, not against a human reference — and the protocol is held fixed so differences in the map reflect differences between models rather than differences in how each was asked."
*Source:* `ARCHITECTURE.md` §1.5.5 (human grounding removed from v1; every domain is permanently model-to-model) and §1.5.3 #1 (prompts held fixed across models within a run). Frames the model-to-model design affirmatively ("by design"), not as an absence or interim state — this is the §1.5.5 binding stance and the Pitfall 4 guardrail. Explicitly names the protocol-fixed control without overpromising.

**Sentence 6** — "The originating question is exploratory: what comes out when you give a large language model a CDA elicitation? LSB answers that question precisely, reproducibly, and at scale across models and time, and releases the verbatim prompts, the verbatim responses, and the analytical code so others can interpret the results on their own terms."
*Source:* `ARCHITECTURE.md` §1.5.7 (exploratory framing — LSB does not test hypotheses) and §1.5 honest-tagline block. Reproduces the exploratory posture verbatim in spirit (lightly compressed: "free-list / pile-sort / interview" → "a CDA elicitation" because the protocols are already named in sentence 2; quoting the long form here would be redundant). The closing clause names the open-data release per `ARCHITECTURE.md` commitment 9 and §6.7, satisfying §1.5.7's "release the information to the community for their own analysis" requirement.

**Footnote rationale.** Names the measures that the full methodology page will cover (Smith's S, Romney CCM, MDS, Procrustes, OCI) and the academic-credit roster (Romney, D'Andrade, Weller, Borgatti, Batchelder) per `ARCHITECTURE.md` §1.5.5 closing paragraph and `DESIGN_SYSTEM.md` §6.1 item 2. Phrased as "coming in Phase 6" not "todo" or "placeholder" — the Phase 6 deliverable is committed per §1.5.6 (the methodology page deserves a dedicated session with Mark) and `PHASE_0_TASKS.md` phase plan.

## 4. Forbidden vocabulary scan

Scanned `methodologySummary` + `methodologyFootnote` against the `ARCHITECTURE.md` §1.5.4 guardrails table and the `CLAUDE.md` §7 table:

| Forbidden phrase | Present? |
|---|---|
| "believes" / "thinks" / "worldview" (applied to models) | No |
| "How models see the world" | No |
| "What the model understands" | No |
| "Cultural bias" (standalone) | No |
| "Within-model consensus" / "Within-model CCM" / "Within-model eigenratio" | No |
| "LSB hypothesizes" / "LSB tested whether" / "LSB confirms" / "LSB predicted X and the data confirmed/refuted" | No |
| "publishable" / "groundbreaking" / "powerful" / "first-of-its-kind" | No |
| "closer to human = better" framing | No (model-to-model is named as design, not as fallback) |
| Specific model names | No |
| Cross-domain generalization claim | No |
| Cost/spend framing | No |

PASS on vocabulary.

## 5. Carry-forward to Coder

1. **Import paths.** `MethodologySummary.tsx` imports the three constants from `copy/methodology_summary.ts`. `methodology_summary.ts` in turn imports `TAGLINE` from `copy/framing.ts` and re-exports it as `taglineQuote`. The single source of truth for the tagline string remains `framing.ts`; `methodology_summary.ts` re-exports rather than re-types.

2. **Tagline placement in the rendered block.** The tagline appears as a **separate paragraph at the head of the MethodologySummary**, set in a slightly larger pull-quote style (UI/UX agent owns the visual treatment per `DESIGN_SYSTEM.md`). The six-sentence prose body follows as the main paragraph. The tagline is *not* inlined inside the body — it functions as the orienting hook above the methodology paragraph, mirroring the `ArticleHeader` subtitle treatment per T13 acceptance criterion 2 (single source of truth, appears verbatim in both `ArticleHeader` and `MethodologySummary`).

3. **Tagline equality test.** A unit test (`apps/dashboard/src/copy/methodology_summary.test.ts` or equivalent) MUST assert `taglineQuote === TAGLINE`. This keeps the single-source-of-truth invariant honest as the codebase evolves — a future hand-edit that diverges the two strings fails the test.

4. **Footnote rendering — conditional.** The footnote should render with the "coming in Phase 6" wording for Phase 5 launch. Once a Phase 6 methodology page URL exists, replace the standalone footnote with a link element pointing to it, keeping the same caption styling. Suggested pattern: a `methodologyPageUrl: string | null` prop on `MethodologySummary` — `null` renders the footnote as plain text, a string renders it as an inline link with the URL on the word "methodology page" or as a trailing "Read the full methodology page →" link. The UI/UX agent owns the exact treatment; the prose is fixed.

5. **WCAG AA contrast for the footnote.** Per T10 caption-token precedent, the footnote text uses `--color-text-caption` (not `--color-text-body`) since it is auxiliary metadata, not primary content. Verify contrast ratio ≥ 4.5:1 against `--color-bg-article` in light mode and dark mode. The link variant of the footnote uses `--color-link` per `DESIGN_SYSTEM.md` link tokens; underline on hover.

6. **No paraphrase.** The six sentences and the footnote are binding source text. The Coder ports verbatim — typo fixes, ASCII-quote normalization, or Prettier-driven whitespace are fine; word changes are not. If the Coder spots a needed change (e.g., a fact has shifted between this verdict and merge), pause and re-route to the CDA SME rather than self-editing.

7. **Reading-list reminder for the Coder.** Before integration, the Coder reviews `ARCHITECTURE.md` §1.5.1 (so the corpus-lens five-link chain in sentence 3 is recognized as the load-bearing passage), §1.5.5 (so the model-to-model framing in sentence 5 is understood as design, not fallback), and §1.5.7 (so the exploratory framing in sentence 6 is not softened in adjacent UI copy).

8. **Sentence count is intentional.** Six sentences is one inside the 5–7 budget; this gives the UI/UX agent room to add a one-sentence Phase-6 callout in the visual layout (e.g., as the lead-in to the footnote) without pushing the block over the budget. If the UI/UX agent's visual treatment needs the prose itself extended, that requires a CDA SME re-review.

## 6. Approval

**PASS-WITH-NOTES.** The verbatim prose in §2 is approved for verbatim port to `apps/dashboard/src/copy/methodology_summary.ts`. The five carry-forward notes in §5 are binding on the Coder integration step; Reviewer enforces them at PR review (especially #2 paragraph-not-inline placement, #3 equality test, #4 conditional footnote rendering, #5 caption-token contrast).

No FAIL. No methodological re-work required. Phase 5 T13 unblocks at the Coder step.

— CDA SME agent (Opus), 2026-05-11
