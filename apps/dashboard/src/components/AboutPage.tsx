/**
 * AboutPage: long-form article for the About tab.
 *
 * Source: Mark-authored, WritingSample/mark-dawson-about.md
 *         (local-only, untracked, not in repo).
 * CV-checked: confirmed by Mark before plan.
 *
 * DESIGN_SYSTEM.md §22 (v0.19.0).
 * Class reuse: deliberately shares .methodology-page* classes with MethodologyPage
 * so the About prose typographic posture is identical. No .about-page__* class tree.
 *
 * Gate verdicts:
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-10-site-copy-verdicts.md (M2 section)
 *   UI/UX  PASS-WITH-NOTES:  docs/status/2026-06-10-site-copy-verdicts.md (M2 section)
 */

export function AboutPage() {
  return (
    <main className="methodology-page" aria-label="About">
      <div className="methodology-page__container">

        {/*
          CITE-TO-DISCLAIM (two protected occurrences, CDA SME M2-N1 BINDING):

          Occurrence 1 (paragraph 2): "I use culture in that broad sense: not just
          nationality or tradition, but the patterned ways people classify, interpret,
          value, and act." This is Mark defining the broad anthropological sense of
          "culture" as a human practice, NOT attributing culture to a model.
          (CDA SME verdict: register-clean; parallel to MethodologyPage.tsx Section 6
          scare-quoted repudiation pattern.)

          Occurrence 2 (paragraph 6): "The Observatory does not claim that models have
          beliefs, intentions, lived experience, or culture in the human sense."
          This is the canonical §1.5 cite-to-disclaim move: the disclaimer sentence
          explicitly repudiates cognition attribution. It must not be flagged by the
          Reviewer's forbidden-vocab grep; it is the substance, not a violation.
          (CDA SME verdict: structurally parallel to MethodologyPage.tsx Section 3
          "not because they have beliefs or lived experience" cite-to-disclaim.)

          Cross-reference precedents:
            MethodologyPage.tsx lines 134-141 (Section 3 comment block)
            MethodologyPage.tsx lines 217-223 (Section 6 comment block)
            docs/status/2026-06-10-site-copy-verdicts.md (M2 CDA SME and UI/UX verdicts)
        */}
        <section className="methodology-page__section" aria-labelledby="about-mark-dawson-heading">
          <h2 id="about-mark-dawson-heading" className="methodology-page__heading">About Mark Dawson</h2>
          <p className="methodology-page__text">
            CogStructureLab grows out of my work at the intersection of culture, technology, intelligence analysis, and human-centered research.
          </p>
          <p className="methodology-page__text">
            I am not an AI engineer, and I do not approach artificial intelligence primarily as a coding problem. My interest is in how AI systems organize human worlds: families, food, holidays, institutions, threats, identities, obligations, social roles, and the countless categories people use to make sense of life. I use culture in that broad sense: not just nationality or tradition, but the patterned ways people classify, interpret, value, and act.
          </p>
          <p className="methodology-page__text">
            I started my career in design anthropology and design research for product design, development, and strategy. I later moved into the DoD and federal enforcement communities in roles spanning counterterrorism, open-source intelligence, and executive protection.
          </p>
          <p className="methodology-page__text">
            CogStructureLab is an attempt to bring those threads together.
          </p>
          <p className="methodology-page__text">
            The Cognitive Structure Observatory applies cultural-domain methods to language models. It asks a practical question: when frontier models are prompted to list and sort terms from everyday domains, what structures appear in their outputs? The Observatory does not claim that models have beliefs, intentions, lived experience, or culture in the human sense. It measures output structure. Any claim beyond that has to be made carefully.
          </p>
          <p className="methodology-page__text">
            That distinction matters. AI systems are increasingly used in settings where cultural, social, and institutional meaning is not background noise. It is the work itself. A model&rsquo;s way of grouping concepts can shape how it summarizes risk, frames identity, interprets conflict, ranks relevance, or misses what a human expert would notice. Technical performance alone does not answer those questions.
          </p>
          <p className="methodology-page__text">
            My goal with CogStructureLab is to make one kind of structure visible, comparable, and reproducible. It is a demonstration of a broader perspective: AI teams need technical expertise, but they also need people who understand how human categories work, how institutions use information, how risk appears in messy social contexts, and how to turn qualitative judgment into disciplined evaluation.
          </p>
          <p className="methodology-page__text">
            That is the space I work in.
          </p>
        </section>

      </div>
    </main>
  );
}
