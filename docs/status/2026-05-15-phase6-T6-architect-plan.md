# Phase 6 T6 — Heatmap color scale design system update — Architect Plan

**Date:** 2026-05-15
**Planner:** Architect agent (Opus)
**Phase scope:** Phase 6 T6 only (defined in `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T6 as "UI/UX agent extends DESIGN_SYSTEM.md §1.2 with a sequential or diverging color scale token set (3–5 stops). Mark approves the palette choice"). Atypical task shape: T6 is primarily a design-system / methodology codification rather than a frontend feature, with a small conditional Coder back-port.
**Status:** Awaiting Mark's direction on the §1.A posture decision (A / B / C) and §1.B answer on diverging scale. UI/UX dispatch follows; CDA SME provides notes-only review on the carry-forward CI/R1 concerns. Coder dispatch is conditional on the posture choice and the back-port decision.

---

## §0. Reading list (mandatory before UI/UX and any Coder dispatch)

1. `/opt/lsb-agent/CLAUDE.md` §6 binding rules — **R10** (no point estimates without uncertainty; carry-forward CDA SME N2 dashed-cell aria-label is the load-bearing precedent), **R12** §1.5.4 forbidden vocabulary (applies to any new caption or §12.8 prose), **R13** design-system gating (T6 IS that gate event for §1.2); §7 forbidden vocabulary table; §8 workflow (one commit per task; direct-to-master); §9 pitfall #6 (Coder may not invent visual decisions — palette stops, hex values, naming convention, contrast pairings are all UI/UX + Mark's call), pitfall #8 (no point estimate without uncertainty — back-port must preserve the dashed-cell rule), pitfall #10 (no scope creep — T6 does NOT touch T4 DriftTracker or any future heatmap consumer).
2. `/opt/lsb-agent/ARCHITECTURE.md` §4.5 lines 1107–1114 (R10 binding text; the heatmap-specific clause at line 1110 reads "Cells whose CI crosses the null value are shown with reduced saturation to signal 'not statistically distinguishable.'" — this is the §4.5 text the T5 dashed-border implementation is a token-constrained substitution for, per CDA SME T5 verdict §5.4; T6 is the natural place for the saturation-rendering refinement if Mark wants it now rather than at T14).
3. `/opt/lsb-agent/DESIGN_SYSTEM.md` v0.4.8 — **§1.2 Color Palette** (file lines 71–118; current state: 11 model colors, 3 origin colors, 2 archival baseline tokens, 1 component-scoped `--color-heatmap-cell-text-dark`, no sequential or diverging tokens), **§3.3.5 R1-state annotations on Register 2 points** (file lines 291–346; **R1 semantic is shape-encoded — filled circle / dashed circle / hollow triangle — over model palette colors; no separate R1-state color tokens exist**), **§12.8 SimilarityHeatmap cell-text contrast specification** (file lines 1618–1656; the WCAG AA contrast spec the new scale must continue to satisfy or supersede), §11 component inventory (file lines 1461–1476), §12.4 model color assignment (file lines 1523–1535).
4. `/opt/lsb-agent/apps/dashboard/src/components/SimilarityHeatmap.tsx` — lines 70–127 (`HEATMAP_BASE_RGB`, `HEATMAP_TEXT_SWITCH_THRESHOLD`, `cellBackground()`, `cellTextFill()`, `ciCrossesNull()`); lines 440–522 (cell render with alpha-blend + dashed-border CI-crosses-null treatment + contrast switch).
5. `/opt/lsb-agent/apps/dashboard/src/components/MDSPlot.tsx` — lines 1–20 R1-state docblock; lines 489–584 R1-a/b/c marker rendering. Reads to confirm R1 markers use model palette colors with shape encoding, NOT a dedicated R1 color palette — so the "color-confusing R1-state markers" risk in the kickoff is a collision between the new sequential scale and **the eleven model colors `--color-model-1` through `-11`** at file lines 75–87 of `tokens.css`, not a collision with R1-specific tokens.
6. `/opt/lsb-agent/apps/dashboard/src/styles/tokens.css` lines 76–122 (existing model + origin + heatmap-component tokens).
7. `/opt/lsb-agent/apps/dashboard/src/styles/similarity-heatmap.css` (current CSS — no color tokens in it; all alpha-blend computation is in TSX).
8. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-architect-plan.md` §2.2 (the "alpha-blend on `--color-text-primary`" decision that T6 is now reconsidering), §2.3 (the dashed-border CI-crosses-null treatment as a token-constrained substitution for §4.5 "reduced saturation").
9. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md` §4 ("Reduced-saturation rendering — dashed border vs. alpha desaturation"); §5.4 (deferred §4.5 text refinement, with suggested replacement sentence that explicitly names T6: *"reduced visual weight (dashed border in the 0.2 release; sequential-palette desaturation when the heatmap color tokens land in T6)"*). This is the binding precedent that T6 either honours by introducing a saturation-rendering path or defers to a follow-up.
10. `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-uiux-plan-verdict.md` F-T5-C1 (the WCAG AA 4.5:1 calculation table at lines 42–55 of the verdict; **this is the contrast spec the new scale must not regress**).
11. `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T6 (one-line scope) and §5 ("§1.2 Color Palette | DESIGN_SYSTEM.md | Update — heatmap sequential or diverging scale tokens | T6").
12. Memory: `feedback_ui_polish_scope.md` (Phase 6 = minimum viable functional dashboard; UI/UX gating reduces to accessibility floor + R10 + readability — for T6 this means the WCAG AA contrast floor at §12.8 plus the R10 dashed-cell rule must not regress; **anything beyond that is FT-designer territory and out of scope**).

---

## §1. Mark's binding directives + T6 framing

1. **T6 is a retroactive codification task, not a forward-looking dependency.** The kickoff (2026-05-12) framed T6 as "before T5 so T5 has tokens to consume." T5 shipped 2026-05-12 without T6 tokens, using `rgba(44, 62, 80, similarity)` on `--color-text-primary`. The natural dependency edge T6 → T5 is retroactive. T6's job is to (a) decide whether to codify what T5 already uses, (b) decide whether to also generalize forward for T4 DriftTracker and any future heatmap consumer, and (c) document the CI-crosses-null treatment that lives in the rendering today but is unnamed in §1.2 or §12.8.
2. **Phase 6 minimum-viable functional surface** (memory `feedback_ui_polish_scope.md`). UI/UX gating reduces to accessibility floor + R10 + readability. No "the palette could be prettier" critique. The bar is *named, documented, contrast-safe, non-regressing tokens*.
3. **WCAG AA contrast floor is the binding bar** — the existing §12.8 specification (white text passes ≥4.5:1 at `similarity > 0.73`; black text passes ≥4.66:1 at `similarity ≤ 0.73`) must continue to hold for **every** stop in the new scale that any rendered cell could land on. If the new scale changes the per-cell hue (Posture B), the §12.8 contrast table must be **recomputed**, not assumed to transfer.
4. **No new dependencies.** No `d3-scale`, `d3-scale-chromatic`, `viridis-js`, `colorjs.io`, `chroma-js`, or similar. The palette is a fixed N-stop set of hex values defined in `tokens.css` and named in DESIGN_SYSTEM.md §1.2. Interpolation, if any, is CSS-native (`color-mix()` is acceptable only if both Mark and the WCAG check approve; otherwise the implementation samples discrete stops). Reviewer R8 enforces.
5. **R10 binding non-negotiable.** The CI-crosses-null dashed-border rule shipped in T5 is binding (CDA SME T5 verdict §4 + §5.2). T6 either (a) preserves the dashed-border treatment verbatim and adds the sequential scale alongside it, or (b) replaces dashed-border with a saturation-reduction rendering — which requires recomputing the WCAG AA contrast check at the desaturated stops, the §5.2 aria-label augmentation language stays unchanged, and the CDA SME T5 §5.4 "T14 §4.5 refinement" is brought forward into T6's commit body.
6. **No methodology surface beyond §12.8 update.** T6 may extend §12.8 to name the scale tokens and document the CI-crosses-null visual rule; T6 MUST NOT add a methodology page section, info-icon, or expandable tooltip about the palette choice (per CDA SME T5 §5.5).
7. **Forbidden vocabulary applies to any LSB-authored prose in DESIGN_SYSTEM.md §1.2 / §12.8 changes** — the existing caption ("Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the no-shared-structure value.") is binding verbatim per CDA SME T5 §5.1 and must not be changed without a fresh CDA SME pass. The §12.8 prose can be extended but must not introduce "model X believes," "worldview," "agrees with," "perceives," or any §1.5.4 forbidden phrase.
8. **Bundle budget.** Posture A: zero new code-path bytes; the alpha computation is unchanged, only token names move. Posture B: ≤ 3 KB gzipped delta if a multi-stop CSS gradient or per-cell hex lookup replaces the alpha-blend formula. Posture C: zero delta now; future Coder PR is on its own budget.
9. **No software-side spend gates** (R14). N/A for T6 — trivially satisfied; no orchestration paths touched.
10. **Direct-to-master per CLAUDE.md §8.** T6 may ship as one commit (DS update only, Posture A no-back-port or Posture C) or two commits (DS update + back-port, Posture A with back-port or Posture B). Architect's preference: **one commit** — the DS update and the SimilarityHeatmap back-port are tightly coupled (rename of constants must move with the token introduction) and bundling them keeps the verdict chain coherent.

---

## §1.A. Open question for Mark — POSTURE DECISION (BLOCKER; required before UI/UX dispatch)

This is the only Mark-level question that gates UI/UX dispatch. The Architect's lean is **Posture A**, but two of three postures are defensible and Mark's choice will materially change what UI/UX evaluates.

### Posture A — Codify the T5 alpha-blend gradient as a 5-stop sequential scale (ARCHITECT'S RECOMMENDATION)

**What it does.** Promote what T5 already renders to **named tokens** in `tokens.css` and DESIGN_SYSTEM.md §1.2, sampled at 5 evenly-spaced stops of the existing `rgba(44, 62, 80, similarity)` formula. Naming proposal (UI/UX confirms or revises): `--color-scale-seq-0` through `--color-scale-seq-4`, computed by pre-compositing the alpha-blend on white at similarity values {0.0, 0.25, 0.5, 0.75, 1.0} and committing the resulting hex strings. SimilarityHeatmap.tsx continues to use `rgba(44, 62, 80, similarity)` for continuous rendering (the tokens are the documented reference points, not the runtime palette — same as how `--color-ellipse-fill`/`stroke` document opacity points without driving D3 interpolation).

**Sample hex values (verification target for UI/UX, not binding here — UI/UX recomputes):**
- `--color-scale-seq-0` ≈ `#ffffff` (similarity 0.00, white)
- `--color-scale-seq-1` ≈ `#cfd2d5` (similarity 0.25)
- `--color-scale-seq-2` ≈ `#9ea5ad` (similarity 0.50)
- `--color-scale-seq-3` ≈ `#646e7a` (similarity 0.75)
- `--color-scale-seq-4` ≈ `#2c3e50` (similarity 1.00 = `--color-text-primary`)

**Back-port to SimilarityHeatmap.** Mechanical: introduce a constant `HEATMAP_BASE_TOKEN = "var(--color-scale-seq-4)"` (or similar) and reference it in the `HEATMAP_BASE_RGB` extraction comment so the source-of-truth pointer in the .tsx file points at the new sequential-scale token instead of `--color-text-primary`. The actual `rgba()` formula is unchanged. **Visual output: byte-identical.** Existing T5 vitest assertions pass without modification.

**CI-crosses-null treatment.** Unchanged — keep the dashed-border rule shipped in T5. Document it in DESIGN_SYSTEM.md §1.2 or §12.8 with a sentence pointing at SimilarityHeatmap as the consumer; defer the §4.5 saturation-rendering refinement to T14 (per CDA SME T5 §5.4). Architect's view: **defer to T14 in Posture A**; the dashed border is functioning, accessible, and SME-approved. Don't fix what isn't broken when the scope is "minimum viable functional dashboard."

**Diverging scale.** Not added in Posture A. Deferred to T4 (DriftTracker) plan if T4 determines it needs one — at which point a separate `--color-scale-div-*` token set is added in T4's UI/UX plan-level verdict and DESIGN_SYSTEM.md gets a v0.4.x bump there.

**Architect's rationale for recommending A:**
1. **Minimum-viable per `feedback_ui_polish_scope.md`.** Phase 6 polish is FT-designer-bound; the Architect-Coder loop's job is to name and document what already works. A "proper perceptually-uniform sequential palette" is the FT designer's call, not UI/UX's at this minimum-viable Phase 6 bar.
2. **Zero regression risk.** Visual output is byte-identical. §12.8 contrast spec transfers unchanged. F-T5-C1 BINDING calculation table at lines 42–55 of the T5 UI/UX verdict remains valid as-is. The CDA SME T5 §5.1/§5.2 caption + aria-label bindings are not re-litigated.
3. **The "T6 unblocks T5" sequencing premise no longer applies.** T5 shipped. The remaining sequencing benefit is **T6 → T4 DriftTracker** (sequential scale available when T4 plans), and Posture A delivers that with a sequential scale named. A diverging scale is a T4-specific question that T4 should drive when it plans.
4. **One commit.** The DS update + the SimilarityHeatmap.tsx comment/constant rename land in the same PR. No multi-step migration.
5. **Aligns with the kickoff "3–5 stops" language.** Kickoff explicitly allows 3 stops as the floor. Architect proposes 5 (better granularity, still trivial to compute) but UI/UX may reduce to 3 if Mark prefers a coarser palette.

**Posture A risks.** One — the §4.5 binding text still says "reduced saturation" while T5/T6 render dashed-border. That's a T14 doc-text refinement per CDA SME §5.4. Not a Posture A blocker.

---

### Posture B — Replace the T5 alpha-blend with a perceptually-uniform multi-stop sequential palette

**What it does.** UI/UX (with Mark's approval) selects a *different* palette — e.g., OWID's blue-to-orange sequential, a viridis-like green-to-yellow, or a custom two-hue interpolation — and defines 5 stops as named tokens. SimilarityHeatmap.tsx is materially reworked to consume the new stops (either via a per-cell hex lookup at discrete bins, or via a CSS multi-stop `linear-gradient` over a `<rect>` with `fill="url(#gradient-id)"`).

**CI-crosses-null treatment.** Two options inside Posture B:
- **B.1** Keep dashed border (same as Posture A); the new palette is a hue change only.
- **B.2** Adopt true saturation reduction (drop the dashed-border treatment; render CI-crosses-null cells at desaturated stops of the new palette). This is the literal §4.5 rendering. Requires recomputing WCAG AA contrast at desaturated stops, recomputing the §5.2 aria-label augmentation (the visual signal changes; the SR-only signal is unchanged), and bringing the CDA SME T5 §5.4 §4.5 refinement into T6's commit body verbatim.

**Diverging scale.** Mark may opt to add `--color-scale-div-*` in the same PR, pre-emptively serving T4 DriftTracker. Adds palette-design surface area; UI/UX must select diverging endpoint hues that don't collide with sequential stops or with model palette colors 1–11.

**Posture B risks (load-bearing, surfaced for Mark):**
1. **Regression risk on §12.8 contrast specification.** The 4.5:1 WCAG AA calculation in F-T5-C1 of the T5 UI/UX verdict assumes the cell background is `rgba(44, 62, 80, similarity)` composited on white. A different palette produces different background luminance values at every stop. The contrast switch at `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73` was empirically tuned to this specific blue tint. The UI/UX agent has to redo the entire table at the new palette and may need to introduce **two** switch thresholds (one for sequential, one for diverging) — or commit to picking a palette whose mid-tone is dark enough that the threshold stays at 0.73, or accept moving the threshold.
2. **Test churn.** T5 has tests asserting specific text-fill values at specific similarity points. Those tests likely change.
3. **Mark approval cycle.** Posture B requires the FT-designer-level palette selection happening inside Phase 6 minimum-viable, which is exactly what `feedback_ui_polish_scope.md` says to avoid. Architect lean: **this should be the FT designer's task post-launch**, not a Phase 6 task.
4. **Bundle delta.** Modest (~1–3 KB) but real. If the per-cell rendering switches from `rgba()` to a per-cell hex lookup against bins, the lookup table is bytes.
5. **CDA SME re-review.** If B.2 is chosen, the dashed-border rule the CDA SME approved at T5 §4 is *replaced*. SME does not need to re-PASS, but the saturation rendering is a methodology-adjacent visual decision the SME has notes-only authority on (per the kickoff), and the §4.5 refinement text changes from "T14 deferred" to "T6 binding" — that's a SME-notes-only event but is non-trivial.

**Architect's read of B:** Defensible if Mark explicitly wants the §4.5 "reduced saturation" rendering to land now rather than at T14, or if Mark wants a palette change for visual-polish reasons that override the minimum-viable framing. Not the recommendation under current Phase 6 framing.

---

### Posture C — Codify a 3-stop sequential scale now (Posture A subset); defer everything else to T4

**What it does.** Posture A minus the 5-stop granularity — define exactly 3 stops (`--color-scale-seq-low`, `--color-scale-seq-mid`, `--color-scale-seq-high`) corresponding to similarity ≈ 0, 0.5, 1.0. Same alpha-blend formula, no back-port required (the .tsx file's `HEATMAP_BASE_RGB` constant stays and is documented as the source-of-truth for both the new mid/high tokens). No diverging scale.

**Posture C trade-off vs. A.** Same regression-risk profile (zero); same bundle profile (zero); same gating profile. Loses two intermediate stops that the FT designer might find useful as anchor points later. Gains nothing meaningful in exchange.

**Architect's read of C:** Almost equivalent to A; if Mark prefers the more cautious "name only what we strictly need" posture, C is fine. Architect lean: **prefer A's 5-stop granularity** because the marginal cost (computing two extra hex values once) is trivial and the marginal benefit (FT designer has stable anchor points to remap against later) is real.

---

### Architect's recommendation summary

**Posture A** with **5 stops** and **dashed-border CI-crosses-null preserved verbatim from T5**. Defer diverging scale to T4. Defer §4.5 saturation-rendering refinement to T14. Back-port SimilarityHeatmap.tsx in the same commit (mechanical constant rename only; no visual change).

If Mark prefers C (3 stops, even more cautious), the plan below adapts trivially — change "5 stops" to "3 stops" in every reference, drop two hex values from §3 AC #1, and the rest is unchanged.

If Mark picks B, the plan needs material rework — UI/UX dispatches with a wider mandate (select a palette, redo the contrast table, decide B.1 vs B.2, decide diverging-or-not), the Coder back-port becomes load-bearing rather than mechanical, and the CDA SME notes-only review becomes a re-review of CDA SME T5 §5.4 implications. **If Mark picks B, the Architect re-plans before UI/UX dispatch.**

---

## §1.B. Surfacing the CDA SME concern from the kickoff

The kickoff (§2 T6) lists CDA SME as **notes-only** with one concern: *"sequential scale must encode the 'CI crosses null' reduced-saturation rule visually without color-confusing R1-state markers."* Two sub-questions to surface:

### §1.B.1. Current state of the CI-crosses-null rule in SimilarityHeatmap (already implemented)

**Implementation today** (T5 shipped, SimilarityHeatmap.tsx lines 446–464):

```
const crossesNull = !isDiagonal && ciCrossesNull(ci);
const strokeDasharray = crossesNull ? "3,2" : undefined;
const strokeWidth = crossesNull ? 1.5 : 1;
const stroke = crossesNull ? "var(--color-text-primary)" : "var(--color-border)";
```

Where `ciCrossesNull(ci)` returns true iff `ci[0] < SIMILARITY_NULL_VALUE < ci[1]` and `SIMILARITY_NULL_VALUE = 0.5` (the rescaled Mantel-correlation null, CDA SME T5 verdict §2 approved). The visual signal is a **dashed border**, not a reduced-saturation cell fill. The CDA SME T5 verdict §4 explicitly approved this as a "token-constrained substitution" for §4.5's "reduced saturation" instruction, with the deferral text in §5.4 naming T6 as one of two possible homes for the §4.5 refinement (the other being T14).

**T6 disposition under Posture A:** the rule is **preserved verbatim**. T6 documents it in DESIGN_SYSTEM.md §1.2 or §12.8 with a one-sentence pointer to the SimilarityHeatmap implementation. The §4.5 doc-text refinement remains a T14 follow-up.

**T6 disposition under Posture B.1:** preserved.

**T6 disposition under Posture B.2:** replaced by saturation-rendering at desaturated stops of the new palette. CDA SME's §5.4 suggested replacement sentence for §4.5 — *"reduced visual weight (dashed border in the 0.2 release; sequential-palette desaturation when the heatmap color tokens land in T6)"* — moves from "T14 binding suggested source text" to "T6 in-scope edit." This is the largest substantive shift across the three postures and is precisely what Mark is being asked about in §1.A.

### §1.B.2. R1-state marker color-collision check

**Source of the kickoff concern:** R1-state markers in MDSPlot (filled circle / dashed circle / hollow triangle per DESIGN_SYSTEM.md §3.3.5 file lines 322–331) carry **shape** as the R1 semantic and **model palette color** as the model identity. They are rendered in `MDSPlot.tsx` lines 489–584. There are **no dedicated R1-state color tokens** in §1.2 — the R1 semantic is purely shape-encoded.

**What this means for T6.** The collision risk is not "new heatmap stops vs. R1-state colors" (no such colors exist). The collision risk is "new heatmap stops vs. the eleven model palette colors `--color-model-1` through `-11`" which are consumed by MDSPlot for both R1 markers and ellipses, and by Legend / DownloadBar swatches.

**Under Posture A.** The sequential scale is a grayscale-blue gradient on the existing `--color-text-primary` base. The mid-stop hex values (e.g., `#9ea5ad`, `#646e7a`) are desaturated cool grays. **Collision check:** the eleven model palette colors at `tokens.css` lines 79–92 are all saturated chroma (OWID-blue, red, orange, green, purple, teal, dark orange, dark blue, dark purple, dark teal, dark gold). Visual inspection confirms no Posture A stop is within typical perceptual distance of any model color. **CDA SME notes-only verdict expected on this point: clean; no further action.** UI/UX confirms in the §12.8 update prose.

**Under Posture B.** Depends entirely on the new palette. If UI/UX proposes (e.g.) an OWID blue-to-orange sequential, the blue endpoint may sit near `--color-model-1` (`#3360a9`, OWID blue) and the orange endpoint may sit near `--color-model-3` (`#e67e22`) or `--color-model-7` (`#d35400`). This is a real collision risk that the UI/UX agent owns. The collision check is *per-stop against each of the 11 model colors* and must produce a documented `≥ ΔE`-or-perceptual-distance verdict in the UI/UX plan-level verdict file. Architect lean: this is one more reason Posture B is overkill at the Phase 6 minimum-viable bar.

**CDA SME notes-only:** scoped to a single question — does the new scale's mid-tone collide with the model palette in a way that would make a heatmap cell look like a model-palette swatch in any context where the two appear adjacent (legend tooltip, sr-only summary cross-references)? The answer under Posture A is "no, the sequential scale is desaturated cool gray; the model palette is saturated chroma; no perceptual collision." Under Posture B this is an open question UI/UX must answer.

---

## §2. Decisions (under Posture A — Architect's recommended default; rewrite required if Mark picks B)

### §2.1. Number of stops — **5**.

Stops sampled at similarity values {0.00, 0.25, 0.50, 0.75, 1.00} of the existing alpha-blend formula. UI/UX may revise to {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} or back to 3-stop {0.0, 0.5, 1.0} per Mark's preference. The kickoff allows "3–5 stops" — Architect picks 5 for granularity. UI/UX has authority to revise.

### §2.2. Token naming convention — **`--color-scale-seq-0` through `--color-scale-seq-4`** (UI/UX confirms or revises).

Rationale: the `-seq-` infix encodes "sequential" so a future `--color-scale-div-*` set can be added without ambiguity. The numeric suffix encodes ordinal position from lightest (0) to darkest (4). Alternative naming considered and rejected: `--color-heatmap-stop-N` (component-scoped; would have to be renamed when DriftTracker or any other consumer wants the same scale), `--color-similarity-low/mid/high` (semantic but couples token name to a single use case).

### §2.3. Hex values — computed by UI/UX from `rgba(44, 62, 80, similarity)` composited on `#ffffff`.

Architect provides sample values in §1.A for orientation; UI/UX recomputes and locks in the verdict. The computation is deterministic (sRGB alpha compositing), not a design choice; UI/UX's job is to (a) verify each computation, (b) confirm each stop passes WCAG AA 3:1 graphical-object contrast on white if used as a standalone swatch (for future legend or downloadable-image use), and (c) confirm none collides perceptually with any of the eleven `--color-model-N` tokens.

### §2.4. Relationship to the existing alpha-blend rendering — **tokens document; the continuous gradient remains.**

The tokens are **reference points**, not the runtime palette. SimilarityHeatmap.tsx continues to compute the per-cell background with `rgba(44, 62, 80, similarity)` for continuous rendering (any of the ~120 cells can land at any similarity value in [0, 1], and discretizing to 5 bins would lose fidelity). The named tokens are what `tokens.css` and §12.8 reference when describing the scale; they are what a future Coder building DriftTracker or any other heatmap consumer reads from when deciding "what does the sequential scale look like at the midpoint?"

This is the same pattern as `--color-ellipse-fill` and `--color-ellipse-stroke` in §1.2 (file lines 100–101): a documented reference opacity for the uncertainty ellipse rendering, not the actual runtime values (MDSPlot composes per-model ellipse fills at 8% of the model color, not from these tokens directly).

UI/UX has authority to deviate from this pattern if there's a reason to make the tokens runtime-consumed (e.g., a CSS `linear-gradient` used as a `fill="url(#gradient-id)"` on the heatmap rects). The Architect's lean is that the alpha-blend formula is simpler and the per-cell computation is bounded (≤ 121 cells), so the runtime path stays as it is.

### §2.5. SimilarityHeatmap back-port — **YES, in the same commit, mechanical-rename only**.

Two edits in `SimilarityHeatmap.tsx`:

1. Update the comment at line 76 (currently `"--color-text-primary"`) to point at the new sequential-scale tokens: `// RGB of --color-scale-seq-4 (≡ --color-text-primary); kept in sync via this comment naming the source token`.
2. Update the comment block at lines 73–78 to reference DESIGN_SYSTEM.md §1.2's sequential-scale subsection (whatever subsection name UI/UX chooses).

**No change** to:
- `HEATMAP_BASE_RGB = "44, 62, 80"` value (RGB triplet of `--color-scale-seq-4`, same as `--color-text-primary`).
- `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73` value or rationale.
- The `cellBackground()` / `cellTextFill()` / `ciCrossesNull()` functions.
- The dashed-border CI-crosses-null treatment.
- The §12.8 contrast-switch logic.
- Any T5 test assertion.

This is what makes Posture A near-zero-risk.

### §2.6. CI-crosses-null treatment — **dashed border preserved verbatim from T5.**

Per CDA SME T5 verdict §4 acceptance of the token-constrained substitution. T6 documents the rule in DESIGN_SYSTEM.md §12.8 with a sentence pointing at SimilarityHeatmap.tsx lines 446–464. The §4.5 doc-text refinement (CDA SME T5 §5.4 suggested replacement sentence) remains a T14 follow-up; T6 mentions T14 in the commit body but does not edit §4.5.

### §2.7. Diverging scale — **NOT added in T6.**

Deferred to T4 DriftTracker plan when (and if) T4 determines a diverging scale is needed. A diverging scale spans `negative null positive` (e.g., drift relative to baseline: -0.15 to 0 to +0.15) and is conceptually distinct from a sequential scale (0 to 1, no signed null). T4 will know whether its data shape calls for diverging and what the endpoints should be. Pre-committing to a diverging palette now invites the same UI/UX selection overhead Posture B carries, for a consumer that doesn't yet exist.

If Mark explicitly wants diverging-now, the Architect re-plans this section.

### §2.8. DESIGN_SYSTEM.md version bump — v0.4.8 → v0.4.9.

Same pattern as T11 (v0.4.6 → v0.4.7) and T12 (v0.4.7 → v0.4.8). One-bullet changelog entry summarizing: "Adds §1.2 sequential color scale token set (`--color-scale-seq-0` through `--color-scale-seq-4`); codifies the T5 alpha-blend rendering as the named sequential scale; extends §12.8 with the CI-crosses-null dashed-border rule documented at the scale level; no SimilarityHeatmap visual change; no other component touched."

### §2.9. Where the §12.8 update lands.

The new §1.2 tokens go in §1.2 (the color palette section). The CI-crosses-null rule documentation goes in §12.8 (SimilarityHeatmap-specific) — extending the existing section, not creating a new subsection. UI/UX may decide a fresh "§1.2.x Sequential Scale" subsection is warranted; that's UI/UX's call.

---

## §3. Acceptance criteria (Posture A baseline; adapts to C trivially; rewrite under B)

1. `apps/dashboard/src/styles/tokens.css` contains five new tokens `--color-scale-seq-0` through `--color-scale-seq-4`, with hex values computed by UI/UX from `rgba(44, 62, 80, similarity)` composited on `#ffffff` at similarity values {0.00, 0.25, 0.50, 0.75, 1.00}. Each token has a comment naming the similarity stop it corresponds to and pointing at DESIGN_SYSTEM.md §1.2.
2. `DESIGN_SYSTEM.md` §1.2 documents the new tokens in a code block with the same five-line comment structure as the existing `--color-model-*` tokens. The block sits between the existing "UI chrome" subsection (file line 103) and "SimilarityHeatmap component-scoped token" subsection (file line 118), or wherever UI/UX determines the natural section order goes.
3. `DESIGN_SYSTEM.md` §1.2 has a short prose comment (2–3 sentences) explaining: (a) the tokens are documented reference points for a sequential scale; (b) the runtime rendering in SimilarityHeatmap.tsx uses the underlying `rgba()` alpha-blend formula for continuous gradient (the tokens are not runtime-consumed); (c) cross-reference to §12.8 for the contrast-switch and CI-crosses-null rules.
4. Each of the five tokens passes WCAG AA 3:1 graphical-object contrast on `#ffffff` when used as a standalone swatch (so a future legend, downloaded PNG legend, or print rendering does not regress accessibility). UI/UX reports the computed contrast in the §1.2 comment or in the plan-level verdict.
5. The §12.8 contrast specification is **unchanged in substance**. UI/UX confirms in the plan-level verdict that the F-T5-C1 WCAG AA calculation table at lines 42–55 of `2026-05-12-phase6-T5-uiux-plan-verdict.md` continues to hold because the new tokens are sampled from the same alpha-blend formula at the same base color.
6. `DESIGN_SYSTEM.md` §12.8 is extended with one paragraph documenting the CI-crosses-null dashed-border rule shipped in T5, pointing at `SimilarityHeatmap.tsx` lines 446–464 as the implementation site, and noting that the §4.5 binding text refinement (per CDA SME T5 §5.4) is a T14 follow-up. The existing §12.8 contrast-switch content (file lines 1618–1656) is preserved verbatim.
7. `apps/dashboard/src/components/SimilarityHeatmap.tsx` is back-ported per §2.5: two comment edits only, pointing the `HEATMAP_BASE_RGB` source-of-truth comment at the new sequential-scale tokens. **No behavior change. No new constants. No new imports. No CSS edits.**
8. `apps/dashboard/src/components/SimilarityHeatmap.tsx` renders visually identical output to the pre-T6 state — every cell background, text fill, border style, dashed pattern, and tooltip is byte-identical. The Tester confirms via the existing T5 vitest suite (zero modifications required).
9. R1-state marker color collision: UI/UX confirms in the plan-level verdict that no new sequential-scale stop is within perceptual collision distance of any `--color-model-1` through `--color-model-11`. UI/UX is the authority on the collision check method (e.g., ΔE * approximation, side-by-side visual inspection, or a one-line CSS test page). The collision-check verdict goes in the §12.8 extension prose (one sentence) or in §1.2's new prose (UI/UX's call).
10. `DESIGN_SYSTEM.md` version header bumped from `v0.4.8` to `v0.4.9`. Footer same. New changelog bullet prepended above v0.4.8 with the summary text from §2.8.
11. `apps/dashboard/src/styles/similarity-heatmap.css` is **unchanged**.
12. `apps/dashboard/src/data/types.ts` is **unchanged**.
13. `cdb_core/schemas.py` is **unchanged** (CLAUDE.md R6 trivially satisfied; no Architect sign-off needed because no schema is touched).
14. `docs/DATA_DICTIONARY.md` is **unchanged** (no schema field touched).
15. `apps/dashboard/src/components/MDSPlot.tsx`, `FreeListCompare.tsx`, `ModelSelector.tsx`, `Legend.tsx`, `DriftTracker.tsx` (not yet built) are **unchanged**.
16. `apps/dashboard/src/styles/app.css` is **unchanged** (the new tokens flow through `tokens.css`; no new global rules needed).
17. `cd /opt/lsb-agent/apps/dashboard && npm run build && npm run test && npm run lint` passes locally before commit. No new test files. No modifications to existing test files.
18. Bundle delta is ≤ 0.5 KB gzipped against the post-T12 baseline (HEAD c094ef3) — five new CSS custom properties, two comment edits in TSX. The Coder reports the measured delta in the commit body.
19. No new dependencies. No new imports.
20. No forbidden vocabulary (§1.5.4) in any committed text — `tokens.css` comments, DESIGN_SYSTEM.md §1.2 and §12.8 additions, the changelog bullet, commit message, commit body. Reviewer's grep against the diff passes.
21. The binding T5 caption text ("Each cell shows how similarly two models organize this domain (1.00 = identical organization; 0.50 = no shared structure). Dashed cells: 95% confidence interval includes the no-shared-structure value.") is **not touched**; the CDA SME T5 §5.1 binding remains intact.
22. The binding T5 aria-label augmentation for dashed cells ("; confidence interval includes the no-shared-structure value of 0.50" per CDA SME T5 §5.2) is **not touched**.
23. One commit. Commit message follows Conventional Commits: `docs(dashboard): T6 — heatmap sequential color scale tokens (DS v0.4.9)` or similar; commit body references the T6 plan path, the UI/UX verdict path, the CDA SME notes-only verdict path, and the §12.8 / §1.2 / §3 AC mapping.

---

## §4. Files to touch

| File | Change | Owner |
|---|---|---|
| `/opt/lsb-agent/apps/dashboard/src/styles/tokens.css` | Add five sequential-scale token declarations in `:root {}` block between line 117 (`--color-surface-hover`) and line 121 (`--color-heatmap-cell-text-dark`), with hex values and per-token comments | UI/UX writes the spec; Coder applies |
| `/opt/lsb-agent/DESIGN_SYSTEM.md` | §1.2 sequential-scale tokens documented; §12.8 CI-crosses-null rule paragraph appended; version header v0.4.8 → v0.4.9; changelog bullet prepended; footer v0.4.8 → v0.4.9 | UI/UX |
| `/opt/lsb-agent/apps/dashboard/src/components/SimilarityHeatmap.tsx` | Two comment edits at lines 73–78 / 76 — pointer to new sequential-scale tokens; **no behavior change** | Coder (mechanical) |
| `/opt/lsb-agent/docs/status/2026-05-15-phase6-T6-architect-plan.md` | This plan (already authored as you read this) | Architect (done) |
| `/opt/lsb-agent/docs/status/2026-05-15-phase6-T6-uiux-plan-verdict.md` | UI/UX plan-level verdict with palette computation table, WCAG AA contrast confirmation, collision check, DS v0.4.9 update applied | UI/UX |
| `/opt/lsb-agent/docs/status/2026-05-15-phase6-T6-cda-sme-verdict.md` | CDA SME notes-only verdict on (a) CI-crosses-null treatment continuity, (b) R1-marker collision summary | CDA SME |

**No changes to:**
- `cdb_core/schemas.py`, `docs/DATA_DICTIONARY.md`, `ARCHITECTURE.md`.
- `apps/dashboard/src/data/types.ts`.
- `apps/dashboard/src/styles/similarity-heatmap.css`, `app.css`, any other CSS module.
- `apps/dashboard/src/components/*.tsx` except `SimilarityHeatmap.tsx` (two-comment edit).
- Any existing test file.
- Any prompt template, any `cdb_*` Python package, any CI workflow.

---

## §5. Out of scope

- **Posture B** unless Mark explicitly selects it in §1.A. If Mark picks B, the Architect re-plans before UI/UX dispatch.
- Diverging scale (`--color-scale-div-*` token set). Deferred to T4 DriftTracker.
- §4.5 `ARCHITECTURE.md` doc-text refinement (CDA SME T5 §5.4 suggested replacement sentence). Deferred to T14.
- DriftTracker (T4), T7 FreeListCompare, T9 failures, T10 failures display, T11 mobile nav (shipped), T12 mobile drawer (shipped), T13 new content, T14 doc sweep — all unchanged by T6.
- Any visual change to SimilarityHeatmap rendering, CI-crosses-null rendering, or contrast-switch behavior.
- Any new D3 / Plotly / color-library dependency.
- Any change to the binding T5 caption text or dashed-cell aria-label augmentation (CDA SME T5 §5.1 and §5.2).
- Any methodology page edit, info-icon, or expandable section about the palette choice (CDA SME T5 §5.5).
- WCAG AA contrast re-tuning at the dark-text arm (the existing `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73` and `--color-heatmap-cell-text-dark = #000000` are kept).
- Dark mode (out of scope project-wide).
- Hierarchical-clustering cell reorder (Phase 7+).
- Any swatch UI in Legend, DownloadBar, or Methodology page.

---

## §6. Gate routing (atypical for T6)

Per the kickoff: **UI/UX owns the palette choice; CDA SME provides notes-only review; Mark approves the palette; Coder dispatch is conditional.**

### §6.1. Mark — POSTURE DECISION (BLOCKER)

Mark answers §1.A: Posture A (Architect's recommendation), Posture B, or Posture C. Until Mark answers, UI/UX is **not** dispatched. If Mark picks Posture B, the Architect re-plans before UI/UX dispatch.

Mark also confirms or overrides on a secondary question: **does Mark want a diverging scale added pre-emptively for T4 DriftTracker?** Architect's recommendation: no, defer to T4. Mark may override.

### §6.2. UI/UX — REQUIRED (palette computation + DS update + verdict)

Once Mark answers §1.A, UI/UX is dispatched. Mandate under Posture A:

1. **Compute** the five hex values from the alpha-blend formula. Verify with WCAG / sRGB compositing math (or `color()` browser DevTools; the math is deterministic).
2. **Confirm** each token passes WCAG AA 3:1 graphical-object contrast on `#ffffff` (for future standalone-swatch use).
3. **Confirm** no stop is in perceptual collision with any `--color-model-1` through `-11`. Method is UI/UX's call (ΔE * 76 or 2000 calculation, side-by-side visual inspection, or test page); the collision-check result is documented.
4. **Confirm** the F-T5-C1 WCAG AA contrast-switch calculation (T5 verdict lines 42–55) continues to hold unchanged because the alpha-blend formula and the base color are unchanged. One-paragraph confirmation in the verdict.
5. **Apply** the DS v0.4.9 update in the same commit as the Coder's back-port (UI/UX writes the spec; the Coder commits the .md and .css together). UI/UX adopts the same posture as T11 / T12 — `**Version:** v0.4.8` → `v0.4.9`, prepend changelog bullet, footer bump, §1.2 token additions, §12.8 paragraph append.
6. **Verdict file** posted to `docs/status/2026-05-15-phase6-T6-uiux-plan-verdict.md` per T11 / T12 format.

### §6.3. CDA SME — NOTES-ONLY (no PASS/FAIL gate; advisory only)

Once UI/UX has the palette computation locked, the Architect routes the plan + UI/UX verdict to CDA SME for **notes-only** review on two questions:

1. Is the CI-crosses-null dashed-border treatment from T5 preserved verbatim under Posture A? (Expected answer: yes; trivially satisfied; one-paragraph confirmation.) If Mark picked Posture B.2, this question becomes the load-bearing CDA SME review of a saturation-rendering replacement — and CDA SME's notes-only authority widens to advisory on the §4.5 doc-text refinement.
2. Does the perceptual collision check (§6.2 item 3) clear the kickoff concern about "color-confusing R1-state markers"? (Expected answer under Posture A: yes — the sequential scale is desaturated cool gray, the model palette is saturated chroma; no perceptual collision. Under Posture B: depends on the palette.)

CDA SME verdict file posted to `docs/status/2026-05-15-phase6-T6-cda-sme-verdict.md`. Notes-only means CDA SME does not block T6 dispatch on a PASS/FAIL gate; the verdict produces carry-forward notes that the Coder applies, but no escalation to Mark is expected.

### §6.4. Coder — CONDITIONAL (one mechanical commit OR no commit, depending on Posture)

**Under Posture A** (Architect's recommendation): Coder is dispatched after UI/UX PASS + CDA SME notes-only filed. Coder's job is the §2.5 two-comment back-port plus committing the DS update UI/UX has authored. **One commit.**

**Under Posture A with no back-port chosen by Mark**: Coder is dispatched only to commit the DS update + tokens.css. No SimilarityHeatmap.tsx edit. UI/UX's commit IS the implementation.

**Under Posture B**: Coder is dispatched for the SimilarityHeatmap.tsx rework (rendering path changes; vitest assertions may need updates), the new CSS path if any, the DS update, and the tokens.css addition. Significantly larger scope. Architect re-plans before this dispatch.

**Under Posture C**: same as Posture A but with 3 tokens instead of 5.

### §6.5. Reviewer — standard 9-check sweep

Standard Reviewer pass per CLAUDE.md §6 and `SECURITY_AND_HARDENING.md` §9 Reviewer rules table. The R10 binding (no point estimate without uncertainty) check is satisfied trivially under Posture A (no behavior change). The R7 check (schema change → DATA_DICTIONARY.md update) is trivially satisfied (no schema touched). The R8 check (no new deps) is trivially satisfied. The forbidden-vocabulary grep covers the diff in full.

### §6.6. Tester — verifies the existing T5 vitest suite passes unchanged under Posture A

The Tester's mandate is unusual for T6: **no new tests**, **no test modifications**. The Tester confirms `cd apps/dashboard && npm run test` passes without modification — this is the regression check for Posture A's "byte-identical visual output" claim. Under Posture B, the Tester rewrites failing T5 tests against the new rendering; that's a separate task plan.

---

## §7. Schema impact

| Touch point | Touched? | DATA_DICTIONARY.md co-update? | Architect sign-off? |
|---|---|---|---|
| `cdb_core/schemas.py` | No | No | No |
| `docs/DATA_DICTIONARY.md` | No | No | n/a |
| `ARCHITECTURE.md` | No (§4.5 refinement deferred to T14) | No | n/a |
| `DESIGN_SYSTEM.md` | Yes (§1.2 add + §12.8 paragraph append + v0.4.9 bump) | No | UI/UX owns; no Architect sign-off |
| `apps/dashboard/src/data/types.ts` | No | No | n/a |
| `apps/dashboard/src/styles/tokens.css` | Yes (add 5 sequential-scale tokens) | No | n/a |
| `apps/dashboard/src/components/SimilarityHeatmap.tsx` | Yes (2 comment edits only) | No | n/a |

**CLAUDE.md R6 (no schema edit without Architect sign-off + DATA_DICTIONARY.md co-update):** trivially satisfied; no schema field changes.

---

## §8. Bundle budget

Post-T12 baseline (HEAD c094ef3): per T12 plan §8 estimate, dashboard bundle sits around 100 KB gzipped. T6 delta:

- Five new CSS custom properties in `tokens.css`: ~0.2 KB gzipped (custom-property declarations compress aggressively).
- Two TSX comment edits: 0 KB (comments are stripped by minification).
- No new code paths, no new imports, no new CSS rules.

**Expected delta: ≤ 0.5 KB gzipped.** Phase 6 cumulative cap is 400 KB; T6 contributes negligibly.

Under Posture B, expected delta is ≤ 3 KB gzipped (per-cell hex lookup table or a CSS gradient definition). Still within cap.

---

## §9. Dependency order

**Upstream of T6:** none. T6 is a documentation-and-codification task; no upstream Coder work is required.

**Downstream of T6:**

- **T4 DriftTracker.** Benefits from having `--color-scale-seq-*` already named and documented when the T4 UI/UX plan-level review evaluates the DriftTracker color-encoding decisions. If T4 needs a diverging scale, that's a T4 UI/UX decision; T6 having sequential tokens does not pre-commit T4 on diverging.
- **T14 documentation sweep.** Inherits the §4.5 doc-text refinement (CDA SME T5 §5.4 suggested replacement sentence); T6 leaves that pending and notes the deferral in §12.8 + commit body.
- **FT designer (post-launch).** Inherits the named sequential scale as a stable anchor point to remap palette stops against, if the FT designer decides a different sequential palette is warranted post-launch.

**Parallel to T6:** any task with no overlap on `DESIGN_SYSTEM.md` §1.2 or `tokens.css` — practically, all other Phase 6 tasks not currently in-flight.

---

## §10. Risks and watch-items

1. **Mark picks Posture B and re-plan is required.** Probability: moderate, depending on Mark's read of the FT-designer-deferral framing. Mitigation: §1.A surfaces the trade-off explicitly; the Architect re-plans before UI/UX dispatch under Posture B.
2. **UI/UX proposes a 7-stop scale or different naming convention.** Probability: low (kickoff allows "3–5 stops"); UI/UX has authority but the kickoff bound is the Architect's stop-count anchor. If UI/UX revises to 3 stops, the plan adapts trivially per §1.A Posture C; revising above 5 stops violates the kickoff and should bounce back to Architect for re-plan.
3. **CDA SME flags the R1-marker collision check as insufficient.** Probability: low under Posture A (the sequential scale is desaturated cool gray; the model palette is saturated chroma; perceptual distance is large at every stop). Under Posture B, this risk is real and is one of three reasons B is not the recommendation.
4. **WCAG AA 3:1 graphical-object contrast fails for `--color-scale-seq-1` (similarity 0.25, hex ≈ `#cfd2d5`).** This is the lightest non-zero stop; its luminance on white is high. If standalone-swatch contrast fails on white, UI/UX has two options: (a) move the stop darker (e.g., recompute at similarity 0.30 instead of 0.25), or (b) document that the lightest stop is non-standalone-safe and is only used in compositional contexts where it is bordered by `--color-border` (per existing SimilarityHeatmap rendering). Architect lean: option (b) — the stop documents a similarity gradient, not a standalone swatch; the contrast check is informative, not blocking, at this stop.
5. **Coder forgets the §2.5 mechanical rename and tries to "improve" the alpha computation.** Reviewer rejects; CLAUDE.md §9 pitfall #6 enforces. Plan §2.5 is binding "mechanical-rename only."
6. **The 5-stop computation accidentally captures the same hex as `--color-text-primary` at stop 4** (which it does, by construction — that's the whole point). UI/UX confirms the redundancy is intentional and the comment at `--color-scale-seq-4` cross-references `--color-text-primary` as the equivalent token. Not a real risk; just naming hygiene.
7. **DESIGN_SYSTEM.md v0.4.9 changelog cross-references the wrong T5 verdict files or omits the §4.5 deferral note.** Mitigation: the §0 reading list paths are absolute; UI/UX cites them verbatim in the changelog bullet per T11 / T12 precedent.
8. **The §4.5 binding text refinement (CDA SME T5 §5.4) gets opportunistically pulled into T6 against this plan's §5 out-of-scope rule.** Mitigation: §5 is explicit; Reviewer rejects scope creep into `ARCHITECTURE.md` §4.5 under T6.

---

## §11. Done mapping (Posture A, single commit)

A T6 commit is **done** when all of the following are true:

- [ ] §3 AC #1–#23 satisfied as written.
- [ ] `cd /opt/lsb-agent/apps/dashboard && npm run build && npm run test && npm run lint` passes with no test modifications.
- [ ] No regression in `SimilarityHeatmap.tsx` visual output (Tester confirms via existing T5 vitest suite).
- [ ] UI/UX plan-level PASS or PASS-WITH-NOTES filed at `docs/status/2026-05-15-phase6-T6-uiux-plan-verdict.md`, with all binding notes applied.
- [ ] CDA SME notes-only verdict filed at `docs/status/2026-05-15-phase6-T6-cda-sme-verdict.md`, with carry-forward notes applied if any.
- [ ] Reviewer PASS or PASS-WITH-NOTES with all notes addressed.
- [ ] Commit message follows Conventional Commits (`docs(dashboard):` or `style(dashboard):` per the diff shape — Architect lean: `docs(dashboard):` because the substantive change is documentation; the .tsx edit is comment-only and the .css edit is documentation-style).
- [ ] Commit body references this plan, the UI/UX verdict, the CDA SME notes-only verdict, the §3 AC mapping, and the bundle delta measurement.
- [ ] No forbidden vocabulary in any diff line.
- [ ] No new dependency added.
- [ ] No schema change.
- [ ] DESIGN_SYSTEM.md version header, footer, and changelog all bumped to v0.4.9.

---

*End of T6 plan. The Architect awaits Mark's §1.A posture decision before dispatching UI/UX.*

---

# Report-back summary (per Architect spec)

**(a) One-sentence summary.** T6 is now a retroactive-codification task — T5 already shipped without T6 tokens, so T6's job is to name and document the alpha-blend gradient already in production (Posture A, my recommendation), or to swap it for a different multi-stop palette (Posture B), or to do a minimal 3-stop subset of A (Posture C).

**(b) Clear recommendation: Posture A — 5-stop sequential scale, mechanical back-port, dashed-border CI rule preserved, diverging scale deferred to T4, §4.5 doc-text refinement deferred to T14.** Rationale in three points:

1. **Aligned with `feedback_ui_polish_scope.md`.** Phase 6 = minimum viable functional dashboard; UI/UX gating = accessibility floor + R10 + readability. Posture A names what works and lets the FT designer remap later. Posture B reintroduces FT-designer-level palette selection inside Phase 6, which is what the memory says to avoid.
2. **Zero regression risk.** SimilarityHeatmap.tsx renders byte-identical output; the §12.8 contrast calculation transfers unchanged; CDA SME T5 §5.1/§5.2 bindings are not re-litigated; existing T5 vitest suite passes without modification. Posture B has documented regression risk on §12.8 (the WCAG AA calculation table assumes the specific blue tint; any other palette requires re-doing the entire table at the new colors).
3. **The sequencing premise no longer applies.** T5 shipped without T6 tokens, so "T6 before T5" is moot. The remaining sequencing benefit is T6 → T4 DriftTracker (sequential scale named when T4 plans). Posture A delivers this; diverging is T4's question to drive when T4 plans.

**(c) Inputs needed from Mark beyond posture choice:**

- **Stop count under Posture A** — Architect proposes 5; kickoff allows 3 to 5. Mark may prefer 3 (Posture C). The plan adapts trivially.
- **Diverging scale now or deferred to T4** — Architect recommends defer to T4. Mark may want it pre-emptively added in T6 to avoid a second DS bump at T4.
- **Palette family if Posture B** — Mark would need to state a preference (OWID blue-orange? viridis-style? custom two-hue? match a published research-paper convention?) before UI/UX can produce a meaningful palette computation. Under Posture A, no palette family question — it's the existing alpha-blend formula on `--color-text-primary`.

**(d) Genuine surprises uncovered during plan drafting:**

1. **R1-state markers don't have their own color tokens.** I checked the §3.3.5 R1-c "hollow triangle" decision and the MDSPlot R1 marker rendering (lines 489–584). R1 markers carry **shape** as the R1 semantic (filled circle / dashed circle / hollow triangle) and **model palette color** as the model identity. There is no separate R1-state color palette. So the kickoff's "without color-confusing R1-state markers" concern reduces to "without color-confusing the eleven `--color-model-N` tokens," which under Posture A is trivially satisfied (cool-gray sequential vs. saturated-chroma model palette). Under Posture B this is a real per-stop collision check UI/UX must run.
2. **The CI-crosses-null rule is shipped as a dashed border, not as reduced saturation.** The T5 plan §2.3 and the CDA SME T5 verdict §4 explicitly named this as a "token-constrained substitution" for §4.5's "reduced saturation" instruction, and §5.4 of the CDA SME verdict suggested replacement text for §4.5 that names T6 as one of two possible homes (the other being T14). So T6 is a load-bearing decision point on whether to honour CDA SME §5.4 now (Posture B.2) or defer to T14 (Posture A). The plan recommends defer; this is the one place where Posture A explicitly chooses the cautious path over a SME-suggested forward improvement.
3. **§12.8's WCAG AA contrast spec is tuned to one specific hue.** The F-T5-C1 BINDING calculation table (T5 UI/UX verdict lines 42–55) assumes `rgba(44, 62, 80, similarity)` composited on white. The `HEATMAP_TEXT_SWITCH_THRESHOLD = 0.73` was empirically derived for this exact blue tint. Any palette change in Posture B forces a full recomputation of that table and possibly a new threshold value (or two thresholds, one per palette). That's the biggest concrete reason the Architect recommends Posture A — the contrast tuning is non-trivial work to redo and the existing tuning is correct.

---

**File paths referenced (all absolute):**

- `/opt/lsb-agent/docs/status/2026-05-15-phase6-T6-architect-plan.md` — destination for this plan (Mark persists)
- `/opt/lsb-agent/docs/status/2026-05-12-phase6-architect-kickoff.md` §2 T6
- `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-architect-plan.md` §2.2, §2.3
- `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-cda-sme-verdict.md` §4, §5.1, §5.2, §5.4
- `/opt/lsb-agent/docs/status/2026-05-12-phase6-T5-uiux-plan-verdict.md` F-T5-C1 lines 42–55
- `/opt/lsb-agent/docs/status/2026-05-15-phase6-T11-architect-plan.md` and T12 plan — format precedents
- `/opt/lsb-agent/DESIGN_SYSTEM.md` §1.2 (lines 71–118), §3.3.5 (lines 291–346), §12.8 (lines 1618–1656), §11 (lines 1445–1481)
- `/opt/lsb-agent/ARCHITECTURE.md` §4.5 line 1110 (R10 heatmap clause)
- `/opt/lsb-agent/apps/dashboard/src/components/SimilarityHeatmap.tsx` lines 70–127, 446–464
- `/opt/lsb-agent/apps/dashboard/src/components/MDSPlot.tsx` lines 489–584 (R1 marker rendering)
- `/opt/lsb-agent/apps/dashboard/src/styles/tokens.css` lines 76–122
- `/opt/lsb-agent/apps/dashboard/src/styles/similarity-heatmap.css` (no edits)
- `/opt/lsb-agent/CLAUDE.md` §6 R10, §7 forbidden vocab, §8 workflow, §9 pitfall #6