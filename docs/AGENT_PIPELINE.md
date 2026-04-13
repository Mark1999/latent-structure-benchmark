# LSB Agent Pipeline

Summary of the six-agent pipeline from `ARCHITECTURE.md` §5.1 and §5.4.

## Pipeline shape

```
Architect → CDA SME → ┬─ (frontend tasks) → UI/UX agent → Coder → Reviewer → Tester
                      └─ (other tasks)    ─────────────→  Coder → Reviewer → Tester
```

The CDA SME and UI/UX agent are **gates, not advisors.** A FAIL verdict stops the plan.

## Agents

| Agent | Model | Role |
|---|---|---|
| Architect | Opus | Owns ARCHITECTURE.md. Decomposes into tasks. Never writes code. |
| CDA SME | Opus | Methodological gatekeeper. Four-axis verdict. |
| UI/UX | Sonnet | Design conscience. Frontend tasks only. Owns DESIGN_SYSTEM.md. |
| Coder | Sonnet | Implements one package/feature at a time. |
| Reviewer | Sonnet | Enforces binding rules. Cannot be overridden except by Mark. |
| Tester | Sonnet | Fixture-based tests. No real API calls. |

## Slack channels

| Channel | Posted by | Purpose |
|---|---|---|
| `#lsb-alerts` | `scripts/qa_check.py` | Operational alerts. Bypasses agent team. |
| `#lsb-cda-sme` | CDA SME agent | Methodological verdicts. |
| `#lsb-ui-ux` | UI/UX agent | Design verdicts. Frontend tasks only. |

Webhook env vars: `LSB_ALERTS_WEBHOOK_URL`, `LSB_CDA_SME_WEBHOOK_URL`, `LSB_UI_UX_WEBHOOK_URL`.

See `ARCHITECTURE.md` §5.1 and §5.4 for full details.
