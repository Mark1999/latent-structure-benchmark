---
name: within-model-phrase-ruling
description: Binding ruling 2026-06-11 RATIFYING "within-model output concentration" / "within-model distribution" / "within-model sampling variance" / "within-model co-occurrence" as register-licit scoping adjectives over §1.5.4. The four banned rows ban "within-model" only when paired with consensus / cultural-consensus / eigenratio / CCM (RWB-importing nouns). Resolves G7-FOLLOWUP-T1 advisory A5 with NO code change. MDSPlot.tsx L298, DataPage.tsx L281, Focus1TermStability.tsx L134 all stand. T-MDS-R1 F3 string remains canonical.
metadata:
  type: project
---

# "Within-model" as a scoping adjective: binding ruling 2026-06-11

## Ruling

**(a) RATIFY.** The L298 MDSPlot R1-b tooltip string — `"Position uncertain. This model's within-model output concentration is low (OCI = X.X; higher means runs converge on one structure). See model profile for within-model distribution."` — is **register-licit** under ARCHITECTURE.md §1.5.4. **G7-FOLLOWUP-T1 advisory A5 is resolved with NO code change.** The two cross-surface usages cited in the dispatch (DataPage.tsx L281, Focus1TermStability.tsx L134) are likewise ratified.

## Rationale

### The §1.5.4 rule is a noun-class rule, not a bare adjective rule

The four banned rows in ARCHITECTURE.md §1.5.4 (lines 172–175) ban specific noun phrases:

| Banned phrase | Banned because the right-hand noun is... |
|---|---|
| Within-model **consensus** | A claim about cultural agreement; imports RWB informant-independence |
| Within-model **cultural consensus** | Same, made explicit |
| Within-model **eigenratio** | Names the statistic by its R2 (RWB CCM) name; the R1 statistic is OCI |
| Within-model **CCM** | Names the R2 method directly at R1 |

The closing paragraph of §1.5.4 (line 179) states the rule's purpose verbatim: "Calling it 'within-model consensus' imports assumptions that do not apply and will be rejected by the Reviewer." The hazard is **noun-class transfer**, not the adjective "within-model" itself.

ARCHITECTURE.md uses "within-model" as a scoping adjective in its own canonical headings: §4.2.0 line 846 — `"**Register 1 — Output distribution analysis (within-model):**"` — and §1.5.4 line 173 right-hand-column replacement explicitly substitutes the banned phrase with `"Output distribution analysis"`, which §4.2.0 then scopes as "within-model" in the heading itself. The architecture document treats "within-model" as the **correct scoping adjective for Register 1**.

### Applying the noun-class test to the three live surfaces

| Surface | Phrase | Right-hand noun | Register / verdict |
|---|---|---|---|
| MDSPlot.tsx L298 (T-MDS-R1 F3) | "within-model output concentration" | **output concentration** | R1a (OCI is canonical name); LICIT |
| MDSPlot.tsx L298 (T-MDS-R1 F3) | "within-model distribution" | **distribution** | R1 output distribution analysis; LICIT |
| DataPage.tsx L281 (§16.2 SME-verbatim) | "within-model sampling variance" | **sampling variance** | R1a sampling-stochasticity language; LICIT (and the sentence is a binding cross-register guard already — it names that bootstrap CIs are R2, not R1) |
| Focus1TermStability.tsx L134 | "within-model co-occurrence" | **co-occurrence** | R1 raw input matrix (not a statistic claim); LICIT |

None of the four nouns (`output concentration`, `distribution`, `sampling variance`, `co-occurrence`) imports RWB informant-independence. None is a CCM-family name. All four are correctly scoped R1 nouns.

### Why "output concentration" specifically is the R1a noun

§4.2.0 line 850 establishes the canonical naming: "The canonical name for the R1a eigenratio is the **Output Concentration Index (OCI)**." The tooltip uses the canonical noun phrase ("output concentration") and the canonical metric name ("OCI") in the same sentence. This is the load-bearing R1-vs-R2 disambiguation the §1.5.4 guard exists to protect. The string does the protection the rule was written for; it is not a violation of it.

### The same-day A5 advisory: corrected on review

In the G7-FOLLOWUP-T1 plan verdict §A5, the SME flagged MDSPlot L298 (originally noted as L284 — line shifted with the wrap; the canonical line at ratification is L298) as a §1.5.4 violation requiring its own verdict cycle. That advisory was over-cautious: the noun-class test above is the operative test, and "within-model output concentration" is on the licit side of the line. The advisory is **withdrawn** by this ruling.

The cycle that the A5 advisory promised happened — this ruling **is** that cycle — and it resolves to RATIFY.

## How to apply

- **No code change at MDSPlot.tsx L298.** T-MDS-R1 F3 string stands byte-identical.
- **No code change at DataPage.tsx L281.** §16.2 SME-verbatim sentence stands.
- **No code change at Focus1TermStability.tsx L134.** Within-model co-occurrence label stands.
- **For any future SME review touching "within-model":** apply the noun-class test (look at the right-hand noun). The four banned partners are `consensus`, `cultural consensus`, `eigenratio`, `CCM`. Any other R1-scoped noun (`output concentration`, `distribution`, `sampling variance`, `output variance`, `co-occurrence`, `runs`, `output`, `sample`) is licit when "within-model" is the scoping adjective.
- **The "register confusion" risk does not migrate to scoping adjectives.** It migrates to *statistic names*. Defend the noun side of the phrase; the adjective is fine.

## Related

- [[project_g7_followup_t1_plan_verdict]] — A5 originated here and is resolved here
- [[project_t_mds_r1_verdict]] — F3 origin; canonical string ratified by this ruling
- [[project_centrality_ci_register_error]] — the canonical R1↔R2 register-error case; the failure mode there was a *statistic-name + noun-class* error, not an adjective error, which is what makes the noun-class test the right test
