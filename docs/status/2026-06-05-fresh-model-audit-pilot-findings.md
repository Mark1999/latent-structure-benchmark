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
- **T3** fix `--font-size-md` → UI/UX picks token (likely base/lg) → Coder. Add audit grep `var(--font-size-(?!xs|sm|base|lg|xl|2xl|3xl)`.
- **T4** `detect --dry-run` mutates detector state (writes before the dry-run branch at cli.py:381) → poison-pill: a dry-run consumes baselines. Thread a `dry_run` flag through detectors. Reviewer+Tester.
- **T5** dashboard TS types contradict published shape (`types.ts:211/217/220` — mds_coordinates flat not nested; similarity_matrix is 2-D array not nested object; phantom `similarity_matrix_array`); consumers hide it with `as unknown as`. Reconcile types, remove casts. F2+F3 = ONE task. Reviewer+Tester.

**P2 — refactor backlog (schedule by adjacency to active work):**
- **T6** adopt the existing `cdb_publish/schemas/manifest.py` pydantic `Manifest` across the 5 cdb_social `domains` parsers (cli.py:137, triggers.py:248/350/426, routes.py:521).
- **T7** extract `displayProvider` (7 copies → the already-exported `familyUtils.ts:30`). UI/UX+Reviewer+Tester.
- **T8 (consider P1 — user-visible)** `shortName` dup'd 6× and ALREADY drifted → same model renders different labels per tab. Bundle with T7 or separate if a canonical-form design call is needed.
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
