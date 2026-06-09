# Methodology placeholder (ship the draft) — UI/UX verdict (2026-06-08)

**Verdict: PASS-WITH-NOTES.** OWID PASS / journalist PASS-WITH-NOTES / cite PASS / WCAG PASS.
NO DESIGN_SYSTEM update. Light gate (ships as placeholder, reuses the existing methodology-page layout).

## Binding implementation notes (Coder)
- **Replace wholesale:** delete the placeholder `<section>` (the `<h2>Methodology</h2>` + "Full
  methodology content coming soon" block, incl. the `--placeholder` paragraph). The 6 draft sections
  take its place, ABOVE the two existing live verbatim sections (Data provenance + Cross-model term map),
  which stay untouched.
- **Heading hierarchy:** the 6 new sections are PEERS of the existing two → each is
  `<section className="methodology-page__section" aria-labelledby="...-heading">` with an
  `<h2 id="...-heading" className="methodology-page__heading">`. Do NOT add an outer "Methodology" h2
  wrapper. Section titles strip the leading numeral ("What is this, really?", "What does &ldquo;corpus
  lens&rdquo; actually mean?", "How does the measurement work? (there is no magic in it)", "What this
  does not measure (or, the picture on the dresser)", "How do I read the charts?", "Do not take my word
  for it").
- **Emphasis:** `**bold**`→`<strong>`, `*italic*`→`<em>` inside `.methodology-page__text`. No new CSS.
- **Bullet lists** (sections 2,3,4): `<ul className="methodology-page__list">` / `<li
  className="methodology-page__list-item">` (classes added for future spacing; browser-default indent ok
  for the placeholder).
- **Entity convention (binding):** apostrophes `&rsquo;`, double quotes `&ldquo;`/`&rdquo;`, matching the
  existing live sections (e.g. "it&rsquo;s", the scare-quoted &ldquo;see family the same way&rdquo;).
- **Cite-to-disclaim comment (binding, from CDA SME):** add a JSX comment near the section-4 scare-quoted
  "see family the same way" noting it is an explicitly-repudiated claim (cite-to-disclaim exception), so
  the Reviewer's forbidden-vocab grep does not flag it.
- **Reuse only** `.methodology-page__section/__heading/__text/__link`. No new classes/tokens/visual
  decisions. `.methodology-page__text--placeholder` rule can stay unused (harmless).

## Non-blocking carry-forward (for Mark's authored final, not this placeholder)
ARCHITECTURE §1.5.6 wants "the mismatch is the finding" as the FIRST paragraph; the draft carries the
spirit in section 4 ("The structure is the finding. The inner life is not on the table.") not at the
top. CDA SME cleared this for a placeholder. Mark decides on the final: add a one-sentence mismatch lede
above section 1, or amend §1.5.6's strict placement rule via the Architect.
