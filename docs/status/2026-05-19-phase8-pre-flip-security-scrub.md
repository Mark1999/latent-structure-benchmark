# Phase 8 — Pre-Flip Security Scrub

**Date:** 2026-05-19
**Run by:** Claude orchestrator at Mark's request
**Scope:** Full repository audit before M11 (the public flip)
**Result:** **PASS after two surgical edits** — repo is safe to flip, with 4 informational decisions for Mark to make

---

## 1. Automated layers — all CLEAN

| Tool | Scope | Result |
|---|---|---|
| `gitleaks` v8.18.4 | Working tree | **0 leaks** |
| `gitleaks` v8.18.4 | Full git history (580 commits, all refs) | **0 leaks** |
| `scripts/prerelease_scan.py` | 8 checks across the tracked tree | **PASS overall** after surgical fixes (Section 3) |

The pre-release scan exits 0 on:
- Check 1: gitleaks full history (PASS, 0 hits)
- Check 2: forbidden vocabulary (PASS, 0 hits)
- Check 3: leaked internal paths (PASS, 0 hits)
- Check 4: real email addresses (PASS, 0 hits — after fix)
- Check 5: API key patterns (PASS, 0 hits)
- Check 6: public URL validity (WARN, 2 hits — both are expected `<TBD-T8-DOI>` placeholders that will be replaced post-T8)
- Check 7: `.env` / credential-file presence (PASS, 0 hits)
- Check 8: license coverage sanity (PASS, 0 hits)

## 2. Manual sweep layers — all CLEAN

I also ran independent sweeps the automated layers may not catch:

| Sweep | Result |
|---|---|
| Provider key shapes (`sk-ant-`, `sk-or-`, `hf_*`, `ghp_`, `gho_`, `xoxb-`, `AIza*`, `ya29.`, `AKIA*`) | 0 real values; all matches are regex pattern definitions in sanitizer/scanner source, or doc references like "we scan for `sk-ant-`" |
| Slack webhook URL values | 1 hit at `tests/cdb_publish/test_failures.py:94` — `T12345ABC/B67890DEF/xAbCdEfGhIjKlMnOpQrStUvW`. Synthetic test fixture (obvious alphabet pattern). Safe. |
| `.env` tracked | Not tracked. Only `.env.example` (intentional template). |
| `HARDWARE.md` tracked | Not tracked (per `feedback_hardware_md_local.md` memory). |
| B2 keys (`K00…` 31-char shape) | 0 hits anywhere in repo |
| Phone numbers (NANP / international) | 0 hits |
| Mailing addresses | 0 hits |
| Auth-y patterns (`token`, `bearer`, `secret`, `password` followed by long strings) | All matches are docs explaining env vars, code accepting `password=password` parameter, or placeholder examples like `LSB_SMTP_PASSWORD=your-gmail-app-password`. No real values. |
| Published `data/results/*.json` (`family/{0.1,0.2}.json`, `food/0.2.json`, `holidays/{0.1,0.2}.json`) | 0 secret-shaped strings in any of the 5 published result files |
| Large tracked files (>100 KB) | All accounted for: 5 result JSONs, 10 screenshot PNGs, `uv.lock`, `ARCHITECTURE.md`. None contain secrets. |
| Git author emails across history | 3 distinct: `markdd2@gmail.com` (Mark), `noreply@anthropic.com` (Claude), `49699333+dependabot[bot]@users.noreply.github.com` (Dependabot). See Section 4 decision 1. |

## 3. Fixes applied (this scrub)

Two surgical edits committed pre-flip:

1. **`docs/status/2026-04-30-phase4a1-t3c-resume-instructions.md`** — replaced 2 occurrences of `markdd2@gmail.com` with `Mark's personal email`. The references were in a historical reminder note (T3C resume instructions, April 30) about a scheduled Gmail-draft event. The PII was non-essential to the historical record.

2. **`docs/status/2026-05-17-phase8-handoff-for-mark.md:83`** — replaced a non-`example.com` configuration placeholder with the RFC 2606 standard form `you@example.com`. The original used a non-reserved domain string that triggered the pre-release scan's email detector. Standard RFC 2606 placeholders (`example.com`) are scanner-safe.

After both fixes, `scripts/prerelease_scan.py` exits PASS.

## 4. Informational items — Mark to decide before flip

These are **not security blockers**, but they affect what's visible to anyone browsing the repo after M11. Decide each before the flip; some have one-way doors.

### Decision 1 — Git author email on past commits

**Status:** Every commit Mark made (`git log` shows ~580 of them) carries `Author: Mark Dawson <markdd2@gmail.com>`. Once the repo is public, this is visible to anyone running `git log` on a clone, viewable on GitHub's commit list pages, and indexable by GitHub search.

**Options:**
- **(a) Accept.** Standard for open-source projects. Most public repos carry the real maintainer email. Easy to opt out of mailing-list spam via GitHub settings (block `noreply` mode).
- **(b) Rewrite history** to replace `markdd2@gmail.com` with `<noreply>` or a GitHub-noreply-style address. **This rewrites every commit SHA**, breaks the audit trail referenced by 50+ status docs, breaks any external clones or forks, and is generally **not recommended** for a research project where reproducibility matters.
- **(c) Configure future commits only.** Run `git config user.email "noreply@cogstructurelab.com"` (or use GitHub's noreply-email form — see `github.com/settings/emails` for the exact value tied to your account). Past commits unchanged, but future commits use the noreply address.

**Recommendation:** **(a) Accept**, or (c) if you want future commits anonymized. Don't (b) — the cost is high and the benefit is marginal (your Gmail address is already publicly associated with your GitHub username).

### Decision 2 — VPS IP `172.238.170.9` in 12 tracked files

**Status:** The Linode VPS IP appears in:
- `HOSTING_AND_DEV_OPS.md` (ops documentation)
- `scripts/prerelease_scan.py` (listed as a known-internal IP for the leaked-paths scan — intentional)
- 10 historical status docs (`docs/status/2026-04-2{2,3}-*` — VPS handoff, backup setup, replay verdicts)

The IP is **already in public DNS** as the A record for `agents.cogstructurelab.com`. So it's not a "leak" in the sense that someone couldn't otherwise find it. The question is whether having the IP textually present in the repo (and therefore in GitHub search / archive.org / etc.) creates a different threat surface.

**Options:**
- **(a) Accept.** Already in DNS; not new information. Removes legitimate ops-doc value if scrubbed.
- **(b) Scrub the IP from all docs except `HOSTING_AND_DEV_OPS.md`** (the canonical operational reference) and `scripts/prerelease_scan.py` (it's a scanner constant). The status docs are historical and the IP detail isn't load-bearing.
- **(c) Add an `lsb-agent-02` shell alias** in DNS (e.g., `vps.cogstructurelab.com` already-resolvable internal name) and reference that everywhere instead of the literal IP.

**Recommendation:** **(a)** — same as your existing posture, and consistent with the rest of the open ops documentation. The DDoS / reconnaissance angle is the same whether the IP is found via DNS or via repo search.

### Decision 3 — `.claude/agent-memory/cda_sme/*` tracked (38 files)

**Status:** The CDA SME agent's persistent memory is committed to the repo. These files contain internal SME deliberations:
- Methodology verdicts (PASS-WITH-NOTES rulings, binding notes labeled B1–B15, S1–S5, etc.)
- Decision history (Phase 4a.1, Phase 4b, Phase 5, Phase 6, Phase 7 verdicts)
- Technical reasoning (e.g., why `_is_recursive_decline()` had a 18/24 false-positive rate)
- References to specific commit SHAs and status docs

Sample: `feedback_detector_role_change_gate.md` explains the Phase 4a.1 T3B detector miscalibration in detail. `MEMORY.md` is an index linking to ~25 verdicts and feedback memories.

**No secrets, no PII, no operational details. But verbose internal-agent-speak.**

**Options:**
- **(a) Keep tracked.** Aligns with the open-methodology ethos. A serious reproducibility-minded researcher might find these informative. Adds methodological transparency.
- **(b) Move to `.gitignore` going forward.** Future SME verdicts not committed. Existing 38 files stay (cannot un-commit without rewriting history).
- **(c) Rewrite history to remove the directory entirely.** Same caveats as Decision 1(b) — high cost, marginal benefit.

**Recommendation:** **(a) Keep tracked.** They demonstrate the rigor of the methodology process and provide an unusual level of audit transparency for an LLM-evaluation project. They're not embarrassing or sensitive.

### Decision 4 — `/opt/lsb-agent` path in ~25 tracked files

**Status:** The VPS path layout `/opt/lsb-agent/...` is referenced in:
- `HOSTING_AND_DEV_OPS.md`
- `ARCHITECTURE.md`
- `SECURITY_AND_HARDENING.md`
- `docs/PHASE_8_LAUNCH_RUNBOOK.md`
- `deploy/systemd/lsb-backup.service`
- ~20 historical status docs

Reveals the deployment path layout but does not expose any actual secret or credential. Common for ops-documented open-source projects (e.g., Postgres / nginx docs always reference standard paths).

**Recommendation:** **Accept.** Not actionable.

## 5. Pre-flip rescan requirement

`scripts/prerelease_scan.py` must be re-run **within 24 hours immediately preceding M12** (the actual flip), per the scan's own gate-status output. This scrub passes today (2026-05-19), but you'll need a fresh run on the day of the flip:

```bash
cd /opt/lsb-agent
uv run python scripts/prerelease_scan.py --report docs/status/$(date +%Y-%m-%d)-phase8-prerelease-scan.md
```

Expected: `Overall: PASS`. If anything changes between now and then (new commits, new tracked files), the rescan catches it.

## 6. Summary verdict

**The repo is safe to flip public.** Two blockers fixed; no remaining security findings. Four informational decisions for Mark (Section 4) — all defaultable to "accept" with no security cost.

The CI gate, the canonical pre-release scan, gitleaks at multiple layers, and the manual sweeps all converge on the same result: nothing in the working tree or git history reveals a credential, an internal-only IP/hostname not already in public DNS, or any PII beyond standard open-source maintainer-email exposure.

**Action items before M11:**
1. ✅ DONE — surgical fixes committed
2. ⏳ Re-run `prerelease_scan.py` within 24h of M11 (per Section 5)
3. ⏳ Mark decides on Section 4 informational items (or accepts defaults)

---

*End of scrub report. Authored by Claude orchestrator, audited by Mark.*
