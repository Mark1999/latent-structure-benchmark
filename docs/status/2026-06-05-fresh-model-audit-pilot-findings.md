# Fresh-Model Audit PILOT — findings + Architect triage (2026-06-05)

First run of the process in `docs/proposed/2026-06-05-fresh-model-audit-runbook.md`. Three read-only Lens-A/B passes (backend correctness, frontend correctness, cross-cutting structural), then Architect triage. Mark verified the top 3 findings at file:line before triage. This file IS the backlog — disposition recorded so a future audit doesn't re-raise declines.

## Verified-real (confirmed at file:line)
- **V1 (P0): social cron loads ZERO domains.** `cli.py:154` builds nested `data_dir/{slug}/{version}.json`, but default `data_dir=apps/dashboard/public/data/` holds FLAT files (`family.v0.3.json`). Cron exits 0 (looked green 2026-06-04) but detection loads nothing. **The 2026-06-04 cron fix stopped the crash but was INCOMPLETE.** Three lenses converged on this.
- **V2 (P0): admin console trigger list permanently empty.** `routes.py:155` reads `data.get("triggers", [])` from `emailed_dedupe_keys.json`; writer `cli.py:261` only ever writes `{"keys":[...]}`. The sole sanctioned LLM-draft site (pitfall #17) is dead; all drafts 404.
- **V3 (P1): `var(--font-size-md)` undefined** (`focus1.css:26`; tokens.css has xs/sm/base/lg/xl/2xl/3xl, no `md`). Silent CSS fallback (pitfall #15) on Focus-1 model headings.

## Triaged backlog
**P0 — fix now:**
- **T1 — DONE (`cabc036`, Reviewer PASS-WITH-NOTES).** completed the social-cron fix. Reads FLAT `data_dir/{slug}.v{version}.json` (fallback `{slug}.json`+warn), added "loaded N domain result(s)" startup guard log. Verified live: `detect --dry-run` logs "loaded 3 domain result(s)" (was silently 0).
- **T2 — DONE (`2cd8bf5`, Reviewer PASS-WITH-NOTES).** admin trigger source. Investigation found the trigger DICTS were never persisted at all (cmd_detect emailed them, saved only dedupe-key strings) and there was no `queue/triggered/` dir — so the Architect's Option A rested on a non-existent path. **Mark chose: cron persists `detected_triggers.json`** (the post-dedupe `new_triggers`, on email-success path only — not dry-run; cleared to `{"triggers":[]}` on zero-trigger days); admin reads that. ALSO fixed the same flat-vs-nested path bug in `routes.py:_load_domain_result_for_trigger` (was loading a STUB) via a shared `published_domain_file()` helper. Verified: admin trigger now loads real family data (15 models), was empty stub.

**P1 — next batch:**
- **T3 — DONE (`147cfe3`).** UI/UX PASS-WITH-NOTES → Coder → Reviewer PASS-WITH-NOTES (note applied) → Tester PASS. `focus1.css:26` `var(--font-size-md)` → `var(--font-size-base)` (UI/UX picked `base`+bold; `lg` reserved for lede/key-finding); DESIGN_SYSTEM §1.1 no-`md` annotation + §13.12 binding `.f1-model-heading` spec (v0.13.1). Verdicts: `docs/status/2026-06-08-T3-font-size-md-uiux-verdict.md`. The recurrence-guard grep was ruled OUT of scope (CI task, not this fix) and spun out → see **T3-guard** below.
- **T3-guard (NEW, P2 CI-hardening — spun out of T3):** add the pitfall-#15 recurrence check (`var(--font-size-(?!xs|sm|base|lg|xl|2xl|3xl))` grep, or stylelint) to CI/lint. Both the UI/UX gate and the Tester ruled this out of the T3 fix as a separate Architect-authorized CI-scope task. Needs Architect sign-off → Coder + Reviewer + Tester.
- **T4 — DONE (`dd1b8ea`).** Architect → Coder → Reviewer PASS → Tester PASS. **Audit under-scoped it:** it named only `detect_new_model`/`detect_new_domain`, but the Architect traced the full dry-run path and ruled the COMPLETE fix — all FOUR active state-mutating detectors poison the baseline under `--dry-run` (`detect_divergence` and especially `detect_monthly_roundup`, whose write is unconditional-on-fire, were missed by the audit). Threaded keyword-only `dry_run` through all four, guarding each `_atomic_write_json` (`monthly_roundup` guard is `if not dry_run:`, NOT gated on triggers); `detect_drift` verified to early-return before state access. 16 regression tests with REAL detectors (the existing dry-run tests mocked the detectors — why the bug shipped); Tester ran a revert-and-confirm-fail cycle proving they catch it. Plan + verdicts: `docs/status/2026-06-08-T4-architect-plan.md`.
- **T5 — DONE (`94bb189`).** Architect → Coder → Reviewer PASS → Tester PASS. Verified the finding was REAL (not a type-shape false positive per runbook lesson #2): four sources (Pydantic `schemas.py:404–407`, `DATA_DICTIONARY:237–256`, `family.json`, the casts) all agree on the flat shapes — only `types.ts` was wrong. Corrected `DomainResultPublished` (mds_coordinates flat, similarity_matrix/similarity_ci 2-D arrays, sutrop_csi list, +cultural_centrality_scores), unified the duplicate inline `DomainExtended` into one exported type, fixed `EllipseParams` (added real `center`, removed phantom `ci_level`), removed all 12 `as unknown as` casts (tsc is now the re-drift gate), deleted phantom `similarity_matrix_array`. +21 shape-conformance tests (31→52). Plan + verdicts: `docs/status/2026-06-08-T5-architect-plan.md`. **Two P2 follow-ups surfaced:** T5-guard (CI grep vs inline `DomainExtended` re-drift) + MDSPlot inline-uncertainty-type unification.

**P2 — refactor backlog (schedule by adjacency to active work):**
- **T6** adopt the existing `cdb_publish/schemas/manifest.py` pydantic `Manifest` across the 5 cdb_social `domains` parsers (cli.py:137, triggers.py:248/350/426, routes.py:521).
- **T7** extract `displayProvider` (7 copies → the already-exported `familyUtils.ts:30`). UI/UX+Reviewer+Tester.
- **T8 — DONE (`c32c773`).** Architect → UI/UX PASS-WITH-NOTES (+ Mark override) → Coder (2 rounds) → Reviewer PASS → Tester PASS. **Scope grew from the audit's "6×" to 16 sites:** the helper was dup'd under THREE names (`shortName` ×6, `shortModelName` ×7, `shortModelDisplayName` ×1 in TermMap) with ~5 distinct behaviors — including Timeline's `grok-4`/`phi-4`→`4` collisions and TermMap's Title-Case branding. Collapsed all 16 to one canonical `displayModel(modelId)` in `lib/familyUtils.ts`. **Two design decisions went to Mark:** (1) strip rule — the UI/UX gate's "strip all prefixes" caused `grok-4`/`phi-4`→`4` collisions; Mark ruled strip org + `claude-` ONLY (keeps model identity, no collisions); (2) TermMap Title-Case → conform to canonical. Re-drift grep guard (all 3 fn names + inline idioms, across `components/**`) added + Tester-proven via revert-cycle. DESIGN_SYSTEM §18 (v0.14.0). Plan + verdicts: `docs/status/2026-06-08-T8-architect-plan.md`, `docs/status/2026-06-08-T8-displaymodel-uiux-verdict.md`. **NOTE:** T8 ⊃ T7 territory — `displayProvider` (T7) already canonical; T7 remains separate P2.
- **T9** compass label-placement algorithm copy-pasted 3× (MDSPlot, Focus1TermStability, Focus2FamilySimilarity) → `lib/labelPlacement.ts`.
- **T10** provider-color hex→token migration incomplete (Timeline.tsx, ProviderTree.tsx still raw hex).
- **T11** OCI threshold 3.0 SoT: dashboard re-hardcodes (analysis.ts:10) the manifest field nothing reads; rebaseline_corpus.py re-hardcodes. CDA SME low-touch confirm + Reviewer+Tester.
- **T12** `_atomic_write_json` reimplemented 3× in cdb_social → one helper.
- **T13** queue path logic reimplemented in routes.py → use queue.py helpers (fold into T2 Option A).
- **T14** publisher.py:148-164 unanchored numeric substring error-classification → anchored regex.
- **T15** heatmap threshold+seq-ramp dup (L1) + ClusterTree hardcoded cluster hex (L2) → tokens. Bundle.
- **T16** F4 fragile useEffect dep (inline `onLensToggle`) → useCallback. Not broken today.
- **T17** stale comment App.tsx:292 (footer-on-food) → fix with next App.tsx touch.

## Declines (don't re-raise)
- **F6** `simToColor` undefined on negative similarity — DECLINE: similarity is bounded ≥0 by the methodology; guard = dead code. (Better: type similarity as `0..1` under T5.)

## Routed to CDA SME (question, not a task)
- **F5** R10 semantics for degenerate uncertainty: when `semi_major<=0` the dot is drawn but the ellipse skipped. Strict R10 reading = suppress the dot too; permissive = honest zero-variance render. No domain ships this today (latent). SME verdict becomes binding precedent → either a code-guard task or a documented decline in DESIGN_SYSTEM.

## Runbook improvements the pilot surfaced (fold into the runbook)
1. **Convergent findings across lenses → auto-promote to P0** (V1 hit from 3 angles).
2. **Each Lens-A pass must spot-check ≥1 finding against real published data** before reporting (kills the F2/F3/F5/F6 type-shape false-positive class).
3. **Verify prior fixes claimed in commit messages by re-running the failure mode** — T1's prior fix read green (no crash) while still loading zero domains; a re-run check catches "green but empty."
