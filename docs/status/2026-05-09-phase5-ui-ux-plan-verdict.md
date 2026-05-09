# UI/UX Agent Plan-Level Verdict — Phase 5 Architect Plan

**Filed:** 2026-05-09
**Reviewer:** UI/UX agent (Sonnet)
**Plan reviewed:** `docs/status/2026-05-09-phase5-architect-plan.md` (commit `f9a33b7`)
**Slack channel:** `#lsb-ui-ux`
**DESIGN_SYSTEM.md state:** updated to v0.4 alongside this verdict (§12 Phase 5 Visual Decisions added)

---

## VERDICT: PASS-WITH-NOTES

| Question | Result |
|---|---|
| 1. OWID design fidelity | PASS |
| 2. 30-second journalist test | PASS |
| 3. Researcher reproduce-and-cite | PASS |
| 4. WCAG AA accessibility | PASS-WITH-NOTES |

The Phase 5 plan is approved for Coder dispatch with eight binding corrections (F1–F8 below) and the v0.4 DESIGN_SYSTEM.md update. The architectural decisions (option (c) cherry-pick, hand-rolled SVG, template-based lede, manual deploy) all hold up under the four-question review. The prototype screenshots are accepted as visual reference baseline.

PASS-WITH-NOTES rather than PASS because three load-bearing visual decisions in the plan need explicit binding before T4–T13 land:
- (a) the WCAG 2.1 SC 2.1.1 keyboard-accessibility failure in T8's "not focusable" disabled-tab spec (binding correction in §12.3)
- (b) the absent extended color palette (binding correction in §12.4 with five new tokens)
- (c) the embed mode `_headers` security gate at T12 (§12.5)
- plus PNG hi-res scaling (T11 / F5), `_headers` review (T12 / F4 / §12.5), and the §7 "Read as table" deferral (§12.6)

---

## Findings

### F1 — package.json version mismatch (T4, plan-confirmed)

The Phase 0 scaffold has `react@19.2.5` paired with `react-dom@18.3.1`. T4 correctly identifies and fixes this. The Reviewer must confirm the fix (bump to react-dom@19.x with matching @types) resolves the runtime React-current-dispatcher crash before passing T4. **No additional action; plan correctly addresses.**

### F2 — VizSwitcher disabled-tab WCAG failure (T8, binding correction)

The T8 plan specifies disabled VizSwitcher tabs as `aria-disabled` and "not focusable." This is a WCAG 2.1 SC 2.1.1 failure — keyboard users cannot discover disabled affordances removed from the focus order.

**Binding correction (DESIGN_SYSTEM.md §12.3):** Disabled tabs must be focusable with `aria-disabled="true"`, surface a tooltip on both hover and focus, and use a non-color-dependent visual indicator to distinguish from the active tab. Tooltip text: `"Coming in a future update"` — not "Phase 6" (phase numbering is internal vocabulary). The T8 plan spec is superseded by §12.3.

### F3 — Extended color palette not specified (T9 / DataExplorer, binding correction)

DESIGN_SYSTEM.md v0.3 specified six model color tokens. Phase 5 ships 11 models (family) and 9 (holidays) on one chart. No palette extension was specified.

**Binding correction (DESIGN_SYSTEM.md §12.4):** Five new tokens added (`--color-model-7` through `--color-model-11`), each verified WCAG AA 3:1 graphical contrast on white. Stable assignment algorithm specified: sorted `model_id` → palette slot. `DataExplorer.tsx` owns palette assignment and passes `Map<model_id, color>` as a prop to children. T4 must add the five new tokens to `apps/dashboard/src/styles/tokens.css`.

### F4 — frame-ancestors CSP vs embed mode (T12, security prerequisite)

`apps/dashboard/public/_headers` currently specifies `frame-ancestors 'none'`. T12 ships an Embed modal whose `<iframe src="...?embed=true">` snippet cannot work without a path-specific relaxation of this directive.

**Binding correction (DESIGN_SYSTEM.md §12.5):** Before T12 can pass UI/UX, the Coder must flag the `_headers` change to the Reviewer; the Reviewer must approve it per `SECURITY_AND_HARDENING.md` before commit. The Coder does not modify `_headers` unilaterally. T12 acceptance criteria must include "Reviewer + SECURITY_AND_HARDENING.md sign-off on the `_headers` frame-ancestors relaxation."

### F5 — PNG hi-res variant DPI scaling not specified (T11, implementation contract)

The plan §1.4 calls for 2000×2000 hi-res PNG export. The SVG-to-canvas serialization at this size requires explicit canvas dimensioning (`canvas.width = 2000; canvas.height = 2000;`) and SVG coordinate-space scaling at 2× the social size's effective scale.

**Binding correction:** T11 implementation must:
- Set `canvas.width = 2000` and `canvas.height = 2000` for the hi-res variant; `canvas.width = 1600`, `canvas.height = 900` for the social variant.
- Scale the SVG coordinate space such that the rasterized output preserves visual proportions across both export sizes (no clipping, no distortion).
- Watermark position computed as a percentage of canvas dimensions (e.g., `bottom: 2%; right: 2%;`), not as fixed pixels. Both export sizes must show the watermark at identical visual weight.
- Watermark text: `"cogstructurelab.com"` at 3% opacity (per §5).

The Reviewer verifies by inspecting both exports at full resolution.

### F6 — "Read as table" toggle deferral (T13, resolved per §12.6)

DESIGN_SYSTEM.md §7 requires a "Read as table" toggle on every visualization. `AccessibilityTableToggle.tsx` is listed as a Phase 6 component in §11 and is explicitly deferred by the Phase 5 plan T13 footnote.

**Ruling:** Deferral accepted. §7 applies at Phase 6 completion, not as a Phase 5 gate.

**Minimum viable Phase 5 screen-reader posture (DESIGN_SYSTEM.md §12.6):** The MDSPlot SVG container must carry a descriptive `aria-label`. Required format: `"MDS cognitive map of {n} frontier language models on the {domain} domain. {first sentence of generated_lede}."` This is binding at T6.

The Reviewer does not reject T13 for absence of the table toggle. The Reviewer does reject T6 for absence of the descriptive SVG `aria-label`.

### F7 — MDSPlot library: hand-rolled SVG approved (T6)

DESIGN_SYSTEM.md §3.2 listed "D3" as the library for MDSPlot. The plan uses hand-rolled React+SVG (per the prototype). The prototype demonstrates full visual fidelity at this approach.

**Ruling:** Hand-rolled React+SVG is approved for Phase 5. D3 zoom/pan is the Phase 6 migration target. DESIGN_SYSTEM.md §3.2 updated to read "D3 or React+SVG" for the MDSPlot row. The Coder is not required to add D3 in Phase 5.

### F8 — Prototype visual reference accepted

The four prototype screenshots (`docs/status/2026-05-09-phase5-prototype-screenshots/`) are accepted as the visual reference baseline. No blocking issues.

**Visual fidelity confirmed:**
- Typography hierarchy correct (48px article title, 20px key finding, 16px body, Lato + JetBrains Mono via Google Fonts in prototype)
- Color palette correct with cycling beyond slot 6 (issue F3 surfaced from this)
- Axis labels correct ("MDS Dimension 1 — relative" — relative qualifier per §3.3 item 2)
- Bootstrap ellipse rendering at 8% fill / 25% stroke per §3.3 item 3
- R1-state legend with rendered marker samples (filled circle / dashed circle / hollow triangle) per §3.3.5 item 4 binding
- Source attribution line includes inline confidence intervals — exemplary practice for the researcher cite path
- "Cite this | View raw data | CC BY 4.0" links present
- Forbidden-vocabulary scan clean (per CLAUDE.md §7)

**Plan §1.2 option (c) cherry-pick confirmed.** The prototype's commit history is not gate-verified; cherry-picking visual choices into a fresh build via the standard gate chain produces a clean commit history with each task's acceptance criteria verifiable. The prototype's Google Fonts CSP violation is correctly identified and resolved in T4 (self-hosted fonts).

---

## Required before any Coder task begins (apply in this order)

1. **Apply DESIGN_SYSTEM.md v0.4 update** — already applied alongside this verdict. Includes §12 (Phase 5 Visual Decisions), extended palette tokens, §3.2 MDSPlot library entry, footer label correction. The Coder reads v0.4, not v0.3.
2. **Push the v0.4 update + this verdict** as a single commit so the Coder's `git log` reflects the gate state at dispatch time.

## Required corrections per task (binding on Coder and Reviewer)

| Task | Correction | Source |
|---|---|---|
| **T4** | Add `--color-model-7` through `--color-model-11` to `apps/dashboard/src/styles/tokens.css` per §12.4 values. Fix react-dom version mismatch (per F1). | F1, F3, §12.4 |
| **T6** | MDSPlot SVG container must carry descriptive `aria-label`: `"MDS cognitive map of {n} frontier language models on the {domain} domain. {first sentence of generated_lede}."` Hand-rolled SVG approved; D3 not required. | F6, F7, §12.6 |
| **T8** | Disabled tabs are focusable with `aria-disabled="true"` and tooltip on focus (`"Coming in a future update"`). T8 plan spec "not focusable" overridden by §12.3. | F2, §12.3 |
| **T9** | DataExplorer owns palette assignment via sorted `model_id` → slot mapping per §12.4. Compute `Map<model_id, color>` at mount; pass as prop to MDSPlot, ModelSelector, Legend. No child computes color from `model_id` directly. | F3, §12.4 |
| **T11** | Hi-res 2000×2000 export uses explicit `canvas.width/height = 2000`. Watermark position as percentage of canvas dimensions. Both export sizes use identical watermark visual weight. | F5 |
| **T12** | Before Embed modal commits, the `_headers` `frame-ancestors` change must be Reviewer-approved per `SECURITY_AND_HARDENING.md`. Coder flags this; does not self-approve. T12 acceptance criteria expanded to include this gate. | F4, §12.5 |
| **T13** | Mobile layout (375px viewport) must be verified before merge per §8. The §7 "Read as table" toggle absence is acceptable per §12.6; the §12.3 VizSwitcher correction (from T8) and §12.6 SVG `aria-label` (from T6) must both be present in the integrated build. | F6, §8, §12.6 |

---

## Dispatch posture

- **T1 (cdb_publish skeleton + manifest writer)** — pure-Python, no frontend, no methodology. **Authorized for immediate Coder dispatch** post-CDA-SME PASS (which is also in hand at commit `fc72cad`).
- **T2 (lede template generator)** — methodology-bound. Requires SME content verdict at dispatch packet stage (per CDA SME PASS-WITH-NOTES Q1–Q5). Not gated by UI/UX.
- **T3 (publish layer domain JSON writer + derived fields)** — methodology-bound for the salience-rank metric (Sutrop CSI per CDA SME Q4). Not gated by UI/UX.
- **T4–T13** — frontend tasks. Each Coder commit goes through UI/UX review post-Coder, before Reviewer. **The corrections above are binding at commit time, not at dispatch time.** The Coder applies them during implementation; UI/UX verifies during the per-commit review.

---

## §1.7 tagline placement — confirmed PASS

The plan's choice (ArticleHeader subtitle + MethodologySummary block, single source `copy/framing.ts`) is correct. Two occurrences with one source-of-truth constant respects the "single source for the binding tagline" discipline. The CDA SME's Q8 typo correction (`categorise` → `categorize`) is binding on the `TAGLINE` constant.

---

## Carry-forward to per-commit UI/UX reviews

The UI/UX agent will review each Coder commit on T4–T13 before the Reviewer sees it. At each per-commit review:
- Check the relevant binding correction from the table above is implemented.
- Check forbidden vocabulary (CLAUDE.md §7).
- Check WCAG AA on the changed surfaces.
- Check OWID design fidelity.
- Check 30-second journalist comprehension if any user-visible text changed.

The plan §6 acceptance criteria become the Reviewer's audit checklist at commit time. This verdict is the planning-stage gate; commit-stage gates remain.

---

*End of UI/UX plan-level verdict for Phase 5. Posted to `#lsb-ui-ux`. The DESIGN_SYSTEM.md v0.4 update is the second-half of this verdict's deliverable; the Coder reads both before T4 starts.*
