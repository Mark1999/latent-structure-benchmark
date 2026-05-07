# LSB Prompt Evolution Log

**Path:** `docs/PROMPT_EVOLUTION_LOG.md`
**Status:** Canonical; append-only by convention. The Reviewer rejects in-place edits to existing entries.
**Update cadence:** one entry per prompt version directory creation; one per campaign run that consumed a version; one per documented G1 / success-rate inflection.

Per the LSB philosophy doc §9, the prompt-evolution history is itself research data preserved for community analysis.

---

## Preamble

### What this log records

This log is the authoritative narrative surface for LSB's prompt-version history. It records:

1. **Prompt-version provenance.** For each directory under `packages/cdb_collect/cdb_collect/prompts/`, the creation date, authorship, reason for creation, and design intent.
2. **Per-campaign success rates.** For each collection campaign that consumed a prompt version, the per-(model_id × prompt_version × domain_slug) success rates, once computed after campaign completion.
3. **G1 and success-rate inflections.** Any documented instance where a success-rate threshold was breached or a G1 gate verdict was issued.

The per-campaign success-rate rows in each version's table are derivable from `data/raw/informants.jsonl` and `data/raw/failures.jsonl` by the T4 success-rate computation, but the narrative context (which campaign produced which version, which model failed at which rate, why a version was created) is not derivable from the JSONL alone.

### Success-rate definition

A cell is **successful** iff it produced a valid `InformantRecord` written to `data/raw/informants.jsonl` with `qa_passed=True`.

A cell is **failed** iff it landed in `data/raw/failures.jsonl` OR produced an `InformantRecord` with `qa_passed=False`.

The per-(model_id × prompt_version × domain_slug) success rate is `n_successful / n_attempts_targeted`, where `n_attempts_targeted=5` for the variance arm and `n_attempts_targeted=30` for the saturation arm (per Phase 4b plan §2 deliverable counts).

If a cell required a retry under the 2-attempt budget, the cell counts as one attempt regardless of the number of provider calls (consistent with the recovery-report §2 retry-pattern interpretation).

Triples with success rate **< 0.80** fire an alert into this log. Triples with success rate **< 0.60** are flagged on the methodology page as known weak-coverage cells. **This metric is non-gating** — G1 is computed against whatever records exist, with insufficient-coverage triples surfaced in the gate diagnostic. Per the failures-as-findings posture, low success rate is a finding, not a kill switch.

### No mid-flight prompt iteration

A new prompt-version directory may be created **only** when one of:

1. A new SME-approved sensitivity study requires it (the 8 v1_s* variants are an instance);
2. A model's per-(model × variant × domain) success rate drops below 0.90 on **two consecutive collection campaigns** under the current version, and a new version's `Reason for creation` field cites the failure pattern verbatim;
3. An SME-approved cross-family contrast study (the v2_soft1 single-arm is an instance).

**No mid-campaign prompt iteration.** A campaign runs once at its scheduled prompt versions, reports success rates, and the log records them. If success rates trigger a v2 iteration, that iteration is a separate, post-campaign run with its own Architect plan.

---

## v1 — canonical baseline

- **Created:** 2026-04-13 (commit `cdd4f68` — M1A-T1/T2 domain loader, adapter protocol, and spend cap)
- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1/`
- **Origin:** Initial v1 design (see PHASE_0_TASKS.md); three-step CDA protocol: free-list (imperative anchor + numbered list + 200-cap), pile-sort (JSON schema + partition constraint), pile-interview (label-per-group)
- **Authored by:** Mark Dawson
- **Reason for creation:** Phase 0 / M1A foundation — the canonical prompt set for the LSB CDA elicitation protocol
- **Status:** Canonical; never edited in place

### Campaigns that consumed v1

*No campaign rows yet. Phase 4a and recovery cells were collected before this log existed; these may be backfilled as historical "pre-log" state. The saturation arm (Phase 4b T5) will add rows here when complete.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(pre-log — Phase 4a + recovery; backfill pending)* | — | — | — | — | — | — |

---

## v1_s1 through v1_s8 — imperative-anchor paraphrase variants

### Common provenance

All eight v1_s* directories were created in a single commit as the Phase 4b sensitivity-study infrastructure. They are paraphrase variants of the v1 canonical free-list prompt, preserving the imperative anchor pattern ("Do not explain or categorize" and cognates), the numbered-list structure, and the 200-item cap. The pile-sort variants preserve the JSON output schema and the partition constraint. The pile-interview prompt is identical across all v1_s* variants and across v1 (this is intentional — sensitivity at the pile-interview step is dominated by upstream pile structure, not interview phrasing).

- **Created:** 2026-04-15 (commit `7a1f2e5` — "feat(analyze): sensitivity study framework and validation gates")
- **Authored by:** Mark Dawson with Claude Opus 4.6 (1M context) assistance under the standard LSB Architect-Coder pipeline. Co-Authored-By attribution in commit `7a1f2e5`.
- **Originally authored as:** Phase 4b sensitivity infrastructure preparation, consumed canonically by Phase 4b Architect plan `5e55ba6` (2026-05-07).
- **Reason for creation:** Phase 4b G1 stability gate requires 8 paraphrased variants per ARCHITECTURE.md §5.3 to measure within-model vs between-model variance across prompt rephrasings.
- **Status:** Canonical; never edited in place

**Note (P1 confound disclosure, per Mark's option-2 ruling, 2026-05-07):** Claude Opus 4.6 is also one of the 20 models tested in the Phase 4b variance arm. The v1_s* variants were authored by Mark with Claude Opus 4.6 assistance under standard LSB review — this was not LLM-autonomous generation; Mark directed and reviewed the output. Readers evaluating per-model G1 stability for `anthropic/claude-opus-4.6` should weight this provenance accordingly. The within-model variance metric is computed per-model on its own variants; the variants are paraphrases of v1 which Mark also wrote, so the dependency is mediated.

---

### v1_s1 — paraphrase 1 (research-project framing)

- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1_s1/`
- **Free-list phrasing anchor:** "For an anthropological research project... Do not add explanations or group them by category"
- **Pile-sort:** imperative anchor preserved; JSON schema + partition constraint unchanged
- **Pile-interview:** identical to v1 (see common-provenance note)

#### Campaigns that consumed v1_s1

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

### v1_s2 — paraphrase 2 (exhaustive-listing framing)

- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1_s2/`
- **Free-list phrasing anchor:** exhaustive-listing instruction variant
- **Pile-sort:** imperative anchor preserved; JSON schema + partition constraint unchanged
- **Pile-interview:** identical to v1

#### Campaigns that consumed v1_s2

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

### v1_s3 — paraphrase 3

- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1_s3/`
- **Free-list phrasing anchor:** paraphrase 3 variant
- **Pile-sort:** imperative anchor preserved; JSON schema + partition constraint unchanged
- **Pile-interview:** identical to v1

#### Campaigns that consumed v1_s3

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

### v1_s4 — paraphrase 4 (exhausted-knowledge framing)

- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1_s4/`
- **Free-list phrasing anchor:** "Do not include any explanations, definitions, or categories alongside the items"
- **Pile-sort:** imperative anchor preserved; JSON schema + partition constraint unchanged
- **Pile-interview:** identical to v1

#### Campaigns that consumed v1_s4

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

### v1_s5 — paraphrase 5

- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1_s5/`
- **Free-list phrasing anchor:** paraphrase 5 variant
- **Pile-sort:** imperative anchor preserved; JSON schema + partition constraint unchanged
- **Pile-interview:** identical to v1

#### Campaigns that consumed v1_s5

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

### v1_s6 — paraphrase 6

- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1_s6/`
- **Free-list phrasing anchor:** paraphrase 6 variant
- **Pile-sort:** imperative anchor preserved; JSON schema + partition constraint unchanged
- **Pile-interview:** identical to v1

#### Campaigns that consumed v1_s6

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

### v1_s7 — paraphrase 7

- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1_s7/`
- **Free-list phrasing anchor:** paraphrase 7 variant
- **Pile-sort:** imperative anchor preserved; JSON schema + partition constraint unchanged
- **Pile-interview:** identical to v1

#### Campaigns that consumed v1_s7

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

### v1_s8 — paraphrase 8 (refrain-framing)

- **Path:** `packages/cdb_collect/cdb_collect/prompts/v1_s8/`
- **Free-list phrasing anchor:** "Refrain from adding any notes, explanations, or categorical headings"
- **Pile-sort:** imperative anchor preserved; JSON schema + partition constraint unchanged
- **Pile-interview:** identical to v1

#### Campaigns that consumed v1_s8

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

## v2_soft1 — softer-phrasing single-arm contrast

- **Created:** 2026-05-07 (this commit — Phase 4b T1)
- **Path:** `packages/cdb_collect/cdb_collect/prompts/v2_soft1/`
- **Authored by:** Mark Dawson with LSB orchestration agent (Sonnet 4.6) under the standard LSB Coder pipeline per Phase 4b Architect plan `5e55ba6` (Q2 option B), accepted by SME at `c4691e8`.
- **Origin:** Mark's parked 2026-05-06 observation (`docs/status/2026-05-06-v2-freelist-prompt-suggestion.md`) that the v1 free-list prompt's imperative phrasing ("Do not explain or categorize") functions as a categorical anchor. v2_soft1 is the single-arm cross-family contrast implementing the softer, request-shaped alternative.
- **Reason for creation:** SME-approved cross-family contrast study (Phase 4b plan §5 rule 3). A single-arm soft-phrasing prompt allows the v1_s* imperative-anchor cluster to be compared against a request-shaped alternative as a diagnostic sub-finding within the Phase 4b variance arm.
- **Status:** Canonical; never edited in place

**Scope rationale (orchestrator decision, 2026-05-07):** v2_soft1 differs from v1 *only at the free-list step*. The v1 pile-sort step's imperatives ("Every item must appear in exactly one pile" + JSON schema) are structural and parser-required, not stylistic — softening them would break analysis. The v1 pile-interview step is already request-shaped ("provide a short label..."), so there is nothing to soften. Per the SME's plan-verdict observation that pile-interview is identical across all v1_s* variants ("acceptable — sensitivity at this step is dominated by upstream pile structure"), v2_soft1 follows the same precedent: `v2_soft1/pile_sort.md` and `v2_soft1/pile_interview.md` are exact copies of v1.

**Single-arm framing (P3 binding for T7):** with n=1 prompt within v2, no within-v2 stability claim is supported. The methodologically interesting comparison is **between** the v1_s* cluster (8 imperative-anchor paraphrases) and the v2_soft1 single arm. Any T7 prose discussing this contrast must use positional language (e.g., "the v2_soft1 single arm sits at MDS coordinates {...} relative to the within-imperative cohort") rather than stability-comparative language ("v2 is more stable than v1").

### Campaigns that consumed v2_soft1

*No campaign rows yet. Will be populated by Phase 4b T4.*

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---

*End of prompt evolution log. Append new entries below this line. Do not edit existing entries in place.*
