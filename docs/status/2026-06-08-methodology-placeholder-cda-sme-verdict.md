# Methodology page placeholder — CDA SME verdict

**Date:** 2026-06-08
**Reviewer:** CDA SME
**Artifact under review:** `docs/proposed/2026-06-08-methodology-page-scaffold.md`, sections 1 through 6
**Disposition context:** Ships as a *placeholder* (replacement for the current "Full methodology content coming soon" stub in `apps/dashboard/src/views/MethodologyPage.tsx`). The two already-live verbatim CDA-SME sections (Data provenance, Cross-model term map and uncertainty) are unchanged and sit below this draft. The bar applied here is "defensible to a skeptical reader as placeholder copy," not "final / Mark-authored / perfect."

---

## CDA SME VERDICT: PASS-WITH-NOTES

| Axis | Verdict |
|---|---|
| Axis 1 — Protocol validity | PASS |
| Axis 2 — Analytical validity | PASS |
| Axis 3 — Claims validity | PASS |
| Axis 4 — Audience translation | PASS-WITH-NOTES |
| Register compliance | PASS |
| Vocabulary compliance | PASS |

---

## Findings (the per-check audit you requested)

### Check 1 — §1.5.1 construct anchor + "corpus lens" first-use definition

PASS. Section 1, in a single paragraph (lines 49–53), introduces the headline term and the methodologically precise long form together, names them as the same idea with different jobs, and gets the construct on the page before any reuse:

- Headline form (line 49): "We call the thing those maps show the **corpus lens**: the shape a model imposes on a domain, inherited from the text it was trained on."
- Long form (lines 51–53): "the latent categorical structure of a training corpus, as refracted through the model's training and alignment."

This satisfies the §1.5.1 anchor requirement and the Reviewer-enforced "define on first use" rule. The "short name is for headlines / long name is the honest one" framing is a clean reader-facing description of the §1.5.1 audience table.

### Check 2 — §1.5.1 five-link chain (corpus → training → alignment → decoding → output)

PASS. Section 2 (lines 70–74) names all five links explicitly, in order, with one-line glosses for each:

- corpus, training, alignment, decoding, output distribution — all present, in canonical order
- Section 2 line 78 then carries the critical methodological qualifier: "We measure the shadow directly. Everything we say about the stages behind it is an inference, not a measurement, and we try to be clear about which is which."

This is the §1.5.1 closing claim ("LSB elicitation operates on the output-distribution link. What it reveals about the corpus, training, alignment, and decoding links is a composed inference, not a measurement.") rendered into Mark's voice. It lands the operational legibility requirement.

### Check 3 — §1.5.3 six known limitations on the page

PASS-WITH-NOTES. All six are present, but limitations 1 and 5 (prompt sensitivity, sampling/stochastic variance) are folded together rather than separated.

| §1.5.3 item | Where it appears in the draft | Note |
|---|---|---|
| 1. Prompt sensitivity | Section 4, "Wording matters" (lines 133–135) | PASS |
| 2. English-only | Section 4, "English only, for now" (lines 136–138) | PASS |
| 3. Corpus opacity | Section 4, "We cannot see the corpus" (lines 139–140) | PASS |
| 4. Alignment confound | Section 4, "Training and tuning are tangled" (lines 141–143) | PASS |
| 5. Temperature / sampling effects | Section 3 (lines 102–104) "resampling the data hundreds of times and watching how much the answer wobbles"; folded into "Wording matters" wobble bucket in section 4 (line 135) | PASS, but see Note A |
| 6. Informant metaphor is metaphor | Section 4, "The interview is a metaphor" (lines 144–145) | PASS |

**Note A (non-blocking, methodological hygiene).** §1.5.3 item 5 is specifically "stochastic decoding introduces run-to-run variance *separate from* prompt sensitivity." The draft conflates the two as a single "wobble" bucket that "shows up as the uncertainty you see on every chart." The substantive claim (wobble exists, is bootstrapped, is shown) is intact. For a placeholder, this is fine. For the Mark-authored final, consider naming sampling variance as its own bullet, because the §1.5.3 contract is that all six appear distinctly on the methodology page. Forward-carry to the Mark-authored revision; do not block placeholder ship.

### Check 4 — §1.5.4 / §7 forbidden vocabulary scan

PASS. The riskiest paragraph (section 4, lines 114–129) deliberately invokes belief/projection language *in order to repudiate it*, which is the canonical exception pattern established for prose surfaces (cite-to-disclaim; the same pattern that landed the §6 Designer Brief appendix advisory on 2026-05-17).

Phrase-by-phrase audit of section 4:

- Line 115: "the two models 'see family the same way,' that they share some value or attitude. **Do not say it.**" — the forbidden phrasing appears in scare-quotes as the very claim being prohibited. The cite-to-disclaim move is explicit in the next sentence: "you would be guessing, not reading the data." This is the published exception pattern. **PASS — no fix needed.**
- Line 123: "The pattern was real. The meaning you reached for was a projection." — attribution is to the reader, not the model. **PASS.**
- Lines 126–129: "We measure categorical structure in a model's output, refracted from the text it learned on. We do not claim it as evidence of belief, preference, cognition, or inner experience, because the model has none of those, and our method could not see them if it did." — this is the canonical anti-attribution sentence. Uses the forbidden vocabulary (belief, cognition) only in the disclaiming clause, never in a positive-attribution clause. **PASS.**
- Line 145: "It is not a claim that there is anybody home." — clean.

The "picture on the dresser" analogy lands correctly: it is an analogy about *the reader's inferential leap*, not about the model's inner life. The point is "an observed pattern can have a mundane cause," and the analogy succeeds on those terms. No anthropomorphizing.

**Other forbidden-vocab scan across all six sections:**

- "worldview" — absent
- "believes / thinks / understands" applied positively to models — absent (the only occurrences are in disclaiming clauses, as above)
- "within-model consensus / within-model …" — absent
- "publishable" — absent (the §6 "citable DOI" reference is to the open data bundle DOI, which is the §6.7 deliverable, not paper publication)
- "hypothesizes / predicted X / confirmed" — absent; §1.5.7 exploratory posture is held throughout
- "closer to human = better" — n/a (no human baseline in v1; section 6 inverts to "check us than trust us")
- "consensus" (line 158) and "agree" (line 158) — Register 2 use (between-model), the legitimate use; **PASS** per §4.2 register framework
- em dashes — none found across the draft (Mark's hard rule held)

**Note for the Reviewer agent at PR time:** if a grep-based forbidden-vocab check fires on the scare-quoted "see family the same way" in line 115, route to the canonical exception precedent in `docs/status/2026-05-17-ft-designer-appendix-s6-advisory.md` (cite-to-disclaim in prose surfaces is permitted). The Reviewer should not reject on that occurrence.

### Check 5 — Audience translation (30-second journalist + reproduce-and-cite)

PASS-WITH-NOTES.

- **30-second journalist read.** Section 1 lands the construct in two short paragraphs and gives the journalist a usable headline term ("corpus lens"). Section 4 stands on its own as the disclaimer the journalist needs in order not to overclaim. Both pass.
- **Reproduce-and-cite read.** Section 6 names the open data bundle, the rebuild path ("rebuild the database from the raw responses, rerun the analysis, and regenerate every figure"), the toolchain-version provenance pointer, and the citable DOI. Clean.

**Note B (non-blocking, §1.5.6 placement).** §1.5.6 binding text says: *"'The mismatch is the finding' is the lead paragraph of the public methods page … Placement: the first paragraph of the public methods page, before any description of specific measures."* This draft does not literally open with the mismatch frame; it opens with the structural-reframe move ("takes a method that anthropologists use to study people and points it at large language models instead"). The spirit of the mismatch frame is carried in section 4 line 129 ("The structure is the finding. The inner life is not on the table.") rather than at the very top.

For placeholder shipping, the structural-reframe opening is defensible and arguably more legible to a cold reader than the mismatch frame would be. For the Mark-authored final, consider either (a) adding a one-sentence mismatch lede above the current section 1 opener, or (b) explicitly editing §1.5.6 to relax the strict "first paragraph" placement constraint in light of the website-as-artifact frame. Forward-carry; do not block placeholder ship.

---

## Required before merge

None blocking. The draft ships as placeholder.

## Carry-forward to the Mark-authored final (non-blocking)

1. **Note A — sampling variance as a distinct bullet.** §1.5.3 item 5 (temperature and sampling effects) is currently folded into the "Wording matters" bullet. In the final pass, lift it to its own bullet so all six §1.5.3 limitations appear distinctly. The substantive content is already present.
2. **Note B — mismatch-frame placement.** §1.5.6 binding text mandates the mismatch frame as the first paragraph. The draft carries the spirit in section 4 but does not literally open with it. Mark's call: add a one-line mismatch lede above section 1, or relax the §1.5.6 placement rule via an architecture-doc amendment.
3. **Reviewer-agent note.** When the Coder ships this into `MethodologyPage.tsx`, attach a comment near the section-4 scare-quoted phrase pointing the Reviewer's grep check at the cite-to-disclaim exception precedent so a future automated forbidden-vocab scan does not false-positive.

---

## Posting

Verdict to `#lsb-cda-sme`.
