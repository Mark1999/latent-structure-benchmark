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
 * Sections 1–6 (placeholder prose, Mark-authored final pending):
 *   - CDA SME PASS-WITH-NOTES: docs/status/2026-06-08-methodology-placeholder-cda-sme-verdict.md
 *   - UI/UX PASS-WITH-NOTES:   docs/status/2026-06-08-methodology-placeholder-uiux-verdict.md
 *
 * The section heading and paragraph text for sections 7–8 are verbatim from the SME verdict.
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
            The Latent Structure Benchmark takes a method that anthropologists use to study people and points
            it at large language models instead.
          </p>
          <p className="methodology-page__text">
            The method is old and unglamorous. If you want to understand how a group of people carves up some
            corner of life, say the world of family, or holidays, or food, you do not start with a theory. You
            ask them to list the things in that world, and then you ask them to sort those things into piles
            that go together. Do that with enough people and patterns fall out: which items everyone names
            first, which things reliably get grouped together, where people agree and where they split. That is
            Cultural Domain Analysis, and it has been around for decades.
          </p>
          <p className="methodology-page__text">
            We run that same protocol on language models, one prompt at a time, as if the model were a person we
            were interviewing. It is not a person, and that &ldquo;as if&rdquo; is doing real work; more on that in section
            4. What comes out is a map of how a given model sorts the everyday words in a domain.
          </p>
          <p className="methodology-page__text">
            We call the thing those maps show the <strong>corpus lens</strong>: the shape a model imposes on a domain,
            inherited from the text it was trained on. Said more carefully, and this is the version we would
            defend to a skeptical researcher, it is the latent categorical structure of a training corpus, as
            refracted through the model&rsquo;s training and alignment. The short name is for headlines. The long name
            is the honest one. They mean the same thing.
          </p>
        </section>

        {/* §6.1 section 2 — What does "corpus lens" actually mean? */}
        <section className="methodology-page__section" aria-labelledby="corpus-lens-heading">
          <h2 id="corpus-lens-heading" className="methodology-page__heading">What does &ldquo;corpus lens&rdquo; actually mean?</h2>
          <p className="methodology-page__text">
            Start with what a category even is, because the whole benchmark rests on it.
          </p>
          <p className="methodology-page__text">
            You, reader, sort the world into categories all day without noticing. A &ldquo;vegetable&rdquo; is a category. So
            is &ldquo;a holiday,&rdquo; &ldquo;a relative,&rdquo; &ldquo;a snack.&rdquo; We group things so we can think about them without drowning
            in detail. A category lets you say a great deal in one short word. The catch is that the grouping is
            a choice, and different sources make different choices. Whether a tomato files under &ldquo;vegetable&rdquo; or
            &ldquo;fruit&rdquo; depends on whether you are cooking or doing botany.
          </p>
          <p className="methodology-page__text">
            A language model makes these choices too, not because anyone taught it a theory of vegetables, but
            because it absorbed an enormous amount of text in which people had already done the sorting. The
            corpus lens is the residue of all that sorting, after it has been pushed through the machine that
            built the model. That machine has five stages, and it helps to name them:
          </p>
          <ul className="methodology-page__list">
            <li className="methodology-page__list-item">the <strong>corpus</strong>, the text the model was trained on,</li>
            <li className="methodology-page__list-item"><strong>training</strong>, which compresses the patterns in that text into the model&rsquo;s weights,</li>
            <li className="methodology-page__list-item"><strong>alignment</strong>, the later tuning that nudges the model toward being helpful and harmless,</li>
            <li className="methodology-page__list-item"><strong>decoding</strong>, the settings that turn the model&rsquo;s internal probabilities into actual words,</li>
            <li className="methodology-page__list-item">and the <strong>output distribution</strong>, the landscape of likely responses we finally get to sample.</li>
          </ul>
          <p className="methodology-page__text">
            When we run a free-list or a pile-sort, we are looking at the shadow that whole chain casts when we
            shine our questions at it. We measure the shadow directly. Everything we say about the stages behind
            it is an inference, not a measurement, and we try to be clear about which is which.
          </p>
        </section>

        {/* §6.1 section 3 — How does the measurement work? (there is no magic in it) */}
        <section className="methodology-page__section" aria-labelledby="measurement-heading">
          <h2 id="measurement-heading" className="methodology-page__heading">How does the measurement work? (there is no magic in it)</h2>
          <p className="methodology-page__text">
            If this takes the mystery out of it, good. There is not much mystery to take.
          </p>
          <p className="methodology-page__text">
            We ask each model two kinds of question, many times over:
          </p>
          <ul className="methodology-page__list">
            <li className="methodology-page__list-item">
              A <strong>free-list</strong>: name the members of a category. &ldquo;List the kinds of family members.&rdquo; We count which
              items show up, and how early, across all the runs. Items that come up often and early are{' '}
              <em>salient</em>; the statistic for that is Smith&rsquo;s S, and a high S just means &ldquo;this is one of the first
              things that comes to mind in this domain.&rdquo;
            </li>
            <li className="methodology-page__list-item">
              A <strong>pile-sort</strong>: here are the items, sort them into piles that belong together. We count how often
              any two items land in the same pile. Do that across runs and across models and you get a similarity
              structure: which things cluster, which sit apart.
            </li>
          </ul>
          <p className="methodology-page__text">
            From the pile-sort similarities we draw the map you see on the dashboard. Items that get grouped
            together sit close; items that rarely co-occur sit far apart. That is multidimensional scaling, which
            is a fancy name for a simple goal: put things on a 2D map so that distance on the map matches how
            unalike they are.
          </p>
          <p className="methodology-page__text">
            Two things we insist on, because they are where this kind of work usually goes wrong:
          </p>
          <p className="methodology-page__text">
            First, we never show a point without showing how sure we are of it. Every position on the map carries
            an uncertainty ellipse, drawn by resampling the data hundreds of times and watching how much the
            answer wobbles. A tight ellipse means the structure is solid. A fat one means do not read too much
            into the exact spot.
          </p>
          <p className="methodology-page__text">
            Second, when something fails, that is data, not garbage. A model that refuses a prompt, or returns an
            empty list, gets recorded and shown, not quietly dropped. A refusal is itself a finding about the
            machine.
          </p>
        </section>

        {/* §6.1 section 4 — What this does not measure (or, the picture on the dresser) */}
        {/*
          CITE-TO-DISCLAIM: The phrase "see family the same way" below appears in scare-quotes
          as the explicit claim being repudiated, not as an endorsement. This is the canonical
          cite-to-disclaim exception pattern (CDA SME Check 4, PASS; see
          docs/status/2026-06-08-methodology-placeholder-cda-sme-verdict.md §Check 4).
          The Reviewer's forbidden-vocab grep should not flag this occurrence.
          Cross-reference precedent: docs/status/2026-05-17-ft-designer-appendix-s6-advisory.md
        */}
        <section className="methodology-page__section" aria-labelledby="what-this-does-not-measure-heading">
          <h2 id="what-this-does-not-measure-heading" className="methodology-page__heading">What this does not measure (or, the picture on the dresser)</h2>
          <p className="methodology-page__text">
            Here is the part to read twice.
          </p>
          <p className="methodology-page__text">
            When you see two models sort family words into the same piles, the words almost beg you to say that
            the two models &ldquo;see family the same way,&rdquo; that they share some value or attitude. Do not say it. Or
            at least, know that you would be guessing, not reading the data.
          </p>
          <p className="methodology-page__text">
            A pattern can be perfectly real and still have a dull cause. Suppose you walked into my home and found
            a single photograph on display in my bedroom, a young woman with a guitar, and nothing else on the
            walls. You could infer a great deal: an old flame, a quiet heartbreak, a story. You would also be
            wrong. The honest explanation is that I am a slob, a cleaner once tidied a toppled stack of prints,
            and that one happened to land in a frame and stay there. The pattern was real. The meaning you
            reached for was a projection. The only way to know the difference is to ask, and not just look.
          </p>
          <p className="methodology-page__text">
            The benchmark is in the same position, with one hard limit: there is no one to ask. So we hold the
            line on what we will claim. We measure categorical structure in a model&rsquo;s output, refracted from the
            text it learned on. We do not claim it as evidence of belief, preference, cognition, or inner
            experience, because the model has none of those, and our method could not see them if it did. The
            structure is the finding. The inner life is not on the table.
          </p>
          <p className="methodology-page__text">
            A few more limits, stated plainly because burying them would be the opposite of the point:
          </p>
          <ul className="methodology-page__list">
            <li className="methodology-page__list-item">
              <strong>Wording matters.</strong> Change the prompt and the output can shift. We hold the prompt fixed across
              models within a run, and we ran a formal study of how much paraphrasing moves the result. Whatever
              wobble is left shows up as the uncertainty you see on every chart.
            </li>
            <li className="methodology-page__list-item">
              <strong>English only, for now.</strong> The benchmark runs in English. Anything it seems to say about another
              culture is really a statement about how English-language text represents that culture, which is not
              the same thing.
            </li>
            <li className="methodology-page__list-item">
              <strong>We cannot see the corpus.</strong> The training data for most of these models is not public. We can show
              you the structure; we usually cannot trace it back to a particular source.
            </li>
            <li className="methodology-page__list-item">
              <strong>Training and tuning are tangled.</strong> Pretraining, alignment, and system prompts all bend the output,
              and our method sees the sum, not the separate parts. For &ldquo;how does this deployed product behave&rdquo;
              that is fine. For &ldquo;what was in the raw corpus&rdquo; it is a real limit.
            </li>
            <li className="methodology-page__list-item">
              <strong>The interview is a metaphor.</strong> Treating the model as an informant is a move we make to borrow a
              good method. It is not a claim that there is anybody home.
            </li>
          </ul>
        </section>

        {/* §6.1 section 5 — How do I read the charts? */}
        <section className="methodology-page__section" aria-labelledby="how-to-read-heading">
          <h2 id="how-to-read-heading" className="methodology-page__heading">How do I read the charts?</h2>
          <p className="methodology-page__text">
            Short version, so the dashboard is not a puzzle:
          </p>
          <ul className="methodology-page__list">
            <li className="methodology-page__list-item">
              <strong>The model map (MDS).</strong> Each labeled point is one model&rsquo;s position for the domain. Closer together
              means more alike in how they sorted the domain. The ring around each point is uncertainty; overlap
              means the difference may not be real.
            </li>
            <li className="methodology-page__list-item">
              <strong>The similarity heatmap.</strong> Every cell is one model-pair, darker for more alike. Cells whose
              confidence interval crosses zero are drawn faint, because we are not sure they differ from chance.
            </li>
            <li className="methodology-page__list-item">
              <strong>The term map.</strong> Here the points are the words themselves, placed by how often models grouped them
              together. This is where you see a domain&rsquo;s internal shape.
            </li>
            <li className="methodology-page__list-item">
              <strong>Consensus.</strong> A single number for &ldquo;how much do the models agree on this domain,&rdquo; with the usual
              uncertainty attached.
            </li>
          </ul>
          <p className="methodology-page__text">
            Every figure links back here, and every figure shows its uncertainty. If a claim on this site does
            not come with a sense of how sure we are, treat that as a bug and tell us.
          </p>
        </section>

        {/* §6.1 section 6 — Do not take my word for it */}
        <section className="methodology-page__section" aria-labelledby="do-not-take-my-word-heading">
          <h2 id="do-not-take-my-word-heading" className="methodology-page__heading">Do not take my word for it</h2>
          <p className="methodology-page__text">
            This is one instrument, built and run by a small operation, and like any single source it has a point
            of view and its blind spots. So we made it checkable.
          </p>
          <p className="methodology-page__text">
            The full open data bundle is public: every raw model response, the processed results, and the code
            that turns one into the other. Given the bundle and an afternoon, you can rebuild the database from
            the raw responses, rerun the analysis, and regenerate every figure on this site. The exact toolchain
            versions and the code commit behind the current numbers are recorded in the data provenance, just
            below. The release carries a citable DOI.
          </p>
          <p className="methodology-page__text">
            We would rather you check us than trust us. Do your own homework.
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
