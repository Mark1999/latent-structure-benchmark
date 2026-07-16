/**
 * DataPage — static Data download tab.
 *
 * All prose is verbatim from:
 *   - data/open_bundle/README.md
 *   - data/open_bundle/huggingface_dataset_card.md
 *   - ARCHITECTURE.md §6.6/§6.7
 * No new framing prose. Coder assembles only.
 *
 * Section render order (UI/UX verdict §20, binding):
 *   B (HF Get-the-data) → D (Cite) → A (header) → C (tarball+warning)
 *   → E (GitHub) → F (what's-in-bundle) → G (licenses) → H (provenance pointer)
 *
 * External-link contract (every external <a>, UI/UX verdict §20):
 *   target="_blank" + rel="noopener noreferrer"
 *   + nested <span className="sr-only">(opens <dest> in new tab)</span>
 *   B2 anchor sr-only = "(starts 1.55 GB download in new tab)"
 *
 * Gate verdicts:
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-08-phase9a-data-tab-cda-sme-verdict.md
 *   UI/UX PASS-WITH-NOTES:   docs/status/2026-06-08-phase9a-data-tab-ui-ux-verdict.md
 *
 * No forbidden vocabulary per ARCHITECTURE.md §1.5.4 / CLAUDE.md §7.
 */

export function DataPage() {
  return (
    <main className="data-page" aria-label="Data download">
      <div className="data-page__container">

        {/* ── Section B: Get the data (HF — primary CTA) ─────────────────── */}
        <section className="data-page__section" aria-labelledby="data-hf-heading">
          <h2 id="data-hf-heading" className="data-page__heading">Get the data</h2>
          <p className="data-page__text">
            The LSB Open Data Bundle v1 is published on HuggingFace Datasets under CC0 1.0 Universal:
          </p>
          <p className="data-page__text">
            <a
              href="https://huggingface.co/datasets/AILLM1999/latent-structure-benchmark"
              target="_blank"
              rel="noopener noreferrer"
              className="data-page__link"
            >
              huggingface.co/datasets/AILLM1999/latent-structure-benchmark
              <span className="sr-only">(opens HuggingFace dataset page in new tab)</span>
            </a>
          </p>
        </section>

        {/* ── Section D: Cite this dataset ───────────────────────────────── */}
        <section className="data-page__section" aria-labelledby="data-cite-heading">
          <h2 id="data-cite-heading" className="data-page__heading">Cite this dataset</h2>
          <pre className="data-page__code-block"><code className="data-page__code-block">{`Dawson, M. (2026). Latent Structure Benchmark (LSB) Open Data Bundle v1.
Zenodo. https://doi.org/10.5281/zenodo.20293554`}</code></pre>
          <p className="data-page__text">
            DOI:{' '}
            <a
              href="https://doi.org/10.5281/zenodo.20293554"
              target="_blank"
              rel="noopener noreferrer"
              className="data-page__link"
            >
              https://doi.org/10.5281/zenodo.20293554
              <span className="sr-only">(opens Zenodo DOI in new tab)</span>
            </a>
          </p>
          <p className="data-page__text">
            The Zenodo record at{' '}
            <a
              href="https://zenodo.org/records/20293554"
              target="_blank"
              rel="noopener noreferrer"
              className="data-page__link"
            >
              https://zenodo.org/records/20293554
              <span className="sr-only">(opens Zenodo record in new tab)</span>
            </a>
            {' '}archives this release and is the canonical citation target.
          </p>
          <p className="data-page__text">
            The project is now the Cognitive Structure Observatory; the next bundle version will adopt the new name. The v1 citation above is the minted bundle name and remains the canonical citation for v1.
          </p>
        </section>

        {/* ── Section A: Header — CDA SME binding: full 3-sentence framing block ── */}
        {/* Source: data/open_bundle/README.md lines 19-26 (verbatim) */}
        <section className="data-page__section" aria-labelledby="data-header-heading">
          <h2 id="data-header-heading" className="data-page__heading">Data</h2>
          <p className="data-page__text">
            The mismatch is the finding. Importing a methodology designed for cultural
            informants into a system that encodes culture without experiencing it is the
            research question, not a limitation. LSB measures the corpus lens: the latent
            categorical structure of a training corpus, refracted through training and
            alignment, surfaced by structured elicitation. Every domain in v1 is
            model-to-model. There are no human baselines.
          </p>
        </section>

        {/* ── Section C: Download the tarball (B2, size warning, SHA256) ─── */}
        <section className="data-page__section" aria-labelledby="data-tarball-heading">
          <h2 id="data-tarball-heading" className="data-page__heading">Download the tarball</h2>
          <div className="data-page__note" role="note">
            Approx. 1.55 GB. Direct download starts when you click.
          </div>
          <p className="data-page__text">
            <a
              href="https://f005.backblazeb2.com/file/lsb-open-data/lsb_open_bundle_v1.tar.gz"
              target="_blank"
              rel="noopener noreferrer"
              className="data-page__link"
            >
              lsb_open_bundle_v1.tar.gz
              <span className="sr-only">(starts 1.55 GB download in new tab)</span>
            </a>
          </p>
          <p className="data-page__text">Verify integrity before use (SHA256):</p>
          <pre className="data-page__code-block"><code className="data-page__code-block">{'7064b325a25f90d2555138e7d944b129e78cbc7e18eace663b058166a6cd5983  lsb_open_bundle_v1.tar.gz'}</code></pre>
        </section>

        {/* ── Section E: Source code (GitHub) ────────────────────────────── */}
        <section className="data-page__section" aria-labelledby="data-github-heading">
          <h2 id="data-github-heading" className="data-page__heading">Source code</h2>
          <p className="data-page__text">
            <a
              href="https://github.com/Mark1999/latent-structure-benchmark"
              target="_blank"
              rel="noopener noreferrer"
              className="data-page__link"
            >
              github.com/Mark1999/latent-structure-benchmark
              <span className="sr-only">(opens GitHub repository in new tab)</span>
            </a>
          </p>
          <p className="data-page__text">
            Rebuild the SQLite database from the canonical JSONL:
          </p>
          <pre className="data-page__code-block"><code className="data-page__code-block">{'python build_db.py informants.jsonl lsb.sqlite'}</code></pre>
          <p className="data-page__text">
            Python 3.11+, no external dependencies. See <code>DATA_DICTIONARY.md</code> §6 for the
            full walkthrough and byte-equivalence verification steps.
          </p>
        </section>

        {/* ── Section F: What's in the bundle ────────────────────────────── */}
        {/* Verbatim from data/open_bundle/README.md + huggingface_dataset_card.md */}
        <section className="data-page__section" aria-labelledby="data-bundle-heading">
          <h2 id="data-bundle-heading" className="data-page__heading">What&rsquo;s in the bundle</h2>
          <p className="data-page__text">
            This bundle contains 1,291 informant records produced by 17 models across 3 domains
            (family, food, holidays). 36 sessions were preserved as failures and 27 as decline
            interviews.
          </p>
          <dl className="data-page__dl">
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>informants.jsonl</code></dt>
              <dd className="data-page__dd">Canonical raw data. One <code>InformantRecord</code> per line. <code>DATA_DICTIONARY.md</code> §1.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>failures.jsonl</code></dt>
              <dd className="data-page__dd">Sessions the pipeline could not complete. Verbatim outputs preserved. §9.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>decline_interviews.jsonl</code></dt>
              <dd className="data-page__dd">Follow-up elicitations for declined or failed sessions. §10.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>lsb.sqlite</code></dt>
              <dd className="data-page__dd">SQLite database built from the JSONL files above. Same data, query-friendly.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>build_db.py</code></dt>
              <dd className="data-page__dd">Build script. Reconstruct <code>lsb.sqlite</code> from JSONL. See reproducibility below.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>DATA_DICTIONARY.md</code></dt>
              <dd className="data-page__dd">Field-by-field schema docs for every file in this bundle.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>prompts/v1/</code></dt>
              <dd className="data-page__dd">Verbatim prompt templates (free_list, pile_sort, pile_interview). CC0.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>domains/v1/</code></dt>
              <dd className="data-page__dd">Domain YAML files (family, holidays, food). CC0.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>MANIFEST.txt</code></dt>
              <dd className="data-page__dd">SHA256 digest, byte size, and path for every file in this bundle.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt"><code>LICENSE-OPENBUNDLE</code></dt>
              <dd className="data-page__dd">CC0 1.0 Universal legal text. Governs all data files in this bundle.</dd>
            </div>
          </dl>
        </section>

        {/* ── Section G: Licenses ─────────────────────────────────────────── */}
        {/* Verbatim from ARCHITECTURE.md §6.6 */}
        <section className="data-page__section" aria-labelledby="data-licenses-heading">
          <h2 id="data-licenses-heading" className="data-page__heading">Licenses</h2>
          <p className="data-page__text">
            LSB uses a split licensing model. The license applied depends on the type of content,
            not the directory structure.
          </p>
          <dl className="data-page__dl">
            <div className="data-page__dl-row">
              <dt className="data-page__dt">Source code</dt>
              <dd className="data-page__dd"><strong>Apache 2.0</strong> — all <code>.py</code>, <code>.ts</code>, <code>.tsx</code>, <code>.js</code>, <code>.yml</code>, <code>.toml</code> files; <code>scripts/</code>; <code>packages/</code>; <code>apps/dashboard/src/</code>; CI configs.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt">Open data bundle</dt>
              <dd className="data-page__dd"><strong>CC0 1.0 Universal</strong> — <code>informants.jsonl</code>, <code>lsb.sqlite</code>, <code>build_db.py</code>, <code>DATA_DICTIONARY.md</code>, prompt templates, domain definitions, and the Backblaze B2 / Zenodo distribution.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt">Raw responses and processed results</dt>
              <dd className="data-page__dd"><strong>CC-BY-4.0</strong> — <code>data/raw/</code>, <code>data/processed/</code>, <code>data/results/</code>; HuggingFace dataset release.</dd>
            </div>
            <div className="data-page__dl-row">
              <dt className="data-page__dt">Documentation and methodology text</dt>
              <dd className="data-page__dd"><strong>CC-BY-4.0</strong> — <code>docs/</code>, <code>README.md</code>, <code>ARCHITECTURE.md</code>, methodology page on cogstructurelab.com.</dd>
            </div>
          </dl>
          <p className="data-page__text">
            All four licenses are permissive and interoperable; together they mean anyone can reuse
            any part of the project for any purpose as long as they attribute (where required).
          </p>
        </section>

        {/* ── Section H: Provenance pointer ──────────────────────────────── */}
        {/* id renamed to data-provenance-pointer-heading (M1, 2026-06-10) to avoid */}
        {/* duplicate-id collision with the moved canonical data-provenance-heading  */}
        {/* section below (WCAG 4.1.1 / aria-labelledby resolution fix).             */}
        <section className="data-page__section" aria-labelledby="data-provenance-pointer-heading">
          <h2 id="data-provenance-pointer-heading" className="data-page__heading">Provenance</h2>
          <p className="data-page__text">
            Toolchain pinning, analytical version strings, and SHA256 manifests are recorded in the
            provenance footer at the bottom of every page on this site.
          </p>
        </section>

        {/* ── Moved from MethodologyPage.tsx (M1, 2026-06-10) ──────────── */}
        {/* §15.5(a) Data provenance (PROMOTE-2, CDA SME §3 Option 1, verbatim) */}
        {/* DESIGN_SYSTEM.md §15.5(a): own <h2>, root-relative link, new tab, (JSON) affordance */}
        <section className="data-page__section" aria-labelledby="data-provenance-heading">
          <h2 id="data-provenance-heading" className="data-page__heading">Data provenance</h2>
          {/* BA-PROV (binding, CDA SME ruling F, 2026-07-13). Replaces 2026-05-30-anchored paragraph.
              Provenance.json anchor markup preserved exactly per UI/UX ruling 4. */}
          <p className="data-page__text">
            The published family, holidays, and food corpora were rebuilt on
            2026-07-12 under the same pinned analytical toolchain (NumPy 2.4.4,
            SciPy 1.17.1, Python 3.12) as the 2026-05-30 recompute, with two
            mechanical changes. First, the corpus-build QA path now class-conditions
            two of its collection-QA checks for reasoning-model informants and for
            dense-tokenizer informants (see the methodology footnote on
            informant-class QA calibration for the mechanism); persisted per-record
            verdicts on the raw records are untouched, and reference-set-dependent
            checks inherit their collection-time verdicts. Second, publication
            membership is now decided by a curator-maintained approved-slate list,
            separately from record-level QA: QA answers whether a record is fit for
            analysis, and the slate answers which models the published basis
            includes. The batch A rebuild widens each of the three published
            domains by up to seven additional frontier models. The pinned versions,
            the exact git commit, and the approved slate for each domain are
            recorded in{' '}
            <a
              href="/data/provenance.json"
              target="_blank"
              rel="noopener noreferrer"
              className="data-page__link"
            >
              provenance.json
              <span className="sr-only"> (opens data provenance manifest in new tab)</span>
              {' '}(JSON)
            </a>
            , which is regenerated on every published bundle.
          </p>
        </section>

        {/* §16.2 — Cross-model term map and uncertainty (food-promote C3/C4, UI/UX F3a) */}
        {/* Moved from MethodologyPage.tsx (M1, 2026-06-10). */}
        {/* M4a sentence: Phase 9a binding disclosure (C4). */}
        {/* C3 sentence: informant-count disclosure for term-MDS bootstrap envelope (C3). */}
        <section className="data-page__section" aria-labelledby="term-mds-heading">
          <h2 id="term-mds-heading" className="data-page__heading">Cross-model term map and uncertainty</h2>
          <p className="data-page__text">
            Term position confidence reflects agreement across models, not within-model sampling variance.
            {/* BA-TERMMAP-COUNTS (binding, CDA SME ruling G, 2026-07-13). Replaces "15 / 14 / 8" sentence. */}
            {' '}The cross-model term map is computed from 22 model informants on family,
            21 on holidays, and 19 on food; ellipse widths and branch-probability
            values are derived from model-resample bootstrap (B=200), so a sparser
            informant pool produces a different bootstrap envelope shape than a
            denser one even when the per-model agreement is similar.
          </p>
        </section>

      </div>
    </main>
  );
}
