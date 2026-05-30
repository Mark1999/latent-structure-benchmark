/**
 * MethodologyPage — long-form article template for the methodology tab.
 *
 * Renders a "Data provenance" section as the final section, per:
 *   - CDA SME PROMOTE-2 verdict §3 Option 1 (binding copy)
 *   - UI/UX PASS-WITH-NOTES verdict T-B (layout/link rules)
 *   - DESIGN_SYSTEM.md §6 + §15.5(a)
 *
 * The section heading and paragraph text are verbatim from the SME verdict.
 * No forbidden vocabulary per ARCHITECTURE.md §1.5.4 / CLAUDE.md §7.
 */

export function MethodologyPage() {
  return (
    <main className="methodology-page" aria-label="Methodology">
      <div className="methodology-page__container">

        {/* Placeholder sections — Mark writes prose for §6.1 sections 1–6 */}
        <section className="methodology-page__section">
          <h2 className="methodology-page__heading">Methodology</h2>
          <p className="methodology-page__text methodology-page__text--placeholder">
            Full methodology content coming soon.
          </p>
        </section>

        {/* §6.1 section 7 — Data provenance (PROMOTE-2, CDA SME §3 Option 1, verbatim) */}
        {/* DESIGN_SYSTEM.md §15.5(a): final section, own <h2>, root-relative link, new tab, (JSON) affordance */}
        <section className="methodology-page__section" aria-labelledby="data-provenance-heading">
          <h2 id="data-provenance-heading" className="methodology-page__heading">Data provenance</h2>
          <p className="methodology-page__text">
            The published family and holidays corpora were recomputed on 2026-05-30 under a
            pinned analytical toolchain (NumPy 2.4.4, SciPy 1.17.1, Python 3.12) so that any
            researcher with the open data bundle can reproduce the published numerics on their
            own machine. The prior figures were valid under the toolchain that produced them;
            what changed is that LSB now pins the NumPy and SciPy versions used for all
            bootstrap and MDS computations, where previously those versions were whatever the
            host environment happened to have installed. Values shifted at the third or fourth
            decimal in bootstrap- and MDS-derived quantities; at two-decimal display rounding,
            the visible effects on this site are family&rsquo;s Smith&rsquo;s S moving from 0.80
            to 0.81 and its 95% confidence interval upper bound from 0.94 to 0.95, and
            holidays&rsquo; 95% confidence interval moving from [0.76, 0.96] to [0.77, 0.97].
            Deterministic quantities such as Smith&rsquo;s S values before display rounding,
            OCI, and the Romney eigenratios that drive the consensus-type classification are
            unaffected at any boundary, and no consensus classification, model ordering, or
            relative geometry on the MDS maps has changed on either domain. The pinned versions
            and the exact git commit are recorded in{' '}
            <a
              href="/data/provenance.json"
              target="_blank"
              rel="noopener noreferrer"
              className="methodology-page__link"
            >
              provenance.json
              <span className="sr-only"> (opens data provenance manifest in new tab)</span>
              {' '}(JSON)
            </a>
            , which is regenerated on every published bundle. The food domain remains on its
            prior toolchain pending a separate methodological review and is not covered by the
            footer above; it will be re-baselined and re-marked once that review completes.
          </p>
        </section>

      </div>
    </main>
  );
}
