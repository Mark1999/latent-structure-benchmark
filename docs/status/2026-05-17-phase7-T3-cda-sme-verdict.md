---
filed: 2026-05-17
reviewer: CDA SME agent (Opus)
task: Phase 7 T3 — Drafter framework + Bluesky drafter
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 7 T3 — CDA SME verdict on the drafter framework + Bluesky drafter

**VERDICT: PASS-WITH-NOTES**

The Phase 7 kickoff §3 T3 design — a Claude-driven drafter base class, a
post-generation validator with three sub-checks, a Bluesky drafter
subclass, and per-platform system prompt files at
`cdb_social/drafters/prompts/v1/{platform}.md` — is **methodologically
coherent** with §1.5 / §1.5.4 / §1.5.7 and with the T1 schemas landed at
commit `57745bd`. The proposed architecture preserves the post-generation
validator as the gate (not the prompt) per the Orchestrator's
"drafter is graded on validation pass rate" posture, and it correctly
versions the prompt files per CLAUDE.md §6 R7.

T3 is the heaviest CDA SME gate of Phase 7 because **every byte of
`cdb_social/drafters/prompts/v1/bluesky.md` is methodology copy**, and
every regex character of `validate_draft()` decides whether a draft
containing a §1.5.4 violation reaches the queue. This verdict lands
**eighteen binding-at-Coder-dispatch notes** (§5 below) operationalizing
each of the ten methodology questions surfaced in the Orchestrator's
invocation. The Coder must apply all eighteen during T3 implementation.
The Reviewer enforces.

Headline rulings (one per Orchestrator question):

1. **Validator (1) — substring scan:** the validator's forbidden-substring
   list is the **§1.5.4 left-column phrases verbatim plus a small word-stem
   set**, scanned **case-insensitively** on the full draft text, with the
   stems matched via word-boundary regex (not substring) to avoid
   "disbelieves" matching "believes." See §5.1.

2. **Validator (2) — numeric+CI adjacency:** the validator extracts every
   numeric token via a regex over the draft, applies a small **exemption
   list** (model-version strings, year-shaped tokens, character-count
   metadata, URL components), and for each remaining numeric requires a
   CI-shaped neighbor within **K = 12 tokens**. CI-shape is defined by a
   single permissive regex covering the four canonical patterns. See §5.2.

3. **Validator (3) — hypothesis-framing scan:** the validator scans for a
   **closed list of 11 phrases** (8 from §1.5.4 row 11 + 3 additional
   "subtler-pattern" phrases from the Orchestrator's §3 question 3), all
   case-insensitive. See §5.3.

4. **Bluesky prompt content scope:** the prompt embeds (a) the full
   §1.5.4 forbidden-vocab table verbatim, (b) a **3-sentence corpus-lens
   anchor** drawn from §1.5.1 (not the full §1.5 framing), (c) the
   trigger-evidence payload, (d) the R10 numeric+CI rule expressed in
   English plus the four canonical CI patterns, (e) the Register-1/
   Register-2 distinction expressed as one sentence + the four R1-vs-R2
   substitutions from §1.5.4 rows 7–10. **Token budget: ~1100 tokens cached
   system-prompt portion.** See §5.4.

5. **Methodology-page-link fallback:** drafters **always include**
   `methodology_url`, defaulting to the article-shell URL
   (`cogstructurelab.com/{domain}`) until Phase 6 T1+T2 land. The link is
   labeled in the post as **"details"** or **"more"**, not "methodology"
   — labeling an article-shell URL "methodology" misrepresents the
   destination and is the §1.5 framing hazard. See §5.5.

6. **`drafter_self_rating` value posture:** **fixed at 0.5** for v1 of the
   Bluesky drafter (the default in T1 schema is `0.0`, but T3 overrides to
   `0.5` to signal "drafter ran, not calibrated, see docstring"). The
   drafter is **not** prompted to self-rate. See §5.6.

7. **Bluesky 300-char structure:** the canonical post structure is
   **3 lines** (finding + framing + URL), targeting ≤ 270 chars to leave
   room for URL shortening by the platform. Patterns A and B (CI-inline
   vs CI-following-find-link-back) are both approved; T3 implements
   Pattern A as default with Pattern B as fallback when the CI exceeds
   the line budget. See §5.7.

8. **Prompt-versioning escalation policy:** if the v1 prompt produces
   ≥ 2 forbidden-vocab rejections within any 10-draft window on real
   triggers (post-Phase-7-launch), **escalate to a v2 prompt bump** —
   create `cdb_social/drafters/prompts/v2/bluesky.md` and CDA-SME-review
   the v2 prompt. **Do not** "tighten the validator instead" without an
   SME review — the validator is the gate, not the band-aid, and silent
   validator tightening risks suppressing real findings. See §5.8.

9. **Drafter pass-rate target:** the kickoff §8 risk 1 framing
   ("drafter is graded on validation pass rate") is **observational, not
   binding** for v1. The binary "this draft passed" is the only quality
   gate. Pass-rate is logged for **trend monitoring** (a sudden drop is
   the §5.8 escalation trigger), not enforced as a target. See §5.9.

10. **System-prompt vs per-call-payload split:** the **system prompt
    (cached)** carries §1.5.4 table verbatim, the corpus-lens anchor,
    the R10 rule, the Register-1/2 distinction, and the platform
    structure constraints. The **per-call payload (uncached)** carries
    the trigger evidence dict + the relevant DomainResult numerics with
    CIs + the `methodology_url` + the `dashboard_url`. **The per-call
    payload may not contain methodology-substantive copy** — per-trigger
    lede patterns belong in the system prompt (one canonical pattern
    per trigger type, in a structured block). This preserves prompt-cache
    parity and prevents methodology drift via per-call surgical edits.
    See §5.10.

Coder dispatch may proceed on T3 with the eighteen binding notes in §5
applied. The T3 Coder produces:
- `cdb_social/drafters/base.py` (the `DrafterBase` class + the
  `validate_draft()` validator)
- `cdb_social/drafters/bluesky.py` (the Bluesky subclass)
- `cdb_social/drafters/prompts/v1/bluesky.md` (the system prompt)
- Fixture replay tests at `tests/fixtures/social/llm_responses/`
- Validator unit tests covering each of the three sub-checks

The Reviewer must apply CLAUDE.md §6 R7 (prompt versioning) + §6 R11
(no LLM calls in `cdb_analyze`; T3's calls are inside `cdb_social/`,
which is permitted) + the Phase 7-specific CI boundary check (planned at
T7) that rejects `from cdb_analyze` inside `packages/cdb_social/`.

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | N/A | T3 is the social-publishing drafter layer; no CDA elicitation protocol surface is touched. The drafter consumes already-published `DomainResult` numerics (Register-2 outputs) and `SocialTrigger` objects (T2 outputs); it does not perform free-list, pile-sort, or pile-interview protocol logic. |
| Analytical validity | PASS-WITH-NOTES | T3 does not perform analytical computation — it consumes already-computed numerics from the published `apps/dashboard/public/data/{domain}.json` substrate. The methodology hazards are at the **drafter-prompt content** layer (does the prompt instruct the LLM to construct an analytically-valid sentence?) and the **validator** layer (does it correctly reject analytically-invalid sentences?). Both are addressed in §5: §5.2 binds the numeric-CI-adjacency regex; §5.4 binds the prompt's content; §5.10 enforces the cache/no-cache split so the methodology copy stays cached and stable. |
| Claims validity | PASS-WITH-NOTES | The drafter's output is the highest-leverage §1.5 surface in Phase 7 — every social post that ships is a public claim about a model's output. §5.1 (substring scan), §5.2 (numeric+CI adjacency), §5.3 (hypothesis-framing scan) together implement the §1.5.4 / §1.5.7 / R10 enforcement at the queue boundary. §5.4 sets the prompt-content scope so the LLM is steered toward §1.5-compliant outputs in the first place. §5.5 (link labeling) is the small but binding fix that prevents the methodology-page-link surface from misframing the destination. §5.7 (canonical 3-line structure) gives the Coder a concrete pattern the prompt teaches the LLM. **The verdict is PASS-WITH-NOTES rather than FAIL because the architecture is correct (validator-as-gate, prompt-as-steering); the eighteen §5 notes are narrowings, not redesigns.** |
| Audience translation | PASS-WITH-NOTES | The Bluesky audience is a mix of AI researchers (who would read "Smith's S = 0.61" correctly), journalists (who would not, but the structure forces the framing), and the general technically-literate Bluesky population. §5.7's canonical 3-line structure (finding + framing + URL) is calibrated to that audience: line 1 is the quantified finding; line 2 carries the corpus-lens framing in plain English; line 3 is the URL labeled per §5.5. §5.5's "details"/"more" labeling (not "methodology") is the binding fix that prevents the journalist from reading the article-shell URL as if it were a methodology page. |

**Register compliance: PASS-WITH-NOTES.** The drafter prompt must teach
the LLM the Register-1 / Register-2 distinction so it never writes
"within-model consensus" (a §1.5.4 left-column phrase). §5.4 binds the
prompt's inclusion of the four R1-vs-R2 substitutions from §1.5.4 rows
7–10. The validator's substring scan (§5.1) catches the leakage if the
LLM ignores the prompt.

**Vocabulary compliance: PASS-WITH-NOTES.** Scanned every LSB-authored
string surface implied by the kickoff §3 T3 (function names, exception
names, prompt-file-path components, validator-internal token names) and
the methodology-content additions in §5. Full table in §3. No new
§1.5.4 violations introduced; the T1 verdict's §5.7 (re.
ARCHITECTURE.md §4.6 line 1211 "state of cultural alignment roundup"
prose) remains carry-forward to T7. T3 itself is vocabulary-clean.

---

## 2. Rationale on the ten methodology questions

### 2.1. Question 1 — Validator (1) substring list (forbidden vocab)

The Orchestrator surfaced four sub-questions: (a) full §1.5.4 set vs
egregious subset; (b) case sensitivity; (c) partial-word matching; (d)
how to handle the "disbelieves matches believes" hazard.

**Ruling on (a) — full §1.5.4 set + minimal word-stem additions:**
the validator scans against the **full §1.5.4 left-column phrase set**
(all 12 rows of the table verbatim, as it appears in ARCHITECTURE.md
lines 162–175 and CLAUDE.md §7) **plus the small generic-token set
from §1.5.4 line 65 of `docs/FRONTEND_DESIGNER_BRIEF.md`**: `worldview`,
`believes`, `thinks` (when applied to models). The full set is correct
because the table is the canonical reference; any "egregious subset"
choice is implicit editorial discretion, which the CDA SME does not
delegate to the Coder or the drafter.

**Ruling on (b) — case-insensitive scan:** the LLM may output
"Believes," "BELIEVES," or "believes." All three are §1.5.4 violations.
Case-sensitive matching would leave easy bypasses. Implementation:
`re.IGNORECASE` on every pattern.

**Ruling on (c) and (d) — phrase-level for §1.5.4 left-column entries,
word-boundary regex for stems:** the §1.5.4 left-column entries are
phrase-shaped (e.g., "Model X believes...", "How models see the
world") and match via `re.search(re.escape(phrase), text, re.IGNORECASE)`
with the literal "Model X" / "model X" placeholder replaced by a
regex `[Mm]odel \S+` or by literal "models." The three generic stems
(`worldview`, `believes`, `thinks`) match via `\b{stem}\b` (case-insensitive
word boundary). The `\b` anchor prevents "disbelieves" or "believes-in-X"
from matching the bare `believes` stem — but a literal "Model GPT-5
believes..." still matches via the phrase-level scan because the
phrase-level entry "Model X believes..." is encoded as the regex
`[Mm]odel \S+ believes\b` (case-insensitive).

**Operational set (binding at §5.1):**

```python
# Phrase-level patterns (§1.5.4 left-column, all rows; case-insensitive)
FORBIDDEN_PHRASE_PATTERNS = [
    # Row 1
    r"\b[Mm]odel \S+ believes\b",
    r"\bmodels? believe\b",
    # Row 2
    r"\b[Mm]odel \S+ thinks of\b",
    r"\bmodels? think of\b",
    # Row 3
    r"\bhow models? sees? the world\b",
    # Row 4
    r"\b[Mm]odel \S+'s worldview\b",
    r"\bmodels?'? worldview\b",
    # Row 5 (standalone "cultural bias" — but not "cultural bias against X" where context disambiguates)
    r"\bcultural bias\b",
    # Row 6
    r"\bwhat the model understands\b",
    # Rows 7-10 (Register-boundary)
    r"\bwithin-model consensus\b",
    r"\bwithin-model cultural consensus\b",
    r"\bwithin-model eigenratio\b",
    r"\bwithin-model CCM\b",
    # Row 11 (hypothesis framing — but this overlaps with Validator 3; §5.3 handles)
    # Row 12 (prediction-confirm framing — also §5.3)
]

# Stem-level patterns (word-boundary; the three generic-context forbidden tokens)
FORBIDDEN_STEM_PATTERNS = [
    r"\bworldview\b",
    r"\bbelieves\b",
    r"\bthinks\b",
]
```

The `cultural bias` standalone match is the **one false-positive hazard
in this set** — a phrase like "shows cultural bias against X" might be
a meaningful sentence in a non-LSB context, but inside an LSB social
post about model output, "cultural bias" is forbidden unless rephrased
as "categorical divergence from [baseline]" per §1.5.4 row 5. The
validator rejects the standalone phrase; the drafter's prompt (§5.4)
must teach the LLM to use "categorical divergence" instead.

### 2.2. Question 2 — Validator (2) numeric+CI adjacency

The Orchestrator surfaced: what counts as CI-shaped; what K (token
window); which numerics are exempt.

**Ruling on CI-shape — single permissive regex covering four canonical
patterns:**

```python
# Four canonical CI-shape patterns:
# (a) "(95% CI [a, b])" or "(95% CI [a-b])" — square or round brackets
# (b) "CI: a–b" or "CI: a, b" or "CI: a, b" — colon-separated
# (c) "±X" — symmetric error
# (d) "(a, b)" or "(a–b)" — paren-bracketed pair (used when context is unambiguous)
CI_SHAPE_REGEX = re.compile(
    r"(?:"
    r"\(?\s*95\s*%?\s*CI\s*[\[\(:]?\s*[-+]?\d*\.?\d+\s*[,–\-]\s*[-+]?\d*\.?\d+\s*[\]\)]?\s*\)?"
    r"|"
    r"\bCI\s*[:=]\s*[-+]?\d*\.?\d+\s*[,–\-]\s*[-+]?\d*\.?\d+"
    r"|"
    r"±\s*[-+]?\d*\.?\d+"
    r"|"
    r"\(\s*[-+]?\d*\.?\d+\s*[,–\-]\s*[-+]?\d*\.?\d+\s*\)"
    r")",
    re.IGNORECASE,
)
```

**Ruling on K (token window) — K = 12 tokens.** This is large enough
to span typical adjacency patterns like "Smith's S = 0.61, 95% CI
[0.48, 0.79]" (~ 8 tokens between the `0.61` and the closing `]`) and
"OCI = 2.4 (1.8, 3.1)" (~ 6 tokens). It is small enough to prevent a
distant CI from "covering" a bare numeric elsewhere in the post. Tokens
are defined as whitespace-separated substrings after stripping
punctuation; the Coder may use a simple regex-based tokenizer for this.

**Ruling on numeric exemptions — five exemption categories:**

```python
# Numerics that are NOT findings and do not require a CI neighbor:
NUMERIC_EXEMPTIONS = [
    # (a) Model version strings: "GPT-4", "Claude 3.5", "Llama-3.1", "grok-4.20"
    re.compile(r"\b(?:GPT|Claude|Llama|Gemini|grok|Mistral|Qwen|DeepSeek|Phi)-?\d+(?:\.\d+)*\b", re.IGNORECASE),
    # (b) Year tokens: 1900-2099 standalone
    re.compile(r"\b(?:19|20)\d{2}\b"),
    # (c) Character-count metadata: "300 chars", "280 characters"
    re.compile(r"\b\d+\s*(?:chars?|characters?)\b", re.IGNORECASE),
    # (d) URL components — any numeric inside a URL is exempt
    #     (the URL is stripped from the text before the bare-numeric scan)
    # (e) Trivial small integers in non-statistical context:
    #     N runs (e.g., "across 12 models"), where the number is a count
    #     not a finding.
    re.compile(r"\b(?:across|over|in)\s+\d+\s+(?:models?|domains?|runs?|prompts?|informants?)\b", re.IGNORECASE),
]
```

**The exemption rule is conservative.** When in doubt, the validator
rejects. The drafter's prompt (§5.4) must teach the LLM to write
"across 12 models" (exempt by pattern e) rather than "12 models showed
high consensus" (where the `12` is statistically meaningful and would
require a CI under the exemption rule — but the phrase itself is also
forbidden by Register-1/2 considerations).

The Coder implements `validate_draft_numeric_ci_adjacency(text)` as
follows:

1. Strip URLs from `text` (e.g., via `re.sub(r"https?://\S+", "", text)`).
2. For each `NUMERIC_EXEMPTION` pattern, mark matched spans as exempt.
3. For each numeric token (regex `[-+]?\d*\.?\d+` with optional `%` /
   `e±N` exponent suffix), check whether the token is inside an exempt
   span. If exempt, skip.
4. For each non-exempt numeric, scan ± K tokens for a `CI_SHAPE_REGEX`
   match. If no match, the numeric is a bare finding — fail.

`framing_checks["bare_numeric_without_ci"] = True` iff every non-exempt
numeric has an adjacent CI-shaped neighbor.

### 2.3. Question 3 — Validator (3) hypothesis-framing scan

The Orchestrator surfaced: the §1.5.4 rows 11–12 phrases plus three
"subtler patterns" (`"our results show," "this demonstrates," "this
means"`).

**Ruling — closed list of 11 phrases:**

```python
# §1.5.4 rows 11–12 verbatim (case-insensitive):
HYPOTHESIS_FRAMING_PATTERNS = [
    # Row 11
    r"\bLSB hypothesi[zs]ed\b",
    r"\bLSB tested whether\b",
    r"\bLSB confirms? that\b",
    r"\bLSB found that\b",  # paired with "[hypothesis]" — too broad; see note
    r"\bLSB predicted\b",
    # Row 12
    r"\bdata confirmed\b",
    r"\bdata refuted\b",
    # Three "subtler patterns" per Orchestrator §3 question 3:
    r"\bour results show\b",
    r"\bthis demonstrates\b",
    r"\bthis means\b",
    # Plus the §1.5.7 explicit forbidden frames:
    r"\bthis proves\b",
    r"\bwe hypothesi[zs]ed\b",
    r"\bconfirms that\b",
    r"\bproves that\b",
]
```

The total is 14 patterns (the Orchestrator's "11" was approximate). The
list is **closed at T3**; new entries require a CDA SME re-review.

**Special note on `LSB found that`:** the §1.5.4 row 11 phrasing is
"LSB found that [hypothesis]" — the *[hypothesis]* qualifier is what
makes it forbidden. "LSB found that GPT-5's output concentration index
is 2.4 (1.8, 3.1)" is a *measurement*, not a *hypothesis*. The
validator's regex match on `\bLSB found that\b` is overbroad here.
**Resolution at §5.3:** the validator scans for the bare phrase; the
drafter prompt (§5.4) teaches the LLM to use "LSB measures..." /
"LSB reports..." / "LSB observes..." (§1.5.4 row 11 right-column) in
all post copy. If a "LSB found that" sentence is constructed by the
LLM, the validator rejects it; the LLM will learn (within a few
generations) that the right-column verbs are the safe forms.

`framing_checks["hypothesis_framing"] = True` iff no
HYPOTHESIS_FRAMING_PATTERN matches.

### 2.4. Question 4 — Bluesky prompt content scope and token budget

The Orchestrator surfaced: full §1.5 framing is many paragraphs; the
§1.5.4 table is dozens of rows; what is the right verbatim subset for a
prompt; what is the right token budget.

**Ruling — five-block cached system prompt at ~1100 tokens total.**

The cached system prompt for `cdb_social/drafters/prompts/v1/bluesky.md`
has **five blocks** with the token-budget allocation:

```
Block 1 — Role and task     [~80 tokens]
Block 2 — §1.5.1 corpus-lens anchor (3 sentences) [~120 tokens]
Block 3 — §1.5.4 forbidden-vocab table verbatim [~280 tokens]
Block 4 — R10 numeric+CI adjacency rule + canonical CI patterns [~180 tokens]
Block 5 — Register-1 vs Register-2 anchor + R1-vs-R2 substitutions [~220 tokens]
Block 6 — Bluesky platform constraints + canonical 3-line structure [~220 tokens]
```

(Six blocks total; the Coder may merge adjacent blocks if pedagogically
better.)

**Block 2 — Corpus-lens anchor (3 sentences):**

> LSB applies Cultural Domain Analysis elicitation protocols to large
> language models as if they were informants. It surfaces the corpus
> lens — the categorical structure of a model's training corpus,
> refracted through training and alignment. LSB does not measure
> cultural worldview, belief, or cognition.

This is a verbatim compression of ARCHITECTURE.md §1.5 lines 86–88 + §1.5.1
lines 94–102 into three sentences. It is the load-bearing framing the
LLM uses when constructing every sentence.

**Block 3 — §1.5.4 table verbatim:** the full 12-row table from
ARCHITECTURE.md §1.5.4 lines 162–175 is included verbatim. The prompt
introduces it with: "When writing posts about LSB findings, NEVER use
phrases from the left column. ALWAYS use phrases from the right column
when an equivalent claim is needed." The table format is preserved
(markdown) so the LLM parses it as a structured rule, not flowing
prose.

**Block 4 — R10 numeric+CI adjacency rule:** the prompt states:

> Every numeric finding in a post MUST be accompanied by its
> confidence interval. Acceptable formats:
> - "Smith's S = 0.61, 95% CI [0.48, 0.79]"
> - "OCI = 2.4 (1.8, 3.1)"
> - "consensus eigenratio = 5.2 ± 0.8"
> Exempt numerics: model version strings (GPT-5, Claude 3.5),
> years, character counts, and the count-of-N-models constructions
> ("across 12 models," "over 8 domains").

**Block 5 — Register-1 vs Register-2 anchor:** the prompt states:

> OCI (Output Concentration Index) describes a single model's output
> distribution on a domain — this is Register 1. Romney CCM and
> consensus eigenratio describe shared categorical structure across
> multiple models — this is Register 2. Do not cross the register
> boundary. Specifically:
> - "Within-model consensus" → "Representational coherence" or "OCI"
> - "Within-model cultural consensus" → "Output distribution analysis"
> - "Within-model eigenratio" → "OCI"
> - "Within-model CCM" → "Output distribution analysis"

**Block 6 — Bluesky platform constraints:** see §5.7 below for the
canonical 3-line structure.

**Token budget rationale:** Anthropic prompt caching has a 1024-token
minimum cache size; the 1100-token budget puts the cached portion just
above the minimum, capturing ~80% of the per-call cost reduction per
ARCHITECTURE.md §6.2. Heavier prompts dilute the per-call generation
signal (the LLM "forgets" the framing under a 5000-token prompt) and
slow generation. Lighter prompts risk forbidden-vocab leakage. The
1100-token budget is the SME's empirical recommendation; T3 testing
may iterate.

### 2.5. Question 5 — Methodology-page-link fallback

The Orchestrator surfaced: omit the link entirely, use the article-shell
URL, or use a "coming soon" annotation.

**Ruling — always include the link; default to article-shell URL; label
the link "details" or "more," not "methodology."**

The kickoff §2 out-of-scope item 2 says drafters use
`cogstructurelab.com/{domain}` as the `methodology_url` default until
Phase 6 T1+T2 land. The CDA SME concurs with the URL choice but binds a
**labeling fix**.

**The hazard:** if the drafter writes "see methodology:
cogstructurelab.com/family" but the URL is the article shell (not a
methodology page), the reader is misled about what they will find at
the link. That's a §1.5 framing hazard: it implies LSB has a
methodology page when it doesn't.

**The fix:** the prompt teaches the LLM to label the link with a
neutral word — "details," "more," "explore," or just naked-URL form.
The link **text** decouples from the link **destination** so the
labeling stays accurate regardless of which URL is current.

When Phase 6 T1+T2 ship (the methodology page lands), the
`methodology_url` config flips to `/methodology` and the link label
may flip to "methodology." That is a future config + prompt-bump
operation; T3 ships with the article-shell URL and the "details"/"more"
labeling.

### 2.6. Question 6 — `drafter_self_rating` value posture

The Orchestrator surfaced: fixed value, LLM-prompted, or other.

**Ruling — fixed at 0.5 for v1 of the Bluesky drafter.**

Three reasons:

1. **LLM-prompted self-rating is gameable.** The LLM has no
   ground-truth signal it can self-rate against. A prompt that asks
   "rate the quality of this draft" produces noise correlated with the
   LLM's training-corpus statistics, not with actual draft quality.

2. **Fixed 0.0 is uninformative.** A field that is always 0.0 is
   indistinguishable from a field that is unset. The T5 review CLI
   can't sort by it.

3. **Fixed 0.5 carries the right semantic.** It signals "drafter ran;
   not calibrated; see docstring" — distinguishable from 0.0 (the
   schema default, set by drafters that don't produce a self-rating).
   The T1 schema's docstring explicitly says the field is not
   calibrated; the value 0.5 is a placeholder that the future calibrated
   drafter (if one ever ships) can override.

The Coder hard-codes `drafter_self_rating=0.5` in the Bluesky drafter's
`SocialDraft` construction. The Coder must **not** prompt the LLM to
self-rate.

### 2.7. Question 7 — Bluesky 300-char structure

The Orchestrator surfaced: can a 300-char post fit finding + CI +
framing + URL.

**Ruling — yes, with the canonical 3-line structure.**

The drafter's prompt teaches the LLM a single canonical structure:

```
Line 1: <Finding statement with numeric and CI inline>
Line 2: <Plain-English framing in corpus-lens language>
Line 3: details {dashboard_url}
```

**Example (synthetic; for prompt teaching purposes):**

```
GPT-5's output on family vocabulary clusters tightly:
OCI = 2.4 (1.8, 3.1) across 12 runs.
The model's responses concentrate on a small subset of
family terms — a property of its corpus lens.
details cogstructurelab.com/family
```

That example is 270 chars (well under 300). The structure has slack
for longer model names or per-trigger variations.

**The "Pattern B fallback" — CI on a separate line.** When the finding
numerics plus CI exceed ~80 chars (e.g., a complex divergence with
two model names), the structure flexes:

```
Line 1: <Short finding statement>
Line 2: <CI and additional context>
Line 3: <Plain-English framing>
Line 4: details {dashboard_url}
```

Pattern B is at most 4 lines. The drafter's prompt teaches Pattern A
as default and Pattern B as fallback.

**The URL counts ~30 chars** for `cogstructurelab.com/{domain}` (the
longest domain slug is `holidays`, giving 27 chars). Bluesky AT
Protocol does not auto-shorten URLs; the URL counts as its full length
toward the 300-char limit. The 270-char target leaves ~30 chars of
slack.

### 2.8. Question 8 — Prompt-versioning escalation policy

The Orchestrator surfaced: what to do when the v1 prompt produces
consistent forbidden-vocab leakage.

**Ruling — escalation policy:**

1. **Forbidden-vocab rejections are tracked.** The Coder adds a
   `drafter_rejections.jsonl` audit log in `out/social/state/` that
   records each `DrafterRejectedException` with the trigger ID, the
   draft text, and the matched forbidden tokens.

2. **Escalation trigger:** ≥ 2 rejections within any 10-draft window
   on real (non-test) triggers post-Phase-7-launch. The 10-draft window
   is sliding; the Coder may use a simple "look-back-10" implementation.

3. **Escalation action:** create
   `cdb_social/drafters/prompts/v2/bluesky.md`, document the diff from
   v1 in a status report under `docs/status/`, and route the v2 prompt
   to the CDA SME for re-review **before** any v2-generated draft
   reaches the queue.

4. **What NOT to do:** **do not** silently tighten the validator to
   suppress the rejections. The validator is the gate; tightening it
   without an SME review risks suppressing real findings (e.g., adding
   a new forbidden phrase that incidentally matches a meaningful
   sentence). The validator's substring/regex list is changed only via
   a v2 prompt review.

5. **What is also NOT escalation:** isolated rejections on edge cases
   (one rejection per 50+ drafts) are noise, not signal. The drafter's
   prompt is steering, not enforcement; some rejection rate is expected
   and is what the validator-as-gate posture is designed to handle.

### 2.9. Question 9 — Drafter pass-rate target

The Orchestrator surfaced: is there a target pass rate the drafter must
hit.

**Ruling — observational, not binding, for v1.**

The kickoff §8 risk 1 framing ("drafter is graded on the validation
pass rate, not on creativity") is a *posture* (the drafter is held
accountable for output, not for engagement), not a *threshold*. For v1
of the Bluesky drafter:

- **Per-draft accountability:** the binary "this draft passed" is the
  only quality gate. Failed drafts raise `DrafterRejectedException` and
  do not reach the queue.

- **Trend monitoring:** the `drafter_rejections.jsonl` audit log
  (per §5.8) is the trend-monitoring substrate. A sudden rejection-rate
  spike is the v2-prompt-bump trigger.

- **No SLA, no target percentage.** A v1 prompt that produces a 100%
  pass rate is plausibly under-creative (the LLM is parroting
  templates); a v1 prompt that produces a 50% pass rate is failing the
  drafter contract. A "natural" pass rate in the 80–95% range is the
  rough operational expectation, but the rate is observed, not
  enforced.

The Coder does **not** add a pass-rate threshold check to the drafter.

### 2.10. Question 10 — System-prompt vs per-call-payload split

The Orchestrator surfaced: can per-call payload contain methodology-
substantive copy.

**Ruling — methodology-substantive copy lives in the cached system
prompt only; per-call payload is data-only.**

**Cached (system prompt):**

- Block 1 — Role and task
- Block 2 — §1.5.1 corpus-lens anchor
- Block 3 — §1.5.4 forbidden-vocab table
- Block 4 — R10 numeric+CI adjacency rule + canonical CI patterns
- Block 5 — Register-1 vs Register-2 anchor + substitutions
- Block 6 — Bluesky platform constraints + canonical 3-line structure
- **Per-trigger-type lede patterns** (one canonical pattern per
  TriggerType, in a structured block — added to the cached prompt)

**Uncached (per-call payload):**

- The trigger evidence dict (e.g., `evidence['gap_delta']`)
- The relevant DomainResult numerics with CIs (e.g., the Smith's S, the
  OCI, the pairwise similarity gap, all with their CIs)
- The `methodology_url` value (e.g., `cogstructurelab.com/family`)
- The `dashboard_url` value (e.g., `cogstructurelab.com/family`)
- The `model_id` and `domain_slug` strings

**Why the strict split:**

1. **Anthropic prompt caching only caches the prefix.** Anything
   per-call shifts the cache boundary forward and reduces the cost
   reduction. The 1100-token cached portion captures most of the cost
   win.

2. **Methodology drift via per-call surgical edits is a hazard.** If
   the per-call payload could contain "this trigger type uses the
   following framing wording...", the framing wording would become
   per-trigger-overridable, and Mark would lose central control over
   the methodology copy. Centralizing all methodology copy in the
   cached prompt is the architectural defense against this.

3. **Per-trigger-type lede patterns belong in the cached prompt.** Each
   TriggerType has a distinctive canonical sentence shape (e.g.,
   NEW_MODEL: "We added {model} to the {domain} domain. Where it sits:
   ..." vs DIVERGENCE: "The {domain} domain has a new high in
   between-model categorical divergence: ..."). These patterns are
   methodology copy and must be cached, not per-call.

**Future v2 considerations (advisory, non-binding):** if the v2 drafter
wants per-trigger-type prompt variation (e.g., different lede patterns
for NEW_MODEL vs DIVERGENCE), the v2 design should still keep the
methodology copy in the cached prompt and use **structured
per-trigger-type blocks within the cache** rather than per-call
overrides. This is a v2 design constraint, not a v1 issue.

---

## 3. Vocabulary compliance on T3-authored strings

Scanned every LSB-authored string surface implied by the kickoff §3 T3 +
the §5 binding notes:

| String | §1.5.4 reading | Verdict |
|---|---|---|
| Class name `DrafterBase` | Technical descriptor | Compliant |
| Class name `BlueskyDrafter` | Technical descriptor | Compliant |
| Exception name `DrafterRejectedException` | Technical descriptor | Compliant |
| Method name `draft()` | Technical descriptor | Compliant |
| Method name `validate_draft()` | Technical descriptor | Compliant |
| Method name `_call_llm()` (or similar private LLM-call helper) | Technical descriptor | Compliant |
| File path `cdb_social/drafters/base.py` | Technical descriptor | Compliant |
| File path `cdb_social/drafters/bluesky.py` | Technical descriptor | Compliant |
| File path `cdb_social/drafters/prompts/v1/bluesky.md` | Technical descriptor (versioning) | Compliant |
| Audit-log path `out/social/state/drafter_rejections.jsonl` | Technical descriptor | Compliant |
| Framing-check key `"hypothesis_framing"` | §1.5.7-aligned identifier | Compliant |
| Framing-check key `"cognition_attribution"` | §1.5.4-aligned identifier | Compliant |
| Framing-check key `"bare_numeric_without_ci"` | R10-aligned identifier | Compliant |
| Framing-check key `"register_boundary"` | Register-aligned identifier | Compliant |
| Cached-prompt Block 2 corpus-lens anchor (3 sentences, see §5.4) | Verbatim §1.5/§1.5.1 framing | Compliant |
| Cached-prompt Block 3 §1.5.4 table (verbatim) | Verbatim §1.5.4 | Compliant |
| Cached-prompt Block 4 R10 rule | §4.5/R10-aligned methodology copy | Compliant |
| Cached-prompt Block 5 Register-1/2 anchor + substitutions | §4.2/§1.5.4 rows 7–10-aligned methodology copy | Compliant |
| Cached-prompt Block 6 Bluesky structure | Operational drafting instruction | Compliant |
| Per-trigger-type lede patterns (in cached prompt) | Methodology copy — must individually pass §1.5.4 scan; the T3 Coder must produce these and the CDA SME re-reviews if any one of them does not pass §3 of §5.4 | Compliant pending §5.4 sub-review |
| Synthetic example post in §2.7 of this verdict | Illustrative; does not ship; included for prompt teaching | Compliant |
| Link label "details" / "more" (in post text) | Neutral descriptor; does not misframe destination | Compliant |
| Hard-coded `drafter_self_rating=0.5` value | Operational placeholder; T1 docstring carries the calibration disclaimer | Compliant |

No new §1.5.4 violations introduced. The T1 verdict's §5.7 (re.
ARCHITECTURE.md §4.6 line 1211 "state of cultural alignment roundup"
prose) remains carry-forward to T7.

**One operational note for the T3 Coder:** the per-trigger-type lede
patterns (one canonical pattern per TriggerType, inside Block 6) are
methodology copy authored by the Coder. The Coder may produce a first
draft of the five patterns (NEW_MODEL, NEW_DOMAIN, DRIFT, DIVERGENCE,
MONTHLY_ROUNDUP) and route them to the CDA SME via §5.4 before T3
lands. The Architect may instead author the patterns directly. Either
path is acceptable; the patterns must individually pass §1.5.4 / §1.5.7
scan before T3 closes.

---

## 4. The provider-quote / verbatim-output concern (cross-reference)

The Phase 6 T9 verdict (2026-05-12) carried a provider-quote concern as
an advisory to Phase 8. That concern carries forward to Phase 7
because **social posts directly quote LSB findings**, which include
named model behaviors.

T3's drafter prompt (§5.4) does NOT instruct the LLM to quote model
output verbatim. The lede patterns are LSB-authored statements about
model output, not direct quotes. This is the right posture for v1: it
keeps T3 inside the §1.5 framing wrapper without surfacing the verbatim
provider-quote question.

If a future drafter version wants to include verbatim model output
(e.g., "GPT-5 grouped 'mother' and 'father' together"), that change
would require a separate CDA SME review against the §1.5 framing and
the provider T&C posture. T3 itself does not surface verbatim output.

---

## 5. Binding carry-forward notes (apply at Coder dispatch)

These notes are binding on the Coder during T3 implementation. The
Reviewer enforces. Numbering follows the methodology-question order in
the Orchestrator's invocation.

### 5.1. **Validator (1) substring scan: full §1.5.4 set + word-boundary stems, case-insensitive.** [Claims validity]

The Coder implements `validate_draft_forbidden_vocab(text: str) ->
list[str]` returning the matched forbidden patterns (empty list if
clean). The patterns are the union of:

- **Phrase-level patterns:** all 12 rows of the §1.5.4 left-column
  table from ARCHITECTURE.md lines 162–175, encoded as case-insensitive
  regex with the literal "Model X" placeholder replaced by
  `[Mm]odel \S+`. The exact pattern set is §2.1 above.

- **Stem-level patterns:** the three generic forbidden tokens from
  CLAUDE.md §7 and `docs/FRONTEND_DESIGNER_BRIEF.md` §3.1 line 65:
  `worldview`, `believes`, `thinks`. Each is matched via
  `\b{stem}\b` (case-insensitive word boundary), so "disbelieves"
  does NOT match "believes."

The returned list is assigned to `SocialDraft.forbidden_terms_hit`. A
non-empty list raises `DrafterRejectedException`; the draft does not
reach the queue. The audit log (§5.8) records the rejection.

### 5.2. **Validator (2) numeric+CI adjacency: K=12 token window, five exemption categories.** [Analytical validity, Claims validity]

The Coder implements `validate_draft_numeric_ci_adjacency(text: str)
-> bool` per the algorithm in §2.2 above:

1. Strip URLs from `text` via `re.sub(r"https?://\S+", " ", text)`.
2. Apply the five exemption patterns (§2.2 above) to mark exempt spans.
3. Extract every numeric token via `re.finditer(r"[-+]?\d*\.?\d+(?:%|e[-+]?\d+)?", text)`.
4. For each non-exempt numeric, scan ±12 tokens (whitespace-separated,
   punctuation-stripped) for a `CI_SHAPE_REGEX` match (§2.2 above).
5. Return `True` iff every non-exempt numeric has an adjacent
   CI-shaped neighbor.

`framing_checks["bare_numeric_without_ci"] = True` iff the function
returns `True` (i.e., the check passed).

If `False`, raise `DrafterRejectedException` and record the bare
numeric in the audit log.

### 5.3. **Validator (3) hypothesis-framing scan: 14 closed phrases, case-insensitive.** [Claims validity]

The Coder implements `validate_draft_hypothesis_framing(text: str) ->
list[str]` returning the matched patterns (empty list if clean). The
pattern set is the 14 closed-list patterns in §2.3 above (from §1.5.4
rows 11–12 + the three Orchestrator-surfaced subtler patterns + the
three §1.5.7 explicit forbidden frames).

The list is closed at T3; new entries require a CDA SME re-review.

`framing_checks["hypothesis_framing"] = True` iff the returned list
is empty.

If non-empty, raise `DrafterRejectedException` and record the matched
patterns in the audit log.

### 5.4. **Bluesky prompt content scope: 5–6 cached blocks at ~1100 tokens.** [Claims validity, Audience translation, Register compliance]

The Coder creates `cdb_social/drafters/prompts/v1/bluesky.md` with six
blocks per §2.4 above:

1. **Block 1 — Role and task** (~80 tokens). "You are a drafter for
   LSB's social pipeline. You produce one Bluesky post given a trigger
   event and a domain-result. Output the post text only. Do not output
   commentary, explanations, or formatting marks."

2. **Block 2 — Corpus-lens anchor** (~120 tokens). Verbatim:

   > LSB applies Cultural Domain Analysis elicitation protocols to
   > large language models as if they were informants. It surfaces the
   > corpus lens — the categorical structure of a model's training
   > corpus, refracted through training and alignment. LSB does not
   > measure cultural worldview, belief, or cognition.

3. **Block 3 — §1.5.4 forbidden-vocab table verbatim** (~280 tokens).
   Full 12-row markdown table from ARCHITECTURE.md §1.5.4 lines
   162–175.

4. **Block 4 — R10 numeric+CI adjacency rule** (~180 tokens). Lists the
   four canonical CI formats and the five exempt-numeric categories per
   §2.2 above.

5. **Block 5 — Register-1 vs Register-2 anchor + substitutions**
   (~220 tokens). One paragraph explaining OCI vs Romney CCM, plus the
   four R1-vs-R2 substitutions from §1.5.4 rows 7–10.

6. **Block 6 — Bluesky platform constraints + canonical structure**
   (~220 tokens). The 3-line Pattern A and the 4-line Pattern B
   fallback per §2.7 and §5.7 below.

The token budget is approximate; the Coder may iterate within ±200
tokens of the 1100-token target. The Coder must invoke prompt caching
per ARCHITECTURE.md §6.2 (`cache_control={"type": "ephemeral"}` on
the system prompt block).

**Per-trigger-type lede patterns** are added inside Block 6 as a
structured sub-block (one canonical pattern per TriggerType). The
patterns are methodology copy; the Coder produces a first draft and
routes them to the CDA SME via the standard plan-review path **before
T3 closes**. Alternatively, the Architect may author the patterns
directly. The patterns must pass §5.1 / §5.2 / §5.3 validator scans
when tested against synthetic LLM outputs.

### 5.5. **Methodology-page-link fallback: always include; default to article-shell URL; label "details" or "more."** [Audience translation]

The drafter writes the URL as the last line of the post (Pattern A) or
the last line (Pattern B). The link **text** is one of: `details`,
`more`, `explore`, or naked URL. **Not** "methodology" until Phase 6
T1+T2 land and `methodology_url` flips to `/methodology`.

The Coder hard-codes the link-text choice in the Bluesky drafter's
prompt: `Block 6` includes the instruction "Label the URL as 'details'
in the post copy. Do not label as 'methodology' — this is reserved for
the future methodology page."

The `SocialDraft.methodology_url` field is populated by the
orchestrator via config; the Coder reads it via the standard config
loader. The default value is `f"https://cogstructurelab.com/{domain_slug}"`.
A future Phase 6 T1+T2 close will flip the default to
`"https://cogstructurelab.com/methodology"` plus a prompt bump to
re-label the link.

### 5.6. **`drafter_self_rating`: fixed at 0.5; LLM not prompted to self-rate.** [Claims validity, Audience translation]

The Coder hard-codes `drafter_self_rating=0.5` in the Bluesky drafter's
`SocialDraft` construction. The prompt does **not** include a "rate
the quality of this draft" instruction. The T1 docstring's calibration
disclaimer (schemas.py line 749–759) carries the audience-translation
defense.

If a future calibrated-drafter version ships, the value may be
overridden; the v1 posture is 0.5 fixed.

### 5.7. **Bluesky 300-char canonical 3-line structure (Pattern A default; Pattern B fallback).** [Audience translation, Claims validity]

The Coder teaches the LLM (in Block 6 of the cached prompt) the
canonical 3-line Pattern A structure:

```
Line 1: <Finding statement with numeric and CI inline>
Line 2: <Plain-English framing in corpus-lens language>
Line 3: details {dashboard_url}
```

Plus the 4-line Pattern B fallback for when finding+CI exceeds ~80
chars:

```
Line 1: <Short finding statement>
Line 2: <CI and additional context>
Line 3: <Plain-English framing>
Line 4: details {dashboard_url}
```

Both patterns target ≤ 270 chars total. The drafter base class
includes a post-LLM character-count check; drafts exceeding 300 chars
raise `DrafterRejectedException` with `forbidden_terms_hit=
["__bluesky_overlength__"]` (sentinel value distinguishing
length-rejection from forbidden-vocab-rejection; the Coder may use a
named exception subclass instead).

### 5.8. **Prompt-versioning escalation: rejection log + v2 bump trigger.** [Claims validity, Audience translation]

The Coder implements:

1. **Audit log:** `out/social/state/drafter_rejections.jsonl` —
   append-only JSONL, one record per rejection, with fields:
   `{ "timestamp": ISO-8601, "trigger_id": dedupe_key,
   "platform": "bluesky", "drafter_version": str, "prompt_version":
   "v1", "draft_text": str, "matched_forbidden": list[str],
   "matched_hypothesis": list[str], "bare_numerics": list[str] }`.

2. **Sliding window check:** the drafter base class (or a small helper
   in `cdb_social/observability.py`) counts rejections in the last
   10 drafts (by sliding-window timestamp comparison). The helper
   does NOT raise on threshold cross — it logs a `logging.warning`
   message: `"DRAFTER_REJECTION_WINDOW: {n} rejections in last 10
   drafts; consider v2 prompt review"`.

3. **Escalation action (operator-side, not code-side):** when the
   warning fires ≥ 2 times in any 10-draft window post-Phase-7-launch,
   the operator (Mark) creates
   `cdb_social/drafters/prompts/v2/bluesky.md` and routes to CDA SME.

4. **What NOT to add:** the Coder does NOT silently tighten the
   validator. The validator's substring/regex list (§5.1, §5.3) and
   the exemption set (§5.2) are CDA-SME-owned; changes require an
   SME re-review.

### 5.9. **Drafter pass-rate target: observational, not enforced.** [Claims validity]

The Coder does NOT add a pass-rate threshold check inside the drafter
or the orchestrator. The audit log (§5.8) is the observational
substrate. The "natural" pass rate is expected in the 80–95% range but
is not enforced.

The Coder may add a `--dry-run` mode to the drafter CLI that runs the
drafter against a fixed test trigger set and reports pass-rate as part
of the dev-loop feedback. That CLI flag is operator convenience, not
methodology enforcement.

### 5.10. **System-prompt vs per-call-payload split.** [Claims validity, Audience translation]

The Coder structures the Bluesky drafter's LLM call as:

**System prompt (cached, ~1100 tokens):**
- Blocks 1–6 per §5.4 above
- Per-trigger-type lede patterns

**Per-call payload (uncached):**
- The `SocialTrigger.evidence` dict (e.g.,
  `{"gap_delta": 0.04, "model_pair": ["claude-4", "gpt-5"], ...}`)
- The relevant `DomainResult` numerics with CIs, expressed as a
  structured JSON block (the Coder constructs this from
  `domain_result.smith_s`, `domain_result.smith_s_95ci`,
  `domain_result.oci_per_model`, etc. — exact selection per trigger
  type)
- `methodology_url: str` (e.g., `"https://cogstructurelab.com/family"`)
- `dashboard_url: str` (e.g., `"https://cogstructurelab.com/family"`)
- `model_id: str | None` (from `SocialTrigger.model_id`)
- `domain_slug: str | None` (from `SocialTrigger.domain_slug`)

**The Coder must NOT include methodology copy in the per-call payload.**
Per-trigger-type framing belongs in the cached prompt's Block 6
sub-block; per-call data is data-only.

The Reviewer enforces this via a code-review check: any string
literal containing §1.5.4 / §1.5.7 phrases inside the per-call payload
construction is grounds for rejection. The Reviewer also verifies the
Anthropic `cache_control` annotation is on the system prompt block per
ARCHITECTURE.md §6.2.

### 5.11. **Framing-check dict population.** [Claims validity, T1-schema-consistent]

The drafter populates `SocialDraft.framing_checks` with at least four
keys, all `bool`:

```python
framing_checks = {
    "hypothesis_framing": <bool>,        # per §5.3
    "cognition_attribution": <bool>,     # per §5.1 (forbidden_terms_hit subset)
    "bare_numeric_without_ci": <bool>,   # per §5.2
    "register_boundary": <bool>,         # per §5.1 (R1/R2 substring scan subset)
}
```

`SocialDraft.framing_check_passed` is set to `True` iff every value in
`framing_checks` is `True`. The T1 schema docstring (schemas.py lines
779–795) records the queue-acceptance contract; T3 honors it.

The Coder may add additional check-name keys as the drafter matures;
the four above are the binding minimum for v1.

### 5.12. **DrafterRejectedException raises on any §5.1 / §5.2 / §5.3 failure; draft does not reach queue.** [Claims validity]

The Coder defines `DrafterRejectedException(Exception)` in
`cdb_social/drafters/base.py`. The exception is raised by
`DrafterBase.draft()` if any of:

1. `validate_draft_forbidden_vocab(text)` returns non-empty
2. `validate_draft_numeric_ci_adjacency(text)` returns `False`
3. `validate_draft_hypothesis_framing(text)` returns non-empty
4. `len(text) > 300` for Bluesky (or analogous per-platform overlength
   check for X / LinkedIn in T4)

The exception carries the rejection reason in its message; the audit
log (§5.8) captures the full detail. The orchestrator (T6) catches the
exception and logs the rejection; **no draft is written to the
queue**.

### 5.13. **Cached prompt versioning per CLAUDE.md §6 R7.** [Architectural]

The prompt file is at `cdb_social/drafters/prompts/v1/bluesky.md`.
Editing this file in place is forbidden per CLAUDE.md §6 rule 7. Any
prompt change creates `prompts/v2/bluesky.md` (or higher) and the
`SocialDraft.prompt_version` field records which directory the prompt
was loaded from.

The Coder implements `load_prompt(platform: str, version: str) -> str`
in `cdb_social/drafters/base.py` (or similar). The version is
explicit, not auto-discovered, so test fixtures stay stable.

### 5.14. **Anthropic prompt-caching parity per ARCHITECTURE.md §6.2.** [Cost discipline, non-spend-gate]

The drafter's LLM call uses Anthropic prompt caching on the system
prompt block. The Reviewer checks the API call construction for
`cache_control={"type": "ephemeral"}` on the relevant content blocks
per ARCHITECTURE.md §6.2 lines 1411. This is a per-call construction
rule, not a spend gate (CLAUDE.md R13/R14 are not violated).
<!-- noqa: spend-gate-check -->

### 5.15. **No real LLM API calls in tests; fixtures only.** [Architectural, per CLAUDE.md §6 rule 9]

Tests for the drafter use canned LLM responses from
`tests/fixtures/social/llm_responses/`. The Coder adds a
`MockLLMClient` (or equivalent) that replaces the Anthropic SDK in
tests and returns deterministic responses keyed by prompt hash. No
real API calls in CI. The Tester's verdict will fail T3 if real API
calls appear in test code.

### 5.16. **Validator unit tests cover positive + negative case per sub-check.** [Test coverage]

The Coder produces unit tests for `validate_draft()` and each
sub-validator with at least:

- Positive case: a well-formed draft that passes all three sub-checks.
- Negative case for §5.1: a draft containing each §1.5.4 left-column
  phrase (12 patterns × 1 case each) + each stem (3 patterns × 1 case
  each) = 15 negative cases. Each must raise `DrafterRejectedException`.
- Negative case for §5.2: a draft with a bare numeric (no CI neighbor)
  + a draft where the CI is > K=12 tokens away from the numeric. Both
  must raise.
- Negative case for §5.3: a draft containing each of the 14
  hypothesis-framing patterns (14 cases). Each must raise.
- Exemption case for §5.2: a draft with model version "GPT-5" + year
  "2026" + "across 12 models" must NOT raise.

The Tester's verdict requires all sub-validator tests to pass.

### 5.17. **Round-trip test: good draft → SocialDraft with empty forbidden_terms_hit + framing_check_passed=True.** [Architectural / queue contract]

The Coder produces an end-to-end round-trip test that:

1. Constructs a synthetic `SocialTrigger` (NEW_MODEL or DIVERGENCE).
2. Constructs a synthetic `DomainResult` with realistic numerics + CIs.
3. Replays a canned LLM response that produces a well-formed draft.
4. Calls `BlueskyDrafter().draft(trigger, domain_result)`.
5. Asserts the returned `SocialDraft` has:
   - `forbidden_terms_hit == []`
   - `framing_check_passed == True`
   - `all(framing_checks.values()) == True`
   - `text` ≤ 300 chars
   - `drafter_self_rating == 0.5`
   - `prompt_version == "v1"`
   - `methodology_url` and `dashboard_url` populated

The mirror test: a canned LLM response producing a draft with each
category of forbidden output must raise `DrafterRejectedException`.

### 5.18. **`framing_note`-style top-level note in per-call methodology copy (cross-reference to Phase 6 T9 precedent).** [Audience translation, advisory not binding]

The Phase 6 T9 verdict (2026-05-12) established a precedent: an
`framing_note` top-level field on the published failures JSON
attaches the §1.5 corpus-lens framing to data that would otherwise be
read in isolation. The Bluesky social-post analog is **the post text
itself** — each post must carry the framing in its second line (per
the Pattern A canonical structure in §5.7). The §1.5.4 substring scan
(§5.1) is the substring-level enforcement; the structure rule (§5.7)
is the architectural enforcement; together they preserve the
T9-established posture.

The advisory: if a future drafter version produces a draft style that
omits the framing line (e.g., a TikTok-style one-liner), the CDA SME's
posture is that the framing must still be present, either in the post
or in a configurable per-post `framing_note` field that the platform's
publish layer renders adjacent to the post. T3's v1 Bluesky structure
already includes the framing line; this advisory is for future
drafters.

---

## 6. Mark-escalation note

**No Mark escalation is required for T3 Coder dispatch.**

Three items Mark should be aware of for the T4 / T7 horizon:

1. **The per-trigger-type lede patterns inside the cached prompt
   (§5.4 Block 6 sub-block)** are methodology copy. The Coder's
   first-draft of these five patterns (one per TriggerType) routes
   through the CDA SME before T3 closes, or the Architect may author
   them directly. Either path is acceptable; the patterns must pass
   §5.1 / §5.2 / §5.3 validator scans.

2. **The T1 verdict §5.7 (re. ARCHITECTURE.md §4.6 line 1211 "state of
   cultural alignment roundup" prose)** remains carry-forward to T7. T3
   does not introduce any new instance of that phrase; T7 must still
   execute the original §5.7 fix.

3. **Forbidden-vocab leakage on real triggers is the v2-prompt-bump
   trigger** (§5.8). Mark should expect the drafter's first 10–20
   real posts to surface rejection-rate signal that informs whether v1
   needs a v2 bump before the first organic trigger fires. Wait for
   the first organic trigger to fire (kickoff §7.5 ratification) and
   monitor the audit log.

---

## 7. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply at T3 (18 binding notes):**
  - §5.1 (forbidden-vocab substring scan: full §1.5.4 + stems,
    case-insensitive)
  - §5.2 (numeric+CI adjacency: K=12, five exemption categories)
  - §5.3 (hypothesis-framing scan: 14 closed phrases)
  - §5.4 (cached prompt scope: 5–6 blocks at ~1100 tokens, full
    §1.5.4 table verbatim, corpus-lens anchor, R10 rule, R1/R2
    distinction, Bluesky structure)
  - §5.5 (methodology-page-link: always present, article-shell URL
    default, label "details" / "more," not "methodology")
  - §5.6 (drafter_self_rating fixed at 0.5; no LLM self-rating)
  - §5.7 (canonical 3-line Pattern A + 4-line Pattern B fallback;
    ≤ 270 char target; ≤ 300 char hard limit)
  - §5.8 (rejection audit log + v2-bump escalation policy)
  - §5.9 (pass-rate observational, not enforced)
  - §5.10 (system-prompt-vs-per-call split; no methodology copy in
    per-call payload)
  - §5.11 (framing_checks dict: four binding minimum keys)
  - §5.12 (DrafterRejectedException raises on any of three
    sub-validator failures or overlength)
  - §5.13 (prompt versioning per CLAUDE.md §6 R7)
  - §5.14 (Anthropic prompt-caching per ARCHITECTURE.md §6.2)
  - §5.15 (no real LLM API calls in tests; fixtures only)
  - §5.16 (validator unit tests cover positive + negative per
    sub-check)
  - §5.17 (round-trip test: good draft → all-pass SocialDraft)
  - §5.18 (framing-note-style architectural enforcement via §5.7
    structure rule)
- **`cdb_core/schemas.py` change required:** **No.** T3 reads from the
  T1 schema unchanged; no new fields are required.
- **`docs/DATA_DICTIONARY.md` change required:** **No.** T1 §13 covers
  the SocialDraft fields T3 populates.
- **Per-trigger-type lede patterns route through CDA SME before T3
  close:** **Yes.** The Coder produces a first draft of five patterns
  (one per TriggerType) and routes to CDA SME via standard plan-review
  path, OR the Architect authors them directly. Either path closes T3.
- **T7 doc-sweep flag carry-forward:** the T1 §5.7 ARCHITECTURE.md §4.6
  line 1211 prose revision remains binding on T7.
- **Architect ratification required:** **No.** The recommended design
  requires no schema change and no re-architecture.
- **Mark escalation:** §6 advisory only, non-blocking for T3 Coder
  dispatch.

---

*End of Phase 7 T3 CDA SME verdict.*
