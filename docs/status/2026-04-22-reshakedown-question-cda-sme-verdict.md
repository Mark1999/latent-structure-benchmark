# Pre-Phase-4a Re-Shakedown Question — CDA SME Verdict

**Date:** 2026-04-22
**Reviewer:** CDA SME (agent)
**Question:** Does Phase 4a require another shakedown test before kickoff, or is the 2026-04-21 re-shakedown (PASSED) sufficient?
**Channel:** `#lsb-cda-sme` (saved to repo per preference)
**Preceding verdict:** `docs/status/2026-04-22-shakedown-findings-cda-sme-verdict.md` (this is a follow-on narrow question after that PASS-WITH-NOTES verdict)

---

## Verdict: **Position C — host replay only, no new API calls**

Copy the existing 2026-04-21 shakedown JSONL onto the Linode, run `scripts/analyze.py` and `scripts/qa_check.py` against it on the new host, and assert byte-identical reproduction of the Surface-side outputs. Zero API spend. Catches genuine host-class risks (encoding, locale, filesystem under the `lsb` systemd user, headless Claude Code stdio) without paying to re-verify model output that was already validated.

---

## Methodological reasoning

**The host-change question, honestly answered.** A reasonable peer reviewer reviewing *published methodology* would not raise the host as a concern. The shakedown validates pipeline code, not network paths. Provider API semantics are specified at the API surface — the adapter's contract is with the JSON response, not with the TCP route. The 2026-04-21 PASS covers every methodologically load-bearing component: protocol dispatch, free-list parsing, pile-sort parsing, gates, consensus classification, split G1, bootstrap annotation, OCI computation, centrality sign preservation. None of that is host-sensitive.

**But "orthogonal to methodology" ≠ "orthogonal to Phase 4a integrity."** The two UTF-8 bugs (`9b7bfea`, `fd55cde`) that the 2026-04-21 run surfaced were not predicted by unit tests — they were surfaced by *real execution against real bytes*. Locale defaults, filesystem encoding under the `lsb` systemd user, Python 3.12 stdio semantics, and headless Claude Code invocation are all genuine unknowns on the Linode. These would corrupt a Phase 4a run just as thoroughly as a methodology bug, even though they aren't methodology bugs per se.

**Position A** (proceed directly) is methodologically defensible but operationally optimistic. **Position B** (minimal smoke re-shakedown) spends real money re-validating something already validated. **Position C** threads the needle.

---

## Position C — scope

**Input:** copy `data/shakedown/shakedown-20260421/` from the Surface host (containing `informants.jsonl`, the sensitivity cell, the determinism cell, and the 2026-04-21 reference `DomainResult` JSONs) onto the Linode at a non-canonical path — `/tmp/shakedown-replay/` or `data/shakedown/shakedown-20260421-replay/`. Do **not** put it at `data/raw/`. The `data/shakedown/` gitignore and the `build_db.py` exclusion protect it.

**Commands on the Linode:**
1. Run `scripts/analyze.py` for `family` and `holidays` against the replayed JSONL.
2. Run `scripts/qa_check.py` on the JSONL.
3. At least one of the above must execute via headless Claude Code invocation (not just an interactive shell) to exercise the stdio path that Phase 4a will use.

**Pass criteria (all four must hold):**
1. The two `DomainResult` JSONs produced on the Linode are **byte-identical** to the 2026-04-21 Surface outputs. `diff -q` on pretty-printed canonicalized JSON. If float-format differences across Python patch versions produce spurious diffs, fall back to a stable-sort-keyed re-dump and document the tolerance.
2. All eight §8 sanity checks pass identically to the 2026-04-21 run (`docs/status/2026-04-21-shakedown-findings.md` §2 table).
3. `qa_check.py` reports the same `qa_passed` booleans per record.
4. Headless Claude Code invocation exercised at least once during the replay.

**If any of 1–3 fails:** stop. File as a blocker. Do not kick off Phase 4a.

`check_9_backup_freshness` is expected to fire in its new role; that's orthogonal to this replay and not a fail condition.

---

## Cost estimate

- **Position C: $0.** No API calls. Hours of operator/agent time only — plausibly 30–60 minutes end-to-end, most of it waiting for analysis to finish.
- (Reference: Position B minimum would be ~$5 for a Claude-Sonnet × family × N=2 smoke plus a sensitivity-cell-equivalent exercise. A true full re-shakedown would approach $20–50.)

---

## Register / vocabulary compliance

N/A — this is a methodological decision, not a generated text artifact.

---

## Operational sequencing

1. Copy `data/shakedown/shakedown-20260421/` from the Surface to the Linode (Mark's operational step — scp, rsync, or manual).
2. Run the replay on the Linode against the four pass criteria above.
3. On success: Phase 4a is unblocked. On failure: surface the specific discrepancy and do not proceed.
4. **After** replay success: delete `data/shakedown/shakedown-20260421/` from both the Surface (per `SHAKEDOWN_PROTOCOL.md` §10) and the Linode (the replay copy). Retain the private-repo off-host archive through Phase 4d per protocol §10.

---

*End of verdict. Position C unblocks Phase 4a at zero API cost contingent on byte-identical replay on the Linode.*
