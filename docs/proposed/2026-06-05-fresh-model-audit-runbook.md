# Fresh-Model Codebase Audit — RUNBOOK (proposed 2026-06-05)

**Status:** Proposal / standing process. Not yet adopted as policy — Mark decides whether to run it and on what cadence. This documents *how* to run a periodic whole-codebase review with a newer/updated Claude model when one ships, in a way that captures the value (fresh eyes catch accumulated drift) while containing the risk (context-blind false positives, churn, over-confident findings).

**Audience:** Mark + the LSB agent pipeline (Architect routes findings; Reviewer/Tester verify before anything ships).

---

## 0. The one-sentence version

When a materially better Claude model ships, run a **scoped, read-only, findings-only audit** of the existing code; route every finding through the **Architect as triage**; act only on findings that survive triage **and** normal Coder → Reviewer → (test/browser verify). The model's confidence is a starting point, never a verdict.

---

## 1. Why this exists (and why it is NOT "rewrite with the new model")

Two distinct things happen on a model upgrade:
1. **Automatic:** the pipeline agents (Architect, CDA SME, Reviewer, Coder, Tester) inherit the session model, so all *new* work already runs on the newer model the day you launch on it. Nothing to do.
2. **This runbook:** a *deliberate* fresh-eyes pass over the *accumulated existing code* — written and reviewed by older models — to surface issues, drift, and refactor candidates that incremental task-by-task work never looks across.

**The value** (real): newer models catch issue-classes older ones waved through (e.g. the Opus 4.8 honesty/self-checking gain ≈ 4× less likely to pass a flaw); a fresh pass is the best *generator* of refactor candidates (duplication, cross-cutting structural faults); it catches the silent-drift class — e.g. the 2026-06-04 manifest schema-drift bug where 5 consumers each parsed `manifest["domains"]` differently and rotted silently for 8 days because nothing looked *across* them.

**The risk** (must be contained):
- **Newer ≠ wiser on *our* code.** A fresh model has no memory of deliberate decisions and will confidently flag them as mistakes (e.g. `scripts/inject_centrality_ci.py` kept as a one-off on purpose; `main.py` ruff-excluded on purpose; human baselines removed by the 2026-05-07 amendment, not "missing").
- **Churn.** ~half of fresh-review findings are aesthetic ("I'd write it differently"), which LSB's no-scope-creep rule exists to resist.
- **Over-confidence.** Documented in-session (2026-05/06): the latest model produced multiple confident-but-wrong self-assessments (the "zoom is fixed" claims disproved by browser verification; a silently-failed edit; an unapproved dep pushed before review). **Findings are hypotheses, not conclusions.**

---

## 2. When to trigger (cadence)

Run on the **earlier** of:
- A **major Claude model release** that Anthropic flags as a step-change in coding/reasoning/honesty (not a point bump).
- **Quarterly**, if no major release intervened.
- **Ad hoc** when Mark suspects accumulated rot (e.g. after a silent-failure incident like the social cron).

Do NOT run it every session or continuously — it is a periodic audit, not a standing background job. (Contrast: the QA_Runner watches *production runs*; this watches *the codebase*.)

---

## 3. Scope — three bounded lenses (pick per run; don't boil the ocean)

Run one or more of these as **separate** audits. Each is read-only and produces a findings list only.

**Lens A — Correctness & security sweep** *(highest confidence, lowest churn — default first choice)*
- Tooling: the `/code-review` skill (and `/code-review ultra` for a deep multi-agent cloud pass on a branch), plus `/security-review` for the security-specific pass.
- Targets: real bugs, edge cases, error-handling gaps, injection/secret-handling, async/race issues, silent-failure patterns (swallowed exceptions, the "exit 0 on error" class).

**Lens B — Cross-cutting structural audit** *(the manifest-drift lesson, generalized)*
- Targets: the "N consumers each parse the same thing N ways" class; duplicated logic that drifts (e.g. the compass label-placement algorithm copy-pasted into 4 components; provider-color maps once duplicated across ~7 files); a single conceptual change requiring edits in many places; comprehension cost ("had to read 4 files for a 1-line change").
- Output: refactor candidates with the duplication/coupling named — feeds the Architect's refactor backlog (see the refactoring guidance discussed 2026-06-05).

**Lens C — Methodology re-examination** *(GATED — handle with care)*
- A newer model "thinking the bootstrap/measure should be different" is a **methodology claim**, not a code review. It does NOT flow like A/B.
- Any Lens-C finding goes to the **CDA SME** as a question, not to the Coder as a task. Changing published methodology can destabilize published numbers (Smith's S, OCI, Romney eigenratio, CIs) and the open-data reproducibility guarantee. Treat with the same gravity as the Remedy B / re-baseline work.

---

## 4. The procedure (read-only audit → triage → verified action)

**Step 1 — Brief the auditor with context (prevents re-litigating settled decisions).**
Point the reviewing model at, at minimum: `CLAUDE.md` (esp. §1.5 framing, §7 forbidden vocab, §9 pitfalls list — the 17 known traps), `ARCHITECTURE.md`, and the relevant `docs/status/` verdict trail for the area. The pitfalls list is the single highest-value input — it tells the auditor which "smells" are deliberate.

**Step 2 — Run the audit, read-only, findings-only.**
The reviewing model/skill produces a **prioritized findings list**: each finding = `file:line` + severity (blocker / should-fix / nit) + one-line rationale + which lens. It does **NOT** apply changes. (`/code-review` without `--fix` is exactly this; `/code-review ultra` for the heavy pass.) Save the raw findings to `docs/status/YYYY-MM-DD-fresh-model-audit-<lens>.md`.

**Step 3 — Architect triage (the load-bearing filter).**
Hand the raw findings to the **Architect** (which holds project context via the docs). The Architect classifies each finding:
- **Real + actionable** → becomes a scoped task (one commit each, normal gates).
- **Context-blind false positive** → rejected with a one-line reason (e.g. "deliberate per 2026-05-07 amendment"). Record the rejection so the *next* audit doesn't re-raise it.
- **Aesthetic / churn** → declined per no-scope-creep.
- **Methodology (Lens C)** → routed to CDA SME, not implemented.
This triage is what converts a noisy fresh-review into a credible backlog. **Do not act on raw findings directly.**

**Step 4 — Verify before acting (the in-session lesson, codified).**
Every accepted finding goes through the normal pipeline: Coder → Reviewer → Tester, with **mechanical verification** (tests/CI) or **browser verification** (for dashboard) — never on the reviewing model's authority alone. A "fix" that claims success is browser/CI-confirmed before merge. (This is precisely what caught the false "zoom fixed" claims and the unapproved-dep push this session.)

**Step 5 — Close the loop.**
Update the audit findings doc with disposition per finding (task-created / rejected-with-reason / SME-routed). Append a short summary line to the NEXT-STEPS checkpoint.

---

## 5. Anti-patterns (do NOT)

- ❌ Let the reviewing model **apply changes directly** from a whole-codebase pass (no triage, no per-finding gate).
- ❌ Treat findings as a **to-do list** instead of a triage input.
- ❌ Run it **without the context brief** (Step 1) — guarantees false positives on deliberate decisions.
- ❌ Implement **Lens-C methodology** findings without the CDA SME.
- ❌ **Bundle** audit fixes with unrelated work, or chain many findings into one mega-commit (one task = one commit holds).
- ❌ Run it **mid-flight** on other in-progress work.

---

## 6. The standing reminder (top of every audit)

> A newer model's review is a **hypothesis generator, not an oracle.** It is more likely to be right than the previous model — and still routinely confident and wrong. Every finding is triaged for project context and verified mechanically before it ships. The 2026-05/06 sessions are the proof: the latest model self-reported "fixed" three times on a zoom bug that browser verification showed was still broken. Confidence is the start of the check, not the end of it.

---

## 7. Pilot option

Before adopting on a cadence, run **one Lens-A `/code-review` pass now** on the current codebase as a pilot — see what the current model surfaces on existing code, run it through Architect triage, and judge the signal-to-noise before committing to the process. Low cost, read-only, and it calibrates expectations.
