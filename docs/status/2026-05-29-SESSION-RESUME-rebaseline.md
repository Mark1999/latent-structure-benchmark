# SESSION RESUME RUNBOOK — re-baseline launch (2026-05-29)

**Why this file exists:** the live session was relaunched inside a zellij session (named `lsb`) on the VPS so the ~10-hour corpus re-baseline can run while Mark travels. If `claude --continue` lost context, READ THIS to pick up exactly where we left off. Mark is a project manager, not an engineer — keep him informed in plain language.

## One-line state
The original centrality-CI register-error remediation (Remedy B) is **DONE and on origin/master, deploying**. We are now mid-execution on the follow-on reproducibility/cleanup bundle. The re-baseline script is built but not yet committed or launched.

## Exact git state at handoff
- Local `master` = `b143a25`. **4 commits ahead of `origin/master` (`7fa8ad9`), UNPUSHED:**
  - `b143a25` feat(core): pin numpy==2.4.4 / scipy==1.17.1
  - `f56b739` chore(memory): SME re-baseline precedent
  - `6f5f566` docs(status): SME re-baseline verdict
  - `8ff8f14` docs(status): Architect dep-pin sign-off
- **Untracked, NOT committed:** `scripts/rebaseline_corpus.py` (633 lines, valid, has the SME threshold guard) and `out/rebaseline/` (smoke-test leftovers: rebaseline.log + a stub baseline_manifest.json — DELETE these before the real run).

## RESUME ACTIONS (in order)
1. **Push the 4 unpushed commits** to origin/master (fast-forward; CI green).
2. **Reviewer gate on `scripts/rebaseline_corpus.py`** (Remedy-B-bundle T3). Confirm: staging-only output (no live-file overwrite, no auto-commit), the 6-threshold guard, manifest fields, no LLM imports (R11), no `data/raw/*.jsonl` edits. Then **commit it** (`feat(analyze): re-baseline corpus script with SME threshold guard — T3`). Delete the smoke leftovers in `out/rebaseline/` first (or let the script overwrite).
3. **Launch the regen.** We are inside zellij now, so claude stays alive across Mark's disconnect — use the harness background mechanism (`run_in_background: true`) so completion re-invokes the agent. Read the script for its exact entrypoint/flags; intended invocation ≈ `uv run python scripts/rebaseline_corpus.py` (all domains: family → holidays → food, B=500). Confirm to Mark "the regen is running" before he detaches.
4. **On completion** (hours later): read `out/rebaseline/baseline_manifest.json`, the `numeric-deltas-*.md`, and any `THRESHOLD-CROSSING-*.md`.
   - If any domain HALTED on a threshold crossing (food is the load-bearing risk: eigenratio 6.586 vs 5.0 boundary; one OCI 3.74 vs 3.0) → **do NOT publish that domain.** Escalate to the CDA SME for a lede-class ruling. This is a separate CDA-significant event, not something to push through.
   - If all clean → review deltas (expected: rounding-level, 3rd–4th decimal), then promote staging → live (`data/results/**` + `apps/dashboard/public/data/**`), Reviewer gate, commit, push. Cloudflare redeploys.
5. **Before/with promotion**, land the SME-required audience surfaces (binding, verdict N1–N3): methodology-page **data-provenance paragraph** (date, pinned versions, "prior numerics not recoverable; valid under their respective toolchains, the defect was unpinning", no forbidden vocab, no wrong/correct framing) + **link to baseline_manifest.json**. Then the **footer version note (T5)** "Calculated with NumPy 2.4.4 / SciPy 1.17.1" on every screen, sourced from the manifest (Mark chose mechanism A). T5 is UI/UX-gated; verify in a real browser via Playwright.
6. **Remaining bundle tasks** (independent of the regen): T6 methodology link from the centrality block (= CDA SME note M3; UI/UX, reuse the Phase 6 T14 link pattern), T7 vitest seed (deps `@testing-library/react` + `@testing-library/jest-dom` already approved; CentralityChart/Table render-with/without-CI + read-as-table toggle tests).

## Binding references
- CDA SME re-baseline verdict (the guard + 3 surfaces): `docs/status/2026-05-29-rebaseline-cda-sme-verdict.md`
- Dep-pin sign-off: `docs/status/2026-05-29-numpy-scipy-pin-architect-signoff.md`
- Remedy B (the completed remediation, context): `docs/status/2026-05-28-remedy-b-*`

## Decisions already made (don't re-litigate)
- Pin to current 2.4.4/1.17.1, re-baseline forward (done).
- Footer version strings from the published manifest field (mechanism A).
- Test deps approved.
- Reconciliation of master was a force-push of the remediated line; backup at `origin/backup/master-pre-remediation-2026-05-29` and on `origin/feature/visualization-fixes`.

## Don't
- Don't auto-publish the re-baseline; staging until reviewed.
- Don't run parallel file-writing agents in the same tree (caused a bundled-commit race earlier; sequence or use worktree isolation).
- Don't use Mark's "Claude in Chrome" extension — it's not reachable from this CLI; use the Playwright MCP for live UI checks.
