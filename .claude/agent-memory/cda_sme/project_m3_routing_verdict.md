---
name: project-m3-routing-verdict
description: M3 deep-link URL routing plan — CDA SME routing-confirmation PASS 2026-06-10; all four axes N/A; one advisory on em-dash glyph hygiene in plan prose vs. final title strings.
metadata:
  type: project
---

M3 plan (deep-link URL routing for top-level NavBar tabs) reviewed 2026-06-10. Verdict: PASS (routing confirmation, all four axes N/A).

**Why:** M3 touches only `apps/dashboard/src/App.tsx`, a new pure `lib/navRouting.ts`, and vitest specs. No methodology surface, no analysis measure, no schema, no lede, no §1.5 framing copy, no model-facing vocabulary. The only generated text is `document.title` = `"Cognitive Structure Lab - <Label>"` using the existing brand string + existing tab labels (`Explore`, `Methodology`, `Collection records`, `Data`, `About`). Architect-pinned ASCII hyphen-minus spacer (§3) satisfies the no-em-dash hard rule unambiguously.

**How to apply:** Routing/SPA-fallback plans that touch zero methodology surface and zero generated lede/register text are CDA SME N/A. Mirror the M4 CSP-decision PASS pattern: quick confirmation, all four axes N/A, single advisory if any prose hygiene risk surfaces. Reuse this template for M5+ infrastructure plans.

**Advisory carried forward to Coder:** the plan body's §3 sentence about en-dash vs. em-dash contains two literal `—` em-dash glyphs as illustrative-but-unfenced text before the final "Pin: ASCII hyphen-minus" decision. Final pin is unambiguous and correct. Coder must not paste either ambiguous glyph into a title string, code comment, commit message, or appended gate-trail verdict.

Related: [[project_m2_about_page_verdict]] [[project_m1_methodology_replace_verdict]] [[feedback_no_em_dashes]]
