# LSB Operator Glossary

**Audience:** Mark + anyone operating or reviewing the project. Plain-language definitions of the working vocabulary used in runbooks, status docs, gate verdicts, and session conversations. The public-facing explanation of the methodology lives on the website's methodology page; this file is the internal phrasebook. Definitions favor honesty over precision; where a term has a load-bearing technical definition, the pointer to the binding doc is given.

---

## The data lifecycle

**Campaign.** One deliberate batch of data collection, with an id like `phase9b-food-20260611`. Campaigns are the only time LSB spends money on model APIs. Everything after a campaign is computation on already-collected data.

**Collection / elicitation.** Actually interviewing the models: the free-list, pile-sort, and pile-interview prompts of the CDA protocol. Runs on this VPS via `scripts/collect.py`. Appends to `data/raw/informants.jsonl`.

**Collection mode.** Which variant of the protocol a record came from. `single_pass`: one session does free-list then pile-sort then pile-interview on the model's own items (the slate-standard mode). `cross_model_consensus`: the model sorts a shared item deck derived from everyone's free-lists (a supplement, not a substitute; mixing modes in one analysis basis caused the 2026-06-11 contamination incident). When widening a domain's slate, collect single_pass.

**Append-only.** `data/raw/*.jsonl` files are never edited, only appended. Bad records stay forever with `qa_passed=False`. Enforced by a PreToolUse hook and convention, not CI (the files are gitignored).

**QA-passed.** A record the pipeline could fully parse and that cleared the software-only quality checks. Never a judgment of whether the model's answer was "good." A model with zero QA-passing runs stays out of the analysis slate but its failures remain published findings.

**Failures are findings.** The standing directive: refusals, empty outputs, unparseable responses, and transport errors are preserved verbatim and surfaced on the Collection records page, because which prompts a model will not answer is part of its behavior.

**Re-baseline.** Re-running the entire cross-model analysis from the raw corpus, needed whenever the model set changes because every cross-model number (similarity, consensus, centrality, MDS positions) is computed across the whole slate. Output goes to staging, never straight to live. `scripts/rebaseline_corpus.py`, pinned NumPy/SciPy.

**Staging.** `out/rebaseline/`: the darkroom. Freshly computed results wait here for guards, adjudication, and the GO decision. The website never reads staging.

**Guards / guard trip.** Six automatic threshold checks the re-baseline runs against the previously published values (consensus boundary crossings, centrality sign flips, classification changes). A trip HALTS the process and writes a crossing report. A trip is not an error; it means the new data may legitimately change a published claim, so a human plus the CDA SME must rule before anything ships.

**Adjudication.** The CDA SME's ruling on a guard trip or methodology question: real signal (promote, with copy updated), artifact (investigate first), or something subtler. Recorded in the gate trail and agent memory.

**Promotion.** Moving a staged, adjudicated result into the live path: copy into `data/results/` (the official versioned record), regenerate the published JSON under `apps/dashboard/public/data/`, ship the required copy changes, commit and push. The site redeploys and the new result is public. Always gated (Reviewer, CDA SME, UI/UX); never automatic.

**Version pinning / analysis_version.** Every published `DomainResult` carries a version (food v0.1, v0.2, ...). Promotion creates a new version rather than overwriting; superseded results stay reproducible and citable forever. This is why an old classification can be honestly left live while a new one is investigated.

**Open data bundle.** The complete public dataset (raw responses, results, prompts, code, manifests) on HuggingFace/Zenodo/B2 under CC0. The dashboard is a downstream consumer of the same data.

## The pipeline (how work ships)

**The gated pipeline.** Architect, then CDA SME, then UI/UX (frontend work only), then Coder, then Reviewer, then Tester. Gates issue PASS / PASS-WITH-NOTES / FAIL; notes are mandatory, FAIL bounces the plan. Defined in CLAUDE.md section 3.

**Gate / verdict.** A gate is a checkpoint agent with veto power. A verdict is its written ruling, saved to `docs/status/` so the audit trail survives.

**Gate trail / verdicts file.** The `docs/status/YYYY-MM-DD-*-verdicts.md` file collecting every verdict for a task cycle. Commit messages reference it.

**SME-bound / byte-identical string.** Copy the CDA SME has approved word-for-word. It ships exactly as written, protected by a test asserting the exact bytes; changing it requires a fresh SME ruling.

**Stop condition.** The standing rule that an agent halts and surfaces a question rather than improvising on ambiguity (CLAUDE.md section 8). A correct stop is a success, not a failure.

**Fix-forward.** The precedent for mid-campaign bugs: patch the code, keep historical records as they are, document in the data dictionary. No backfilling, preserving the append-only audit trail.

**Worktree.** A temporary isolated git checkout each Coder works in so parallel tasks cannot contaminate each other's commits. The orchestrator merges the reviewed commit back to master.

## Measurement terms (one-liners; the methodology page is the real explanation)

**Slate.** The set of models whose data enters a domain's cross-model analysis. A model can be in the corpus but out of the slate (for example zero QA-passing runs, or wrong collection mode for the similarity basis).

**Corpus lens.** The project's name for what LSB measures: the categorical structure a model's training corpus imposes on a domain, surfaced through elicitation. Binding framing in ARCHITECTURE section 1.5.

**Eigenratio (Romney CCM).** The one-number summary of how much the slate shares a single way of organizing a domain. Above 5.0 the project labels strong consensus; below, weak. Computed across the whole slate, which is why adding models forces a re-baseline.

**Consensus type / classification.** The published label (STRONG_CONSENSUS, WEAK_CONSENSUS, ...) derived from the eigenratio. Lede-class: changing it changes a public claim, hence the guards.

**consensus_type_override.** A field letting the published label differ from the auto-derived one, with an auditable reason. Introduced for food v0.2, where the point estimate is strong-side but the uncertainty interval crosses the threshold, so the conservative label is published with the indeterminacy disclosed.

**Bootstrap / CI.** Recomputing a statistic hundreds of times over resampled data to measure how sure we are of it. The resulting interval (CI) is the uncertainty band. House rule R10: no published point estimate without its uncertainty, applied to charts and, since food v0.2, to the headline classification itself.

**OCI (Output Concentration Index).** A within-model number: how strongly one model's repeated runs converge on the same structure. Low OCI gets the dashed-marker treatment on the Model Map (R1-b).

**R10.** Shorthand for the no-point-estimate-without-uncertainty rule.

**R1-a / R1-b / R1-c.** The Model Map's three rendering states: normal dot with ellipse; low-concentration dashed treatment without ellipse; deterministic-output hollow triangle. DESIGN_SYSTEM section 3.3.5.

**Registers (1/2/3).** The discipline separating within-model statements, cross-model statements, and (historical) human-baseline statements so vocabulary from one is not smuggled into another. The noun-class test (2026-06-11 ruling): after "within-model," nouns like consensus are banned, nouns like output concentration are fine.

**Small-n warning.** The flag that a slate is below the size where the consensus method is statistically reliable (15 models). Ships visibly with any affected classification.

**Lede.** The one-paragraph finding statement at the top of a domain view. Generated in the publish layer (never client-side), CDA-gated, rendered verbatim.

---

*Maintained by hand. When a session mints a term that outlives the session, add it here.*
