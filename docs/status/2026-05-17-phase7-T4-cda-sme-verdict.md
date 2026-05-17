---
filed: 2026-05-17
reviewer: CDA SME agent (Opus)
task: Phase 7 T4 — X + LinkedIn drafters (draft-only)
slack_channel: "#lsb-cda-sme"
verdict: PASS-WITH-NOTES
---

# Phase 7 T4 — CDA SME verdict on the X + LinkedIn drafters (draft-only)

**VERDICT: PASS-WITH-NOTES**

T4 extends the T3 drafter framework (DrafterBase + validate_draft +
unified drafter_audit.jsonl + four-key framing_checks dict + 14
hypothesis-framing patterns + K=12 token window) to two additional
platforms: X (thread-shaped output, `\n---\n` segment delimiter, per-
segment validation) and LinkedIn (long-form single-post output, looser
char budget). Neither has live publishing in Phase 7 per Mark's
ratification of §7.1 (Bluesky-only live).

**The T3 PASS-WITH-NOTES verdict (18 binding notes) carries forward
verbatim** — the validator semantics, the cache/no-cache split, the
methodology-link labeling ("details"/"more", not "methodology"), the
fixed `drafter_self_rating=0.5`, the `framing_checks` four-key dict,
the rejection audit log, and the prompt-versioning escalation policy
all apply to X and LinkedIn unchanged. T4 inherits the T3 base class;
the binding question is whether T4 introduces **new** methodology
surfaces beyond T3, and the answer is **yes at three points**:

1. **X is a thread.** Per-segment vs cross-segment R10 enforcement is a
   new architectural decision the T3 verdict did not address. The T4
   ruling (Option A: each segment independently passes all four
   validator checks) is binding and explained in §2.2.

2. **X segment 1 ("hook tweet") carries disproportionate reader
   weight.** Many X readers see only segment 1. Per-segment validation
   alone is insufficient — segment 1 needs **additional structural
   constraints** that T3 did not require. See §2.8.

3. **LinkedIn's 3000-char budget is 10× Bluesky's 300-char budget.**
   The K=12 token CI-adjacency window from T3 was sized against
   compact Bluesky 3-line patterns. Scaling it for 3000-char content
   is a methodology question. **Ruling: K stays at 12.** See §2.6.

This verdict lands **twelve binding-at-Coder-dispatch notes** (§5
below) operationalizing all ten Orchestrator methodology questions.
The Coder applies all twelve at T4 implementation. The Reviewer
enforces. Combined with T3's 18 binding notes, T4 closes Phase 7's
methodology gate on the drafter layer.

Coder dispatch may proceed on T4 with the §5 notes applied. The T4
Coder produces:
- `cdb_social/drafters/x.py` (X subclass; thread-shaped output)
- `cdb_social/drafters/linkedin.py` (LinkedIn subclass; long-form)
- `cdb_social/drafters/prompts/v1/x.md` (X system prompt)
- `cdb_social/drafters/prompts/v1/linkedin.md` (LinkedIn system prompt)
- Optional shared `cdb_social/drafters/thread_utils.py` for the
  segment-split / per-segment validation helpers
- Fixture replay tests at `tests/fixtures/social/llm_responses/x/` and
  `.../linkedin/`
- Per-segment validator tests covering forbidden-vocab, R10,
  hypothesis-framing per segment; cross-segment hook-tweet structural
  tests on X

---

## 1. Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | N/A | T4 is the social-publishing drafter layer; no CDA elicitation protocol surface is touched. Same posture as T3. |
| Analytical validity | PASS-WITH-NOTES | T4 inherits T3's validator; the per-segment X validation rule (§5.2 below) and the LinkedIn K=12 retention (§5.6 below) preserve R10 enforcement at the per-statement level rather than the per-document level. The X hook-tweet structural rule (§5.8 below) prevents the "CI lives in segment 2, hook in segment 1" hazard that would let R10 technically pass while misleading the segment-1-only reader. |
| Claims validity | PASS-WITH-NOTES | The drafter's output is the highest-leverage §1.5 surface — every social post is a public claim. T4's per-segment Option A validation (§5.2), the X hook-tweet rules (§5.8), and the LinkedIn anti-thought-leadership wording (§5.9) extend the T3 §1.5 enforcement to the new platform surfaces. The 12 binding notes are narrowings of the T3 architecture, not redesigns. |
| Audience translation | PASS-WITH-NOTES | X audience skews toward the first tweet; §5.8 binds segment-1 structure so the §1.5 framing is present even in the partial-read case. LinkedIn audience skews toward "thought leadership" prose; §5.9 binds the prompt's anti-thought-leadership defense. Both new platforms inherit T3's "details"/"more" link labeling. |

**Register compliance: PASS-WITH-NOTES.** Both new platform prompts
must teach the LLM the Register-1 / Register-2 distinction with the
same §1.5.4 rows 7–10 substitutions T3 codified. The validator's
substring scan (inherited from T3) catches leakage if the LLM ignores
the prompt.

**Vocabulary compliance: PASS-WITH-NOTES.** Scanned T4-implied
artifact names (file paths, class names, exception names, prompt-file
identifiers). T4 introduces no new §1.5.4 violations at the LSB-authored
identifier surface. Full table in §3.

---

## 2. Rationale on the ten methodology questions

### 2.1. Question 1 — X drafter system prompt content scope

**Ruling — six cached blocks parallel to Bluesky, with Block 6
specialized for thread structure.**

The X drafter system prompt mirrors the T3 Bluesky six-block structure
(§5.4 of the T3 verdict). Blocks 1–5 are nearly identical because the
methodology is identical. Block 6 is the platform-constraint block and
differs from Bluesky's:

- Block 1 — Role and task (~80 tokens). Same posture as Bluesky:
  produce raw post text only, no commentary, no JSON. **Differs**:
  the role description specifies "thread-shaped output, segments
  joined by `\n---\n`, up to 3 segments maximum."
- Block 2 — Corpus-lens anchor (~120 tokens). **Identical to
  Bluesky** verbatim.
- Block 3 — §1.5.4 forbidden-vocab table (~280 tokens). **Identical
  to Bluesky** verbatim. The table is platform-agnostic.
- Block 4 — R10 numeric+CI adjacency rule (~180 tokens). **Identical
  to Bluesky** verbatim except for one X-specific addendum (~30
  tokens): "Each thread segment is independently validated. A
  numeric finding in segment 1 must carry its CI in segment 1, not
  defer the CI to segment 2." Total ~210 tokens for Block 4 on X.
- Block 5 — Register-1 vs Register-2 anchor (~220 tokens). **Identical
  to Bluesky** verbatim.
- Block 6 — X platform constraints + thread structure + hook-tweet
  rules + per-trigger lede patterns (~320 tokens). **X-specific**;
  see §5.4 below for the full content.

**Token budget: ~1240 tokens cached** (vs ~1100 for Bluesky). The
extra ~140 tokens accommodate the thread-structure rules and hook-
tweet constraints. Still above Anthropic's 1024-token cache minimum
and well below the 5000-token threshold at which LLM-attention to the
framing begins to dilute.

**No Block 7.** The Orchestrator's question 1 asked whether X should
get a thread-specific Block 7 separate from the platform-constraint
Block 6. The CDA SME ruling: **no — keep thread rules inside Block 6
alongside the rest of the platform constraints**. Splitting them
across two blocks invites the LLM to treat them as independent rules
when they are tightly coupled (e.g., the hook-tweet structural rules
in §5.8 below depend on the thread-segmentation rules).

### 2.2. Question 2 — X per-segment validation rule (Option A/B/C)

The Orchestrator surfaced three options:
- **Option A:** Each segment must independently satisfy all four
  validator checks (forbidden vocab, R10, hypothesis framing, register
  boundary). Any segment failure rejects the whole thread.
- **Option B:** Forbidden vocab + register boundary apply per-segment;
  R10 applies across the whole thread (number in segment 1, CI in
  segment 2 is OK).
- **Option C:** Hybrid — R10 per-segment for findings but not for
  contextual numerics.

**RULING — Option A.** Each segment independently passes all four
validator checks. Any segment failure rejects the whole thread.

Rationale:

1. **The R10 contract is per-statement, not per-document.** R10
   exists because a bare numeric implies exactness. A reader who
   sees a numeric in isolation reads it as exact. If a thread reader
   only sees segment 1 (the common partial-read case on X), and
   segment 1 contains a bare numeric with the CI parked in segment 2,
   the segment-1-only reader is misled. Option B explicitly enables
   this hazard.

2. **Option C's "findings vs contextual numerics" distinction is the
   CDA SME's call, not the validator's.** The validator already has
   the five exemption categories (model versions, years, character
   counts, count-of-N, URLs) from T3 §5.2. Those are the contextual
   numerics. Anything outside the exemption set is a finding and
   needs a CI. There is no third category that gets a "CI parked in
   a different segment" pass.

3. **Operational simplicity.** Option A is one rule: "each segment
   passes all four checks." Option B and Option C introduce per-
   register exception logic that the Reviewer would have to enforce
   manually. Option A is mechanically enforceable by running
   `validate_draft(segment)` once per segment.

4. **The cost of Option A is low.** A drafter that wants to make a
   thread-spanning finding can replicate the CI in both segments —
   "Smith's S = 0.61, 95% CI [0.48, 0.79]" in segment 1 and "(CI
   [0.48, 0.79] as above)" in segment 2. Repetition is not a
   methodology violation; missing CI is.

**Implementation:** the X drafter's validator wrapper splits the
raw text on `\n---\n`, then calls
`validate_draft(segment_text)` once per segment. Any non-empty
`forbidden_terms_hit` or any failed `framing_checks` value in **any
segment** raises `DrafterRejectedException` with the segment index
attached. See §5.2 binding note.

### 2.3. Question 3 — X thread length cap

**Ruling — 3 segments maximum, 280 chars per segment hard limit, 250
chars per segment target.**

X allows up to 25 tweets in a thread but rambling threads dilute the
finding. Three segments is the methodology-defensible cap:

- **Segment 1 (hook):** the finding statement with numeric + CI. Per
  §5.8 below, segment 1 also carries the framing.
- **Segment 2 (context):** optional second-order detail (e.g., comparison
  baseline, per-trigger lede continuation).
- **Segment 3 (link):** "details {dashboard_url}" + optional one-line
  call to action.

Threads exceeding 3 segments raise `DrafterRejectedException` with
`forbidden_terms_hit=["__x_thread_too_long__"]` (sentinel value
distinguishing structural rejection from vocab rejection).

**Per-segment char limits:**
- Hard limit: 280 chars per segment (X's current limit; the free-tier
  Twitter limit was 280, X's paid tiers vary, 280 is the conservative
  floor)
- Target: 250 chars per segment to leave 30-char URL display buffer
- Hard fail: any segment exceeding 280 chars raises with sentinel
  `__x_segment_overlength_{idx}__`

The Coder may implement these as a single `_check_x_thread_structure()`
helper that runs before per-segment `validate_draft()`.

### 2.4. Question 4 — LinkedIn drafter system prompt content scope

**Ruling — six cached blocks parallel to Bluesky, with Block 6
specialized for long-form structure and Block 5.5 adding anti-
thought-leadership defense.**

The LinkedIn drafter system prompt structure:

- Block 1 — Role and task (~80 tokens). Same posture as Bluesky.
  **Differs**: the role description specifies "long-form single-post
  output, no thread structure, professional tone."
- Block 2 — Corpus-lens anchor (~120 tokens). **Identical** verbatim.
- Block 3 — §1.5.4 forbidden-vocab table (~280 tokens). **Identical**
  verbatim.
- Block 4 — R10 numeric+CI adjacency rule (~180 tokens). **Identical**
  verbatim. The K=12 window stays per §2.6 ruling below — no LinkedIn-
  specific R10 addendum needed.
- Block 5 — Register-1 vs Register-2 anchor (~220 tokens). **Identical**
  verbatim.
- **Block 5.5 — Anti-thought-leadership defense (~140 tokens).**
  LinkedIn-specific addition (see §2.9 below for content). This is the
  one new methodology block T4 introduces.
- Block 6 — LinkedIn platform constraints + long-form structure +
  per-trigger lede patterns (~280 tokens). **LinkedIn-specific**;
  see §5.4 below for the full content.

**Token budget: ~1300 tokens cached** (vs ~1100 for Bluesky). The
extra ~200 tokens accommodate Block 5.5 (anti-thought-leadership) and
Block 6 (long-form structure with per-trigger patterns adapted to
LinkedIn's length budget).

### 2.5. Question 5 — LinkedIn character target

**Ruling — target 800–1500 chars; hard limit 3000 chars.**

Rationale:
- LinkedIn's hard post limit is 3000 characters. Posts beyond this
  truncate.
- 800–1500 chars is the LinkedIn engagement sweet spot per platform
  analytics generally (one paragraph of context + the finding + one
  paragraph of framing fits this range comfortably).
- The 1500-char target gives the drafter room to include one full
  per-trigger lede pattern + an extended framing paragraph + the
  details URL, all in one post.

**Implementation:**
- Hard limit: 3000 chars per post. Posts exceeding raise
  `DrafterRejectedException` with sentinel
  `__linkedin_overlength_3000__`.
- Soft target: 1500 chars. **Not enforced as a hard rejection** — the
  prompt teaches the LLM to target 800–1500 chars, but a 2000-char
  post that passes all four validator checks reaches the queue.
- Minimum: no lower bound. A 400-char LinkedIn post is acceptable if
  it carries the finding + CI + framing + URL.

### 2.6. Question 6 — LinkedIn validator K window

**Ruling — K stays at 12. Do not scale K with content length.**

Rationale:

1. **R10's contract is local adjacency, not document-spanning
   coverage.** The K=12 window measures how close the CI is to its
   numeric *within a sentence-or-clause unit*. A 3000-char LinkedIn
   post is still composed of sentences and clauses; if a numeric and
   its CI are not within 12 tokens of each other within the same
   clause, the reader's adjacency cue is lost regardless of the
   total document length.

2. **Scaling K with content length would dilute R10.** A K=120
   window on a 3000-char post would allow a numeric in paragraph 1 to
   be "covered" by a CI in paragraph 3 — exactly the cross-paragraph
   parking that Option A on X exists to prevent.

3. **K=12 has empirical cover.** T3's K=12 setting was tested against
   the four canonical CI shapes; the adjacency window comfortably
   spans "Smith's S = 0.61, 95% CI [0.48, 0.79]" (~8 tokens) and
   "OCI = 2.4 (1.8, 3.1)" (~6 tokens). LinkedIn posts use the same
   four shapes. No scaling needed.

4. **The drafter learns to repeat CIs.** If LinkedIn-long-form
   prompts the LLM to mention a finding twice (once in the lede, once
   in the closing), the LLM must replicate the CI both times. That is
   the right behavior: each mention is a separate adjacency check.

**No code change vs T3.** The Coder uses the T3 validator unchanged
on LinkedIn drafts.

### 2.7. Question 7 — Cross-segment R10 enforcement on X (already
ruled in §2.2)

Already resolved by Option A in §2.2. The validator runs per-segment;
the segment-1-only reader is protected by §2.2 + §5.8 (hook-tweet
rules).

### 2.8. Question 8 — X hook tweet (segment 1) structural rules

**Ruling — segment 1 must satisfy three additional structural
constraints beyond the per-segment validator:**

1. **Segment 1 must name what is being measured.** Specifically,
   segment 1 must contain at least one of the canonical LSB
   measurement nouns: `Smith's S`, `OCI`, `eigenratio`, `consensus`,
   `categorical structure`, `categorical divergence`, `pile-sort`,
   `free-list`, `corpus lens`. If none of these appear in segment 1,
   the thread is rejected with sentinel
   `__x_segment_1_no_measurement_noun__`.

2. **Segment 1 must carry the finding's CI inline.** Even though the
   per-segment R10 already requires this (Option A in §2.2), the
   hook-tweet rule restates it as a positive constraint: segment 1
   must contain at least one CI-shape match (per the
   `CI_SHAPE_REGEX` from T3 §5.2). If not, the thread is rejected
   with sentinel `__x_segment_1_no_ci_shape__`.

3. **Segment 1 must not attribute intent or cognition to a model.**
   This is the §1.5.4 substring scan applied to segment 1
   specifically, but as a hook-tweet hard rule. Words like "decides,"
   "chooses to," "prefers" (when applied to a model) join the
   forbidden-stem list for segment 1 only. The Coder implements
   `_X_SEGMENT_1_FORBIDDEN_STEMS` with three entries: `decides`,
   `chooses`, `prefers`.

These three constraints implement the "hook-tweet carries
disproportionate reader weight" methodology rule. They apply only to
segment 1; segments 2 and 3 are subject to the standard per-segment
validation only.

**Implementation:** the Coder adds a `_validate_x_hook_tweet()` helper
that runs before the per-segment `validate_draft()` loop. The helper
takes the first segment text and runs:
1. Measurement-noun presence check (regex over the canonical noun
   list).
2. CI-shape presence check (single `CI_SHAPE_REGEX.search()`).
3. Intent-attribution forbidden-stem scan (three regex patterns).

Any failure raises `DrafterRejectedException` with the appropriate
sentinel.

### 2.9. Question 9 — LinkedIn anti-thought-leadership defense

**Ruling — Block 5.5 of the LinkedIn prompt explicitly defends
against thought-leadership prose.** The block content (~140 tokens):

> LinkedIn rewards posts that sound authoritative. Resist the
> default. LSB is a measurement project, not a thought-leadership
> project. The following thought-leadership patterns are forbidden:
>
> - **Do NOT write:** "I've been thinking about how AI models..."
> - **Do NOT write:** "Here's what we're learning about AI models..."
> - **Do NOT write:** "AI is reshaping how we think about..."
> - **Do NOT write:** "The future of AI..."
> - **Do NOT write:** "A surprising finding about AI models..."
>
> Instead:
>
> - **Write:** "LSB measured [finding] across [n] models."
> - **Write:** "[Finding] with 95% CI [a, b] in the [domain] domain."
> - **Write:** "[Finding] is one categorical-structure measurement
>   from LSB's [date] collection."
>
> The post should read as a measurement report, not as a personal
> reflection. The personal pronoun "I" is forbidden in LSB social
> posts. The corporate "we" refers only to the LSB project, never to
> "the AI community" or "humanity."

**Additional validator addendum for LinkedIn:** the Coder extends the
forbidden-vocab patterns with three LinkedIn-specific entries (applied
to LinkedIn drafts only via a `_LINKEDIN_FORBIDDEN_PATTERNS` list):

```python
_LINKEDIN_FORBIDDEN_PATTERNS = [
    re.compile(r"\bI'?ve been thinking\b", re.IGNORECASE),
    re.compile(r"\bthe future of AI\b", re.IGNORECASE),
    re.compile(r"\bAI is reshaping\b", re.IGNORECASE),
]
```

(These are LinkedIn-specific because they're idiomatic to that
platform's thought-leadership genre; they would be over-restrictive
on Bluesky or X.)

**First-person pronoun rule:** the LinkedIn validator additionally
scans for `\bI\b` (case-sensitive, word-bounded) and rejects if the
draft contains it outside of quoted material. The rationale: LSB
posts are project statements, not personal essays. The Coder
implements `_check_linkedin_no_first_person(text)` with one regex.

### 2.10. Question 10 — Per-trigger lede patterns for X and LinkedIn

**Ruling — one canonical pattern per TriggerType for each platform,
scaled to the platform's format.**

The T3 Bluesky prompt has five per-trigger patterns (NEW_MODEL,
NEW_DOMAIN, DRIFT, DIVERGENCE, MONTHLY_ROUNDUP). T4's X and LinkedIn
prompts each get the same five trigger types, with platform-specific
formatting:

**X per-trigger patterns:** each is a **3-segment thread template**.
Segment 1 is the hook (must pass §5.8 hook rules); segment 2 is
context; segment 3 is the URL line. See §5.4 binding note for the
full content. Total ~6 LSB-authored example threads = ~120 tokens
inside Block 6.

**LinkedIn per-trigger patterns:** each is a **single long-form
post template** with a hook paragraph + context paragraph + framing
paragraph + URL line. See §5.4 binding note. Total ~5 LSB-authored
example posts ≈ ~200 tokens inside Block 6.

**Routing:** the Coder produces a first draft of these patterns; they
must pass T3's `validate_draft()` when run against synthetic LLM
outputs. The Architect may instead author them directly. Either path
closes T4. The CDA SME re-reviews the pattern files if any pattern
fails T3 validation in test fixtures.

**Pattern scope binding:** one canonical pattern per TriggerType per
platform. **Not** two patterns per trigger (e.g., a "short" and
"long" pattern). Multiple-pattern-per-trigger introduces selection
logic at the prompt level that complicates the LLM's task without
adding methodology coverage. If a future v2 prompt wants pattern
variation, that is a v2 design issue, not a v1 issue.

---

## 3. Vocabulary compliance on T4-authored strings

| String | §1.5.4 reading | Verdict |
|---|---|---|
| Class name `XDrafter` | Technical descriptor | Compliant |
| Class name `LinkedInDrafter` | Technical descriptor | Compliant |
| File path `cdb_social/drafters/x.py` | Technical descriptor | Compliant |
| File path `cdb_social/drafters/linkedin.py` | Technical descriptor | Compliant |
| File path `cdb_social/drafters/prompts/v1/x.md` | Technical descriptor (versioning) | Compliant |
| File path `cdb_social/drafters/prompts/v1/linkedin.md` | Technical descriptor (versioning) | Compliant |
| Optional helper file `cdb_social/drafters/thread_utils.py` | Technical descriptor | Compliant |
| Helper function name `_validate_x_hook_tweet` | Technical descriptor | Compliant |
| Helper function name `_check_linkedin_no_first_person` | Technical descriptor | Compliant |
| Sentinel `__x_thread_too_long__` | Technical descriptor | Compliant |
| Sentinel `__x_segment_overlength_{idx}__` | Technical descriptor | Compliant |
| Sentinel `__x_segment_1_no_measurement_noun__` | Technical descriptor | Compliant |
| Sentinel `__x_segment_1_no_ci_shape__` | Technical descriptor | Compliant |
| Sentinel `__linkedin_overlength_3000__` | Technical descriptor | Compliant |
| Sentinel `__linkedin_first_person__` | Technical descriptor | Compliant |
| Prompt-block name "anti-thought-leadership defense" | Methodology copy; defends §1.5 framing | Compliant |
| Per-trigger lede patterns (in cached prompts) | Methodology copy — must individually pass §1.5.1 / §1.5.4 / §1.5.7 scans (Coder/Architect produces; CDA SME re-reviews if T4 fixture tests fail) | Compliant pending §5.4 sub-review |
| LinkedIn forbidden-pattern regex strings (`I'?ve been thinking`, `the future of AI`, `AI is reshaping`) | Methodology copy; enforce anti-thought-leadership rule | Compliant |
| X hook-tweet forbidden stems (`decides`, `chooses`, `prefers`) | Methodology copy; enforce §1.5 anti-cognition-attribution for the hook | Compliant |

No new §1.5.4 violations introduced. The T1 verdict's §5.7 (re.
ARCHITECTURE.md §4.6 line 1211 "state of cultural alignment roundup"
prose) remains carry-forward to T7. T4 itself is vocabulary-clean.

---

## 4. Cross-references

### 4.1. T3 binding notes carry forward verbatim

All 18 T3 binding notes (§5.1–§5.18 of the T3 verdict) apply to T4
unchanged. The Coder applies them at T4 implementation:

- T3 §5.1 (forbidden-vocab substring scan) — applies per-segment on X,
  whole-document on LinkedIn (plus the LinkedIn-specific addendum in
  §5.5 below).
- T3 §5.2 (numeric+CI adjacency, K=12) — applies per-segment on X,
  whole-document on LinkedIn at K=12 unchanged (§2.6 ruling).
- T3 §5.3 (hypothesis-framing scan) — applies per-segment on X,
  whole-document on LinkedIn unchanged.
- T3 §5.4 (cached prompt scope) — adapted to X (~1240 tokens) and
  LinkedIn (~1300 tokens); see §5.4 below for the full content.
- T3 §5.5 (methodology-link labeling: "details"/"more", not
  "methodology") — applies to both new platforms unchanged.
- T3 §5.6 (`drafter_self_rating=0.5` fixed) — applies to both new
  drafters unchanged.
- T3 §5.7 (Bluesky 300-char canonical structure) — Bluesky-specific;
  X and LinkedIn have their own structure rules (§5.4 below).
- T3 §5.8 (rejection audit log + v2-bump escalation) — applies; the
  unified `drafter_audit.jsonl` already supports per-platform
  filtering via the `platform` field.
- T3 §5.9 (pass-rate observational) — applies; no per-platform target.
- T3 §5.10 (system-prompt-vs-per-call split) — applies unchanged. The
  X drafter's per-call payload is data-only (trigger evidence +
  numerics + URLs); the LinkedIn drafter's per-call payload is the
  same.
- T3 §5.11 (`framing_checks` four-key dict) — applies to both new
  drafters unchanged. The four canonical keys cover the methodology
  surface; no new keys are introduced at T4.
- T3 §5.12 (`DrafterRejectedException` on validator failure or
  overlength) — applies to both new drafters with platform-specific
  length limits.
- T3 §5.13 (prompt versioning per CLAUDE.md §6 R7) — applies
  unchanged.
- T3 §5.14 (Anthropic prompt-caching per ARCHITECTURE.md §6.2) —
  applies to both new drafters' system prompts.
- T3 §5.15 (no real LLM API calls in tests; fixtures only) — applies
  to T4 fixture tests.
- T3 §5.16 (validator unit tests cover positive + negative per
  sub-check) — applies to T4 unit tests; tests must additionally cover
  per-segment positive/negative cases on X.
- T3 §5.17 (round-trip test: good draft → all-pass SocialDraft) —
  applies; the X round-trip test must verify all three segments pass
  validation; the LinkedIn round-trip test must verify long-form
  draft passes.
- T3 §5.18 (framing-note architectural enforcement via structure rule)
  — applies; the X hook-tweet rule (§5.8 of this verdict) and the
  LinkedIn long-form structure (§5.4) both ensure the framing is
  present even in the partial-read case.

### 4.2. Provider-quote / verbatim-output concern (cross-reference)

Same posture as T3 §4: T4's drafter prompts do NOT instruct the LLM to
quote model output verbatim. The per-trigger lede patterns are
LSB-authored statements about model output, not direct quotes. This
is the right posture for v1 and keeps T4 inside the §1.5 framing
wrapper.

---

## 5. Binding carry-forward notes (apply at Coder dispatch)

These twelve notes are binding on the Coder during T4 implementation.
The Reviewer enforces.

### 5.1. **X drafter system prompt: six cached blocks, ~1240 tokens, no Block 7.** [Claims validity, Audience translation, Register compliance]

The Coder creates `cdb_social/drafters/prompts/v1/x.md` with six
blocks per §2.1 above:

1. Block 1 — Role and task (~80 tokens). Mention thread output up to
   3 segments, joined by `\n---\n`.
2. Block 2 — Corpus-lens anchor (~120 tokens). **Verbatim same as
   T3 §5.4 Block 2** — three sentences from §1.5.1.
3. Block 3 — §1.5.4 forbidden-vocab table (~280 tokens). **Verbatim
   same as T3 §5.4 Block 3** — 12-row markdown table.
4. Block 4 — R10 numeric+CI adjacency rule (~210 tokens). **Same as
   T3 §5.4 Block 4 + 30-token addendum:** "Each thread segment is
   independently validated. A numeric finding in segment 1 must carry
   its CI in segment 1, not defer the CI to segment 2."
5. Block 5 — Register-1 vs Register-2 anchor (~220 tokens). **Verbatim
   same as T3 §5.4 Block 5.**
6. Block 6 — X platform constraints + thread structure + hook-tweet
   rules + per-trigger patterns (~320 tokens). See §5.4 below for full
   content.

No Block 7. Thread rules live inside Block 6.

The Coder invokes prompt caching per ARCHITECTURE.md §6.2
(`cache_control={"type": "ephemeral"}` on the system prompt block).

### 5.2. **X per-segment validation: Option A — each segment independently passes all four checks.** [Claims validity, Analytical validity]

The X drafter's `draft()` method overrides the inherited
`DrafterBase.draft()` (or wraps the validator call) to:

1. Split raw text on `\n---\n` into segments.
2. Check segment count ≤ 3 (raise `__x_thread_too_long__` if not).
3. Check each segment ≤ 280 chars (raise
   `__x_segment_overlength_{idx}__` if not).
4. Call `_validate_x_hook_tweet(segments[0])` (per §5.3 below).
5. For each segment, call `validate_draft(segment)`. If any segment
   returns a non-empty `forbidden_terms_hit` or any failed
   `framing_checks` value, raise `DrafterRejectedException` with the
   segment index attached to the exception message.
6. Aggregate `forbidden_terms_hit` across all segments (de-duplicated)
   into the final `SocialDraft.forbidden_terms_hit`.
7. Aggregate `framing_checks` as the AND across all segments — each
   key is True iff True in every segment.

The Coder implements this in `cdb_social/drafters/x.py` or in a shared
`cdb_social/drafters/thread_utils.py` helper. Either path is
acceptable.

The Reviewer verifies that **R10 is not relaxed across segments** —
i.e., the validator does not combine segments into a single document
for R10 scanning. Each segment is scanned independently.

### 5.3. **X hook-tweet (segment 1) structural rules: three additional checks.** [Claims validity, Audience translation]

The Coder implements `_validate_x_hook_tweet(segment_1_text: str)` in
`cdb_social/drafters/x.py` (or in `thread_utils.py`). The helper runs
three checks:

1. **Measurement-noun presence:** regex over a canonical noun list:
   ```python
   _X_HOOK_MEASUREMENT_NOUNS = re.compile(
       r"\b(?:Smith['']?s\s+S|OCI|eigenratio|consensus|"
       r"categorical\s+(?:structure|divergence)|"
       r"pile[-\s]?sort|free[-\s]?list|corpus\s+lens)\b",
       re.IGNORECASE,
   )
   ```
   No match → raise with sentinel `__x_segment_1_no_measurement_noun__`.

2. **CI-shape presence:** `CI_SHAPE_REGEX.search(segment_1_text)` from
   T3 §5.2. No match → raise with sentinel
   `__x_segment_1_no_ci_shape__`.

3. **Intent-attribution forbidden stems (hook-only):**
   ```python
   _X_SEGMENT_1_FORBIDDEN_STEMS = [
       re.compile(r"\bdecides\b", re.IGNORECASE),
       re.compile(r"\bchooses\b", re.IGNORECASE),
       re.compile(r"\bprefers\b", re.IGNORECASE),
   ]
   ```
   Any match → raise with sentinel
   `__x_segment_1_intent_attribution_{stem}__`.

These three checks run **before** the per-segment `validate_draft()`
loop in §5.2 above. Failure at this stage rejects the whole thread.

### 5.4. **Per-trigger lede patterns for X (3-segment threads) and LinkedIn (long-form posts).** [Claims validity, Audience translation, Register compliance]

The Coder authors per-trigger patterns inside Block 6 of each prompt.
One canonical pattern per TriggerType per platform. The patterns must
individually pass T3's `validate_draft()` when run against synthetic
LLM outputs in T4 fixture tests.

**X canonical patterns (one 3-segment thread per TriggerType):**

NEW_MODEL example structure:
```
[Segment 1]
LSB added {model_id} to the {domain} domain. OCI = {value} ({lo}, {hi}).
The model's corpus lens on {domain} vocabulary: {brief}.
---
[Segment 2]
Across {n} runs, {model_id}'s output concentrates on {pattern}.
This is a Register 1 measurement (within-model output distribution).
---
[Segment 3]
details {dashboard_url}
```

DIVERGENCE example structure:
```
[Segment 1]
{Domain} domain: new high in categorical divergence.
Gap = {value} ({lo}, {hi}) between {model_a} and {model_b}.
---
[Segment 2]
LSB observes the widest output-distribution gap recorded for this
domain (Register 2 — categorical structure across models).
---
[Segment 3]
details {dashboard_url}
```

(NEW_DOMAIN, DRIFT, MONTHLY_ROUNDUP follow the same 3-segment shape.
DRIFT is disabled in v1 per kickoff §2 out-of-scope.)

**LinkedIn canonical patterns (one long-form post per TriggerType):**

NEW_MODEL example structure (~600–800 chars):
```
LSB added {model_id} to the {domain} domain across {n} models.

The model's Output Concentration Index (OCI) on this domain is
{value}, 95% CI [{lo}, {hi}]. OCI is a Register 1 measurement —
it describes a single model's output distribution across repeated
runs on one domain.

{Brief plain-English description of the model's categorical structure
on the domain, using corpus-lens language.}

This is one measurement from LSB's {date} collection.

details {dashboard_url}
```

(Other TriggerTypes follow analogous long-form shapes.)

**Routing:** the Coder produces first drafts of these patterns and
runs them through T3's `validate_draft()` in test fixtures. If any
pattern fails, the Coder revises. If after one revision cycle a
pattern still fails, the Coder routes to the CDA SME for re-review
before T4 closes. The Architect may instead author the patterns
directly. Either path closes T4.

**Pattern scope:** **one** canonical pattern per TriggerType per
platform. No multi-pattern selection logic in v1.

### 5.5. **LinkedIn anti-thought-leadership defense: Block 5.5 + three LinkedIn-specific forbidden patterns + first-person pronoun rule.** [Claims validity, Audience translation]

The Coder includes Block 5.5 of the LinkedIn prompt verbatim per
§2.9 above. Additionally, the Coder extends the LinkedIn drafter's
validator wrapper with:

1. **Three LinkedIn-specific forbidden patterns** (applied to LinkedIn
   drafts only, NOT to Bluesky or X):
   ```python
   _LINKEDIN_FORBIDDEN_PATTERNS = [
       re.compile(r"\bI'?ve been thinking\b", re.IGNORECASE),
       re.compile(r"\bthe future of AI\b", re.IGNORECASE),
       re.compile(r"\bAI is reshaping\b", re.IGNORECASE),
   ]
   ```
   Matches augment `forbidden_terms_hit` and reject the draft.

2. **First-person pronoun rule:**
   ```python
   _LINKEDIN_FIRST_PERSON_RE = re.compile(r"\bI\b")  # case-sensitive
   ```
   Any match outside quoted material raises with sentinel
   `__linkedin_first_person__`. The Coder may implement quote-aware
   skipping by stripping content between matched quote-marks before
   the regex scan; if that adds material complexity, the Coder may
   ship the strict rule (rejection on any `\bI\b`) and document the
   limitation. The strict rule is the CDA SME's preferred posture.

These extensions live in `cdb_social/drafters/linkedin.py` as a
LinkedIn-drafter-specific validator wrapper that runs **after** the
inherited `validate_draft()` and **before** the
`SocialDraft` construction.

### 5.6. **LinkedIn validator K window: K=12 unchanged from T3.** [Analytical validity]

The Coder does NOT modify the K=12 constant in
`cdb_social/drafters/base.py`. The LinkedIn drafter calls the
inherited `validate_draft_numeric_ci_adjacency()` unchanged.

The rationale (per §2.6 above) is that R10's local-adjacency
contract does not scale with document length; a K=120 window would
introduce a cross-paragraph parking hazard that defeats R10.

### 5.7. **X thread length cap: 3 segments max, 280 chars per segment hard, 250 chars per segment target.** [Claims validity, Audience translation]

The Coder implements `_check_x_thread_structure(text: str)` in the X
drafter. The helper:

1. Splits text on `\n---\n` into segments.
2. Raises `DrafterRejectedException` with sentinel
   `__x_thread_too_long__` if len(segments) > 3.
3. Raises `DrafterRejectedException` with sentinel
   `__x_segment_overlength_{idx}__` if any segment exceeds 280 chars.
4. (Soft target: 250 chars per segment is the prompt-taught target,
   not a hard enforcement.)

The check runs before the per-segment validator loop.

### 5.8. **LinkedIn length: 3000 char hard limit, 1500 char soft target, no minimum.** [Claims validity, Audience translation]

The LinkedIn drafter's `_get_length_limit()` override returns 3000.
The inherited `_check_length()` raises with sentinel
`__linkedin_overlength_3000__` (note: the Coder may need to extend
the inherited `_check_length` sentinel naming to include the platform
name; the T3 base class uses `__overlength_{limit}__` — the LinkedIn
override should produce a recognizable sentinel).

The soft 1500-char target is taught in the prompt Block 6; not
validator-enforced.

### 5.9. **X drafter inheritance: subclass of DrafterBase with per-segment validation override.** [Architectural]

The Coder creates `cdb_social/drafters/x.py` with:

```python
class XDrafter(DrafterBase):
    platform: Platform = Platform.X
    drafter_version: str = "x-v1"
    prompt_version: str = "v1"
    ...
```

The Coder overrides the inherited `draft()` method (or adds a
pre-validation hook) to implement the per-segment validation flow per
§5.2. The system prompt is loaded via `load_prompt("x", "v1")`. The
per-call payload follows T3 §5.10 (data-only).

### 5.10. **LinkedIn drafter inheritance: subclass of DrafterBase with LinkedIn-specific validator extensions.** [Architectural]

The Coder creates `cdb_social/drafters/linkedin.py` with:

```python
class LinkedInDrafter(DrafterBase):
    platform: Platform = Platform.LINKEDIN
    drafter_version: str = "linkedin-v1"
    prompt_version: str = "v1"
    ...
```

The Coder overrides `_get_length_limit()` to return 3000. The Coder
adds the LinkedIn-specific forbidden-pattern check and first-person
pronoun check per §5.5 as a post-validate hook in the `draft()`
method (or via composition with a shared helper).

### 5.11. **Fixture tests cover per-platform positive + negative cases.** [Test coverage]

The Coder produces unit tests for the X and LinkedIn drafters at
`packages/cdb_social/tests/test_drafters_t4.py` (or per-platform test
modules). At minimum:

**X tests:**
- Positive: a well-formed 3-segment thread that passes all checks.
- Negative case: thread with 4 segments → `__x_thread_too_long__`.
- Negative case: thread with a 290-char segment →
  `__x_segment_overlength_{idx}__`.
- Negative case: segment 1 missing measurement noun →
  `__x_segment_1_no_measurement_noun__`.
- Negative case: segment 1 missing CI-shape →
  `__x_segment_1_no_ci_shape__`.
- Negative case: segment 1 contains `decides` →
  `__x_segment_1_intent_attribution_decides__`.
- Negative case: segment 2 contains a §1.5.4 forbidden phrase →
  rejection with segment index attached.
- Cross-segment R10 negative case: numeric in segment 1, CI in
  segment 2 → segment 1 rejected for bare numeric (validates
  Option A enforcement).

**LinkedIn tests:**
- Positive: well-formed 800-char post that passes all checks.
- Negative case: post with `I've been thinking` → forbidden hit.
- Negative case: post with `\bI\b` → `__linkedin_first_person__`.
- Negative case: post exceeding 3000 chars →
  `__linkedin_overlength_3000__`.
- Negative case: post with §1.5.4 phrase → forbidden hit.
- Positive case: post with `I've` in a context where it does NOT match
  any forbidden pattern (the regex must not over-match — e.g., a
  hypothetical "I've-been-thinking" should not match the pattern, but
  the pattern as written DOES match this case — the Coder should
  document this edge).

**Shared:**
- Round-trip test: synthetic SocialTrigger + DomainResult + canned
  LLM response → SocialDraft with all-pass framing_checks.
- Audit-log test: a rejected draft writes a record to
  `drafter_audit.jsonl` with `outcome: "reject"` and the correct
  per-platform fields.

The Tester's verdict requires all sub-validator tests to pass.

### 5.12. **No methodology copy in per-call payload (T3 §5.10 carries forward).** [Claims validity]

Both X and LinkedIn drafters' per-call payloads are data-only. The
Reviewer enforces this via code-review check: any string literal
containing §1.5.4 / §1.5.7 phrases inside the per-call payload
construction is grounds for rejection.

The X drafter's per-call payload may carry one additional structured
hint: `n_segments_target: 3` (or `2` for short-finding cases). This
is a structural data point, not methodology copy. It is the only
allowed exception.

The LinkedIn drafter's per-call payload may carry one additional
structured hint: `target_char_count: 1500` (the soft target from
§5.8). Same posture — structural data point, not methodology copy.

---

## 6. Mark-escalation note

**No Mark escalation is required for T4 Coder dispatch.**

Three items Mark should be aware of:

1. **X and LinkedIn drafters produce drafts only.** Neither platform
   has live publishing in Phase 7 per Mark's §7.1 ratification. The
   T6 publisher will raise `PublisherNotEnabled` for both platforms.
   Approved X and LinkedIn drafts sit in `out/social/queue/approved/`
   for Mark to post manually if desired. This is by design.

2. **The X hook-tweet structural rules (§5.3 / §5.8) are stricter
   than the per-segment validator alone.** Segment 1 has three
   additional checks (measurement noun, CI shape, intent-attribution
   stems) that segments 2 and 3 do not have. Mark should expect the
   X drafter's rejection rate to be higher than the Bluesky or
   LinkedIn drafters initially — the hook-tweet rules are the
   strictest in the pipeline. This is intentional.

3. **The LinkedIn first-person pronoun rule (§5.5) is strict.** Any
   `\bI\b` match rejects the draft. If Mark wants to relax this
   later (e.g., allow quoted first-person statements), a v2 prompt
   bump with CDA SME re-review is the path. The strict v1 rule is the
   CDA SME's recommendation because LinkedIn's thought-leadership
   genre is the most likely §1.5 leakage vector across all three
   platforms.

---

## 7. Summary of binding outputs

- **Verdict:** PASS-WITH-NOTES
- **Coder must apply at T4 (12 binding notes plus all 18 T3 notes
  carrying forward):**
  - §5.1 X prompt: 6 cached blocks at ~1240 tokens
  - §5.2 X per-segment validation: Option A (independent per segment)
  - §5.3 X hook-tweet structural rules: 3 additional checks
  - §5.4 Per-trigger lede patterns: one canonical per TriggerType per
    platform
  - §5.5 LinkedIn anti-thought-leadership: Block 5.5 + 3 forbidden
    patterns + first-person pronoun rule
  - §5.6 LinkedIn K=12 unchanged
  - §5.7 X thread cap: 3 segments max, 280 chars per segment hard
  - §5.8 LinkedIn 3000-char hard, 1500-char soft
  - §5.9 X drafter inheritance + per-segment override
  - §5.10 LinkedIn drafter inheritance + validator extension
  - §5.11 Fixture tests: positive + negative per platform
  - §5.12 No methodology copy in per-call payload (T3 §5.10 forward)
- **`cdb_core/schemas.py` change required:** **No.** T4 reads from
  T1 schemas unchanged.
- **`docs/DATA_DICTIONARY.md` change required:** **No.** T1 §13 covers
  SocialDraft fields.
- **Per-trigger lede patterns route through CDA SME if T4 fixture
  tests fail:** **Yes** — first revision cycle is at the Coder level;
  failure after revision routes to CDA SME.
- **T7 doc-sweep flag carry-forward:** the T1 §5.7 ARCHITECTURE.md
  §4.6 line 1211 prose revision remains binding on T7.
- **Architect ratification required:** **No.** The recommended design
  requires no schema change and no re-architecture.
- **Mark escalation:** §6 advisory only, non-blocking for T4 Coder
  dispatch.

---

*End of Phase 7 T4 CDA SME verdict.*
