# OBSERVATORY-RENAME — gate verdicts

**Task:** Public dashboard copy rename, "the Latent Structure Benchmark" to "the Cognitive Structure Observatory."
**Authority:** `docs/status/2026-06-12-observatory-rename-decision.md` (Mark, 2026-06-12). Target name confirmed by Mark 2026-06-16.
**Scope:** Public dashboard copy only (MethodologyPage, AboutPage, DataPage, NavBar) plus their tests and a DESIGN_SYSTEM.md changelog bump. FROZEN: minted bundle name, Zenodo DOI, B2/HF/GitHub URLs, SHA256, `CITATION_FIRST_LINE`. Out of scope: `cdb_*` code, `CLAUDE.md`/`ARCHITECTURE.md` body, CSS class/test-function names, `failures_findings.ts` LSB pipeline-actor tokens.

---

## CDA SME — PASS-WITH-NOTES (2026-06-15)

Full record: `.claude/agent-memory/cda_sme/project_observatory_rename_verdict.md`.

Binding notes:
- **N1** MethodologyPage instrument-naming line: swap to "The Observatory runs a version of that protocol on language models, one prompt at a time." Section 2 forebears citations stay byte-identical.
- **N2** AboutPage cite-to-disclaim sentence: substitution of the proper-noun subject permitted ("The Observatory does not claim that models have beliefs, intentions, lived experience, or culture in the human sense."); the disclaim STRUCTURE is protected; comment block AND test assertions update in lockstep or it is a FAIL.
- **N3** DataPage Section D added line, approved verbatim: "The project is now the Cognitive Structure Observatory; the next bundle version will adopt the new name. The v1 citation above is the minted bundle name and remains the canonical citation for v1."
- **N4** Optional framing fold-in limited to decision-doc sentences, byte-identical, no new measurement claims.
- **N5** `failures_findings.ts` LSB tokens stay (pipeline-actor role, not instrument-naming).
- **N6** (advisory) main.tsx / app.css header comments deferred to the internal sweep; do not pre-edit.
- **N7** (binding) NavBar treatment routed to UI/UX; source comment refreshes in lockstep with chrome.

Four-axis: Claims PASS, Audience PASS, Protocol/Analytical N/A (rule-15 freeze respected), Register PASS, Vocabulary PASS.

---

## UI/UX — PASS-WITH-NOTES (2026-06-16)

Four-question scorecard: OWID fidelity PASS · 30-second journalist PASS · researcher reproduce-and-cite PASS · WCAG AA PASS.

**N7 resolution — NavBar (binding): Option B.** Inner brand span changes from `/ LSB` to `/ Observatory`; two-part `.nav__brand` structure retained; no CSS, class, or token changes. Source comment (NavBar.tsx ~L9) refreshes to "Observatory and data presentation remain primary; About must not dominate the nav." in the same commit.

**DESIGN_SYSTEM.md (binding):** bump to v0.24.0, add changelog entry, update §22.1 positioning sentence ("benchmark" → "Observatory"), add §24 documenting the NavBar brand treatment. Copy-only; no new tokens/classes/visual changes.

**Copy substitutions (binding):**
- MethodologyPage: "The Latent Structure Benchmark" → "The Cognitive Structure Observatory" (intro + what-if sentence); "LSB runs a version of that protocol..." → "The Observatory runs a version of that protocol..." (N1); generic "This benchmark does not measure..." → "This instrument does not measure..."; "The benchmark can show structure..." → "The Observatory can show structure...". Section 2 forebears citations byte-identical.
- AboutPage: paragraph 6 subject + disclaim sentence → "The Cognitive Structure Observatory..." / "The Observatory does not claim..."; header comment Occurrence 2 and `AboutPage.test.tsx` case 4 assertion + case 5 `disclaimP` selector update in lockstep (N2).
- DataPage: insert N3 paragraph inside Section D after the canonical-citation-target sentence, before `</section>`. `CITATION_FIRST_LINE` and the `<pre><code>` citation block FROZEN.

**Verification:** `npm run test` (only `AboutPage.test.tsx` requires edits) + live-DOM check of brand and all four pages before done.

---

## Routing

Both gates satisfied (CDA SME PASS-WITH-NOTES, UI/UX PASS-WITH-NOTES). Coder → Reviewer → Tester. One commit per CLAUDE.md §8, referencing this file and the CDA SME memo.
