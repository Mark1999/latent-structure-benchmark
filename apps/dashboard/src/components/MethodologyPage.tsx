/**
 * MethodologyPage — long-form article template for the methodology tab.
 *
 * Sections 1-8 are Mark-authored final prose (M1, 2026-06-10).
 * The two terminal sections (Data provenance and Cross-model term map and uncertainty)
 * have moved to DataPage.tsx per the M1 atomic section move:
 *   - CDA SME PASS-WITH-NOTES: docs/status/2026-06-10-site-copy-verdicts.md
 *   - UI/UX PASS-WITH-NOTES:   docs/status/2026-06-10-site-copy-verdicts.md
 *
 * A single "Provenance" pointer section (Section 9) links in-app to /data.
 * DESIGN_SYSTEM.md §6, §6.3, §15.5(a), §16.2 (v0.18.0).
 *
 * No forbidden vocabulary per ARCHITECTURE.md §1.5.4 / CLAUDE.md §7.
 */

export function MethodologyPage() {
  return (
    <main className="methodology-page" aria-label="Methodology">
      <div className="methodology-page__container">

        {/* §6.1 section 1 — What is this, really? */}
        <section className="methodology-page__section" aria-labelledby="what-is-this-heading">
          <h2 id="what-is-this-heading" className="methodology-page__heading">What is this, really?</h2>
          <p className="methodology-page__text">
            The Latent Structure Benchmark takes a method built for cultural informants, people with lived
            experience of the world they describe, and points it at systems that encode culture without
            experiencing any of it. That mismatch is not a flaw to hide or a caveat to get to later. It is
            the finding. What comes out when you hand an interview protocol to something that is not an
            informant is the whole object of study here.
          </p>
          <p className="methodology-page__text">
            Put another way, the Latent Structure Benchmark is a what-if exercise.
          </p>
          <p className="methodology-page__text">
            What happens if we take a decades-old cognitive anthropology method I have used in field studies
            and apply it to large language models?
          </p>
          <p className="methodology-page__text">
            We did not start with a grand theory. We started with a practical question: if we ask models to
            list and sort everyday concepts, what patterns show up? Are those patterns stable? Do different
            models organize the same domain in similar ways? Do some models drift, flatten, refuse, or produce
            odd structures?
          </p>
          <p className="methodology-page__text">
            We have not answered all of that yet. Maybe you will.
          </p>
        </section>

        {/* §6.1 section 2 — Cultural Domain Analysis */}
        <section className="methodology-page__section" aria-labelledby="cultural-domain-analysis-heading">
          <h2 id="cultural-domain-analysis-heading" className="methodology-page__heading">Cultural Domain Analysis</h2>
          <p className="methodology-page__text">
            The method is old and unglamorous, which is part of its charm.
          </p>
          <p className="methodology-page__text">
            If you want to understand how a group of people carves up some corner of life, say family,
            holidays, or food, you do not start by lecturing them about your theory. You ask them to list the
            things in that world. Then you ask them to sort those things into piles that go together.
          </p>
          <p className="methodology-page__text">
            Do that with enough people and patterns start to fall out: which items everyone names first, which
            things reliably get grouped together, where people agree, and where they split. That is Cultural
            Domain Analysis.
          </p>
          <p className="methodology-page__text">
            None of the method is mine. It comes out of cognitive anthropology, and the people who built it
            should be named. A. Kimball Romney, Susan Weller, and William Batchelder worked out the formal
            theory of agreement in{' '}
            <a
              href="https://doi.org/10.1525/aa.1986.88.2.02a00020"
              target="_blank"
              rel="noopener noreferrer"
              className="methodology-page__link"
            >
              &ldquo;Culture as Consensus&rdquo;
              <span className="sr-only"> (opens in new tab)</span>
            </a>
            {' '}(1986). Weller and Romney&rsquo;s{' '}
            <a
              href="https://doi.org/10.4135/9781412986069"
              target="_blank"
              rel="noopener noreferrer"
              className="methodology-page__link"
            >
              <em>Systematic Data Collection</em>
              <span className="sr-only"> (opens in new tab)</span>
            </a>
            {' '}(1988) is the practical handbook for the elicitation techniques LSB borrows. Stephen Borgatti
            wrote the standard guide to{' '}
            <a
              href="http://www.analytictech.com/mb870/Readings/elicitation.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="methodology-page__link"
            >
              domain elicitation
              <span className="sr-only"> (opens in new tab)</span>
            </a>
            {' '}(1999) and built ANTHROPAC, the software a generation of fieldworkers ran these analyses on.
            Roy D&rsquo;Andrade&rsquo;s{' '}
            <a
              href="https://doi.org/10.1017/CBO9781139166645"
              target="_blank"
              rel="noopener noreferrer"
              className="methodology-page__link"
            >
              <em>The Development of Cognitive Anthropology</em>
              <span className="sr-only"> (opens in new tab)</span>
            </a>
            {' '}(1995) tells the story of the whole field. If you want the real thing rather than my summary,
            start with Weller and Romney. It is short, practical, and this site stands on it.
          </p>
          <p className="methodology-page__text">
            LSB runs a version of that protocol on language models, one prompt at a time.
          </p>
          <p className="methodology-page__text">
            A model is asked to produce a free-list of terms. It is then asked to sort terms into piles and
            name those piles. We repeat that process across runs, across models in the same family, and across
            different frontier models.
          </p>
          <p className="methodology-page__text">
            The working name for what we measure is the <strong>corpus lens</strong>: the shape a model
            imposes on a domain, inherited from the text it was trained on and refracted through training,
            alignment, decoding, and deployment.
          </p>
          <p className="methodology-page__text">
            The short version is &ldquo;corpus lens.&rdquo; The careful version is &ldquo;latent categorical structure in
            model output.&rdquo; The short version is easier to say. The careful version is what I would defend to
            a skeptical researcher.
          </p>
        </section>

        {/* §6.1 section 3 — What corpus lens means */}
        {/*
          CITE-TO-DISCLAIM: The phrase "not because they have beliefs or lived experience" below
          appears in a disclaiming clause that explicitly repudiates cognition attribution,
          not as an endorsement. This is the canonical cite-to-disclaim exception pattern
          (CDA SME M1-N1; see docs/status/2026-06-10-site-copy-verdicts.md §CDA SME gate verdict).
          The Reviewer's forbidden-vocab grep should not flag this occurrence.
          Cross-reference precedent: docs/status/2026-05-17-ft-designer-appendix-s6-advisory.md
        */}
        <section className="methodology-page__section" aria-labelledby="what-corpus-lens-means-heading">
          <h2 id="what-corpus-lens-means-heading" className="methodology-page__heading">What corpus lens means</h2>
          <p className="methodology-page__text">
            People sort the world into categories all day without noticing. A &ldquo;vegetable&rdquo; is a category.
            So is &ldquo;a holiday,&rdquo; &ldquo;a relative,&rdquo; or &ldquo;a snack.&rdquo; Categories let us think without drowning
            in detail.
          </p>
          <p className="methodology-page__text">
            The catch is that categories are choices. A tomato is a fruit if you are doing botany and a
            vegetable if you are making dinner.
          </p>
          <p className="methodology-page__text">
            Language models make these choices too, not because they have beliefs or lived experience, but
            because they absorbed a great deal of text in which people had already done the sorting. When we
            ask a model to list or sort terms, we are sampling the output of that whole system.
          </p>
          <p className="methodology-page__text">
            That system includes the training corpus, training process, alignment, decoding settings, and
            final output distribution. We measure the output directly. Anything we say about the hidden
            causes behind it is an inference.
          </p>
        </section>

        {/* §6.1 section 4 — How the measurement works */}
        <section className="methodology-page__section" aria-labelledby="measurement-heading">
          <h2 id="measurement-heading" className="methodology-page__heading">How the measurement works</h2>
          <p className="methodology-page__text">
            We ask each model two kinds of questions many times over.
          </p>
          <p className="methodology-page__text">
            <strong>Free-list:</strong> name the members of a category.<br />
            Example: &ldquo;List kinds of family members.&rdquo;
          </p>
          <p className="methodology-page__text">
            We count which items appear, how often they appear, and how early they appear. Items that show
            up often and early are salient.
          </p>
          <p className="methodology-page__text">
            <strong>Pile-sort:</strong> sort these items into piles that belong together.<br />
            We count how often any two items land in the same pile. Across runs and models, that gives us a
            similarity structure: which terms cluster together and which sit apart.
          </p>
          <p className="methodology-page__text">
            The maps on the dashboard come from those similarity structures. Terms or models that are closer
            together behaved more similarly. Terms or models farther apart behaved less similarly.
          </p>
          <p className="methodology-page__text">
            There is no magic in this. The math is doing a simple job: turning repeated sorting behavior
            into a visible structure.
          </p>
        </section>

        {/* §6.1 section 5 — Uncertainty and failure */}
        <section className="methodology-page__section" aria-labelledby="uncertainty-and-failure-heading">
          <h2 id="uncertainty-and-failure-heading" className="methodology-page__heading">Uncertainty and failure</h2>
          <p className="methodology-page__text">
            Two rules matter.
          </p>
          <p className="methodology-page__text">
            First, we do not show points without showing uncertainty. The ellipses on the maps are there
            because the exact position of a term or model can wobble. A tight ellipse means the structure
            is relatively stable. A wide one means you should not overread the exact placement.
          </p>
          <p className="methodology-page__text">
            Second, failures are data. If a model refuses, returns an empty answer, or produces something
            the pipeline cannot parse, we preserve it. That failure is part of the model&rsquo;s behavior under
            the protocol.
          </p>
          <p className="methodology-page__text">
            Quietly dropping failures would make the benchmark cleaner and less honest.
          </p>
        </section>

        {/* §6.1 section 6 — What this does not measure */}
        {/*
          CITE-TO-DISCLAIM: The phrase "see family" below appears in scare-quotes
          as the explicit claim being repudiated, not as an endorsement. This is the canonical
          cite-to-disclaim exception pattern (CDA SME Check 4, PASS; see
          docs/status/2026-06-08-methodology-placeholder-cda-sme-verdict.md §Check 4).
          The Reviewer's forbidden-vocab grep should not flag this occurrence.
          Cross-reference precedent: docs/status/2026-05-17-ft-designer-appendix-s6-advisory.md
        */}
        <section className="methodology-page__section" aria-labelledby="what-this-does-not-measure-heading">
          <h2 id="what-this-does-not-measure-heading" className="methodology-page__heading">What this does not measure</h2>
          <p className="methodology-page__text">
            This benchmark does not measure belief, intent, consciousness, preference, or inner experience.
          </p>
          <p className="methodology-page__text">
            When two models sort family terms in similar ways, it is tempting to say they &ldquo;see family&rdquo; the
            same way. Do not do that. Or at least know that you are guessing.
          </p>
          <p className="methodology-page__text">
            A pattern can be real without meaning what you first think it means. The benchmark can show
            structure in model output. It cannot tell you that the model understands, values, or experiences
            that structure.
          </p>
          <p className="methodology-page__text">
            The structure is the finding. The inner life is not on the table.
          </p>
          <p className="methodology-page__text">
            A few limits, stated plainly:
          </p>
          <ul className="methodology-page__list">
            <li className="methodology-page__list-item">
              <strong>Prompt wording matters.</strong> Change the prompt and the output can move.
            </li>
            <li className="methodology-page__list-item">
              <strong>English only, for now.</strong> Claims about other cultures are really claims about
              English-language representations of those cultures.
            </li>
            <li className="methodology-page__list-item">
              <strong>We cannot see most training corpora.</strong> We can measure output structure, but
              usually cannot trace it back to specific sources.
            </li>
            <li className="methodology-page__list-item">
              <strong>Training and tuning are tangled.</strong> Pretraining, alignment, system prompts, and
              decoding all shape the result.
            </li>
            <li className="methodology-page__list-item">
              <strong>The interview is a metaphor.</strong> Treating a model as an informant lets us borrow
              a useful method. It is not a claim that anyone is home.
            </li>
          </ul>
        </section>

        {/* §6.1 section 7 — How to read the charts */}
        <section className="methodology-page__section" aria-labelledby="how-to-read-heading">
          <h2 id="how-to-read-heading" className="methodology-page__heading">How to read the charts</h2>
          <ul className="methodology-page__list">
            <li className="methodology-page__list-item">
              <strong>Model map:</strong> each point is a model. Closer points mean more similar sorting
              behavior. The ring shows uncertainty.
            </li>
            <li className="methodology-page__list-item">
              <strong>Term map:</strong> each point is a word or phrase. Nearby terms were grouped together
              more often.
            </li>
            <li className="methodology-page__list-item">
              <strong>Similarity heatmap:</strong> each cell compares a pair of models. Darker means more alike.
            </li>
            <li className="methodology-page__list-item">
              <strong>Consensus:</strong> a summary measure of how strongly models converge on a shared
              structure for the domain.
            </li>
          </ul>
          <p className="methodology-page__text">
            If a chart makes a claim, it should also give you some sense of uncertainty. If it does not,
            treat that as a bug.
          </p>
        </section>

        {/* §6.1 section 8 — Do not take my word for it */}
        <section className="methodology-page__section" aria-labelledby="do-not-take-my-word-heading">
          <h2 id="do-not-take-my-word-heading" className="methodology-page__heading">Do not take my word for it</h2>
          <p className="methodology-page__text">
            This is one instrument, built by a small operation. It has a point of view and blind spots.
            So the data is public.
          </p>
          <p className="methodology-page__text">
            The open bundle includes raw model responses, processed results, prompts, domain files, code,
            manifests, and a rebuild path. Given the bundle and some time, you can rebuild the database and
            check the published figures yourself.
          </p>
          <p className="methodology-page__text">
            I would rather you check the work than trust the prose.
          </p>
        </section>

        {/* §6.3 Provenance pointer — in-app link to Data page (M1, 2026-06-10) */}
        {/* DESIGN_SYSTEM.md §6.3: internal SPA route, no target="_blank" */}
        <section className="methodology-page__section" aria-labelledby="provenance-pointer-heading">
          <h2 id="provenance-pointer-heading" className="methodology-page__heading">Provenance</h2>
          <p className="methodology-page__text">
            Detailed provenance, toolchain versions, hashes, and bootstrap notes are available on
            the{' '}
            <a href="/data" className="methodology-page__link">Data page</a>.
          </p>
        </section>

      </div>
    </main>
  );
}
