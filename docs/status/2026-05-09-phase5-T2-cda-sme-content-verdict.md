# CDA SME Content Verdict — Phase 5 T2 (template-based lede generator)

**Filed:** 2026-05-09
**Reviewer:** CDA SME (Opus)
**Commit reviewed:** `9e5a138` (HEAD) — template-based lede generator
**Plan-level verdict:** `docs/status/2026-05-09-phase5-cda-sme-plan-verdict.md` (PASS-WITH-NOTES, Q1–Q11)
**Slack channel:** `#lsb-cda-sme`
**Scope:** Q1–Q5 binding-note compliance at the dispatch-packet stage, before the Reviewer agent inspects the commit.

**Files reviewed:**
- `packages/cdb_publish/cdb_publish/lede.py` (175 lines, generator + branch logic + format helper)
- `packages/cdb_publish/cdb_publish/templates/lede_v1.py` (140 lines, 8 patterns)
- `tests/cdb_publish/test_lede.py` (639 lines, 12 tests)
- `data/results/family/0.2.json` (n=11, all R1-a, smith_s=0.7106, CI=[0.50, 0.91])
- `data/results/holidays/0.2.json` (n=9, 2 R1-b, smith_s=0.7757, CI=[0.47, 0.96])
- `packages/cdb_core/cdb_core/schemas.py` lines 195–211 (ConsensusType six-value Literal)
- `DESIGN_SYSTEM.md` §3.3.5 item 6 line 331 (verbatim all-deterministic copy)
- `ARCHITECTURE.md` §1.5 line 86 (canonical tagline; US English "categorize")

---

## VERDICT: PASS-WITH-NOTES

| Axis | Result |
|---|---|
| Axis 1 — Protocol validity | N/A (publish-layer formatter; no protocol change) |
| Axis 2 — Analytical validity | PASS-WITH-NOTES (one downstream concern, T2 itself correct) |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS |
| Register compliance | PASS (R1 OCI used as concentration descriptor in branch logic; R2 STRONG_CONSENSUS / WEAK_CONSENSUS / SUBCULTURAL / TURBULENT / CONTESTED / DETERMINISTIC properly attributed at the cross-model level; R3 N/A) |
| Vocabulary compliance | PASS (zero §1.5.4 hits in any pattern; zero T9 verb hits; zero T14 hits; zero B6 internal-state-phrase hits) |

T2 is methodologically sound and **clears the SME content gate**. PASS-WITH-NOTES rather than PASS because of one forward-carry concern (S1 below) that does not block T2 but binds Note K T4-redo or any future analysis layer that touches `DomainResult.consensus_score` semantics. Reviewer + Tester are authorized to proceed on T2 as-shipped; no rework required at T2 itself.

---

## Q1–Q5 verification (binding from plan-level verdict)

### Q1 — schema-literal ConsensusType branch predicates

**Verified.** `_select_pattern()` in `lede.py` lines 96–136 enumerates the six schema literals exactly:
- `STRONG_CONSENSUS` (line 114, with three sub-branches per Q5)
- `WEAK_CONSENSUS` (line 122)
- `SUBCULTURAL` (line 125)
- `TURBULENT` (line 128)
- `CONTESTED` (line 131)
- `DETERMINISTIC` (line 109, fast-path to `all_deterministic` pattern)

**`NO_CONSENSUS` substring scan:**
- `git grep "NO_CONSENSUS" packages/cdb_publish/` returns **2 hits, both in negation comments** (`lede.py:16` "does not exist and must never appear here", `lede_v1.py:16` "does not exist and must not appear anywhere"). These are documentation guards reinforcing the schema discipline, not branch predicates. No live-code reference to `NO_CONSENSUS` anywhere.
- `git grep "NO_CONSENSUS" tests/cdb_publish/` returns zero hits.

The Reviewer's "any string `\"NO_CONSENSUS\"` in the T2 commit is an automatic Reviewer rejection" rule (Q1 enforcement) is satisfied: the only occurrences are in negation-form documentation strings, not Literal-style references. **PASS.**

The fall-through fallback at line 134–136 (`consensus_type is None or unexpected → "turbulent"`) is methodologically defensible — `turbulent` is the descriptively weakest of the non-strong branches and avoids overclaiming. Acceptable.

### Q2 — small-n warning surface

**Verified — option (b) routing.** No pattern in `templates/lede_v1.py` embeds small-n acknowledgment in the lede sentence. This is consistent with the plan-level verdict's "Option (b) is the SME-preferred default" — small-n routes to the SourceAttribution component (T10) and the MethodologySummary block (T13), not to the lede surface.

**Forward-carry binding (carries to T10 + T13):** the small-n caveat must surface at T10 (SourceAttribution reads `romney_small_n_warning` from published JSON) and at T13 (MethodologySummary prose acknowledges small-n posture per Q9). T2 itself is not the surface; **PASS at T2**, binding forward to T10 / T13.

### Q3 — descriptive-locational vs convergence-to-truth framing

**Verified.** I read all eight patterns in `lede_v1.py` for the four sub-checks:

- **No convergence-to-truth language:** Patterns use "organized around a shared categorical structure," "shows where each model sits relative to that consensus," "different region of cognitive space," "active categorical divergence." None imply external ground truth. The phrase "the runs did not converge on a single sort" in `strong_consensus_with_low_oci` is a within-model run-to-run description, not a model-to-truth claim — methodologically correct usage of "converge" in the within-model variance sense. **PASS** but flagging in S2 (advisory) for potential audience confusion.
- **No causal language:** No "because of," "leads to," "due to," "as a result of" anywhere in the eight patterns.
- **No introspective language:** No "the model decides," "the model chooses," "the model thinks about," "the model considers." The verbs are "vocabulary is organized," "vocabulary organizes into," "models produced low output concentration," "models show negative centrality" — descriptive of output, not of internal reasoning.
- **Position language present:** "sits relative to," "located in a different region," "shows where each model sits," "diverge from it," "diverges from the rest" — all locational.

**PASS Q3.**

### Q4 — top_freelist_terms salience-rank choice

**N/A at T2.** Q4 binds T3, not T2. Out of scope for this content verdict.

### Q5 — STRONG_CONSENSUS sub-branches for R1-b

**Verified.** `_select_pattern()` lines 114–120 implements the three sub-branches exactly per Q5 binding:

```python
if result.consensus_type == "STRONG_CONSENSUS":
    n_low_oci = _count_low_oci_models(result)
    if n_low_oci > n / 2:
        return "strong_consensus_majority_low_oci"
    if n_low_oci >= 1:
        return "strong_consensus_with_low_oci"
    return "strong_consensus_homogeneous"
```

R1-b detection (`_count_low_oci_models()` lines 63–72) uses the correct definition: `not deterministic_output AND oci < OCI_LOW_CONCENTRATION_THRESHOLD` (3.0). This matches the plan-level §3.3.5 R1-state binding.

**Real-corpus validation (mental smoke):**

- **Family (n=11, all R1-a):** All 11 models have oci > 3.0; n_low_oci=0; pattern fires `strong_consensus_homogeneous`. Lede output: *"Across 11 frontier models, family vocabulary is organized around a single shared categorical structure (Smith's S = 0.71, 95% CI [0.50, 0.91]). The map below shows where each model sits relative to that consensus -- and which models diverge from it."* — matches Test 1 substring expectations.
- **Holidays (n=9, 2 R1-b):** n_low_oci=2 (oci=0.0, oci=2.55), 2 < 9/2=4.5; pattern fires `strong_consensus_with_low_oci`. Lede output: *"Across 9 frontier models, holidays vocabulary is organized around a shared categorical structure (Smith's S = 0.78, 95% CI [0.47, 0.96]). 2 of these 9 models produced low output concentration on this domain -- their position on the map is shown without a confidence ellipse, signalling that the runs did not converge on a single sort."* — matches Test 2 substring expectations including "2 of these 9 models produced low output concentration" and "confidence ellipse."

**Q5 PASS.** The Q5-binding R1-b surface is satisfied for the holidays corpus, the failures-as-findings posture is preserved (the two R1-b models are surfaced, not hidden), and the strong-consensus claim correctly does not pivot on the R1-b model positions ("their position on the map is shown without a confidence ellipse" is locational and qualified, not a superlative comparative claim about those models' divergence).

---

## Carry-forward bindings verification

### B6 (a)–(e) public-copy guardrails

I scanned all eight patterns for the five guardrail violations:

- **(a) No "incorrect" framing for predecessor work:** no "incorrect," "wrong," "flawed," "erroneous" anywhere. **PASS.**
- **(b) No cross-provider/cross-failure-mode/cross-prompt-type generalization without evidence:** patterns are scoped to "{n} frontier models" (the actual corpus count) and "{domain}" (the actual domain). No generalization beyond the slice. **PASS.**
- **(c) No internal-state claims about models:** no "the model knows," "the model believes," "the model decided," "the model preferred." Verbs apply to *output* ("vocabulary is organized," "models produced low output concentration"). **PASS.**
- **(d) No "PLUS disproportionate CN-origin decline pattern" augmentation:** N/A (Phase 5 publish layer does not surface decline patterns; this binding applies to Phase 4a Note K surfaces). **N/A.**
- **(e) No "publishable" framing:** zero hits for "publishable," "publication," "research result," "novel finding." **PASS.**

### T8 — descriptive-shape discipline

No causal language ("because," "due to," "as a result"), no introspective language ("the model decides," "the model considers"), no stimulus-as-cause framing ("when prompted with X, the model thinks Y"). Patterns describe *what the output looks like*, not *what caused it*. **PASS.**

### T9 — forbidden softer verbs

Substring scan of all eight pattern strings for `recognizes`, `recognises`, `identifies`, `interprets`, `comprehends`, `perceives` applied to models: **zero hits.** Test 10's `_FORBIDDEN_PHRASES` list (lines 442–466) substring-checks all of these in both US- and UK-English forms. **PASS.**

### T14 — no "publishable"/"publication" framing

Substring scan: zero hits in any of the eight patterns. Test 10 substring-checks both. **PASS.**

---

## All-deterministic verbatim discipline (DS §3.3.5 item 6)

**Byte-identical comparison.**

DESIGN_SYSTEM.md §3.3.5 item 6 line 331:
> *"All selected models produced deterministic output on this domain — the same categorical structure on every run. Cross-model comparison remains valid; see below. Methodology page explains what deterministic output signals about model architecture."*

`templates/lede_v1.py` lines 132–138 `all_deterministic` pattern (concatenated from the parenthesized string):
> *"All selected models produced deterministic output on this domain — the same categorical structure on every run. Cross-model comparison remains valid; see below. Methodology page explains what deterministic output signals about model architecture."*

**Byte-identical match.** Em-dash is U+2014 in both (verified by `git grep "—" packages/cdb_publish/cdb_publish/templates/lede_v1.py` returning the line). Em-dash is **not** a hyphen (-) and **not** an en-dash (–). **PASS.**

Test 8 (`test_all_deterministic_verbatim_copy`) asserts exact equality against `_ALL_DETERMINISTIC_COPY` constructed verbatim from the DS spec. The test is correct and the implementation matches. **PASS.**

Test 9 (`test_deterministic_consensus_type_verbatim_copy`) verifies that `consensus_type="DETERMINISTIC"` also routes to the same verbatim copy. This is the correct schema-literal handling per Q1; both routes (R1-c-from-all-models and R1-c-from-consensus-type) produce the same output. **PASS.**

---

## US English consistency (Q8 carry-forward from plan-level)

`grep "organis|categoris" packages/cdb_publish/` returns **one hit, in a meta-comment** at `templates/lede_v1.py:27` — "US English throughout: 'organized' not 'organised'." This is documentation explicitly marking the US-English discipline; **not** a UK-English live-code occurrence.

`grep "organize|categorize" packages/cdb_publish/` returns **9 hits, all in live patterns** (lines 12, 51, 62, 75, 99, 110, 114) plus the meta-comment. All US-English. **PASS.**

The canonical tagline at `ARCHITECTURE.md` §1.5 line 86 uses "categorize" (US English); the lede patterns are consistent with the canonical doc spelling. T13's tagline placement (separate task, separate SME content verdict) carries this forward.

---

## Tests verification

**12 tests as specified by the brief.** Coverage:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_family_real_corpus_strong_consensus_homogeneous` | Real-corpus family fixture; `strong_consensus_homogeneous` pattern; substring assertions on n, Smith's S, CI |
| 2 | `test_holidays_real_corpus_strong_consensus_with_low_oci` | Real-corpus holidays fixture; `strong_consensus_with_low_oci` pattern; **Q5 R1-b surface assertion** |
| 3 | `test_strong_consensus_majority_low_oci_pattern` | Synthetic majority-R1-b; `strong_consensus_majority_low_oci` pattern |
| 4 | `test_weak_consensus_pattern` | Synthetic WEAK_CONSENSUS |
| 5 | `test_subcultural_pattern` | Synthetic SUBCULTURAL with negative-centrality language |
| 6 | `test_turbulent_pattern` | Synthetic TURBULENT |
| 7 | `test_contested_pattern` | Synthetic CONTESTED |
| 8 | `test_all_deterministic_verbatim_copy` | All-R1-c → byte-identical DS §3.3.5 item 6 verbatim |
| 9 | `test_deterministic_consensus_type_verbatim_copy` | `consensus_type="DETERMINISTIC"` → same verbatim |
| 10 | `test_vocabulary_discipline_across_all_patterns` | §1.5.4 + T9 + T14 + B6 forbidden-phrase scan across all 9 pattern instances |
| 11 | `test_generate_lede_is_deterministic` | Same fixture → byte-identical output on two calls |
| 12 | `test_no_llm_imports_in_lede_py` | AST scan for forbidden LLM client imports (CLAUDE.md §6 R11 forward-discipline; cdb_publish is allowed in principle but T2 ships none) |

**Vocabulary test substring list completeness (Test 10 lines 442–466):**
Required by brief and present: `believes`, `thinks`, `worldview`, `the model understands`, `the model recognizes`, `the model interprets`, `the model perceives`, `the model comprehends`, `the model identifies`, `publishable`, `publication`, `cultural bias`. **Plus** UK-English `recognises` form, plus `model recognizes / identifies / interprets / comprehends / perceives` (without "the" prefix), plus B6 `the model decided / chose / preferred`. **Comprehensive.** **PASS.**

**Real API call check (CLAUDE.md §6 R9):**
Tests use either real corpus fixtures from `data/results/` (Tests 1, 2, 11) or synthetic `_build_domain_result()` constructed entirely in-memory (Tests 3–10, 12). No `requests`, `httpx`, `anthropic`, `openai`, etc. imports. **PASS.**

**Verbatim integrity test (Test 8):**
`_ALL_DETERMINISTIC_COPY` (lines 40–46) is constructed by concatenating the verbatim strings; the test asserts `lede == _ALL_DETERMINISTIC_COPY` byte-for-byte. The em-dash U+2014 is preserved. **PASS.**

---

## Findings (advisory, non-blocking)

### S1 — `consensus_score` field-name semantic ambiguity (forward-carry binding for analysis-layer SME review)

**Finding.** `cdb_core/schemas.py` line 340 docstrings `consensus_score` as "retained as alias for romney_eigenratio" — implying eigenratio values (range ~1–20+ for the LSB Romney measure). But the actual corpus content stores Smith's S (range 0.0–1.0):
- `data/results/family/0.2.json` line 9997: `consensus_score: 0.7107` (Smith's S range), `romney_eigenratio: 12.10` (eigenratio range). Both fields populated; values are clearly different measures.
- `data/results/holidays/0.2.json` line 8213: `consensus_score: 0.7757` (Smith's S range), `romney_eigenratio: 10.15` (eigenratio range).

The lede labels `consensus_score` as "Smith's S" — methodologically correct for the *actual values* in the corpus, but semantically inconsistent with the schema docstring. The lede is doing the right thing; the schema docstring is wrong, or the analysis layer wrote the wrong field, or the schema is awaiting cleanup.

**This is not a T2 defect.** The lede generator dutifully consumes whatever is in `consensus_score` and labels it "Smith's S." The corpus's actual values support that label.

**Forward-carry binding (post-Phase 5):** the `cdb_analyze` consensus-write path and the `cdb_core/schemas.py` field docstring need an SME content review to reconcile (a) field naming (`consensus_score` vs. `smiths_s` vs. `romney_eigenratio`), (b) which value the analysis layer writes, (c) which value the publish layer surfaces. If a future analysis run writes eigenratio (12.10) into `consensus_score` per the schema docstring, the lede would say "Smith's S = 12.10" which would be a methodological error. This binds **before any future analysis layer change** that touches the consensus-write path. Document for the next analysis-layer SME review (likely Note K T4-redo or the Phase 6 0.3 re-analysis preparation).

**Test 4–7 implication.** The synthetic test fixtures in Tests 4–7 use `consensus_score` values in the eigenratio range (3.8, 3.2, 2.1, 1.8), which is *not* what the corpus actually contains under that field. This makes the tests less representative of real corpus output but does not fail any assertion: the tests verify pattern-selection branch logic and substring formatting, both of which are independent of the value's range. **Acceptable for T2 testing scope.**

### S2 — "did not converge on a single sort" — within-model semantic clarity

**Finding.** The `strong_consensus_with_low_oci` pattern (lede_v1.py lines 61–69) ends with: *"signalling that the runs did not converge on a single sort."* This is a within-model description (run-to-run variance), and methodologically the word "converge" is correct — OCI is literally a concentration statistic measuring how concentrated runs are around a central tendency; low OCI means runs did not converge.

**Audience risk.** A journalist reading the lede may read "converge" as a model-to-truth claim ("the runs did not converge on the right answer") rather than as a within-model run-to-run description. The §1.5.7 exploratory framing is preserved at the protocol level (the lede describes output behavior, not normative truth) but the verb "converge" carries connotative baggage.

**Disposition.** Not a Q3 violation (the text is descriptive of within-model output behavior, not of model-to-external-truth alignment), and rewriting now risks departing from the descriptive accuracy of "convergence" in the variance sense. **Flagging for T13 methodology summary** — when T13 prose is drafted, the methodology summary should explain what "low output concentration" / "low OCI" means (the runs do not concentrate on a single categorical structure) so the lede's "did not converge" reads with the within-model meaning a journalist needs to ground the phrase. **Forward-carry binding to T13 SME content verdict.**

### S3 — Smith's S labeling consistency check (no action)

**Finding.** The lede label "Smith's S" is consistent with the docstring at `cdb_publish/templates/lede_v1.py:30` ("`{s}` -- Smith's S consensus score, formatted to 2 decimals"). The schema's field-name docstring conflict (S1) does not propagate to the lede surface because the lede chose its own label rather than echoing the schema field name. Methodologically defensible; the schema-docstring conflict is upstream.

---

## Final disposition

**Verdict:** PASS-WITH-NOTES.

**T2 itself:** PASS. No rework required. Reviewer + Tester are authorized to proceed.

**Forward-carry from T2 SME content verdict:**

| Note | Origin | Binding scope |
|---|---|---|
| **S1** | T2 content verdict | `consensus_score` semantic-ambiguity reconciliation. **BINDING on the next analysis-layer SME content review** (likely Note K T4-redo or 0.3 re-analysis preparation). The current lede is correct against the actual corpus values; the schema docstring is what diverges. |
| **S2** | T2 content verdict | "did not converge" verb usage in `strong_consensus_with_low_oci`. **ADVISORY for T13 methodology summary** — the prose should explain low-OCI semantics so the lede phrase reads with the intended within-model meaning. |
| Q2 carry | plan-level | small-n caveat at T10 SourceAttribution + T13 MethodologySummary. **BINDING on T10 + T13.** |
| Q6–Q11 | plan-level | T13 methodology summary prose. **GATED on separate SME content verdict at T13 dispatch.** |

**Posted to `#lsb-cda-sme`. Binding for T2 closure. Reviewer + Tester proceed.**

---

*End of CDA SME content verdict for Phase 5 T2. The next SME content gate is T13 (MethodologySummary prose) at the T13 dispatch packet.*
