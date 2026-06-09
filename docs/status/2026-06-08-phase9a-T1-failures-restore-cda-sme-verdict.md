---
filed: 2026-06-08
reviewer: CDA SME agent (Opus)
task: Phase 9a T1 — Restore failures-as-findings surface (placement change: top-level NavBar tab + domain selector)
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
scope: Re-affirmation under placement change. NOT a re-litigation of T9 / T10. All seven binding strings + S1–S7 carry-forward notes from `docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md` and `docs/status/2026-05-12-phase6-T10-cda-sme-verdict.md` remain in force at content level.
---

# Phase 9a T1 — CDA SME re-affirmation under top-level-tab placement

**VERDICT: PASS-WITH-NOTES**

The Architect's Phase 9a T1 plan restores the failures-as-findings surface
dropped by the 2026-05-25 rebuild, under Mark's 2026-06-08 directive that
relocates the surface from the bottom of an article page to a dedicated
top-level NavBar tab with its own domain selector. The plan correctly carries
the T9 §5.1 `framing_note` byte-identity contract and the T10 S1-S7 binding
copy forward verbatim. The placement change is methodologically benign and
arguably tightens §1.5.6 ("the website is the artifact" / failures are
first-class evidence) by elevating failures from a sibling of MethodologySummary
on one article view to a sibling of Explore / Methodology / Data in the global
nav.

Coder dispatch may proceed on this verdict with the four binding M-notes
below applied, plus the seven T10 binding strings (verbatim) and the T9 §5.1
`framing_note` byte-identity assertion already specified in the plan's §5
and §7-AC5.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS | The published JSON shape, the per-record audit trail (sha256_manifest, model_version_returned, prompt_verbatim of the decline-interview prompt), and the two-step protocol rendering (basic identity → LSB-authored follow-up prompt → model output → reasoning trace → provenance) are unchanged from T10. The Architect's plan §4 reaffirms each. The top-level-tab placement does not change which records are surfaced or in what order — same protocol artifacts, same fidelity floor. |
| Analytical validity | PASS | No Register 1/2/3 statistic is computed at this surface; failures carry no point estimate; the R10 uncertainty-floor rule is correctly N/A (no chart, no lede, no Smith's-S). The Architect's call that "no chart-lede involved" at plan §3 is correct. The sha256_manifest is preserved in the expanded view per the carried-forward T10 plan, preserving the byte-identity verification path against `data/raw/decline_interviews.jsonl`. |
| Claims validity | PASS-WITH-NOTES | The `framing_note` verbatim text in both `failures/family.json` and `failures/food.json` (read 2026-06-08) matches the T9 §5.1 binding string byte-for-byte; rendering it verbatim as the intro `<p>` directly below the tab's `<h1>`/`<h2>` is the correct claims-validity move and preserves the corpus-lens framing without re-litigation. The `originating_outcome_class` enum verbatim-in-mono rendering with no LSB-authored expansion is approved and carries the T9 §3 + T10 §2.6 reasoning forward unchanged. Four M-notes below operationalize the placement-change residuals (tab label, intro paragraph as page-level framing, no Explore-context leak). |
| Audience translation | PASS-WITH-NOTES | A reader landing directly on the Failures tab (e.g., via deep link or external referral) without first reading Methodology must still see the corpus-lens framing inside the tab's own header region. Because the `framing_note` is rendered verbatim as the first paragraph below the heading, this requirement is met as planned. The S1 quotation-pump defense (no verbatim model bytes in the summary row) carries forward unchanged. M1 below tightens the tab label / page heading so the chrome surrounding the framing_note does not pre-attribute. |

Register compliance: **PASS** — no register surface touched. No OCI, no
Romney CCM, no Procrustes, no Smith's-S lede. The plan's §3 ruling that
"a Smith's-S lede over failures is a category error" is correct and
unchanged from T10.

Vocabulary compliance: **PASS** with M1 binding (see §3.1). All seven T10
binding strings (`SECTION_HEADING`, `RECORD_TYPE_LABEL.failure`,
`RECORD_TYPE_LABEL.decline_interview`, `EMPTY_CAPTION`,
`ERROR_FRAMING_MISSING`, `ERROR_FETCH_FAILED`, summary-row field-shape
descriptor) remain in force and are §1.5.4-clean. The new chrome introduced
by the placement change (NavBar tab label, page heading H1 if separate from
the SECTION_HEADING H2, domain selector label) is scanned in §3.

---

## 2. Re-affirmation of T9 / T10 framing under the placement change

### 2.1. `framing_note` verbatim rendering — REAFFIRMED

Both `apps/dashboard/public/data/failures/family.json` and `food.json`
carry the T9 §5.1 verbatim string (byte-identical). The Architect's plan
§5 binds the Coder to render this string verbatim as the intro `<p>`
below the heading, with a byte-identity vitest assertion (AC5). This is
the correct §1.5 framing for the surface and is reaffirmed without
revision. The T9 §5.1 wording stands.

### 2.2. Classification-display (pitfall #13) — REAFFIRMED

The `originating_outcome_class` enum is rendered verbatim in `<code>`
mono with no LSB-authored human-readable expansion in either the summary
row or the expanded view's "Outcome class" block label. This preserves
the T9 §3 per-value compliance reasoning (each enum value names an
LSB-side detection rule, not a model state-of-mind), and the T10 §2.6
"verbatim enum forces the careful reading" rationale. Carry-forward
unchanged.

Badge labels `"Collection failure"` (red) / `"Follow-up interview"`
(neutral) per T10 S4a remain unchanged. They name LSB-pipeline outcome
categories, not model state. The Coder must not introduce variants
("Failed run," "Refusal," etc.) — the binding strings are the T10
strings, verbatim.

Pitfall #13 (input vs. output classification boundary) — N/A at this
surface. The T1 component reads pre-classified records from
`failures/{slug}.json`; it does not run any classifier. The detector role
boundary remains internal to `cdb_publish`.

### 2.3. Top-level-tab placement — REAFFIRMED, with M1 binding

The placement change from "bottom-of-article H2 sibling of
MethodologySummary" (T10) to "top-level NavBar tab sibling of Explore /
Methodology / Data" (Phase 9a T1, Mark directive) **does not weaken
§1.5.6**. Two routes of reasoning converge:

1. **Hierarchy reading.** T10's H2-sibling decision (T10 §2.4) was motivated
   by "failures are evidence parallel to the methodology context, not
   subordinate to it." A top-level tab is the strongest expression of
   that posture available in the rebuilt frontend's information
   architecture: failures are a peer of the model-comparison evidence
   (Explore), not nested inside it. This is consistent with the
   2026-04-23 directive ("failures are findings, not a debug log") and
   with §1.5.6 ("the website is the artifact" — the artifact's primary
   nav surface should expose its primary evidence categories).

2. **Discoverability.** A bottom-of-article placement is discoverable only
   by readers who scroll through a domain's Explore page. A top-level tab
   is discoverable from anywhere in the dashboard, including via direct
   URL. The latter is the stronger surface for "failures are first-class
   evidence."

The framing risk Mark flagged in the orchestrator's question — "could a
standalone Failures tab read as 'models failing' rather than 'the LSB
pipeline's output distribution includes non-parseable responses'?" — is
real but addressable at the chrome layer. The `framing_note` paragraph
is the primary defense (and is verbatim per §2.1 above). M1 below adds a
defense at the NavBar tab label + page heading layer.

### 2.4. Empty state for food — REAFFIRMED

`food.json` shows `n_records: 0`. The plan §4's "first-class, not a
defect" disposition with the T10 S2 verbatim caption is the correct
§1.5 framing. This is reaffirmed without revision. The Coder must render
the T10 S2 binding string byte-for-byte:

> **`"This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts."`**

No error icon, no greyout, no skeleton, no "coming soon," no "data not
yet available." The absence is the observation. AC9 in the plan covers
this; AC9's vitest assertion against the food fixture is the right
regression test.

### 2.5. LSB-authored chrome strings — REAFFIRMED with M1, M2, M3

All seven T10 binding strings remain in force and are §1.5.4-clean.
Block labels ("Prompt LSB sent" / "Model output to the follow-up prompt"
/ "Provenance") per T10 S4b + S6 remain in force. Counts caption template
per T10 §4 table row 4 remains in force. The new chrome introduced by
the placement change is scanned in §3 below.

---

## 3. Binding M-notes (apply at Coder dispatch)

### M1. NavBar tab label and page heading must not pre-attribute. [Audience translation, Claims validity]

The plan §3 says the tab label is `"Failures"`. The bare word "Failures"
on a top-level nav tab risks reading as "model failures" (a state-of-model
claim) rather than "LSB pipeline output records that did not produce a
parseable primary-step response" (the correct framing).

**Binding requirement.** Use one of these two tab-label strings; the
Coder picks one and applies consistently:

- **Option A (preferred):** `"Collection records"` — parallel to the T10
  SECTION_HEADING and names the LSB-pipeline artifact category.
- **Option B (acceptable):** `"Failures"` — short, positively reclaimed
  per the 2026-04-23 directive ("failures are findings"), but requires
  M2 below at the page-heading level.

If Option B is chosen for the NavBar tab, the **page heading inside the
tab MUST be the full T10 SECTION_HEADING string**
`"Collection records and follow-up interviews"` rendered as `<h1>` (or
the tab's top-level heading, whatever the rebuilt frontend's
heading-hierarchy convention is for tabbed pages). The page heading
expands the short tab label into the longer descriptive form.

Either way, the verbatim `framing_note` paragraph remains the first
content `<p>` below the heading. The Architect's plan §3 keeps this; M1
just constrains the chrome above it.

**Coder regression-test:** the NavBar tab label string and the page
heading string match the chosen option byte-for-byte.

### M2. Page heading inside the Failures tab. [Audience translation]

Independent of M1's option choice, the page heading rendered inside the
Failures tab must be `"Collection records and follow-up interviews"`
(the T10 SECTION_HEADING string), preserved verbatim. T10 specified this
as `<h2>` because it was a sibling of MethodologySummary's `<h2>` inside
an article view. Under the top-level-tab placement, the level shifts —
this is a tab's primary heading, not an article section heading.

**Binding decision:** the heading text is `"Collection records and
follow-up interviews"`, byte-for-byte. The HTML level (`<h1>` vs `<h2>`)
is a UI/UX concern, not a CDA SME concern; the UI/UX gate decides based
on the rebuilt frontend's per-tab heading-hierarchy convention. The
binding constraint is the text string, not the element name.

### M3. Domain selector label must not introduce psychological framing. [Audience translation]

The plan §3 says the Failures tab reuses the existing domain-picker
component. If the existing component has a label string (e.g., "Domain"
or "Select domain"), that string is approved as-is — it is a data
identifier surface, not prose. **If the placement change requires a new
label string adjacent to the picker** (e.g., "Show failures for:" or
similar), the Coder must use one of:

- `"Domain"` (matches the existing picker convention)
- `"Show records for"` (LSB-authored, no attribution)
- `"Domain shown"` (LSB-authored, no attribution)

**Forbidden adjacent strings:**
- `"Show failures from"` (treats models as the subject of "failures")
- `"Models that failed in"` (model-state attribution)
- `"Refusals in"` (forbidden enum-name in prose)
- `"Where models declined"` (cognition attribution)

If the existing domain-picker label is reused without revision, no new
string is introduced and M3 is satisfied trivially.

### M4. No leakage of Explore-context strings into the Failures tab. [Claims validity, Audience translation]

The Architect's plan §3 notes that UI/UX decides whether the Failures
tab defaults to the same domain currently selected in Explore or has its
own selector defaulting to family. Either choice is methodologically
fine, **but** if the tab inherits the Explore-tab's domain selection,
the Coder must NOT also inherit any Explore-tab chrome strings that
frame the domain in chart-lede language (e.g., "Showing family for
{model}" or "Family categorization across models").

**Binding requirement.** The Failures tab renders ONLY:
1. The page heading (M2: `"Collection records and follow-up interviews"`).
2. The verbatim `framing_note` paragraph.
3. The domain selector (M3-compliant label).
4. The counts caption (T10 §4 template, fed by the JSON's
   `n_records` / `n_failure_records` / `n_decline_interview_records`).
5. The records list or the empty-state caption (T10 S2).

Specifically, NO chart-lede string, NO Smith's-S string, NO
"this model categorizes" framing, NO consensus-score language, NO
"category map" language. The plan §3's "no chart-lede involved" rule
is binding at the tab level, not just at the records-rendering level.

**Coder regression-test:** the rendered Failures tab's text content
(excluding model verbatim bytes inside `<pre>` blocks) contains none of
the substrings: `"consensus"`, `"Smith's S"`, `"categoriz"` (without
`-pipeline` suffix), `"agree"`, `"believe"`, `"think"` (lowercased
match), `"worldview"`. (The T10 S1 quotation-pump defense already
prevents model bytes from appearing in summary rows.)

---

## 4. Vocabulary compliance scan on new placement-related chrome

| String | §1.5.4 reading | Verdict |
|---|---|---|
| Tab label `"Collection records"` (M1 Option A) | Technical/descriptive | Compliant |
| Tab label `"Failures"` (M1 Option B, requires M2 full-heading expansion) | Positively reclaimed pipeline-state term per 2026-04-23 directive | Compliant under M2 |
| Page heading `"Collection records and follow-up interviews"` (M2, T10 SECTION_HEADING verbatim) | Technical/descriptive | Compliant (carried forward) |
| Domain selector label (existing or M3-compliant) | Data identifier | Compliant under M3 |
| Counts caption template (T10 §4 verbatim) | Counts, technical | Compliant (carried forward) |
| Empty-state caption (T10 S2 verbatim) | First-class state | Compliant (carried forward) |
| All seven T10 binding strings | (carried forward unchanged) | Compliant |

No forbidden vocabulary detected in the placement-change-specific chrome
after M1-M4 are applied. **PASS** on vocabulary compliance.

---

## 5. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply at dispatch:**
  - M1: NavBar tab label is `"Collection records"` (preferred) or `"Failures"` (acceptable only with M2 full-heading expansion).
  - M2: Page heading inside the Failures tab is `"Collection records and follow-up interviews"` (T10 SECTION_HEADING verbatim; HTML element level is UI/UX call).
  - M3: Domain selector label is the existing picker label, OR one of `"Domain"` / `"Show records for"` / `"Domain shown"`. Forbidden adjacent strings listed.
  - M4: No Explore-tab chrome strings leak into the Failures tab. Forbidden substrings listed for the chrome regression-grep test.
  - **Plus all binding strings + carry-forward notes from T9 §5.1 + T10 S1-S7** (referenced in the plan §10 and §5, unchanged).
- **`framing_note` verbatim assertion:** APPROVED (already in plan AC5). Both `family.json` and `food.json` carry byte-identical T9 §5.1 strings.
- **Empty-state caption (food, n_records=0):** APPROVED first-class framing with T10 S2 binding string verbatim.
- **`originating_outcome_class` rendering:** verbatim in `<code>` mono, no LSB-authored expansion in either summary row or expanded view. Carried forward unchanged.
- **Badge labels:** `"Collection failure"` / `"Follow-up interview"` per T10 S4a — carried forward unchanged.
- **Block labels:** `"Follow-up prompt LSB sent"` / `"Model output to the follow-up prompt"` / `"Reasoning trace the provider surfaced"` / `"Provenance IDs"` per T10 S4b + S6 — carried forward unchanged.
- **`cdb_core/schemas.py` change required:** No.
- **T14 doc-sweep flag raised:** No new flag; the existing T9 §5.2 + T10 S3 + T10 S7 flags (methodology-page link wiring from the framing_note "See the methodology page" string and from the "Outcome class" block label) remain open and unaffected by the placement change.
- **Mark escalation:** None required. The placement change is Mark's directive; M1-M4 are operationalizations, not new architectural decisions.

---

*End of Phase 9a T1 CDA SME re-affirmation verdict.*
