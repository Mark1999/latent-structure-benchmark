---
name: project-observatory-rename-verdict
description: OBSERVATORY-RENAME plan PASS-WITH-NOTES 2026-06-15 — public instrument rename Latent Structure Benchmark to Cognitive Structure Observatory; dashboard public-copy only; FROZEN strings byte-identical
metadata:
  type: project
---

# OBSERVATORY-RENAME — CDA SME verdict 2026-06-15

**Verdict:** PASS-WITH-NOTES. Authority: docs/status/2026-06-12-observatory-rename-decision.md.

## Scope

Public dashboard copy only: MethodologyPage / AboutPage / DataPage / NavBar.
FROZEN: minted bundle name "Latent Structure Benchmark (LSB) Open Data Bundle v1",
Zenodo DOI, B2/HF/GitHub URLs, SHA256, CITATION_FIRST_LINE test constant.
OUT OF SCOPE: cdb_* code, CLAUDE.md, ARCHITECTURE.md body (deferred internal sweep
per decision doc §4), data regeneration, CSS class names, test function names.

## Binding notes (apply during Coder pass)

**N1 (BINDING) — MethodologyPage line 114 swap.** Plan §4a left this as
SME-optional. Ruling: **swap to "The Observatory runs a version of that protocol
on language models, one prompt at a time."** Reason: bare-instrument-naming
prose mid-Section-2; leaving the only LSB token here makes the page read as
half-renamed. The §6.1 Section 2 forebears citations (Romney/Weller/Borgatti/
D'Andrade and DOI links) stay byte-identical.

**N2 (BINDING) — AboutPage paragraph 6 disclaim sentence.** What is protected by
M2-N1 is the cite-to-disclaim STRUCTURE ("does not claim that models have
beliefs, intentions, lived experience, or culture in the human sense"), not the
proper-noun subject. Substitution permitted: "The Observatory does not claim
that models have beliefs, intentions, lived experience, or culture in the human
sense." Comment block (AboutPage.tsx L32-38) AND test assertions
(AboutPage.test.tsx L73 + L91) MUST update in lockstep. If any of the three
diverges, FAIL.

**N3 (BINDING) — DataPage Section D added line wording.** Approved verbatim:
"The project is now the Cognitive Structure Observatory; the next bundle
version will adopt the new name. The v1 citation above is the minted bundle
name and remains the canonical citation for v1." No em dashes (semicolon +
period only). Placement: inside Section D, after the canonical-citation-target
sentence at L78, before the closing </section>. No other DataPage prose
changes.

**N4 (BINDING) — Optional framing fold-in scope.** If Architect/Coder folds in
the decision doc §"Candidate framing language" at MethodologyPage Section 1,
allowed sentences are ONLY those in the decision doc, byte-identical, em-dash-
substituted. No new measurement claims may enter under cover of "framing." If
in doubt, do the swap-only pass.

**N5 (BINDING) — failures_findings.ts LSB tokens stay.** Plan correctly
identifies these as pipeline-process classifications (LSB-as-classifier-actor),
a semantic role distinct from instrument-naming. The noun "LSB pipeline" / "LSB
parser-state" / "LSB request timeout" name the software pipeline, not the
public instrument. No edits in this file.

**N6 (ADVISORY) — internal-doc deferred sweep.** main.tsx file-header comment
and app.css file-header comment carry "LSB Dashboard" references. Out of scope
this commit per decision doc §4. When the deferred internal sweep runs, those
become "Cognitive Structure Observatory Dashboard" or similar. Note for
future-task safety: do NOT pre-emptively edit these in this pass.

**N7 (BINDING) — NavBar source-comment.** NavBar.tsx L9 ("Benchmark and data
remain primary") is a doc-comment naming a deferred internal token. If UI/UX
picks Option A (drop subtitle) or Option B (/ Observatory), the source comment
should also be refreshed in the same commit so the chrome and its self-
description do not diverge. UI/UX owns the exact comment wording.

## Four-axis scorecard

- Axis 1 Protocol validity: N/A (rule-15 freeze respected; no protocol code)
- Axis 2 Analytical validity: N/A (no analysis code touched)
- Axis 3 Claims validity: PASS (with N1-N4 applied)
- Axis 4 Audience translation: PASS (N5/N7 preserve pipeline-vs-instrument
  semantic distinction)
- Register compliance: PASS
- Vocabulary compliance: PASS (em-dash hook enforces; no §1.5.4 leaks)

## Routing

UI/UX gate next, then Coder. Live-DOM verification (A11) is load-bearing per
[[feedback_live_dom_verification]]. One commit per CLAUDE.md §8. Gate trail at
docs/status/2026-06-12-observatory-rename-verdicts.md.

Related: [[project_about_methodology_rewrite_0610]] (M1+M2 origin verdicts);
[[project_m2_about_page_verdict]] (M2-N1 cite-to-disclaim protection).
