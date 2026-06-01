# Findings note → CDA SME question: gpt-5.2 low salience in family is positional, not structural (2026-06-01)

**Status:** Question for the CDA SME gate. No code change proposed. No schema change.
**Trigger:** Two external AI reviews independently claimed gpt-5.2 has an "under-calculated"
/ anomalously low salience score and proposed fixes (aggressive loader-side normalization;
a model-architecture "entropy / corporate polyphony" story). Both were checked against the
data and both are wrong about the cause. This note records what the data actually shows and
asks the SME to ratify the framing before anything is written for public consumption.

**Scope of trust:** Per Mark (2026-06-01), **family is currently the only complete collection
run.** food (0.2) and holidays (0.3) are partial; their salience magnitudes are NOT used here
and should not be cited until those runs complete.

---

## 1. The observation (family, full run, 45–51 runs/major model)

gpt-5.2's position-weighted salience is low relative to peers:

| model | n_runs | top-item CSI | sum top-5 CSI |
|---|---|---|---|
| claude-sonnet-4-6 | 49 | 1.000 | 2.283 |
| claude-opus-4-6 | 49 | 1.000 | 2.276 |
| google/gemini-2.5-pro | 49 | 1.000 | 2.219 |
| openai/gpt-5.4 | 51 | 0.622 | 1.676 |
| **openai/gpt-5.2** | **45** | **0.181** | **0.775** |
| mistralai/mistral-small-2603 | 49 | 0.158 | 0.550 |

This is robust at full sample, not a small-n artifact.

## 2. The cause is positional, not structural

gpt-5.2's **frequency** consensus is maximal — the opposite of fragmentation:

| gpt-5.2 item | appears in | mean position | CSI |
|---|---|---|---|
| `mother` | **45/45 runs** | 5.5 | 0.181 |
| `father` | **45/45** | 6.2 | 0.162 |
| `parent` | **45/45** | 6.5 | 0.153 |
| `self`   | 8/45 | 1.0 | 0.178 |

Contrast claude-sonnet-4-6: `mother` 49/49 at **position 1.0** (CSI 1.000), `father` 49/49 at
position 2.0.

gpt-5.2 names the prototypical kin terms in **every run** but does not front-load them; it
opens variably (sometimes with `self` at position 1) and places `mother`/`father`/`parent`
around positions 5–7. Smith's S and Sutrop CSI are position-weighted, so a universally-present
term that is never listed first scores low. **The indices are behaving exactly as designed** —
they are detecting an ordering property of the output, not a coherence deficit.

Corroborating: the Smith's-S vs Sutrop-CSI agreement ρ for gpt-5.2 is 0.955 (above the 0.85
flag). The two indices agree, so this is not a metric-disagreement artifact.

## 3. Secondary contributor: register-variant spreading (NOT a normalization defect)

gpt-5.2 emits both registers — `mom` (18/45) alongside `mother` (45/45); `dad` (18/45)
alongside `father`. Other models collapse to one canonical form. This splits position/frequency
weight across two strings. This is a genuine property of the output, **not** a parsing bug:
`mom` and `mother` are distinct lexical items and must not be merged. Merging them (the
"aggressive normalization" proposed by external review #1) would corrupt every model's results
and is explicitly the trap flagged in CLAUDE.md §9 pitfall and the prior audit triage.

## 4. What this falsifies

- **External review #1 (loader does no normalization → string fragmentation):** false.
  Normalization runs at collection time (`free_list.py:39–62`); `mother` matches `mother`
  45/45. The CSI collapse is positional, not lexical.
- **External review #2 (entropy optimization / "corporate polyphony" / fragmented categorical
  structure):** falsified by the data. There is zero content fragmentation — `mother` is 45/45.
  An architecture/alignment-level property would also be domain-invariant; gpt-5.2's holidays
  output (partial run, treat as indicative only) front-loads `new year's day` 45/45 at position
  1, CSI 1.0. The model front-loads a prototype when its output has one.

## 5. Proposed framing (LSB-legal — for SME ratification)

> "In the family domain, gpt-5.2's free-list output names the prototypical kin terms in every
> run (`mother`, `father`, `parent` each at 45/45) but does not consistently list them first,
> and it distributes weight across register variants (`mom`/`mother`). Position-weighted
> salience indices (Smith's S, Sutrop CSI) therefore score it lower than models whose output
> front-loads a single canonical prototype. The low salience reflects list-ordering behavior,
> not weaker categorical structure or lower frequency consensus."

No cognition attribution; describes output behavior; "low salience" is explicitly NOT glossed
as "weaker structure."

## 6. Questions for the SME

1. Is the §5 framing acceptable for a methodology-page note / lede, or does it still over-claim?
2. Should the dashboard surface a **frequency-consensus** view alongside position-weighted
   salience, so a reader can see that gpt-5.2's low salience is purely positional? (This is the
   single most clarifying disambiguation in the data; it would also be an argument *for* the
   existing Sutrop-CSI-plus-ρ design.) If yes, that becomes a UI/UX-gated task — out of scope
   for this note.
3. Do we want a standing QA note attached to family results recording the positional/register
   explanation, so future readers don't reach for the two wrong external explanations?

## 7. Explicitly NOT proposed

- No loader-side normalization change (would corrupt all models; banned trap).
- No schema change.
- No change to the salience indices themselves — they are working correctly.
