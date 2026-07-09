# Admin Console From the Laptop: Access Options and Ops-Console Direction

**Document:** `docs/proposed/2026-07-09-admin-console-access-proposal.md`
**Status:** PROPOSED. Options analysis for Mark. Option 1 needs zero changes and
works today; Option 2 is a small operational change with a security consideration;
Option 3 is a scoped build that needs an Architect plan.
**Origin:** Mark's request (2026-07-09): use the admin console from the laptop
instead of going through the Claude Code CLI for everything.

---

## 1. Current state

The admin console (`python -m cdb_social.admin_console`) is a Flask app that binds
to `127.0.0.1:8000` by design (Phase 7 kickoff §11.6: loopback bind IS the security
boundary; no auth, no TLS, deliberately). It currently covers the social pipeline
only: pending triggers, per-trigger draft requests (the sole sanctioned LLM-draft
site), stage, publish.

The VPS (`lsb-agent-02`) is on the tailnet at `100.108.153.127`, and Mark's devices
are on the same tailnet. Two of the three options below lean on that.

## 2. Option 1 (works today, zero changes): SSH local forward

From the laptop:

```
ssh -L 8000:127.0.0.1:8000 lsb@100.108.153.127
# then on the VPS, inside that session (or a zellij pane):
uv run python -m cdb_social.admin_console
# then open http://localhost:8000 in the laptop browser
```

Cursor's remote-SSH session can hold the tunnel; VS Code/Cursor also auto-forward
ports it sees listening. Security posture unchanged: the app still only ever
listens on loopback, and the tunnel is authenticated by the SSH key.

Friction: the tunnel must be up, and the console process must be running. Fine for
occasional social publishing; annoying as a daily ops surface.

## 3. Option 2 (zero code change, persistent): tailscale serve

```
# on the VPS, once:
tailscale serve --bg 8000
# then from any tailnet device:
https://lsb-agent-02.<tailnet-name>.ts.net
```

`tailscale serve` proxies the loopback port onto the tailnet with TLS and tailnet
identity. The app keeps its loopback bind (§11.6 intact at the process level); no
public internet exposure (serve is tailnet-only; `funnel` would be public and must
NOT be used).

Security consideration to decide explicitly: the console can PUBLISH social posts,
and tailnet exposure means every device on the tailnet can reach it (the tailnet
currently includes a non-operator device). Mitigations, pick one:
- run `tailscale serve` only while using it, then `tailscale serve --off` (moral
  equivalent of Option 1 with better UX), or
- Tailscale ACLs restricting the port to Mark's devices, or
- add a simple shared-secret login to the console (small Coder task, Reviewer-gated,
  SECURITY_AND_HARDENING.md applies).

Also needs the console process running persistently (a systemd user unit is the
clean form; small ops task, documented in HOSTING_AND_DEV_OPS.md when done).

## 4. Option 3 (the real ask, scoped build): an ops console

Mark's stated goal is broader than social publishing: operate the project from a
browser instead of routing everything through the CLI. Prior art and constraints:

- The visual-inspection preference is on record: evaluation and classification
  tasks need rendered tables/piles/frequency bars, not raw JSON (internal ops
  dashboard, distinct from the public `apps/dashboard/`).
- `scripts/lsb_inspect.py` already computes most of what an ops view would show.
- The B-1 boundary (no autonomous LLM calls) and the guard-trip human gate must
  survive any UI: buttons may RUN existing scripts and SHOW their output, but the
  only LLM-call button remains the social draft trigger, and promotion past a
  tripped guard stays impossible from the UI.

Candidate scope for a v1 ops console (extend the existing Flask app, same package,
served per Option 2):

1. **Campaign status:** live tail of collection runs, per-model/per-domain progress,
   qa_check failures (read-only views over informants.jsonl and logs).
2. **Corpus browser:** lsb_inspect views rendered as tables (records by model and
   domain, failures with raw logs, decline interviews).
3. **Rebaseline panel:** staged-vs-published deltas (the numeric-deltas reports),
   guard status, manifest provenance. Strictly read-only; promotion stays CLI+gates.
4. **Trigger/draft panel:** what exists today.

Not in v1: anything that mutates data, launches paid collection, or promotes
results. Those keep their existing gated paths.

This is an Architect-plan task (multi-file, new routes, new templates; frontend
work but internal-ops, so the reduced UI/UX gate per the ui-polish-scope precedent:
accessibility floor and readability, not OWID fidelity).

## 5. Recommendation

Do Option 1 today (it is a one-liner). Decide the Option 2 exposure question (the
publish-button-on-the-tailnet point) before making it persistent. Queue Option 3 as
a proper Architect plan once the model refresh and any political-domain decision
have their slots; it is the piece that actually removes the CLI-for-everything
friction.
