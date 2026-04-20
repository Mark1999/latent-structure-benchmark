---
name: QA_Runner aggregate-check pattern (Check 8 and beyond)
description: Architectural pattern for QA aggregate checks that run per-(model, domain) instead of per-record, and the constraints they must respect.
type: project
---

Check 8 (Smith's S / Sutrop CSI rank agreement, threshold ρ ≥ 0.85) introduced the first aggregate check in `scripts/qa_check.py`. Unlike Checks 1–7, aggregate checks:

1. Run on a group of records (per-(model, domain)), not on individual records.
2. Post alerts to `#lsb-alerts` but do **not** mutate `qa_passed` on any record — that field is per-record semantics only.
3. Import `cdb_analyze` at function scope, because `scripts/collect.py` imports only `check_record` from `qa_check.py` during live collection, and the live-collection path must not pull `cdb_analyze` into its dependency graph (§4.1.6 minimal-import profile).

**Why:** The QA_Runner's §4.1.6 promise ("boring, deterministic, fast, minimal imports") binds the per-record path that runs inside `collect.py`. The aggregate path runs only on manual or post-collection invocation, so function-scope imports preserve the live-collection invariant while still giving the aggregate path access to analysis primitives.

**How to apply:** If a future SME review adds another aggregate-level diagnostic, it should:
- Live in a new `check_*_aggregate` function alongside `check_salience_agreement`.
- Be invoked from `run_aggregate_checks` alongside the existing check.
- Use a dedicated `post_*_alert` function if the failure shape differs from `post_to_slack` (which is record-shaped).
- Document scope/threshold/failure-mode in `ARCHITECTURE.md` §4.1.6 in the same PR that wires it in.
- Never mutate `InformantRecord.qa_passed`.
- Enforce a minimum-group-size floor (e.g., the N=10 shared-item floor for Check 8) before firing, so rank statistics don't trip spuriously on small groups.
