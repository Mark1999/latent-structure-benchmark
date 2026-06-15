# Rename: Latent Structure Benchmark to Cognitive Structure Observatory

**Date:** 2026-06-12
**Status:** Mark's decision, recorded. Drives the gated public-copy pass (status doc trail in `docs/status/2026-06-12-observatory-rename-verdicts.md`).

## Decisions (Mark, 2026-06-12)

1. The public instrument name changes from "the Latent Structure Benchmark" to "the Cognitive Structure Observatory."
2. "Cognitive Structure Lab" stays as the umbrella brand in the navbar; the Observatory is the instrument the Lab runs ("Lab runs the Observatory").
3. The published open-data bundle keeps its minted name "Latent Structure Benchmark (LSB) Open Data Bundle v1" and its Zenodo DOI, FROZEN. A one-line note records that the project is now the Cognitive Structure Observatory and the next bundle version adopts the new name. A minted citation must not silently change.
4. Internal code namespaces (`cdb_`, `lsb-agent`) and internal docs (`CLAUDE.md`, `ARCHITECTURE.md`, etc.) are NOT renamed in this pass. Deferred as a cheap internal sweep with no external impact.

## Rationale (Mark)

"Benchmark" implies a standard against which a result is judged closer to or farther from a correct answer. This project has no such standard. It is a stimulus-and-response exercise: apply a plain prompt, observe what structure appears in the output, and compare that structure against the same model's other runs and against other models. "Observatory" names that honestly. It observes a thing that exists independently of the observer, does not perturb or rank it, and makes it visible for others to interpret. The name agrees with the project's binding section 1.5 framing (exploratory, not hypothesis-testing; failures are findings; no point estimate without uncertainty) instead of fighting it, which "benchmark" did (the methodology page currently has to disclaim its own title).

## Candidate framing language (for the CDA SME gate and Mark to finalize; not yet binding)

> The Cognitive Structure Observatory applies a plain stimulus to a language model and records what comes back. We ask a model to list the things in a domain and sort them into groups, then we do it again, and again, across runs of the same model and across different models. We are not measuring the model against a correct answer, because there isn't one. We are watching what structure appears in the output, and asking how stable that structure is against itself and how far it diverges from other models. Stimulus, response, comparison. Nothing more is claimed, and nothing more is needed.

## Scope of the rename pass

Public dashboard copy only: methodology page, about page, navbar brand, and generic "benchmark" prose on the data page. FROZEN: the bundle proper-noun name and the Zenodo citation string. Out of scope: analysis code (rule 15 freeze), code namespaces, internal docs, data-file regeneration. Gated Tier 1 (CDA SME plus UI/UX) with live-DOM verification before done, because external reviewers see this next.
