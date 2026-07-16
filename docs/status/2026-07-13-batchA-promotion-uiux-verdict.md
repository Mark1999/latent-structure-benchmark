# UI/UX Verdict: Batch A Promotion Frontend (runbook Step 5 copy pass)

**Date:** 2026-07-13
**Reviewer:** UI/UX agent (persisted by orchestrator; agent session had no write access)
**Scope:** Public dashboard surfaces for the batch A promotion: MethodologyPage (BA-QA-FN
section, F3-V3-E footnote), DataPage (BA-PROV, BA-TERMMAP-COUNTS), FailuresFindings
(six Fable disclosure placements), ContentArea (food v0.3 override badge + deep link),
consensus_disclosure.ts constant versioning, ProvenanceFooter.
**Bound strings:** CDA SME verdict docs/status/2026-07-13-batchA-promotion-cda-sme-verdict.md
(strings not editable by this gate).

---

UI/UX VERDICT: PASS-WITH-NOTES

1. OWID design fidelity:      PASS
2. 30-second journalist:      PASS
3. Researcher cite path:      PASS
4. WCAG AA:                   PASS

DESIGN_SYSTEM.md update:      required
Version bump: v0.25.0. Adds section 25 (batch A promotion copy patterns).
Updates section 6.1 (methodology page section inventory), section 19
(FailuresFindings Fable disclosure pattern as section 19.20), and section 23.2
(consensus_disclosure.ts versioning convention). No new tokens. No new CSS
classes (Fable disclosure reuses existing .failures-findings__impact). The
Coder applies the spec texts in the rulings below verbatim to DESIGN_SYSTEM.md
before implementing anything else.

---

## Findings (pre-ruling basis)

No new visualization types introduced. The CI/badge/disclosure patterns established
at section 23 (v0.23.0) are extended but not redesigned. All color references verified
against tokens.css: the Fable disclosure reuses --color-text-primary via
.failures-findings__impact, WCAG compliant at ~7:1. The QA footnote reuses
.methodology-page__text, also compliant. --color-surface-note exists and is unused by
these placements (no new callout box needed; inline flow is sufficient). No phantom
var(--...) references introduced.

The food v0.3 badge deep-link update from #food-v02-footnote to #food-v03-footnote is
the U3 one-click path. Retaining the v0.2 anchor byte-identical satisfies the
researcher-cite test: any prior citation to /methodology#food-v02-footnote continues
to resolve.

The six Fable placements all use existing class .failures-findings__impact in inline
reading-order position above the relevant records group. Inline flow is programmatic
association under WCAG 1.3.1 (the disclosure precedes the rows it describes in DOM
order; no aria-describedby required when the relationship is established by reading
order and visual proximity).

## Enumerated rulings

**Ruling 1. BA-QA-FN placement and heading.**
Elect option (b): standalone section between "Uncertainty and failure" and "What this
does not measure." Rationale: QA calibration is a measurement-system property, not a
core-protocol step; the sequence uncertainty -> QA calibration -> scope is the natural
reading order for a skeptical reader. Markup: section with
aria-labelledby="informant-class-qa-calibration-heading", h2
id="informant-class-qa-calibration-heading" className="methodology-page__heading" text
"Informant-class QA calibration", BA-QA-FN verbatim in one
p.methodology-page__text. Reading order: after section
uncertainty-and-failure-heading, before section what-this-does-not-measure-heading.
DESIGN_SYSTEM.md section 6.1 inventory gains this entry between sections 5 and 6.

**Ruling 2. F3-V3-E anchor treatment.**
Both anchors coexist. The v0.2 paragraph (id="food-v02-footnote") is retained verbatim
for citation stability. The v0.3 paragraph gets id="food-v03-footnote". The
ContentArea.tsx badge deep-link is updated from /methodology#food-v02-footnote to
/methodology#food-v03-footnote. The FOOD-FIX-A mode-coherent paragraph directly above
receives the "at v0.2" scoping phrase (no SME pass needed per the SME verdict).
Paragraph order in food-methodology-footnotes: FOOD-FIX-A (scoped), food-v02-footnote
(retained), food-v03-footnote (new, F3-V3-E verbatim). DESIGN_SYSTEM.md gains
section 23.4: versioned methodology footnote anchors; each food-domain analysis version
has its own id="food-v{NN}-footnote" paragraph; prior-version paragraphs are never
removed; the override badge deep-link always targets the current-version anchor.

**Ruling 3. Fable-5 disclosure markup pattern.**
Two new exports in apps/dashboard/src/copy/failures_findings.ts:
FABLE_DISCLOSURE_FRAMING (BA-FABLE-FRAMING verbatim) and FABLE_DISCLOSURE_BOUND
(the 2026-07-10 (d) bound string verbatim). One shared FableDisclosureNote functional
component in FailuresFindings.tsx rendering the two strings as two
p.failures-findings__impact paragraphs (framing first, bound string second).
Failures surface: render immediately before the failures records list when
data.records has any model_id === 'claude-fable-5', after the counts caption and
before the first record, visible on first render without scroll. Records surface:
render immediately before the summary table when by_model has any
model_id === 'claude-fable-5'. Conditional check is model_id equality, not a
hardcoded domain name. CSS reuse .failures-findings__impact (tokens confirmed
present in tokens.css). DESIGN_SYSTEM.md gains section 19.20: behavioral-context
disclosure note pattern, conditional on model_id presence in fetched data, visible on
first render, no interaction required.

**Ruling 4. DataPage paragraph swaps.**
No structural change. The paragraph in section data-provenance-heading is replaced with
BA-PROV verbatim; the provenance.json anchor markup preserved exactly (href, target,
rel, className, sr-only span, trailing " (JSON)"), integrated inline at the sentence
ending "...recorded in provenance.json, which is regenerated on every published
bundle." The second sentence in section term-mds-heading is replaced with
BA-TERMMAP-COUNTS verbatim; the first sentence is untouched.

**Ruling 5. consensus_disclosure.ts constant naming.**
Rename CI_DISCLOSURE_TEXT to CI_DISCLOSURE_TEXT_V02 (assertion byte-identity to
F3-R3-C unchanged). Add CI_DISCLOSURE_TEXT_V03 with F3-V3-C verbatim. SMALL_N_TEXT
unchanged (no rename, no version suffix; SME ruling C keeps it dormant).
ContentArea.tsx renders CI_DISCLOSURE_TEXT_V03. Test promote-food-v02-strings.test.tsx:
T2a import renamed to _V02; add T2a-v3 (byte-identity of _V03 to F3-V3-C); extend
em-dash guard to F3-V3-C; T2b unchanged; T2d updated to assert _V03 renders in
ContentArea when consensus_type_override is set; T2f unchanged (food-v02-footnote
byte-identity to F3-R3-E); add T2f-v3 (food-v03-footnote renders, text normalizes to
F3-V3-E). DESIGN_SYSTEM.md section 23.2 gains the _V{NN} suffix convention: prior
versioned constants retained for citation stability; ContentArea always imports the
highest-version constant in active use; tests assert byte-identity per versioned
constant independently.

**Ruling 6. ProvenanceFooter.**
No code change needed. The component reads generated_at_utc and domains from
/data/provenance.json dynamically (section 15.5(b), v0.12.0); the regenerated
provenance.json (2026-07-12, family/holidays/food present) renders correctly from
existing code.

## Required before merge

1. DESIGN_SYSTEM.md updated to v0.25.0 with section 25, section 6.1 amendment,
   section 19.20, section 23.2 and section 23.4 amendments exactly as specified.
2. QA calibration section inserted at the exact DOM position specified.
3. id="food-v02-footnote" paragraph retained byte-identical; new
   id="food-v03-footnote" paragraph with F3-V3-E verbatim; badge deep-link updated.
4. FableDisclosureNote renders on both surfaces for all three domains when
   claude-fable-5 is present in fetched data (model_id equality check).
5. CI_DISCLOSURE_TEXT renamed to _V02; _V03 added with F3-V3-C verbatim;
   ContentArea imports _V03.
6. Test updates per ruling 5.
7. Reviewer grep: no var(--font-size-md) in any new JSX; no bare CI_DISCLOSURE_TEXT
   reference remains (only _V02 and _V03).
