# CLAUDE.md — LSB Team Constitution

**Document name:** `CLAUDE.md`
**Version:** v1.0 (first canonical version, aligned with `ARCHITECTURE.md` v0.7 and `DESIGN_SYSTEM.md` v0.2)
**Status:** Binding for all Claude Code agents working on LSB
**Audience:** Architect, CDA SME, UI/UX, Coder, Reviewer, Tester agents — and Mark
**Companion docs:** `ARCHITECTURE.md` (binding for data, schema, agent pipeline, phase plan), `DESIGN_SYSTEM.md` (binding for all frontend work), `PHASE_0_TASKS.md`, `SECURITY_AND_HARDENING.md`, `HOSTING_AND_DEV_OPS.md`, `PHASE_4C_CANDIDATE_SOURCES.md`, `docs/DATA_DICTIONARY.md`, `docs/grounding_submission_template.md`

> **Read this file at the start of every task.** It is short on purpose. The detailed specs live in the companion docs above; this file is the routing layer.

---

## 0. What this file is

`CLAUDE.md` is the LSB team constitution. It tells Claude Code agents how to work on this project — the pipeline they belong to, the rules they're bound by, the docs they have to read, the words they're not allowed to use, and what "done" looks like. It does **not** duplicate the architecture, the design system, or the data dictionary; those are referenced and trusted. When this file disagrees with `ARCHITECTURE.md` or `DESIGN_SYSTEM.md`, the more specific document wins and this file should be updated to match.

This file is read at the start of every task. Keep it short. Resist the urge to inline content from the companion docs; cross-reference instead.

---

## 1. What LSB is

The Latent Structure Benchmark (LSB) applies Cultural Domain Analysis (CDA) elicitation protocols to large language models as if the models were informants. It surfaces the **corpus lens** — the categorical structure of a model's training corpus, refracted through training and alignment. The website at [`cogstructurelab.com`](https://cogstructurelab.com) is the primary deliverable; the benchmark, the open data bundle, and the social pipeline all exist to make the website credible, useful, and discoverable.

**LSB is a website that uses research methods, not a research project that has a website.** This framing matters because it determines tradeoffs across the whole project. Visual polish, copy quality, and load performance on the dashboard are first-class concerns. Methodological rigor is in service of the dashboard, not the other way around. The bar for the methodology page is "credible to a skeptical reader," not "publishable in *Nature*."

**LSB does *not* measure cultural worldview, belief, or cognition.** Models do not have lived experience. They synthesize statistical patterns from text corpora. The §1.5 framing in `ARCHITECTURE.md` is binding on every piece of generated text in this project — every lede, every social post, every dashboard string, every README sentence, every commit message, every PR description. The forbidden vocabulary list in §7 of this file is enforced by both the CDA SME agent (during plan review) and the Reviewer agent (during PR review). Non-negotiable.

---

## 2. Reading requirements

The source-of-truth hierarchy. Read these in this order, only as needed for the task at hand. If a task touches a particular concern, the corresponding doc is mandatory before you start writing code or generating text.

| # | Doc | When required |
|---|---|---|
| 1 | [`ARCHITECTURE.md`](ARCHITECTURE.md) | **Always.** Before any task. **§1.5 is binding on all generated text.** |
| 2 | [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md) | **Before any frontend task.** Required for any work touching `apps/dashboard/`, any new component, any visual change to an existing component, any new color or font or spacing decision, any change to the dashboard's article-with-explorer page model. |
| 3 | [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) | Before touching `cdb_core/schemas.py` (especially `InformantRecord` or `GroundingRef`) or `scripts/build_db.py`. |
| 4 | [`SECURITY_AND_HARDENING.md`](SECURITY_AND_HARDENING.md) | Before touching `apps/dashboard/`, `packages/cdb_collect/`, or any CI/CD configuration. The Reviewer rules table in §9 is enforced on every PR. |
| 5 | [`HOSTING_AND_DEV_OPS.md`](HOSTING_AND_DEV_OPS.md) | Before any deployment-related task or any task touching `.github/workflows/`, Cloudflare Pages config, or environment variables. |
| 6 | [`PHASE_0_TASKS.md`](PHASE_0_TASKS.md) | The canonical decomposition for the Coder's first session. Read before any P0 task. |
| 7 | [`PHASE_4C_CANDIDATE_SOURCES.md`](PHASE_4C_CANDIDATE_SOURCES.md) | Before any task touching `data/grounding/`, `packages/cdb_analyze/grounding.py`, or the Phase 4c family-domain grounding workflow. |
| 8 | [`docs/grounding_submission_template.md`](docs/grounding_submission_template.md) | Before any work on the researcher submission workflow or before reviewing a researcher submission PR. |

**Reading is mandatory, not advisory.** A Coder who skips `DATA_DICTIONARY.md` and proceeds to "improve" the `GroundingRef` schema is going to break the open data contract. A Coder who skips `DESIGN_SYSTEM.md` and invents a chart color is going to get rejected by the UI/UX agent. The Reviewer agent rejects PRs that show evidence of skipped reading (e.g., schema changes without matching dictionary updates, new components with off-palette colors, generated text with forbidden vocabulary).

---

## 3. The agent pipeline

```
Architect → CDA SME → ┬─ (frontend tasks) → UI/UX agent → Coder → Reviewer → Tester
                      └─ (other tasks)    ─────────────→  Coder → Reviewer → Tester
```

**The CDA SME and the UI/UX agent are gates, not advisors.** A FAIL verdict from either one stops the plan and bounces it back to the Architect for rework. PASS-WITH-NOTES is acceptable but the notes are mandatory — the next agent in the pipeline must apply them. PASS is the only verdict that allows the plan through unmodified.

**The QA_Runner (`scripts/qa_check.py`) is *outside* this pipeline.** It watches collection runs in production and posts directly to `#lsb-alerts`, bypassing the agent team entirely. See `ARCHITECTURE.md` §1 commitment 8 and §4.1.6.

**Frontend vs. non-frontend.** A task is "frontend" if it touches `apps/dashboard/`, `DESIGN_SYSTEM.md`, or any visual artifact (component, page, chart, image, generated copy that will appear on the dashboard). Frontend tasks pass through the UI/UX agent. Everything else (collection, analysis, schemas, scripts, CI, docs not bound by the design system) skips the UI/UX gate.

---

## 4. Agent responsibilities

| Agent | Model | Role | Posts to |
|---|---|---|---|
| **Architect** | Opus | Owns `ARCHITECTURE.md`. Decomposes features into Coder-sized tasks. Hands every plan to the CDA SME first; for frontend tasks, the post-SME plan additionally passes through the UI/UX agent. **Never writes code.** | — |
| **CDA SME** | Opus | Methodological gatekeeper. Reviews every plan on four axes: protocol validity, analytical validity, claims validity, audience translation. Verdict: PASS / PASS-WITH-NOTES / FAIL with rationale and four-axis scorecard. Also reviews researcher grounding submission PRs. | `#lsb-cda-sme` |
| **UI/UX agent** | Sonnet | Design conscience of the frontend. **Frontend tasks only.** Reviews every frontend plan on four questions: OWID design fidelity, the 30-second journalist test, the researcher reproduce-and-cite test, WCAG AA accessibility. Owns `DESIGN_SYSTEM.md` and updates it before passing any plan through that requires a visual decision the design system does not yet cover. | `#lsb-ui-ux` |
| **Coder** | Sonnet | Implements one package or one feature at a time. Receives only plans with the necessary gate verdicts. **Never invents visual decisions.** Routes visual questions back to the UI/UX agent and pauses until the design system is updated. | — |
| **Reviewer** | Sonnet | Enforces the rules in §6 and the Reviewer rules table in `SECURITY_AND_HARDENING.md` §9. Rejects PRs that violate any rule. Cannot be overridden by the Coder or by the Architect — only Mark can override a Reviewer rejection, and only with a documented architectural decision. | — |
| **Tester** | Sonnet | Every package ships with fixtures from `tests/fixtures/`. **No real API calls in tests.** pytest for Python, vitest for the dashboard. | — |

For the full responsibility specifications and verdict formats, see `ARCHITECTURE.md` §5.1.

---

## 5. Slack channels

Three operational channels. Each has a different audience, latency expectation, and routing rule.

| Channel | Posted by | Latency | Routing rule |
|---|---|---|---|
| `#lsb-alerts` | `scripts/qa_check.py` (QA_Runner); `weekly-cost-alert.yml` (GitHub Actions) | Minutes — operational firefighting | **Bypasses the agent team entirely.** Mark monitors in real time. |
| `#lsb-cda-sme` | CDA SME agent | Hours to a day — development gating | Verdicts (PASS / PASS-WITH-NOTES / FAIL) with four-axis scorecard. Researcher grounding PR reviews also post here. |
| `#lsb-ui-ux` | UI/UX agent | Hours to a day — frontend gating | Verdicts with four-question scorecard. `DESIGN_SYSTEM.md` updates also post here. Frontend plans only. |

**Webhook env vars:** `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`. Stored in `.env` (never committed) and in 1Password. See `HOSTING_AND_DEV_OPS.md` §6 and `SECURITY_AND_HARDENING.md` §8 for the secret-handling specifics.

---

## 6. The binding rules

These rules apply to every task. Numbering matches `ARCHITECTURE.md` §5.2. The Reviewer agent rejects PRs that violate any of them.

1. **Read `ARCHITECTURE.md` before starting any task.** §1.5 is binding on all generated text.
2. **Read `SECURITY_AND_HARDENING.md`** before touching the dashboard, the collection layer, or CI/CD.
3. **Read `HOSTING_AND_DEV_OPS.md`** before any deployment work.
4. **Read `PHASE_4C_CANDIDATE_SOURCES.md`** before any grounding work.
5. **Read `PHASE_0_TASKS.md`** for the Phase 0 decomposition.
6. **Read `docs/DATA_DICTIONARY.md`** before touching `cdb_core/schemas.py` (especially `InformantRecord` or `GroundingRef`) or `scripts/build_db.py`.
7. **Never edit `cdb_core/schemas.py` without Architect sign-off.** Schema changes ripple everywhere. Changes to `InformantRecord` or `GroundingRef` require a matching `DATA_DICTIONARY.md` update in the same PR — the Reviewer agent enforces this.
8. **Prompt templates are versioned.** Never edit a published prompt template in place; copy it to a new version directory under `packages/cdb_collect/prompts/v{N}/`.
9. **No API keys in the repo.** Use `.env` + `python-dotenv`; `.env.example` is tracked, `.env` is ignored. The `gitleaks` pre-commit hook is the first line of defense; GitHub secret scanning is the second.
10. **No real model calls in tests.** Use fixtures from `tests/fixtures/`.
11. **No point estimates without uncertainty in any visualization.** See `ARCHITECTURE.md` §4.2.6 and §4.5. The Reviewer agent rejects any new viz that cannot express uncertainty.
12. **No LLM calls in `cdb_analyze`.** LLMs are informants in `cdb_collect`, not analysts in `cdb_analyze`. The Reviewer's static import check on `cdb_analyze` enforces this — any PR that imports `anthropic`, `openai`, `google.generativeai`, `huggingface_hub.InferenceClient`, or any other LLM client library inside `packages/cdb_analyze/` is rejected automatically. The single exception is the lede generator, which lives in `cdb_publish` (not `cdb_analyze`) precisely to keep this boundary visible. See `ARCHITECTURE.md` §4.2 binding constraint and §1 commitment 6.
13. **Architect plans must be CDA-SME-approved before reaching the Coder.** For frontend tasks, plans must additionally carry a UI/UX agent PASS or PASS-WITH-NOTES verdict before reaching the Coder.
14. **Read `DESIGN_SYSTEM.md` before any frontend task.** The UI/UX agent owns this document; the Coder may not invent visual decisions outside of it. If a frontend task needs a visual decision the design system does not yet cover, the Coder pauses, surfaces the question to the UI/UX agent, and only resumes once the design system has been updated.
15. **Researcher grounding submission PRs** follow the workflow in `ARCHITECTURE.md` §4.2.5. CI validates the format (schema check, format check, item-intersection report, gitleaks PII scan). The CDA SME agent reviews the methodology. Mark merges. The PR template lives at `.github/PULL_REQUEST_TEMPLATE/grounding_submission.md`.

---

## 7. Forbidden vocabulary

The §1.5.4 language guardrails table from `ARCHITECTURE.md` is binding on every piece of generated text — ledes, social posts, dashboard copy, READMEs, commit messages, PR descriptions, agent verdicts. The Reviewer agent rejects any text containing the left-column phrases.

| Don't say | Say instead |
|---|---|
| "Model X believes..." | "Model X's output treats..." |
| "Model X thinks of family as..." | "Model X categorizes family terms as..." |
| "How models see the world" | "How models organize domain vocabulary" |
| "Model X's worldview" | "Model X's categorical structure" / "Model X's corpus lens" |
| "Cultural bias" (standalone) | "Categorical divergence from [baseline]" |
| "What the model understands" | "What the model's outputs pattern as" |

**Generic terms also forbidden in any model-facing context:** `worldview`, `believes`, `thinks` (when applied to models). The plain-language term for what LSB measures is **corpus lens** — see `ARCHITECTURE.md` §1.5.1.

The forbidden vocabulary applies to text *about* the models that LSB measures. It does not apply to general-purpose English usage in unrelated contexts (a code comment that says "I think this loop terminates" is fine). The Reviewer agent uses judgment; the rule is about how LSB talks about its subjects, not about whether the word "think" can ever appear in the codebase.

---

## 8. How we work

Cultural defaults for all agents and humans on this project. Most of these are common sense; they're written down because common sense is uncommon when six different agents are reading the same task description.

**One commit per task. Do not bundle.** If you finish a task and notice an obviously useful change you could make at the same time, the answer is no — commit the current task, note the observation in the commit body or a follow-up task, and let the Architect decide whether to schedule it. Bundling makes review harder, makes rollback harder (revert is per-commit), and makes the agent pipeline's gating verdicts ambiguous.

Default workflow for this repo is **direct commits to `master`**, not branch+PR. LSB is a single-operator project; the PR ceremony (branch, push, browser handoff to open a PR without `gh` CLI, CI re-running identical locally-passed tests, manual merge) adds friction without adding quality. The agent pipeline (Architect → CDA SME → Coder → Reviewer → Tester) is what produces quality, not the GitHub UI. Each gate verdict is saved to `docs/status/YYYY-MM-DD-{task-id}-verdicts.md` (or appended to an existing F{N}-verdicts file) so the audit trail survives outside of PR comments. Commit body should reference the verdict file.

**When to branch+PR instead:**
- Experimental or multi-day work you want to throw away cleanly if it doesn't pan out
- Schema changes to `cdb_core/schemas.py` that might need clean rollback (the `DATA_DICTIONARY.md` co-update makes diffs noisy; a branch isolates them)
- Dependabot-style dependency bumps where CI on a throwaway branch is the point
- Any change where Mark explicitly says "branch this one"

**Tests still run locally before every commit** (see below). Direct-to-master does not relax the test gate; it removes the CI re-run of already-passing local tests.

**No surprise scope creep.** If a task's acceptance criteria don't cover something you think needs doing, stop and surface it to the Architect rather than improvising. The Architect is the only role authorized to expand a task's scope; the Coder is not, the Reviewer is not, and the Tester is not.

**Ask before assuming.** If the spec is ambiguous, the right move is to ask Mark or to ask the Architect, not to pick the interpretation that seems most convenient. Specifically: when an architectural decision is implied but not stated, treat it as not stated and surface it. Improvising on ambiguous architectural decisions is how projects accumulate technical debt that nobody can later trace back to a specific commit.

**Commit messages follow Conventional Commits.** `feat(scope):`, `fix(scope):`, `chore(scope):`, `docs(scope):`, `test(scope):`, `refactor(scope):`, `ci(scope):`, `perf(scope):`. The scope is the affected package (`core`, `collect`, `analyze`, `publish`, `social`, `dashboard`, `scripts`, `docs`, `ci`). The first line is under 72 characters. Longer descriptions go in the commit body. Reference the relevant `ARCHITECTURE.md` section in the body if the change is architecturally significant.

**Commit (or PR) descriptions reference the task ID and the gate verdicts.** Phase 0 commits reference the P0-T{N} ID from `PHASE_0_TASKS.md`. Frontend changes link to the UI/UX agent verdict file in `docs/status/`. CDA-significant changes link to the CDA SME verdict file in `docs/status/`. The Reviewer rejects commits that don't reference the necessary gate verdicts. (When branch+PR is used under the exceptions above, the same rule applies to the PR description.)

**Tests run locally before every commit.** `uv run pytest && uv run ruff check . && uv run mypy packages/` is the minimum. For frontend changes, `npm run build && npm run test && npm run lint` from `apps/dashboard/`. Direct-to-master makes this non-negotiable: CI is not a safety net here, it's a redundant confirmation.

**No "I'll fix the lint after."** Lint is part of done.

**Stop conditions.** Pause and surface the question to Mark or to the Architect when:
- The spec is ambiguous in a way that would commit the project to an unstated architectural decision
- A task requires changes outside its declared scope
- A test fails in a way that suggests the underlying behavior is wrong (not just the test)
- A schema change would break the data dictionary or the open data bundle reproducibility guarantee
- A frontend change would require a visual decision not in `DESIGN_SYSTEM.md`
- A security or privacy concern arises that wasn't anticipated by `SECURITY_AND_HARDENING.md`

In all of those cases, the right action is to stop, document the situation, and ask. The wrong action is to push through with a guess.

---

## 9. Common pitfalls (LSB-specific)

These are mistakes that have happened on similar projects, or that the LSB design specifically guards against. Each one is easy to make if you're moving fast and skipping the doc reading.

1. **Conflating `model_id` with `model_version_returned`.** `model_id` is the user-supplied alias (e.g., `claude-opus-4-6`). `model_version_returned` is the exact version string the API returned in the response. They look similar but they are not the same — providers silently roll snapshots under moving aliases. The longitudinal view (`DriftTracker.tsx`) joins on `model_version_returned`, not `model_id`. Get this wrong and the entire temporal analysis is meaningless. See `ARCHITECTURE.md` §3.2 InformantRecord and `docs/DATA_DICTIONARY.md` §1.1.

2. **Putting an LLM call in `cdb_analyze`.** It is *very* tempting to "just have Claude summarize this matrix for the lede." Don't. The lede generator lives in `cdb_publish`, not `cdb_analyze`, and it receives only already-computed numeric findings. The §1 commitment 6 / §4.2 binding constraint exists because an analysis pipeline that depends on an opaque model to interpret another opaque model is not falsifiable. The Reviewer's static import check rejects this automatically — even helper functions and utility wrappers are caught.

3. **Treating `groundings` as a singleton.** The v0.7 schema is `DomainResult.groundings: list[GroundingRef]`, not `DomainResult.grounding: GroundingRef | None`. A domain can have zero, one, or many baselines. Code that does `result.grounding.mds_coordinate` will fail; code that does `result.groundings[0].mds_coordinate` will fail when `groundings` is empty. Always handle the list semantics explicitly, and treat the empty case as a normal first-class state per `ARCHITECTURE.md` §1.5.5.

4. **Writing dashboard copy that says "no human baseline available yet."** Ungrounded is not a placeholder waiting for data. It is a complete first-class state. The State 0 copy in `DESIGN_SYSTEM.md` §4.1 says "This domain is studied model-to-model. Researcher contributions welcome." The Reviewer rejects copy that frames absence as a defect.

5. **Forgetting to update `DATA_DICTIONARY.md` when changing a schema.** Reviewer rule R7 (in `SECURITY_AND_HARDENING.md` §9) requires that any change to `InformantRecord` or `GroundingRef` carry a matching update to the data dictionary in the same PR. There is no "I'll update the docs in a follow-up PR" — the open data contract depends on the dictionary being in lockstep with the schemas.

6. **Inventing visual decisions instead of routing to the UI/UX agent.** If the design system doesn't cover a question, the Coder does not pick a color, font, spacing, or interaction pattern. The Coder pauses, surfaces the question to the UI/UX agent, and waits for the design system to be updated. This is annoying for tight loops; it is also how the dashboard avoids the "looks like a research demo" outcome that would sink the project's credibility.

7. **Using "worldview," "believes," or "thinks" in any generated text about models.** The §1.5.4 forbidden vocabulary applies to ledes, social posts, dashboard copy, README content, commit messages, PR descriptions, and agent verdicts. The Reviewer rejects on detection. There is no exception for "but it's just a comment in the code" — the rule is about how LSB talks about its subjects, and it applies wherever LSB talks about its subjects.

8. **Building a dashboard component that displays a point estimate without an uncertainty ellipse.** Reviewer rule (in `ARCHITECTURE.md` §4.5) is that no visualization may display a point estimate without its associated uncertainty. Bare points on an MDS plot don't ship. Heatmap cells without CIs don't ship. The bootstrap module exists for a reason.

9. **Calling a real API in a test.** Tests use fixtures from `tests/fixtures/`. The fixture convention is documented in `tests/fixtures/README.md`. There is no exception for "but I just need to verify the adapter works once" — adapter integration tests run against fixtures, not against real providers. Real-API verification happens during structured collection campaigns on the project VPS (formerly `lsb-agent-01`, decommissioned 2026-04-19; new VPS TBD — see `HOSTING_AND_DEV_OPS.md` top-of-doc banner), not in CI.

10. **Editing existing lines in `data/raw/informants.jsonl`.** The file is append-only by convention and by tooling. The CI append-only check rejects any PR that modifies pre-existing lines. If you find yourself wanting to "fix" a record, the answer is no — the bad record stays in place (with `qa_passed=False` and `qa_notes` documenting the failure), and the audit trail remains intact.

11. **Committing a webhook URL.** Slack webhook URLs are credentials. Anyone with the URL can post to the channel. They live in `.env` and in 1Password, never in the repo. `gitleaks` has a custom rule for them.

12. **Assuming `data/grounding/{domain}/` is a single directory with one baseline.** The v0.7 schema makes it `data/grounding/{domain}/{baseline_id}/`. A single-baseline domain has one subdirectory; a multi-baseline domain has many. Code that hard-codes a path like `data/grounding/family/cooccurrence.csv` is broken — it should be `data/grounding/family/{baseline_id}/cooccurrence.csv` and iterate over all baselines in the parent directory.

---

## 10. When you're stuck

Escalation order, fastest to slowest:

1. **Re-read the relevant companion doc.** Most stuck moments are caused by a doc reference being skipped. Going back to `ARCHITECTURE.md`, `DESIGN_SYSTEM.md`, or `DATA_DICTIONARY.md` resolves more than half of "I'm stuck" cases.
2. **Surface the question in the relevant Slack channel.** Methodological questions go to `#lsb-cda-sme`. Visual questions go to `#lsb-ui-ux`. Operational questions go to `#lsb-alerts` only if they're time-sensitive; otherwise, ask Mark directly.
3. **Pause the task and write a question for Mark.** A clearly written question that names the ambiguity is more useful than a plausible guess. Mark would rather wait an hour and answer a good question than spend a day rolling back a bad guess.
4. **Never improvise architectural decisions.** When in doubt, treat the ambiguity as a stop condition. The cost of pausing is hours; the cost of an undocumented architectural decision is months.

---

## 11. What "done" means

A task is done when **all of the following are true**:

- [ ] All acceptance criteria in the task spec are met
- [ ] Tests pass locally (`ruff`, `mypy`, `pytest`, the no-LLM-imports static check, `gitleaks`). If branch+PR is used under §8 exceptions, CI is also green.
- [ ] For frontend tasks: `npm run build && npm run test && npm run lint` passes locally
- [ ] The Reviewer agent has issued a PASS or PASS-WITH-NOTES verdict, with all notes addressed; verdict saved to `docs/status/`
- [ ] For frontend tasks: the UI/UX agent has issued a PASS or PASS-WITH-NOTES verdict, with all notes addressed; verdict saved to `docs/status/`
- [ ] For methodologically significant tasks: the CDA SME agent has issued a PASS or PASS-WITH-NOTES verdict, with all notes addressed; verdict saved to `docs/status/`
- [ ] The commit message follows Conventional Commits (§8) and references the task ID + verdict file paths
- [ ] No forbidden vocabulary in any committed text (the Reviewer's spot check passes)
- [ ] No new dependency was added without Architect sign-off
- [ ] No schema change to `cdb_core/schemas.py` without a matching `DATA_DICTIONARY.md` update
- [ ] The task is one commit (not bundled with other work). If the §8 exceptions triggered a branch+PR, the PR contains exactly one task.

A task is **not** done if any of the above is missing, even if the code "works." The pipeline gates exist to keep the project's compounding decisions consistent over time; bypassing a gate to ship faster is borrowing against future maintainability.

---

*End of `CLAUDE.md` v1.0. This file is binding for all Claude Code agents working on LSB. Read it at the start of every task. When this file disagrees with `ARCHITECTURE.md` or `DESIGN_SYSTEM.md`, the more specific document wins and this file should be updated to match.*