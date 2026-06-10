---
name: project-tm-c-plan-verdict
description: TM-C term-map label declutter plan verdict 2026-06-10 — PASS-WITH-NOTES; one binding caption/aria-label note plus advisories on salience-source paper trail and post-implementation visual re-confirmation.
metadata:
  type: project
---

TM-C Architect plan verdict 2026-06-10. PASS-WITH-NOTES.

**Why:** Plan implements DESIGN_SYSTEM.md §3.1.1(c) (label-only declutter — collision-aware cluster-label placement + zoom-dependent term-label density keyed to per-model salience rank). Spec was authored under TM-A specifically as TM-C's acceptance surface. Plan correctly preserves R1-a/R1-b/R1-c invariants (AC6), generated_lede surface untouched, no LLM in cdb_analyze, no schema change. Decision C forbids client-side salience recomputation (pitfall 2 / §1 commitment 6 honored). Decision B determinism contract is testable (AC8). §1.5 framing not at risk because the term dots remain at all zoom levels — only labels are gated.

**Binding methodology notes (must land in the executed work):**

1. **Caption / aria-label addition required at default zoom (AC4 surface).** Hiding ~50% of term labels at k=1 risks a journalist mistake — the visible label subset could be read as "the model's full vocabulary." Mitigation already in place (dots render at all zoom levels; lens reveals labels; published `generated_lede` carries the claim) is necessary but not sufficient by itself. The Coder MUST add a static caption (or chart-area aria description) at default zoom in the form: "Labels shown for top-salience terms at this zoom level. Zoom in or hover with the magnifying lens to see all terms." Exact wording is UI/UX-routed but the semantic content is CDA-SME-binding. The grep target is the literal string `top-salience` (or "top salience") at AC4's render path. Forbidden-vocab pre-check applies to this added string.

2. **Salience-source paper trail.** Decision C correctly forbids client-side salience recomputation and routes to `terms` array order (already salience-sorted by the upstream pipeline). The Coder commit body MUST name the salience-source field (e.g., Smith's S or Sutrop CSI) actually flowing through the prop and confirm it is a published-finding measure, not a recomputation. If the Coder discovers the salience rank is implicit in iteration order rather than carried by a named field, that ambiguity is a stop condition — surface back to me before paste. (This is consistent with Decision C's "pause and surface" rule but I am pinning it as a CDA-SME-binding paper-trail requirement in the verdict file.)

**Advisories (non-binding):**

- A1: AC3 visual re-confirmation is sound but the screenshot scenario (Family / 15 models / 20 clusters) is the worst-case spotted; a second informal check at a sparser scenario (e.g., Holidays / 5 models / 8 clusters) would catch the inverse failure mode (over-aggressive hiding when there is no collision pressure). Advisory to Coder.
- A2: Decision A extracting `labelPlacement.ts` is sound; the determinism test (AC8 case iii) is the load-bearing falsifiability hook for this entire task.
- A3: AC6 grep-the-diff rule for `<circle>`, `<ellipse>`, `<polygon>` is the right out-of-scope gate.
- A4: §1.5.4 forbidden-vocab grep (AC13) and em-dash grep (AC12) are both correctly attached.

**Four-axis scorecard:**
- Protocol validity: PASS — no collection-prompt / free-list / pile-sort / interview text altered.
- Analytical validity: PASS — no measure (Smith's S, Sutrop CSI, OCI, B', Romney CCM, MDS, Procrustes, bootstrap, ARI, Mantel, drift) altered; salience source is already-published data per Decision C.
- Claims validity: PASS-WITH-NOTES — binding note 1 above (caption/aria-label at k=1 to prevent "this is the full vocabulary" misread).
- Audience translation: PASS — 30-second journalist read preserved at default zoom once binding note 1 lands.

**Register / vocabulary compliance:** PASS. No R1/R2/R3 confusion in plan text; §1.5.4 forbidden vocabulary not present in plan text.

**How to apply:** On next dispatch (UI/UX gate, then Coder) this verdict file's two binding notes must be acknowledged in the UI/UX verdict (binding note 1 names a string UI/UX owns the exact wording of; binding note 2 names a paper-trail requirement Coder owns at commit time). FAIL the Reviewer step if either is missing from the final commit.

Links: [[project_phase9a_T3_heatmap_reaffirm_verdict]] (prior CI-crosses-null R10 carry-forward pattern), [[feedback_review_rigor_on_thresholds]] (50% threshold at k=1 is a published-finding-shaping cutoff — tested by AC4 step rule).
