/**
 * MethodologyPage — long-form article template for the methodology tab.
 *
 * Renders a "Data provenance" section and a "Cross-model term map and
 * uncertainty" stub section, per:
 *   - CDA SME PROMOTE-2 verdict §3 Option 1 (binding copy)
 *   - CDA SME food-promote verdict C1.a / C3 / C4 (binding copy amendments)
 *   - UI/UX food-promote verdict F3a (term-MDS stub, §16.2)
 *   - UI/UX PASS-WITH-NOTES verdict T-B (layout/link rules)
 *   - DESIGN_SYSTEM.md §6 + §15.5(a) + §16.2
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
            The published family, holidays, and food corpora were recomputed on 2026-05-30 under a
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
            , which is regenerated on every published bundle.
          </p>
        </section>

        {/* §16.2 — Cross-model term map and uncertainty (food-promote C3/C4, UI/UX F3a) */}
        {/* M4a sentence: Phase 9a binding disclosure (C4). */}
        {/* C3 sentence: informant-count disclosure for term-MDS bootstrap envelope (C3). */}
        <section className="methodology-page__section" aria-labelledby="term-mds-heading">
          <h2 id="term-mds-heading" className="methodology-page__heading">Cross-model term map and uncertainty</h2>
          <p className="methodology-page__text">
            Term position confidence reflects agreement across models, not within-model sampling variance.
            The cross-model term map is computed from 15 model informants on family, 14 on holidays, and
            8 on food; ellipse widths and branch-probability values are derived from model-resample
            bootstrap (B=200), so a sparser informant pool produces a different bootstrap envelope
            shape than a denser one even when the per-model agreement is similar.
          </p>
        </section>

      </div>
    </main>
  );
}
