# Architect proposals — CDA SME open questions (post-F1)

**Document name:** `docs/proposals/2026-04-20-sme-open-questions.md`
**Status:** Draft proposal — awaiting CDA SME review in the next methodology cycle
**Prepared:** 2026-04-20 (Architect agent, post Sutrop + G1-split + Register-1-wiring + DETERMINISTIC-marker + shakedown-protocol merges)
**Audience:** CDA SME agent (primary reviewer), Mark (approval), Coder (implementation reference once resolved)
**Companion docs:** `docs/SME_REVIEW.md`, `docs/BOOTSTRAP_DESIGN.md` §7 (where the five questions were flagged), `docs/briefings/2026-04-19-sme-implementation-response.md` §3, `docs/SHAKEDOWN_PROTOCOL.md`, `ARCHITECTURE.md` §4.2, §4.2.7, §5.3

---

## 0. Purpose

Five methodological questions were flagged as open at the end of the post-F1 SME review cycle (2026-04-19). Each was left provisional because resolving it cleanly required either real data, empirical calibration, or a downstream deliverable that did not yet exist. Since then:

- PR A wired Register 1 into `run_pipeline` and added the DETERMINISTIC marker.
- PR B un-deferred and implemented the G1 split.
- The shakedown protocol was drafted, machine-enforcement guardrails landed, and the `--temperature` / `--campaign-id` CLI flags were added.

Two of the five questions (Q1, Q5) are resolvable by the shakedown's real-data outputs once it runs. Q4 is resolvable by UI/UX copy work. Q2 and Q3 remain genuinely open — they require Phase 4b saturation data and Phase 4c raw-subject grounding data, respectively.

This document proposes an Architect position on each of the five questions so that (a) the CDA SME has something concrete to review, amend, or reject in their next cycle, (b) the resolution path for each question is visible, and (c) the shakedown doesn't consume empirical evidence whose interpretation is still methodologically undefined.

**Binding status:** this document is a *proposal*, not a decision. Nothing here modifies code or overrides earlier SME guidance. When the CDA SME reviews and returns verdicts, the accepted resolutions become binding and land as a follow-up PR (or PRs, one per question).

---

## 1. Question 1 — Low-OCI ellipse-suppression cutoff

### Current state

`DESIGN_SYSTEM.md` §3.3.5 defines the Register 1 display convention on Register 2 points. State R1-b fires when `oci < 3.0`: no ellipse is rendered, the point is drawn with dashed stroke and 60% fill opacity, and the tooltip names the position as "uncertain." The cutoff (3.0) is flagged **provisional** in four places: the §3.3.5 R1-b row, the four binding invariants, the Implementation requirements section, and `docs/BOOTSTRAP_DESIGN.md` §7 open question 1.

### Proposed Architect resolution

**Keep the provisional value at 3.0 until Phase 4b saturation data is in hand, then calibrate empirically.** Calibration procedure:

1. After the saturation analysis runs (Phase 4b, per `ARCHITECTURE.md` §5.3 / §4.2.7), collect the OCI values across all (model, domain, prompt_variant) cells that reached operational N.
2. Plot the OCI distribution. Identify a natural gap in the density (if one exists) between "concentrated" and "diffuse" regions.
3. If a natural gap exists, set the cutoff at the gap's trough.
4. If no natural gap exists, set the cutoff at the OCI value corresponding to the **30th percentile** of the distribution — the bottom-third of models by concentration. Rationale: the reader should see uncertainty annotation on roughly one-third of models to make the signal visually distinguishable from "most models have no ellipse."
5. The finalized cutoff ships as **one coordinated PR** touching all four surfaces simultaneously per the existing §7 commitment: `OCI_LOW_CONCENTRATION_THRESHOLD` in the TS config, any schema-level reference, the methodology-page prose, and `DESIGN_SYSTEM.md` §3.3.5. Reviewer rejects partial updates.

### Rationale

The shakedown (4 models × 2 domains × N=8) is too thin to fix the cutoff — 4 OCI values don't establish a distribution. But the shakedown will surface whether OCI at 3.0 is *bite-y* (some models below, some above) or *vacuous* (all models above or all below), which constrains the calibration direction. The final value waits for Phase 4b's fuller distribution across the 12-model slate × prompt variants.

### Resolvability status

- **Shakedown:** partial — OCI distribution across 4 models is small but directional (tells us which rough range the cutoff lives in).
- **Phase 4b:** final — the full saturation + sensitivity data produces the calibration-ready OCI distribution.

### What the CDA SME needs to decide

- Is the 30th-percentile default correct, or should it be 25th or 40th? The principle is "signal distinguishable from background," not a specific percentile.
- Is a "natural gap" rule (calibration step 2) too judgment-heavy? If so, lock in percentile-only.
- Should the cutoff be per-domain rather than global? A single global cutoff is simpler; a per-domain cutoff might be more honest if some domains are structurally lower-concentration than others. The Architect lean is global for v1, per-domain for v2.

---

## 2. Question 2 — Saturation-N × compute budget

### Current state

`ARCHITECTURE.md` §4.2.7 specifies the saturation sweep: Claude Opus 4.6 + GPT-4o + Llama 3.1 70B across family + holidays, sweeping N = 5, 10, 15, 20, 25, 30. `docs/BOOTSTRAP_DESIGN.md` §7 flags the open question as "whether Register 1 bootstrap should use that N or something smaller to reduce compute further." The default for v1 is "use operational N."

### Proposed Architect resolution

**Use the saturation-analysis-derived operational N for Register 1 bootstrap. Do not reduce below that.** Reasoning:

1. The saturation analysis's *purpose* is to identify the minimum N at which within-model results stabilize. Using a smaller N for bootstrap would deliberately sample below the point where results stabilize — producing a CI on a noisier signal than the point estimate.
2. Compute cost is dominated by the bootstrap resampling factor (B=500), not the N per resample. Reducing N from (say) 20 to 10 saves ~50% on per-bootstrap cost, but the B=500 factor dominates the overall runtime.
3. The Phase 4a monthly spend cap ($300) already accounts for the full operational N; there is no budget pressure to go lower.

If compute *does* become a bottleneck at v2 scale (larger model slate, more domains, higher B), the first lever to pull is **reducing B to 200** rather than reducing N. B=200 still gives stable CIs at typical matrix sizes; N < operational is methodologically worse than B=200.

### Rationale

The saturation analysis's output — operational N — is already a "this is the smallest you can afford" number. Going below it is deliberately under-sampling. The architect's strong prior is that N is load-bearing and B is elastic.

### Resolvability status

- **Shakedown:** no — saturation analysis is not in the shakedown scope; operational N comes from Phase 4b.
- **Phase 4b:** yes — saturation analysis produces operational N, and the compute budget is observable once Phase 4a has run.

### What the CDA SME needs to decide

- Is the "N load-bearing, B elastic" ordering correct methodologically? It is standard in bootstrap literature (larger N > more bootstraps when forced to choose) but the CDA SME may have a specific objection.
- Should there be a minimum N floor independent of saturation (e.g., N ≥ 10 regardless) to prevent a degenerate "saturation analysis said N=5 is sufficient" result from shipping results on N=5?

---

## 3. Question 3 — Human-OCI bootstrap treatment (purposive samples)

### Current state

`docs/BOOTSTRAP_DESIGN.md` §7 notes: *"if the human subject pool is a purposive or convenience sample from one community, the CI does not reflect cross-population variance."* `GroundingRef.human_oci` field exists (per schema) with the current plan being: bootstrap subjects with replacement, report the CI with the standard `underestimates_uncertainty=True` flag. The SME previously flagged that human samples produce the **opposite** underestimation direction from model samples — the CI is narrow *because the population sampled is narrow*, not because N is effectively smaller than nominal.

### Proposed Architect resolution

**Two changes when `human_oci` is populated:**

1. **Add a new `human_oci_sample_type: Literal["purposive", "representative", "random", "unknown"]` field to `GroundingRef`** (schema change, requires Architect sign-off — which this proposal surfaces). The field is populated at researcher-grounding-submission time from a dropdown on the submission form; defaults to `"unknown"` if not specified.
2. **Add a binding methodology-page note** (on any human baseline that has `human_oci` populated) that reads verbatim:

   > "Human OCI is computed by resampling subjects with replacement from the baseline's `pile_sort_raw.csv`. For purposive or convenience samples (the typical case for early CDA literature), the bootstrap CI under-estimates uncertainty because the sample is not random with respect to the population of interest. A narrow CI here means 'these specific subjects agree with each other,' not 'humans in general would agree.' Treat human OCI as a within-sample concentration statistic, not as a population-level estimate."

The first change lets the dashboard condition its visual treatment on `sample_type` (similar to the Register 2 R1-b/R1-c distinction): `purposive` samples get a different marker annotation than `random` samples would. The second change locks in the caveat so it ships alongside every human OCI, not as an afterthought.

### Rationale

The single `underestimates_uncertainty` flag is the wrong shape for the human case. For models, `True` means "narrow because draws are correlated through one stochastic process." For purposive human samples, `True` means "narrow because the sample doesn't cover population variance." These are different mechanisms with different implications. Distinguishing them at the schema level (via `sample_type`) rather than conflating them under a single flag is the honest approach.

### Resolvability status

- **Shakedown:** no — the shakedown uses only models, no human grounding data.
- **Phase 4c (human baseline acquisition):** partial — the Romney 1996 baseline is an aggregate similarity matrix without raw subject data, so `human_oci` is not populated for it. The first researcher submission with `pile_sort_raw.csv` is when this question becomes operational, which is Phase 6+ in the plan.
- **Now:** resolvable at the schema level (adding the field) even before any researcher submission arrives. Recommended to land the schema change pre-emptively so the submission form can use it.

### What the CDA SME needs to decide

- Is `Literal["purposive", "representative", "random", "unknown"]` the right four values? Other anthropological vocabulary (convenience sample, stratified sample) may warrant inclusion.
- Is the proposed methodology-page copy correct, or does it overstate/understate the purposive-sample caveat?
- Should `unknown` be the default, or should the submission form require the researcher to pick explicitly (refuse the submission if unspecified)? Architect lean: require explicit choice, with `unknown` only for legacy imports.

---

## 4. Question 4 — G2 rename sufficiency

### Current state

The G2 gate is the "inter-model similarity dispersion permutation test" (renamed in the post-F1 cycle from "cultural consensus permutation test" to disambiguate from the Romney CCM). The rename is accurate but dense — "inter-model similarity dispersion permutation test" is a mouthful for any surface the dashboard user sees.

### Proposed Architect resolution

**Two-tier vocabulary:**

- **Technical contexts** (code, `docs/DATA_DICTIONARY.md`, `ARCHITECTURE.md`, open data bundle schemas, methodology-page footnotes): keep "inter-model similarity dispersion permutation test."
- **Dashboard / methodology-page body text** (the places a journalist reads): rename to **"structure test"** with an inline gloss on first mention: *"The structure test asks whether the differences between models' categorical structure are larger than random fluctuation. Pass = the models differ in ways that are not just noise."*

The full technical name is one click away (the gloss links to the methodology-page footnote). The short name is four words and readable.

### Rationale

Dense jargon on the primary surface is a user-interface regression from the "credible to a skeptical journalist" bar in `ARCHITECTURE.md` §1.5.6. At the same time, renaming the code-level identifier or schema field is a breaking change that nobody benefits from. The two-tier approach lets the technical audit trail stay precise while the public surface stays readable.

### Resolvability status

- **Shakedown:** yes, partially — the shakedown will include a first real G2 gate evaluation, and seeing the output of the rendered dashboard with the proposed "structure test" name against real data is the fastest way to verify it reads cleanly.
- **UI/UX agent:** binding — they own `DESIGN_SYSTEM.md` copy and methodology-page wording.

### What the CDA SME needs to decide

- Is "structure test" accurate enough, or does the short name mislead the reader about what G2 actually tests? Alternative candidates: "structure signal test," "cross-model structure test," "non-random structure test." Architect lean: "structure test" with the one-line gloss.
- Is the two-tier split (technical vs body) acceptable, or should the full name appear consistently everywhere?

---

## 5. Question 5 — "Mismatch is the finding" methods-page lead-paragraph verification

### Current state

`ARCHITECTURE.md` §1.5.6 makes it binding that "the mismatch is the finding" is the lead paragraph of the public methods page. The Reviewer agent rejects any methods-page draft that does not open with this framing. But no methods-page draft exists yet — the methodology page is Phase 5/6 per §5.3, and this question was flagged as resolvable only "when drafted."

### Proposed Architect resolution

**Draft the methods-page lead paragraph now**, using the shakedown's first real `DomainResult` as the concrete example. Review it in the next CDA SME cycle. The proposed draft:

> *"The Latent Structure Benchmark applies methods developed for studying human cultural knowledge — free listing, pile sorting, pile interviews — to large language models. It treats the model as if it were a cultural informant. The 'as if' is the point, not a concession: what happens when a methodology designed for people with lived experience is pointed at a system that synthesizes patterns from text? The **mismatch is the finding**. Where model outputs align with the methodology's assumptions, we learn what the model encodes. Where they don't, we learn something else about the model — and about the limits of the methodology. Both are results. This page explains what LSB measures, what it does not, and how to read the numbers honestly."*

This draft is ~120 words, opens with the disciplinary framing, names the mismatch explicitly (bolded), gives both readings (align → what's encoded; misalign → what's different), and closes with a pointer to the rest of the methods page. It does not use any §1.5.4 forbidden vocabulary ("worldview," "believes," "thinks," "within-model consensus" — all absent). It does not promise any cross-architecture claim that requires Phase 4 data.

### Rationale

A draft-now approach gets the methodology-page lead into review before Phase 5 kickoff, so the CDA SME can iterate on the prose across multiple cycles rather than seeing it for the first time under release pressure. The shakedown's first real `DomainResult` provides the concrete numbers that a later draft will anchor to, but the lead paragraph is framing — it doesn't depend on specific numbers and should be locked in before Phase 5.

### Resolvability status

- **Now:** yes — the draft above is the Architect's first pass, ready for CDA SME review in the next methodology cycle.
- **Shakedown:** augments — after the shakedown runs, the draft can be extended with a concrete mini-example drawn from a real DomainResult, which makes the abstract "mismatch" concrete for a journalist.

### What the CDA SME needs to decide

- Does the draft correctly lead with "mismatch is the finding" rather than burying it?
- Is the two-reading frame ("align → encoded, misalign → something else about the model and the methodology") correct, or does it overstate what a misalignment tells us?
- Is the ~120-word length right, or should it be shorter (headline-style) / longer (full-abstract style)?

---

## 6. What the CDA SME does with this document

This is a **proposal**, not a PR template or a decision. The CDA SME should, in their next methodology cycle:

1. **Per question, issue a verdict** using their standard four-axis PASS / PASS-WITH-NOTES / FAIL format. A PASS means "Architect resolution is adopted; Coder may now implement." PASS-WITH-NOTES means "adopt with the noted amendments." FAIL means "the Architect proposal is wrong; here's why."
2. **If any question's verdict is PASS or PASS-WITH-NOTES**, the resolution becomes binding and lands as a follow-up PR — one per question, not bundled, per CLAUDE.md §8 "one PR per task." Q4 is the cheapest (doc edit); Q3 is the most expensive (schema change + methodology-page copy + researcher submission form).
3. **If any question is answered "wait for data,"** note which shakedown / Phase 4a artifact resolves it, and queue the re-review for that point.
4. **Post verdict to `#lsb-cda-sme`** per the standard protocol; link back to this document and to the relevant question number.

The Architect commits to updating this document if the CDA SME's amendments materially change any proposal, so that the resolution trail stays auditable.

---

## 7. Summary table

| # | Question | Architect proposal | Resolvable by |
|---|---|---|---|
| 1 | Low-OCI ellipse cutoff | Keep provisional 3.0; calibrate at Phase 4b to 30th-percentile or natural gap; one coordinated PR touches all four surfaces | Phase 4b (partial direction from shakedown) |
| 2 | Saturation-N × compute | Use operational N; if budget pressure, reduce B before N | Phase 4b |
| 3 | Human-OCI purposive samples | Add `human_oci_sample_type` enum to `GroundingRef` + binding methodology-page caveat | Schema-level now; operationally Phase 6+ |
| 4 | G2 rename sufficiency | Two-tier: keep technical name in code/schema/dict; use "structure test" on dashboard body text with one-line gloss | Shakedown (partial) + UI/UX |
| 5 | "Mismatch is the finding" lead | Draft included; CDA SME reviews; locks in before Phase 5 kickoff | Now |

---

*End of proposal. Route to `#lsb-cda-sme` for the next methodology review cycle.*
