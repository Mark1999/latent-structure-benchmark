# Independent Audit Assessment

**Project:** Latent Structure Benchmark (LSB) / Cognitive Structure Lab  
**Prepared for:** AI coding team  
**Prepared by:** Independent external auditor  
**Date:** 2026-04-21  
**Assessment basis:** Read-only inspection of repository documentation, schemas, collection and analysis code, QA and packaging scripts, and current frontend entrypoint. No code was executed. No tests were run. No repository changes were made.

---

## Executive Summary

This project is stronger than a typical speculative "vibe coding" prototype. The repository shows a serious attempt to define a methodological frame, preserve raw provenance, separate collection from analysis, and publish results through a website-first artifact rather than a paper-first workflow.

The core judgment is:

- **The architecture is credible and unusually well specified.**
- **The data integrity posture is materially better than average for an early-stage AI benchmark project.**
- **The implementation is not yet fully caught up to the architecture.**
- **The project is viable as a website-first public research artifact, provided the team narrows the gap between documented intent and live behavior before broad release.**

If the site launched today, the strongest external reaction would likely be:

- positive on originality, seriousness, and transparency;
- skeptical on whether all claimed analytical machinery is fully implemented yet;
- skeptical on whether the frontend/public artifact currently matches the sophistication of the underlying method docs.

My overall audit opinion is:

> **Promising and defensible, but not yet publication-grade as a public benchmark artifact without additional implementation hardening and scope discipline.**

---

## Scope of Inspection

I inspected the following categories of material:

- Governing docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `CLAUDE.md`
  - `DESIGN_SYSTEM.md`
  - `docs/DATA_DICTIONARY.md`
- Workspace/package definitions:
  - root `pyproject.toml`
  - package `pyproject.toml` files
- Core schemas:
  - `packages/cdb_core/cdb_core/schemas.py`
- Collection layer:
  - `packages/cdb_collect/cdb_collect/runner.py`
  - collection protocol modules
  - Anthropic and OpenAI-compatible adapters
  - `scripts/collect.py`
- Analysis and packaging:
  - `packages/cdb_analyze/cdb_analyze/pipeline.py`
  - `scripts/analyze.py`
  - `scripts/qa_check.py`
  - `scripts/build_db.py`
  - `packages/cdb_publish/cdb_publish/__init__.py`
- Frontend entrypoint:
  - `apps/dashboard/package.json`
  - `apps/dashboard/src/App.tsx`

This assessment is therefore strongest on:

- architecture and product framing;
- data contracts and provenance;
- collection and analysis pipeline intent;
- implementation maturity relative to stated goals.

It is weaker on:

- runtime correctness under execution;
- actual dataset quality;
- production deployment readiness;
- CI health and test coverage, since nothing was executed.

---

## What the Project Is Doing Well

### 1. The project has a real conceptual center

The repo is not a pile of disconnected experiments. It has a stable organizing idea:

- use CDA-style elicitation as the observation method;
- treat models as informants for measurement purposes only;
- measure model-imposed categorical structure rather than "belief" or "worldview";
- publish through a public-facing website supported by reproducible data and method pages.

This is important. Many early AI projects fail because they do not know what they are measuring. This repo does.

### 2. The architecture reflects serious methodological caution

The strongest architectural choices are:

- raw-first storage;
- explicit schema contracts;
- append-only historical record intent;
- deterministic analysis boundary;
- no-LLM-in-analysis rule;
- strong attention to provenance, versioning, and uncertainty;
- explicit language guardrails to prevent overclaiming.

That is a materially better posture than most early benchmark projects.

### 3. Raw data provenance is a genuine strength

The `InformantRecord` design is one of the strongest parts of the repo. It captures:

- exact prompts and exact outputs for all three CDA steps;
- provider request IDs;
- model version strings returned by the provider;
- token and latency metadata;
- parsed and verbatim forms;
- SHA256 manifest data;
- QA verdicts.

This is exactly the kind of design choice that helps a public benchmark survive criticism later.

### 4. The project correctly separates collection from analysis

The repo consistently enforces the idea that:

- `cdb_collect` gathers raw records;
- `cdb_analyze` performs deterministic numerical/statistical work;
- `cdb_publish` and the dashboard are presentation layers.

That separation is technically and epistemically sound.

### 5. The repo is already aligned to a website-first artifact

Given the stated decision not to pursue journals, the repo is unusually well aligned with a website-first strategy:

- the docs repeatedly treat the site as the artifact;
- the design system assumes an explorable public-facing instrument;
- the static publish model is appropriate for reproducibility and cost control;
- the data and citation affordances are already part of the intended system design.

This is a good strategic fit for the project.

---

## Principal Findings

The findings below are ordered by practical importance, not by how easy they are to fix.

### Finding 1: Documentation maturity exceeds implementation maturity

**Severity:** High  
**Risk:** External credibility risk

The architecture, design system, and data dictionary are significantly more mature than parts of the live implementation.

The clearest evidence:

- the docs describe a highly developed dashboard and public artifact;
- `apps/dashboard/src/App.tsx` is still a placeholder;
- many richer analytical concepts are defined in schemas and docs, but the main analysis pipeline appears to populate only a subset of them.

This is not unusual in an early project, but it becomes a problem if the public-facing claims are allowed to drift ahead of the live system.

**Implication:** The team must be disciplined about claiming only what is actually implemented and shipped.

### Finding 2: The current analysis pipeline still contains placeholder or partial analytical machinery

**Severity:** High  
**Risk:** Methodological overstatement risk

The current `cdb_analyze` pipeline is credible in structure, but some of the richer measurement apparatus described in the docs is not obviously fully realized in the main orchestration path.

Examples:

- `consensus_score` in the pipeline is currently described and implemented as a placeholder proxy rather than full cultural consensus analysis.
- Numerous richer fields exist in `DomainResult` and related schemas, but the current pipeline does not appear to fully populate all of them.
- Grounding support is strongly represented in the architecture and schema layer, but the inspected analysis entrypoint currently returns empty grounding/default values.

This does not invalidate the project. It does mean the coding team must distinguish:

- what is **specified**,
- what is **partially scaffolded**,
- and what is **actually computed today**.

### Finding 3: The project’s strongest claims are productively narrow; they must stay narrow

**Severity:** High  
**Risk:** Public misinterpretation risk

The project is careful in its docs not to claim that it measures model beliefs, worldviews, or cognition. That caution is correct and necessary.

The danger is not in the current docs. The danger is in future copy, UI text, social sharing, and convenience summaries. A website-first artifact will be judged by its public-facing language more than by its internal schema discipline.

If the public site drifts into anthropomorphic wording, the project will invite avoidable criticism from both technical and academic audiences.

**Implication:** public copy review is not optional. It is a core integrity control.

### Finding 4: The integrity model is strong on provenance but not yet fully demonstrated on reproducibility

**Severity:** Medium-High  
**Risk:** Trust gap

The repo has strong design choices for data integrity:

- append-only raw storage intent;
- SHA256 manifests;
- provider request IDs;
- deterministic QA checks;
- regenerable SQLite packaging.

However, because I did not execute the system, the project has not yet demonstrated to me:

- end-to-end reproducibility under real runs;
- statistical stability of results across realistic campaigns;
- tight consistency between all documented outputs and the generated artifacts.

This is not a design flaw. It is a maturity gap.

### Finding 5: QA exists and is meaningful, but threshold governance needs explicit empirical ownership

**Severity:** Medium  
**Risk:** Reviewer challenge risk

The QA layer is one of the better parts of the implementation. The checks are concrete and operationally useful.

However, at least some thresholds in `scripts/qa_check.py` are already justified in comments by observed model behavior rather than by a stable externally legible methodology. That is understandable, but it means the team should expect questions like:

- Why this threshold and not another?
- Is the threshold domain-specific?
- Is it stable across providers and model families?
- Is it a methodological rule or an operational heuristic?

This should be treated as a documented calibration problem, not an embarrassment.

### Finding 6: The website is strategically correct, but the current frontend is not yet carrying the project’s weight

**Severity:** Medium  
**Risk:** Delivery risk

The website-first strategy is correct for this project. The current inspected frontend implementation is not yet at the level required to serve as the primary publication artifact.

The gap is not merely visual polish. It is functional:

- result explanation;
- trust signaling;
- model/domain exploration;
- provenance visibility;
- uncertainty display;
- citation/export flows.

The site needs to be strong enough to function as:

- the explanation,
- the evidence interface,
- and the shareable publication surface.

### Finding 7: The project has a plausible external audience

**Severity:** Low  
**Risk:** Positioning risk if mis-targeted

This is not a mass-market consumer product. It does have plausible audiences:

- AI eval and benchmark researchers;
- alignment and safety teams;
- interpretability-adjacent researchers;
- HCI and social-science researchers;
- journalists and policy analysts interested in model differences.

The team should not position it as entertainment or a generalized "which AI is best?" leaderboard. Its strongest positioning is as a **public research instrument / comparative behavior atlas / website-native benchmark**.

---

## Audit Opinion on Data and Analysis Integrity

### Raw data integrity

**Opinion:** Strong for current stage

The raw data model is a major asset. It is more careful than average and clearly designed with future criticism in mind.

Most important positive signals:

- verbatim prompt/response capture;
- per-step storage across the CDA workflow;
- provider request IDs;
- returned model version strings;
- manifest hashing;
- explicit QA state.

If maintained consistently, this layer should stand up well under scrutiny.

### Analysis integrity

**Opinion:** Structurally strong, not yet fully evidenced

The deterministic analysis boundary is exactly right. The prohibition on LLM use inside `cdb_analyze` is an excellent choice and should not be weakened.

What still needs work is not the principle but the evidence:

- Are all claimed measures implemented?
- Are they stable under reruns?
- Are uncertainty estimates defensible?
- Are placeholder fields clearly separated from mature ones?

### Output integrity

**Opinion:** Moderate risk until frontend/public copy is hardened

The main output risk is not silent numerical corruption. It is public overinterpretation or overclaiming through the website surface.

This is solvable through:

- conservative copy;
- visible methodology;
- visible caveats;
- and stable provenance/citation affordances.

---

## Will It Stand Up to Rigorous SME Review?

### Human methodological SMEs

**Likely reaction:** Interested but demanding

A strong human SME is likely to say:

- the framing is more careful than average;
- the raw data and provenance model are impressive;
- the conceptual distinction between corpus structure and cognition is correct;
- but the team must prove that the implemented measures fully match the theoretical claims.

This project is much more likely to earn serious attention than dismissal. It is not yet guaranteed a clean pass.

### Technical AI SMEs

**Likely reaction:** Respect for structure, questions about implementation completeness

Technical reviewers will likely respect:

- the schema discipline;
- the deterministic boundary;
- the versioning/provenance choices;
- the website-first clarity.

They will likely challenge:

- placeholder versus final metrics;
- calibration of QA thresholds;
- cross-model comparability assumptions;
- and the distance between docs and shipping UI.

### AI-based reviewer systems

**Likely reaction:** Positive on organization, mixed on maturity

Automated or AI-assisted reviewers will likely score the repo well on:

- explicitness;
- reproducibility intent;
- architecture coherence;
- separation of concerns.

They will likely flag:

- incomplete dashboard implementation;
- placeholders in analysis;
- and any mismatch between claims and live code.

### Bottom-line SME judgment

**My answer:** It is credible enough to engage serious SMEs, but not yet mature enough to assume easy acceptance without pointed critique.

That is a good place to be. It means the project has enough substance to matter.

---

## Priority Recommendations for the Coding Team

### Priority 1: Create a formal "implemented vs specified" map

The team needs a single source of truth that says, for each major analytical and product feature:

- specified in docs;
- scaffolded in schema;
- implemented in code;
- exposed in output;
- visible on site.

This will prevent accidental overclaiming and reduce internal confusion.

### Priority 2: Freeze the public claim surface to implemented reality

Before public launch, the team should audit every public-facing phrase and ensure it matches what the system actually computes today.

Especially sensitive:

- what "consensus" means;
- what "grounding" is live versus planned;
- what drift is actually measured;
- what is generated versus hand-authored;
- what is fully reproducible today.

### Priority 3: Finish the website as an instrument, not a placeholder

The project’s chosen publication surface is the website. That means the frontend is not decorative work. It is core method delivery.

The first public version should prioritize:

- one trustworthy primary explorer;
- visible uncertainty;
- stable citations and permalinks;
- strong methodology and caveat pages;
- download access to underlying data for the displayed result.

### Priority 4: Harden metric maturity and label placeholders explicitly

Any metric that is still provisional, approximate, or proxy-based should be labeled as such internally and externally until upgraded.

This includes:

- placeholder consensus proxies;
- partially wired grounding fields;
- any schema fields not populated in the main run path;
- any derived outputs not yet backed by stable tests.

### Priority 5: Treat copy review as an integrity control

The writing layer is part of the method.

Establish a mandatory review pass for:

- homepage text;
- chart captions;
- domain ledes;
- methodology summaries;
- social/export text;
- tooltip language.

The rule should be simple:

- no anthropomorphic overreach;
- no rhetorical inflation;
- no claim that cannot be tied back to a computed artifact.

### Priority 6: Produce a reproducibility demonstration bundle before major launch

Before broad sharing, the team should be able to demonstrate:

- raw JSONL -> analysis output;
- raw JSONL -> SQLite bundle;
- versioned result reproduction;
- a small canonical run that can be rebuilt cleanly.

This does not need to be journal-grade supplementary material. It does need to be real and inspectable.

---

## Suggested Launch Standard

I would consider the project ready for broad public exposure when all of the following are true:

- the website reflects live implementation rather than aspirational docs;
- the primary displayed metrics are fully implemented and named conservatively;
- every visible result page exposes method, date, model version, and provenance links;
- the team can reproduce at least a small canonical result end-to-end;
- raw/output/download pathways are coherent and documented;
- all public copy has been checked for overclaiming.

If those conditions are met, the project does not need a journal to be taken seriously.

---

## Final Assessment

This repository is not "just" a vibe-coded curiosity anymore. It has crossed into the category of a real research-grade public instrument in development.

Its main strengths are:

- conceptual coherence;
- strong provenance design;
- disciplined schema thinking;
- careful separation of collection, analysis, and publication;
- correct instinct to publish as a website-native artifact.

Its main risks are:

- implementation lag behind documentation;
- provisional analytical machinery being mistaken for mature results;
- a public-facing website not yet strong enough to bear the project’s epistemic burden;
- future copy drifting into overclaim.

My independent auditor conclusion is:

> **The project is worth continuing and worth taking seriously. The shortest path to credibility is not more conceptual expansion. It is disciplined closure of the gap between architecture, analysis implementation, and the website artifact.**

