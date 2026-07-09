# Political Domain Elicitation: Landscape Review and Proposal

**Document:** `docs/proposed/2026-07-09-political-domain-proposal.md`
**Status:** PROPOSED. Discussion draft for Mark. Nothing here is approved; a political
domain is Tier 1 (published claims, methodology copy, §1.5 framing surfaces) and
requires the full Architect + CDA SME pipeline before any collection run.
**Origin:** Mark's request (2026-07-09) to review recent coverage of bias in LLMs and
consider free listing around political topics as the next instrument.

---

## 1. What the last twelve months of bias coverage actually measures

A research sweep (2026-07-09, sources in §4) found six method families dominating
public and academic discussion of political slant in LLMs:

1. **Closed-form questionnaires** (Political Compass and similar): still the workhorse
   of "chatbot leans left" headlines and the weakest instrument class. Answers flip
   under paraphrase and format changes; real users do not administer surveys.
2. **Open-ended audits scored by LLM judges** (OpenAI's five-axis eval, Promptfoo):
   now the vendor standard; imports the judges' own output tendencies.
3. **Open-ended audits scored by human raters** (Stanford 10k raters; Stray et al.
   208k ratings): perception of slant, which moves with tone and rater partisanship.
4. **Paired-prompt symmetry tests** (Anthropic's even-handedness eval): redefines the
   question as differential treatment rather than position; open-sourced.
5. **Corpus/artifact audits** (Grokipedia vs Wikipedia source slant, congressional
   language similarity, party recommendation frequencies).
6. **Internal-representation probes** (SAE work showing RLHF suppresses stance
   expression while partisan geometry persists in representations).

The regulatory layer (EO 14319 "Preventing Woke AI", OMB M-26-04) mandates
"ideological neutrality" for federal procurement without defining any measurement
instrument, which is why the vendor evals appeared within months of it.

**The gap:** every one of these methods operates in stance space (where an output
falls on an opinion scale, or whether opposing framings get symmetric treatment).
Nothing measures the categorical structure of the political domain itself as it
patterns in model output: which items are salient, how they cluster, and how stable
that structure is across runs and versions. That is exactly what CDA elicitation
measures, and it is unoccupied ground.

## 2. What an Observatory political domain would be

Free listing plus pile sort, same protocol as family/holidays/food, on a political
domain. The instrument never asks a model to take a position. It measures:

- **Salience** (Smith's S): which items surface, in what order, at what frequency.
  Agenda measurement, not opinion measurement. No questionnaire can see this.
- **Emergent structure** (MDS/clustering on pile sorts): whether a left-right axis
  appears at all becomes a finding rather than an assumption. Category boundary
  placement (does "immigration" sort with "economy" or with "national identity") is
  itself the structure the framing literature fights over, and nothing in the sweep
  measures it.
- **Consistency** (Romney CCM across runs): the prompt-sensitivity critique that
  undermines questionnaires is, in CDA terms, an informant-reliability question, and
  consensus analysis is the established machinery for it.
- **Refusal structure** (failures-are-findings): political-domain refusal and
  partial-list rates are themselves a publishable structural result, and the existing
  decline-interview follow-up applies unchanged.

Framing discipline: all claims stay at the level of output patterns and categorical
structure. The §1.5.4 vocabulary rules mean we publish "categorical divergence
between models on political-issue vocabulary," never "model X is biased." The one
thing the sweep makes clear is that every actor is fighting over what neutrality
means; an instrument that reports structure without adjudicating neutrality occupies
ground nobody currently holds.

## 3. Candidate stimuli and known risks (for CDA SME review)

Candidate free-list stimuli, deliberately plain, one domain per campaign:

- "List all the political issues facing the country you can think of."
- "List all the political ideologies you can think of."
- "List all the reasons people vote the way they do."

Risks the SME gate must rule on before any plan reaches a Coder:

1. **Item normalization is the instrument.** "Abortion," "reproductive rights," and
   "abortion access" are lexical variants that carry framing. Collapsing or splitting
   them injects exactly the structure being measured. Normalization rules must be
   written, conservative, and documented before collection, not during coding.
2. **"The country" is underspecified.** The stimulus either names a country (and the
   result is scoped to it) or does not (and the model's choice of default country is
   itself a salience finding). SME decision, made in advance.
3. **Safety routing interacts with political prompts.** Expect elevated refusals and
   (for some providers) documented reluctance on political topics. Refusals are
   first-class outcomes here, but collection N may need to be sized for them.
4. **Timing.** Post-EO vendor behavior is actively shifting (OpenAI and Anthropic
   both shipped neutrality evals in late 2025). A dated, versioned baseline now, with
   drift tracking on `model_version_returned`, is more valuable than in any prior
   domain, and more likely to be cited.

## 4. Sources (research sweep 2026-07-09)

Academic/industry: Stanford GSB perceived-slant study (May 2025); IssueBench, TACL
2026 (arXiv 2502.08395); Stray et al. balanced-approval eval (arXiv 2605.28911);
Rozado/Manhattan Institute integrative audit (Jan 2025); Peking/Renmin longitudinal
Political Compass drift study (HSSC, Feb 2025); DeepSeek information-suppression
audit (arXiv 2506.12349); "The Neutral Mask" RLHF/SAE study (arXiv 2606.09735);
Grokipedia vs Wikipedia matched-pair audit (PNAS 2026); Copenhagen voting-advice
study (Apr 2026); Promptfoo Grok 4 eval (Jul 2025).
News: Fortune on Grok system-prompt steering (Jul 2025); NPR on the Grok extremist
output incident (Jul 2025).
Regulatory: EO 14319 (Jul 2025); OMB M-26-04 (Dec 2025); Lawfare and CDT analyses.
Vendor: OpenAI "Defining and evaluating political bias in LLMs" (Oct 2025);
Anthropic "Measuring political bias in Claude" + open-sourced eval (Nov 2025).

## 5. How the next-topic decision gets made (programmatic before generative)

Per the standing rule added to CLAUDE.md §8 on 2026-07-09: topic selection splits
into a programmatic part and a judgment part, and the programmatic part comes first.

- **Programmatic (scripts, no LLM):** candidate stimulus enumeration from the CDA
  literature's standard domain lists; feasibility stats from existing corpus tooling
  (expected items per list, normalization collision rates on pilot vocabulary,
  refusal-rate priors by provider from our own failure records); coverage checks
  (which domains the current slate already saturates).
- **Judgment (Mark, then one SME gate):** which domain is worth the project's
  credibility, stimulus wording, normalization rules, and the claims boundary.
- **Not a brainstorm dispatch:** no open-ended "what should we test next" agent
  sessions. The shortlist comes from scripts and Mark; the SME gate rules on validity.

## 6. Proposed next steps (if Mark wants to proceed)

1. Mark picks or edits a stimulus direction from §3 (or rejects the domain).
2. Architect drafts the campaign plan (Tier 1): stimulus, N, slate, normalization
   protocol, refusal handling, claims boundary.
3. CDA SME gate on the plan, with §3 risks as mandatory review items.
4. Pilot on a small slate before any full campaign (same pattern as family pilot).
