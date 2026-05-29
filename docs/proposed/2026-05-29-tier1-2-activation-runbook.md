# Tier 1–2 capability upgrade — ACTIVATION RUNBOOK (drafted 2026-05-29, INACTIVE)

**Status:** Artifacts are drafted and committed but **NOT active**. Nothing here changes
runtime behavior until the steps in §"Activation" are done. Drafted while Mark traveled
and the re-baseline regen ran; per Mark's instruction "draft without activating."

**Before activating anything:** route through the **Reviewer** (these are guardrails that
gate the whole team) and get Mark's OK. Each hook must be **dry-run tested** with sample
payloads first — a misfiring `PreToolUse` hook can block legitimate work.

---

## Tier 1 — guardrail hooks (drafted, inert)

Scripts live in `.claude/hooks/` and are inert until referenced in `settings.json`.

| Script | Fires on | Action | Mirrors |
|---|---|---|---|
| `check_forbidden_vocab.py` | Write/Edit/MultiEdit | **block (exit 2)** on §7 forbidden vocab | NET-NEW (no CI grep today) |
| `check_informants_append_only.py` | Write/Edit/MultiEdit to `data/raw/informants.jsonl` | **block (exit 2)** | CLAUDE.md §9 pitfall 10 / R-append-only |
| `check_spend_gate.py` | Write/Edit/MultiEdit | **block (exit 2)** on spend-gate tokens (honors `noqa: spend-gate-check`) | CI `no-spend-gate-check` |
| `check_schema_edit.py` | Write/Edit/MultiEdit to `cdb_core/schemas.py` | **soft "ask"** (confirm), reminder only | CLAUDE.md rule 6 / R7 |

Design notes:
- All hooks **fail-open** (exit 0) if stdin can't be parsed — they never brick the session.
- `check_forbidden_vocab.py` blocks multi-word forbidden phrases outright; bare
  worldview/believes/thinks only when within ~48 chars of a model token (limits false
  positives per §7's "judgment" caveat). **Tune the proximity window during testing.**
- `check_schema_edit.py` is a SOFT gate (legit schema edits happen via the pipeline, e.g.
  Remedy B T2). A PreToolUse hook sees one tool call, so it CANNOT verify the
  DATA_DICTIONARY co-update — that stays the Reviewer's R7 check.

### Proposed `settings.json` wiring (DO NOT apply until tested)
Add to `.claude/settings.json` (currently only has `enabledPlugins`). `${CLAUDE_PROJECT_DIR}`
resolves to the repo root.
```jsonc
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Write|Edit|MultiEdit", "hooks": [
        { "type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/check_forbidden_vocab.py" },
        { "type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/check_informants_append_only.py" },
        { "type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/check_spend_gate.py" },
        { "type": "command", "command": "python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/check_schema_edit.py" }
      ]}
    ]
  }
}
```
**VERIFY at activation:** (a) the exact hook input JSON keys (`tool_name`, `tool_input.file_path`,
`tool_input.content` / `.new_string` / `.edits[]`) against current Claude Code docs/version;
(b) that `permissionDecision: "ask"` is honored for the schema hook (else it's a harmless
no-op reminder); (c) the `matcher` syntax. The hooks are written to the contract documented
May 2026 but the running version must be confirmed.

### Dry-run test before wiring (examples)
```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"x.md","content":"the model believes that"}}' \
  | python3 .claude/hooks/check_forbidden_vocab.py; echo "exit=$?"   # expect block (2)
echo '{"tool_name":"Edit","tool_input":{"file_path":"data/raw/informants.jsonl","new_string":"x"}}' \
  | python3 .claude/hooks/check_informants_append_only.py; echo "exit=$?"  # expect 2
echo '{"tool_name":"Write","tool_input":{"file_path":"s.py","content":"CDB_MAX_SPEND_USD=5"}}' \
  | python3 .claude/hooks/check_spend_gate.py; echo "exit=$?"  # expect 2
echo '{"tool_name":"Write","tool_input":{"file_path":"x.md","content":"I think this loop ok"}}' \
  | python3 .claude/hooks/check_forbidden_vocab.py; echo "exit=$?"  # expect 0 (no false positive)
```

---

## Tier 2 — orchestration (drafted, inert)

### `.claude/workflows/lsb-pipeline.js` (drafted)
Encodes Architect → CDA SME → (UI/UX if frontend) → Coder → Reviewer → Tester using the
project subagents, with **`isolation:"worktree"` on the Coder stage** (prevents the
bundled-commit race that hit us 2026-05-28) and gate-FAIL bounce-outs. Only runs when
invoked via the Workflow tool with explicit opt-in: `Workflow({ name:"lsb-pipeline",
args:{ task:"...", kind:"methodology"|"frontend"|"other", contextFiles:[...] } })`.
**VALIDATE** the Workflow API shape (meta literal, `agentType` resolution to `.claude/agents/`,
schema-forced structured outputs) on a small throwaway task before trusting it on real work.

### Per-agent permission scoping — DECIDED (Mark accepted 2026-05-29)
**Finding 1 → NO ACTION.** Agents are already correctly scoped (verified full frontmatter): read-only advisors (architect, ui_ux); read+run gate (reviewer = Bash, no Write); implementers (coder, tester). Do NOT impose blanket read-only.
**Finding 2 → sync defs to the live registry; keep SME Write.** Only `cda_sme` is out of sync: committed file = `Read/Grep/Glob`, but the live platform/FleetView registry grants it `Write/Edit` (it self-authored verdicts this session). There is no `~/.claude/agents` or `/etc/claude-code` override — the platform registry is the source of truth and the repo file is stale. Accepted plan: (a) sync `.claude/agents/cda_sme.md` UP to add `Write` + `Edit` so the file matches runtime; **keep** the SME's Write (bounded — it has no Bash; self-authored verdicts are useful + low-risk); (b) optionally grant `ui_ux` the same `Write/Edit` so both gates self-author verdicts (removes the manual-transcription friction) — Mark's option, not required. **Make the change in the platform registry (FleetView), not just the file** (file-only edit may be a no-op given the drift), and sync the file to match. **Do this Reviewer-gated AFTER Mark returns — NOT during the regen** (the SME is the escalation path if the food domain trips the threshold guard).

### (superseded) Per-agent permission scoping — original FLAG
The generic "make Reviewer/SME read-only" advice **does not fit LSB** and would break things:
- **Reviewer** legitimately runs `pytest`/`ruff`/`npm build` — it NEEDS Bash. Do not remove it.
- **CDA SME** writes verdict files to `docs/status/` — it NEEDS Write. Do not remove it.
- **UI/UX** is already read-only (Read/Glob/Grep) — correct as-is.
- **Coder** has Read/Write/Edit/Glob/Grep (+Bash at runtime) — correct.

**Discrepancy to reconcile (Mark decision):** the committed `.claude/agents/*.md` frontmatter
tool lists **do not match the agents' observed runtime tools** — e.g. `reviewer.md` and
`cda_sme.md` frontmatter read as read-only, yet this session the Reviewer ran Bash and the SME
wrote verdict files. So either the frontmatter is stale or the runtime registry augments it.
**Before imposing any tool restriction, reconcile the source of truth** (the `.claude/agents`
files vs the runtime/FleetView registry). Imposing restrictions against a non-authoritative file
could either do nothing or break a working agent. Recommended: confirm the registry, then make
the frontmatter authoritative and add only path-scoped `permissions.deny` rules (e.g. deny Coder
edits outside `packages/`+`apps/dashboard/`), not blanket tool removals.

---

## Activation (when Mark is back & has reviewed)
1. Reviewer-gate this whole change (guardrails affect the whole team).
2. Dry-run each hook (commands above); confirm no false positives on normal content.
3. Reconcile the agent-def/runtime tool discrepancy (decision above).
4. Apply the `settings.json` hooks block; restart the session so hooks load; re-run the dry-runs live.
5. Validate `lsb-pipeline.js` on a throwaway task.
6. Commit the activation (settings.json + any agent-def reconciliation) as its own reviewed commit.

## Deferred (recommendations only, not drafted)
Tier 3 (`/code-review` in loop, effort control, Slack MCP verdict posting) and Tier 4
(package the pipeline as a versioned plugin).
