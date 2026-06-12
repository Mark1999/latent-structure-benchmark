# New-Model Incorporation Runbook (discover → collect → re-baseline → promote)

**Document:** `docs/proposed/2026-06-08-new-model-incorporation-runbook.md`
**Status:** proposed — stitches the EXISTING scripts + gates into one ordered checklist.
No new tooling; every command below already exists and has been exercised (the
2026-05-29 re-baseline ran the back half end-to-end).
**Audience:** Mark (operator) + the agent pipeline.
**Companion:** `ARCHITECTURE.md` §3.2 (ModelRef), §4.1 (collection), §4.2 (analysis),
§5.3 (phase plan); `docs/PHASE_8_LAUNCH_RUNBOOK.md` (the launch analogue);
`docs/status/2026-05-29-rebaseline-completion.md` (the last real re-baseline).

> **What this is.** A single ordered list for taking a newly-released model (a new
> Opus/Sonnet, a new GPT, an entirely new provider) from "it exists on OpenRouter"
> to "it's live on cogstructurelab.com with every cross-model measure correctly
> re-computed." The process is deliberately MANUAL + GATED — there is no cron, by
> design (a new model can flip a *published* consensus classification, so a human
> must be in the loop). This runbook makes the manual path a checklist.

> **The load-bearing fact (read first).** The cross-model measures — similarity
> matrix, Romney consensus/CCM eigenratio, cultural centrality, MDS layout, OCI,
> bootstrap CIs — are computed ACROSS the whole model set. Adding one model
> retroactively changes ALL of them for the affected domain(s). You cannot just
> append the new model's rows and ship; you must re-run the cross-model analysis
> and re-promote. That is what Steps 3–5 are for.

---

## When to run this
- A flagship you track ships a new version (e.g. `claude-opus-4-7`, a new GPT).
- A genuinely new provider/family appears that's worth tracking.
- You want to widen the slate (more models per family) for a domain.

Cadence is a Phase 9 / Tier-3 decision (on-flagship-release vs monthly vs on-demand)
— **not settled**. Until it is, this runbook is invoked on demand.

---

## Step 0 — Decide scope (1 min, you)
Answer before touching anything:
- **Which model(s)?** Exact `model_id`(s) (e.g. `anthropic/claude-opus-4-7`).
- **New provider/family?** If the family is NOT already in `data/models/registry.json`
  `families` (claude/gpt/gemini/grok/llama/deepseek/mistral/qwen/command/gemma/phi/glm),
  this needs a **code edit** to `scripts/discover_models.py` `FAMILY_CONFIG` first
  (prefixes, origin, openness, tiers, preferred adapter). That edit is a Coder task
  (Architect → Coder → Reviewer), not a runbook step. Flag it and stop here.
- **Which domains?** The active set is `family`, `holidays`, `food`. A new model must
  be collected for EVERY active domain you want it to appear in (each domain re-baselines
  independently).

---

## Step 1 — Discover + register the model (~5 min, you)
```bash
cd /opt/lsb-agent
# Report what OpenRouter is offering vs what we've collected (does NOT write anything):
uv run python scripts/discover_models.py --scan
# Review the NEW / STALE / CURRENT buckets. When you're happy, commit it to the slate:
uv run python scripts/discover_models.py --update-registry
```
- `--scan` queries the OpenRouter catalog, filters to tracked families, and cross-references
  `data/raw/informants.jsonl` to show what's already collected. Read-only.
- `--update-registry` writes `data/models/registry.json` (the canonical slate). A model
  with `"records": 0` means "known but not yet collected."
- **Commit the registry change** on its own: `chore(models): register <model_id> in slate`.

**Gotcha:** `discover_models.py` only sees families in `FAMILY_CONFIG`. A new *company*
won't appear in `--scan` until that dict is extended (Step 0).

---

## Step 2 — Collect the CDA protocol for the new model (~hours, you)
Run the elicitation protocol for the new model across each active domain. Collection is
provider-parallel, so a full slate-cell is single-digit hours, not days.
```bash
# single_pass collection for ONE new model on ONE domain:
uv run python scripts/collect.py --domain family --mode single_pass \
    --model <model_id> --runs N --skip-collected \
    --campaign-id new-model-<model_id>-<yyyymmdd>
# Repeat for holidays and food (and any other active domain).
# Dry-run first to see the plan without spending:
uv run python scripts/collect.py --domain family --mode single_pass \
    --model <model_id> --dry-run
```

### Which collection mode

**`single_pass` is the correct mode for slate incorporation.** Every record in the
current promoted slate used `single_pass`. In this mode, one session does the free-list,
pile-sort, and pile-interview on the model's own items, producing the per-model item
vocabulary that the cross-model analysis requires. Use `single_pass` when adding a new
model to a domain.

**`cross_model_consensus` is a supplement, not a substitute.** It sorts a shared item
deck derived from the full slate's existing free-lists, which means it can only run
meaningfully AFTER `single_pass` data for the new model already exists and has been
incorporated. Records produced by `cross_model_consensus` have a different shape from
`single_pass` records: their free-lists carry a placeholder (`parsed_items=[]`) because
the items were supplied externally, not elicited from the model. That placeholder cannot
enter the consensus free-list basis. Running `cross_model_consensus` alone for slate
incorporation produces records with empty free-lists that are silently excluded from the
similarity basis. See the 2026-06-11 food campaign incident in
`docs/status/2026-06-11-phase9b-food-campaign.md` for the concrete failure this caused
and `docs/GLOSSARY.md` "Collection mode" for the canonical one-liner.

- `--skip-collected` is idempotent: the dedupe key is `(model_id, domain_slug)`. A
  record for the current model in the current `--domain` causes that model to be skipped
  for this run. Records in OTHER domains do not skip this domain. (Prior to commit
  `0c1d9b0` the key was bare `model_id`, which caused cross-domain false-skips; the fix
  is already in place.)
- Output appends to `data/raw/informants.jsonl` (**append-only** — never edit prior lines;
  the CI append-only check + the active `check_informants_append_only` PreToolUse hook
  enforce this).
- `scripts/qa_check.py` (the QA_Runner) watches the run and posts failures to `#lsb-alerts`.
  Failed/refused/partial runs are PRESERVED verbatim (failures-are-findings) with
  `qa_passed=False` — do not delete them.
- Sanity-check what landed: `uv run python scripts/lsb_inspect.py --model <model_id> --domain family`
  (and `--failed` to see any refusals).

**Set N intentionally.** The saturation analysis (ARCHITECTURE §4.2.7) set operational
N at the empirical knee + 20%; match the domain's existing per-model `--runs` count for
that domain so the new model is comparable. Do not assume a default-N value: check what
N the existing slate used for the target domain and match it. If unsure, this is a CDA
SME question, not an operator guess.

---

## Step 3 — Re-baseline ALL cross-model measures (staged, ~hours, you)
This is the step the load-bearing fact demands. Re-run the full analysis from the (now
larger) corpus into STAGING — it does not touch live data.
```bash
# All active domains (sequential: family → holidays → food), pinned env:
uv run python scripts/rebaseline_corpus.py
# Or one domain at a time:
uv run python scripts/rebaseline_corpus.py --domain family
# Quick smoke check of the harness first:
uv run python scripts/rebaseline_corpus.py --smoke
```
- **Must run under the pinned environment** (NumPy 2.4.4 / SciPy 1.17.1) — reproducibility
  guard. The script asserts this.
- Writes staging results to `out/rebaseline/<domain>/<version>.json` and a provenance
  manifest `out/rebaseline/baseline_manifest.json` (numpy/scipy/python/git-commit/platform).
- **Does NOT overwrite `data/results/` or the live dashboard.** Promotion is Step 5.

Note: `rebaseline_corpus.py` DOMAIN_CONFIG carries a `similarity_collection_mode` key
per domain (set to `"single_pass"` for food per FOOD-FIX-A); any stray
`cross_model_consensus` records are basis-excluded before the similarity matrix is
computed, so they cannot contaminate the cross-model measures even if they are present
in the corpus.

### The six threshold guards (the human-in-the-loop reason)
`rebaseline_corpus.py` compares the new staged result against the prior published value and
HALTS (writing `out/rebaseline/THRESHOLD-CROSSING-<domain>.md`) if the new model pushed any
of these across a boundary:

| Guard | Crossing |
|---|---|
| **T-1** | `romney_eigenratio` crosses **5.0** (STRONG ↔ WEAK consensus) |
| **T-2** | `romney_eigenratio` crosses **3.0** (WEAK ↔ TURBULENT/CONTESTED) |
| **T-3** | any `cultural_centrality_scores` entry **flips sign** |
| **T-4** | any per-model `oci` crosses **3.0** while `deterministic_output=False` |
| **T-5** | `romney_consensus_warning` flips |
| **T-6** | `consensus_type` differs from the prior published value |

**Recompute rule (added 2026-06-11, binding).** Before acting on any SME adjudication of a guard trip, mechanically recompute or directly inspect every load-bearing numeric claim in it (eigenratios, CI bounds, matrix shapes, counts, file-line citations) with a small read-only driver, and quote the recomputed values next to the SME's in the campaign status doc. AI gates do editorial review, not analysis; this rule keeps the boundary checkable. See docs/GLOSSARY.md, "Is any of this AI doing the analysis?".

**A guard trip is not a failure — it's a finding.** It means the new model legitimately
changed how the domain reads (e.g. a strong-consensus domain became contested because the
new model is an outlier). **Do NOT promote past a tripped guard.** Escalate to the Architect
+ CDA SME: the SME decides whether the shift is real signal (promote, and the lede/methodology
copy must be updated to reflect the new classification) or an artifact (investigate the new
model's runs first). This is exactly the gate that prevents a silent cron from flipping a
public claim.

---

## Step 4 — Publish to static JSON (staged → buildable)
Once Step 3's staging is clean (or the SME has cleared a guard trip), build the dashboard's
static data from the promoted results:
```bash
# scripts/publish.py wraps cdb_publish.build: reads data/results/ and writes
# apps/dashboard/public/data/*.json — flat published filenames {slug}.v{ver}.json
# + {slug}.json, manifest.json (list of domains), per-domain cooccurrence + focus1 files.
uv run python scripts/publish.py --results-dir data/results --output-dir apps/dashboard/public/data
```
- The published filename convention is FLAT (`family.v0.3.json`, fallback `family.json`) and
  `manifest.json` `domains` is a LIST of `{slug, analysis_version, model_ids, n_models}` —
  the social pipeline + dashboard both depend on this shape (see the 2026-06-04 cron fix and
  audit T1/T5). Don't regress it.
- Bump `analysis_version` when the model set changes so old `DomainResult`s stay citable.

---

## Step 5 — Gated promotion to live (the pipeline)
Promotion is the standard gated process (this is where the agent pipeline re-enters):
1. **Reviewer-gated:** copy `out/rebaseline/<domain>/<ver>.json` → `data/results/<domain>/`
   and the built JSON → `apps/dashboard/public/data/*.json`. Atomic (data + manifest together).
2. **CDA SME-gated:** add/refresh the data-provenance paragraph on the methodology surface
   (cite `baseline_manifest.json`: NumPy/SciPy versions, git commit, date). If a guard tripped
   and was cleared, the SME also signs off the updated lede/classification copy.
3. **UI/UX-gated:** the "Calculated with NumPy x / SciPy y" footer date + any per-domain
   conditional footer, sourced from the manifest.
4. Commit + push; Cloudflare Pages redeploys `cogstructurelab.com`.
5. **Verify live** (browser): the new model appears in the model selector and renders on the
   MDS plot / heatmap / centrality / term map / Focus views for each promoted domain; its
   label is the canonical `displayModel` form (T8); no point estimate without an uncertainty
   ellipse (R10).

---

## Step 6 — Social announcement (automatic, you approve)
After Step 5 redeploys, the published `manifest.json` changes → the daily detect cron's
`detect_new_model` fires → a `NEW_MODEL` trigger lands in the admin console. Then:
```bash
uv run python -m cdb_social.admin_console   # http://127.0.0.1:8050
```
Request a draft (the sole sanctioned LLM-draft site), review against §1.5 framing + §7
forbidden vocab, two-click Stage → Publish. No autonomous posting (pitfall #17 / B-1).

---

## Reproducibility / longitudinal invariants (don't break these)
- **Append-only** `data/raw/informants.jsonl` — all historical runs retained forever; nothing
  overwritten when a model is added or a version supersedes another.
- **Versioned `DomainResult`s** + `baseline_manifest.json` provenance → every prior baseline
  stays reproducible and citable (`scripts/reproduce.py` is a CI guarantee; the open-data
  bundle gives outside researchers the same).
- **`model_version_returned` ≠ `model_id`** — the longitudinal/drift join is on
  `model_version_returned` (the exact string the API returned), not the alias. Providers
  silently roll snapshots under moving aliases (pitfall #1).

---

## What this runbook does NOT yet cover (open / Tier-3 decisions)
- **Cadence** — when to run this (on each flagship release? monthly sweep? on-demand?). Phase 9
  Problem 2.2; unsettled.
- **Automation** — none of Steps 1–5 is scheduled or chained; deliberately manual+gated. If a
  future cadence decision wants partial automation, the guard-trip → SME-escalate boundary
  (Step 3) must remain a hard human gate.
- **New-provider onboarding** — extending `FAMILY_CONFIG` for a new company is a Coder task
  (Step 0), not yet a one-command operation.
- **N / saturation for a new model** — matching N to the domain's saturation knee is a CDA SME
  call (Step 2), not operator-defaulted.

---

*End. This runbook documents existing tooling; the gates inside it (CDA SME on guard trips +
provenance copy, Reviewer on promotion, UI/UX on footer) are unchanged and binding.*
