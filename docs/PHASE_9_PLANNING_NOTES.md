# Phase 9 — Planning Notes (don't lose place)

**Document name:** `docs/PHASE_9_PLANNING_NOTES.md`
**Date created:** 2026-05-19 (immediately after M13 launch + the dashboard-data deploy fix)
**Status:** **paused** — waiting on Mark to answer three scoping questions before any agent is dispatched

> **What this is.** A holding-place capturing where the Phase 9 conversation stopped so Mark can step away and come back without re-deriving the framing. Read this before resuming.

---

## 1. Where we are right now

- Phase 8 is closed. The site is live, the DOI is minted, the launch post is up, the dashboard renders.
- Mark's framing on the v1 dashboard: **"we're very much in the beta period."** Functional, but interpretive friction is high. Researchers landing on `cogstructurelab.com` today cannot tell what they're looking at without context.
- The launch is the start of v1's public life, not the end of LSB development.

---

## 2. The three interconnected problems (Mark's diagnosis, refined)

These have to move together — fixing any one in isolation doesn't solve the user experience.

| # | Problem | Scope of agent involved |
|---|---|---|
| **2.1** | **Interpretive friction on existing surfaces.** MDS coordinates, similarity heatmaps, Romney CCM scores. Hard to read without a guide rail. Phase 6 viz was MVP, not finished. | UX / copy / scaffolding |
| **2.2** | **Data gaps.** More models, more domains, longitudinal snapshots, possibly different measures or aggregations that surface findings the current measures bury. | CDA SME + new collection campaigns |
| **2.3** | **Better viz types for the questions LSB actually answers.** Possibly entirely different chart families, not just polishing the existing ones. | Frontend designer (per `docs/FRONTEND_DESIGNER_BRIEF.md` + `docs/FRONTEND_DESIGNER_BRIEF_APPENDIX.md`) |

Interaction effect: better viz of the wrong data doesn't help. New data without a viz to show it doesn't help. Polished UI without methodology scaffolding doesn't help.

---

## 3. Proposed first step (waiting on Mark to confirm scope)

Dispatch the **Architect** to draft a **Phase 9 kickoff doc** that:

- **Audits the live dashboard** — walks the user journey at `cogstructurelab.com` today and writes down every interpretive failure point ("I see this chart; what is it showing me?")
- **Inventories data gaps** — what's collected, what's not, what would change interpretation
- **Surveys viz alternatives** — for each current chart, what could replace it; for unanswered questions, what would answer them
- **Proposes a decomposition** — does Phase 9 split into 9a/9b/9c? What's gateable to a single agent vs. needing the frontend-designer handoff?

The kickoff doc becomes Mark's **decision surface.** He reads it, refines it, then the Architect decomposes into specific tasks for the agent pipeline.

---

## 4. Three questions Mark needs to answer before dispatch

> **All three should be answered in the same session, before any Architect work begins.**

### 4.1 — Scope width

Does the proposed scope match what's in your head, or are you thinking:

- **Narrower** — just visualization improvements; keep current measures, current data, current methodology framing
- **Same as proposed** — interpretive friction + data gaps + viz alternatives, all in scope
- **Broader** — also revisit research questions, possibly expand to new domains beyond family/holidays/food, possibly add new analytical layers

### 4.2 — Audience for the kickoff doc

- **Inward-looking** — engineer-readable, like the existing `docs/status/*-kickoff.md` precedents (terse, technical)
- **Outward-looking** — something you could share with potential collaborators / advisors / a possible co-author

Inward-looking is faster. Outward-looking requires §1.5-careful framing throughout and another CDA SME review pass.

### 4.3 — When to start

- **Tonight** — dispatch now; tomorrow you wake up to a draft to react to
- **Tomorrow** — sleep on it; pick up fresh
- **Later this week** — let the launch settle first; see what feedback comes in from Bluesky / GitHub / HF before locking scope

---

## 5. Open Phase 8.5 follow-ups (track separately from Phase 9)

These are small items left over from launch — none are blockers for Phase 9 planning, but they shouldn't get lost in the bigger arc.

| Item | Tracked as task | Deadline |
|---|---|---|
| Node.js 20 → 24 GitHub Actions upgrade | #28 | forced 2026-06-02 / removed 2026-09-16 |
| B2 application key rotation | (not tasked; low priority) | none |
| Real methodology page content (replace placeholder) | (likely folded into Phase 9 problem 2.1) | none |
| Skip-to-content site-wide a11y link | (UI/UX agent flagged in T10) | none |
| T6 in-tarball README has `<TBD-T8-DOI>` placeholder forever | (decide whether to rebuild + reupload tarball) | none |
| Post-mortem doc for today's two launch-day gaps (Zenodo Release vs. tag; empty dist/data deploy) | (Claude offered; Mark to decide) | none |

---

## 6. Reference docs to read at pickup

If returning to this cold, in this order:

1. **This file** (orient on where we left off)
2. `docs/PHASE_8_LAUNCH_RUNBOOK.md` — the just-completed runbook; understand what shipped
3. `docs/FRONTEND_DESIGNER_BRIEF.md` + `_APPENDIX.md` — the existing frontend-designer brief (relevant to problem 2.3)
4. `DESIGN_SYSTEM.md` — current visual/token system; will need updates as viz changes
5. `ARCHITECTURE.md` §1.5 + §5.3 (phase plan) — framing constraints and the existing phase-plan precedent
6. `cogstructurelab.com` — open the live dashboard; that's the artifact under question

---

## 7. What to say to Claude when picking up

Three useful prompts depending on where you land:

- *"Phase 9 kickoff — I want scope X, audience Y, dispatch now"* — straight to Architect
- *"Phase 9 kickoff — I have more thoughts, let me brain-dump first"* — conversation first, then Architect
- *"Defer Phase 9 — let me focus on launch reactions and tracked follow-ups instead"* — work the Phase 8.5 items list above

---

*End of Phase 9 planning notes. Resume whenever; this file remembers for you.*
