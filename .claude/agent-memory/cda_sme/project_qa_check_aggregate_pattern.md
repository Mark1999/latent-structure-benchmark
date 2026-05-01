---
name: QA_Runner check tiers (per-record / aggregate / infrastructure)
description: The three-tier QA check architecture in scripts/qa_check.py and the binding constraint that only per-record checks may mutate qa_passed.
type: project
---

`scripts/qa_check.py` has three tiers of QA checks. The binding rule across all three: **only per-record checks (Checks 1–7) may mutate `InformantRecord.qa_passed`.** Aggregate and infrastructure checks fire alerts but never touch the per-record field.

**Tier 1 — Per-record (Checks 1–7).** Run on each `InformantRecord` individually. May set `qa_passed=False` and write to `qa_notes`. Examples: free-list count, free-list uniqueness, pile-sort binarity, pile-sort symmetry, latency, token consistency, provider request ID. Documented in `ARCHITECTURE.md` §4.1.6 table.

**Tier 2 — Aggregate (Check 8).** Runs on a (model, domain) group of records. Posts to `#lsb-alerts` via `post_aggregate_alert` but **never mutates `qa_passed`** on any record in the group. Function-scope imports `cdb_analyze` (live-collection path must keep minimal-import profile per §4.1.6). Example: Smith's S / Sutrop CSI rank agreement (ρ ≥ 0.85). Has a minimum-group-size floor (e.g., ≥ 10 distinct items) before firing.

**Tier 3 — Infrastructure (Check 9).** Runs once per QA sweep with **zero record dependency** (e.g., backup log freshness inspects a filesystem path, not any record). Posts to `#lsb-alerts` via `post_infrastructure_alert` with a header distinct from per-record alerts. **Never mutates `qa_passed` on any record** — this is even more clearly outside the per-record contract than Tier 2, because Tier 3 has no record dependency at all. Established by the F2-T11 split (2026-05-01) after `check_9_backup_freshness` was incorrectly fused into `run_qa_checks` and contaminated `qa_passed=False` on records collected outside the live VPS (CI, fresh clones).

**Why:** `qa_passed` is persisted into the open-data bundle (CC0 JSONL). Conflating per-record structural QA with aggregate or infrastructure state breaks the open-data contract — downstream researchers cannot tell what `qa_passed=False` means without environment-of-collection footnotes the JSONL does not carry. The §4.1.6 commitment is that `qa_passed` is "a per-record QA verdict on deterministic structural properties of that record."

**How to apply:**
- A new check that depends on a property of one record → Tier 1.
- A new check that depends on a group of records (e.g., per-(model, domain)) → Tier 2.
- A new check that depends on operator/host state (disk space, B2 reachability, log mtime) → Tier 3.
- Tier 2 and Tier 3 alerts have distinct headers in `#lsb-alerts` so Mark can disambiguate. No new Slack channel without `CLAUDE.md` §5 update.
- Tier 3 docstrings must explicitly say "Never mutates `InformantRecord.qa_passed`" — this is the load-bearing guard against re-fusion.
- Append-only is binding: records that were marked `qa_passed=False` solely on a Tier 2 or Tier 3 check before the tier system existed stay in place per `CLAUDE.md` §9 pitfall 10. Document the historical cohort in commentary; do not rewrite the JSONL.

**Reading:** `ARCHITECTURE.md` §4.1.6 (formal contract for Tiers 1 and 2; Tier 3 added 2026-05-01); `docs/status/2026-05-01-check9-infra-split-cda-sme-verdict.md` (Tier 3 ruling and rationale).
