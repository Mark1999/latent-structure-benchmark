# Incident — Test data loss on `lsb-agent-01`

**Date:** 2026-04-19
**Severity:** Low (test data only, pre-production)
**Status:** Resolved — folders recreated empty; VPS decommissioned; development moved to Mark's local Surface Laptop Studio
**Related docs:** `HOSTING_AND_DEV_OPS.md` §4.1 (backup layers), `ARCHITECTURE.md` §4.3 (storage), §6 (open data)

---

## 1. Summary

During testing on the Hetzner VPS `lsb-agent-01`, the following directories were lost from the working copy:

- `data/raw/` — holds the canonical append-only `informants.jsonl` once collection is live
- `data/processed/` — intermediate analysis artifacts
- `data/transcripts/` — per-call verbatim transcripts for audit

No git-tracked data was affected. All three directories are listed in `.gitignore` and were always host-local working-copy content.

## 2. Impact

**None to the official corpus.** LSB has not yet begun official collection runs. Everything in the lost directories was test data — adapter smoke runs, protocol dry-runs, and QA fixtures generated during Phase 1 shakedown. No published result, no analysis output, no grounded claim depended on the lost files.

The in-git artifacts that *would* depend on the raw corpus (`data/results/family/0.1.json`, `0.2.json`, the grounding bundle under `data/grounding/family/romney_1996/`) were produced from separate, earlier runs and are untouched. They remain valid as Phase 3 reference outputs; they were not invalidated by this incident.

## 3. Root cause

The four-layer backup plan documented in `HOSTING_AND_DEV_OPS.md` §4.1 was not yet implemented at the time of the loss. Specifically:

- **Layer 1** (local VPS working copy) — active, but this is the primary, not a backup
- **Layer 2** (Synology rsync) — planned, not configured
- **Layer 3** (Backblaze B2 nightly sync) — planned, `lsb-backup.timer` not created
- **Layer 4** (fireproof safe USB SSD) — planned, not rotated

A hardware-or-configuration event on the VPS therefore had no layer to fall back to. Because the lost content was test data, the consequence was recoverable by re-testing rather than by restoring.

## 4. Response

1. Confirmed that no git-tracked data was affected (`git status` clean; `data/domains/`, `data/grounding/`, `data/models/`, `data/results/` intact).
2. Recreated the empty directories locally with `.gitkeep` placeholders.
3. **Decommissioned `lsb-agent-01`.** The Hetzner VPS is no longer in service.
4. **Moved all development to Mark's local MS Surface Laptop Studio (model 1964).**
5. **Deferred VPS selection.** A new VPS will be chosen at a later date; criteria, provider, and the containerization question (Docker vs. native) are open decisions.
6. Updated the affected docs (`HOSTING_AND_DEV_OPS.md`, `ARCHITECTURE.md`, `SECURITY_AND_HARDENING.md`, `CLAUDE.md`) with superseded-pointer callouts linking to this note. Full rewrites are deferred until the new VPS is selected, so the patches are a stopgap, not the final form.

## 5. Lessons and action items

### 5.1 Backup-before-collection is now a precondition

The core lesson: **a backup layer must be active on the collecting host before any official collection run begins.** This is a tightening of the `HOSTING_AND_DEV_OPS.md` §4.1 commitment. The prior framing treated layers 2–4 as Phase 1 / Phase 2 work that could be stood up alongside collection; the corrected framing treats at least one off-host backup layer as a precondition for collection, not a parallel deliverable.

Concretely, before the next official run on the next VPS:

- [ ] At least one off-host backup layer (Backblaze B2 or equivalent) is configured and verified by a test restore
- [ ] The backup cadence is at least daily
- [ ] `scripts/qa_check.py` or a companion check reports on the age of the most recent successful backup
- [ ] `HOSTING_AND_DEV_OPS.md` §4.1 is updated to reflect the new VPS and to mark at least layer 3 as **Active** before collection starts

### 5.2 VPS selection is open

The new VPS has not been selected. Open questions for that decision:

- **Provider.** Hetzner, Fly.io, Railway, Linode, DigitalOcean, or self-hosted on existing hardware are all on the table.
- **Containerization.** Whether to run the collector and QA_Runner in Docker or natively. Leaning native for now (single operator, `uv.lock` already provides Python reproducibility, Windows dev host has Docker-Desktop friction) but some providers assume containers. See the discussion note in project memory `project_infra_pivot.md`.
- **Budget.** Prior VPS cost was ~$12/month for a CPX32. The `ARCHITECTURE.md` §6.2 spend cap was $300/month total including LLM spend; hosting was a minor line item. No reason to change that.

### 5.3 Docs that now misrepresent reality

Until the new VPS is chosen, these docs contain references to `lsb-agent-01` that describe the prior state. Each carries a superseded-pointer callout added in the same PR as this incident note:

- `HOSTING_AND_DEV_OPS.md` — top-of-doc status banner; §2–6 reference the VPS throughout
- `ARCHITECTURE.md` §9 glossary entry for `lsb-agent-01`
- `SECURITY_AND_HARDENING.md` — top-of-doc status banner; §2, §6, §8 reference secret storage paths on the VPS
- `CLAUDE.md` §9 pitfall #9 reference to collection campaigns on the VPS

A full rewrite of these sections is deferred. When the new VPS is selected, those sections will be reworked in a dedicated PR that retires the pointer callouts.

## 6. What is *not* in scope of this incident

- No LLM API key was compromised. Secrets on `lsb-agent-01` at the time of the loss were scoped to the VPS account and were rotated as part of the decommission.
- No public-facing surface was affected. The dashboard is served from Cloudflare Pages (static), which is independent of the collection VPS.
- No CI/CD pipeline was affected.
- No git-tracked data was affected.

## 7. Disposition

Closed 2026-04-19. Reopen only if evidence emerges that in-git artifacts were derived from a lost run (none expected; `data/results/family/0.{1,2}.json` predate this incident).
