# CDA SME Verdict — Check 9 (backup freshness) infrastructure split

**Task ID:** F2-T11
**Plan reviewed:** `docs/status/2026-05-01-check9-infra-split-plan.md`
**Date:** 2026-05-01
**Reviewer:** CDA SME (external)
**Verdict:** **PASS-WITH-NOTES**

---

## Four-axis scorecard

| Axis | Verdict | Notes |
|---|---|---|
| Protocol validity | PASS | Plan does not touch the CDA elicitation protocol (free list, pile sort, pile interview). The split is a software-architecture move on the QA layer. No protocol artifact changes shape, version, or storage. |
| Analytical validity | PASS | `qa_passed` and `qa_notes` are filters that downstream analysis applies before computing salience, OCI, MDS, consensus, etc. Conflating operator-infrastructure state with record-level QA contaminates that filter — records with structurally fine free lists, pile sorts, and interviews get dropped because the operator's backup script lagged, biasing whichever (model, domain) groups happened to collect during that window. The split removes that contamination. The `cdb_analyze` import boundary (§1 commitment 6) is unaffected: check 9 has no `cdb_analyze` dependency. The aggregate-check pattern (Check 8 / `check_salience_agreement`) is the correct template — alerts but no `qa_passed` mutation. |
| Claims validity | PASS | The open-data bundle's `qa_passed` field is a public claim about each record's structural validity. After the split, that claim becomes "this record passed structural QA at write time" — defensible. Today's claim is "this record passed structural QA *and* the operator's backup was fresh," which is unprovable from the record alone and renders historical `qa_passed=False` records ambiguous to downstream researchers (§9 pitfall in `CLAUDE.md`: open-data contract integrity). The plan strengthens the claim by narrowing it. |
| Audience translation | PASS | The methodology page does not currently surface check 9 to the public, so no public-facing copy changes. The distinct alert header ("QA Infrastructure Failure" vs "QA Failure") preserves operational legibility for the only audience that sees these alerts (Mark, in `#lsb-alerts`). No forbidden vocabulary in the plan or proposed code paths. |

**Register compliance:** N/A (this is QA infrastructure, not analytical register code).
**Vocabulary compliance:** PASS (no forbidden terms in the plan; the Coder must keep this clean in the new alert header text and code comments).

---

## Resolution of open methodology questions

### Q1 (load-bearing) — Should `qa_passed=False` ever reflect operator-infrastructure state?

**Ruling: NO. `qa_passed` is strictly a per-record verdict on properties of that record itself.**

Three reasons:

1. **Open-data semantics.** `qa_passed` and `qa_notes` are persisted into `data/raw/informants.jsonl` (CC0 open data bundle). A downstream researcher rebuilding the SQLite database has no way to distinguish "this record's free list / pile sort / interview is structurally suspect" from "the operator's backup script lagged when this record happened to be collected." Conflating the two breaks the open-data contract — the verdict field becomes ambiguous, and the dictionary cannot tell the researcher what `qa_passed=False` means without an environment-of-collection footnote that the JSONL itself does not carry.

2. **Architectural precedent already in the file.** `ARCHITECTURE.md` §4.1.6 already establishes the pattern explicitly for Check 8 (aggregate salience agreement): aggregate-level diagnostics fire alerts to `#lsb-alerts` but do **not** mutate `qa_passed` on any constituent record, because `qa_passed` is "a per-record QA verdict on deterministic structural properties of that record; aggregate-level observations belong on a separate surface." Check 9 is even more clearly outside the per-record contract than Check 8: Check 8 at least operates on (model, domain) groups of records; Check 9 operates on a filesystem path with zero record dependency. If Check 8 cannot mutate `qa_passed`, neither can Check 9.

3. **Falsifiability.** §1.5.2 commits LSB to "the chain of custody is auditable end to end." A `qa_passed=False` whose cause is "the backup script didn't run on the operator's VPS" is not part of the chain of custody for the record; it is part of the chain of custody for the operator's backup process. Mixing these two audit chains makes both less legible.

The architecture document's own §4.1.6 table for Checks 1–7 lists only structural properties of the record (free-list count, free-list uniqueness, pile-sort binarity, pile-sort symmetry, latency, token consistency, provider request ID). Check 9 does not belong in that table.

**Therefore the split is correct and the plan stands.** Q1 is resolved in favor of the Architect's reading.

### Q2 — Disposition of records already on disk with check-9-only failures

**Ruling: option (a). Out of scope for Task 1. Document the historical artifact in the data dictionary commentary; do not rewrite the JSONL.**

Three reasons:

1. **Append-only is a stronger guarantee than retroactive cleanup.** `CLAUDE.md` §9 pitfall 10 is binding: "the bad record stays in place (with `qa_passed=False` and `qa_notes` documenting the failure), and the audit trail remains intact." The Architect's instinct here matches the constitution. Re-evaluating the records in place via a sidecar (option b/c) is technically auditable, but it creates two surfaces a downstream researcher must reconcile (the JSONL and the sidecar), and it tempts a future operator to "just patch the JSONL too, while we're at it." Option (a) avoids that pressure entirely.

2. **The cohort is small and time-bounded.** The records affected by this bug are the records collected since commit `45206cb`. If the commit log is correct that CI has been red on master since `45206cb`, then we know the upper bound on the affected cohort is "everything collected after that commit on a host without `logs/backup.log`." Mark and the Architect together can document the affected commit range in `docs/DATA_DICTIONARY.md` commentary as a known historical artifact, and downstream analysis filters that drop `qa_passed=False` will continue to drop these records — which is the conservative choice for any analysis using the v1 bundle.

3. **The cost-benefit favors documentation over reprocessing.** The records that were marked `qa_passed=False` solely on check 9 are already excluded from analysis; they will remain excluded under option (a). They cost nothing in storage. Option (b)/(c) require a sidecar audit format, a parser that consumes it, an update to `DATA_DICTIONARY.md`, and a migration story for the SQLite build script — all to re-include records that the field flag already correctly identifies as structurally fine. The juice is not worth the squeeze for v1.

**If Mark later wants the affected cohort re-included**, that is a separate methodology decision that would benefit from being made on a larger cohort (e.g., once a full Phase 4 collection pass has run cleanly under the split). It is not a Task 2 candidate today.

**Task 2 is therefore dropped. Only Task 1 is in scope.**

The data-dictionary commentary referenced above is a small, separate edit that can ride on Task 1's commit (or a follow-up `docs(docs):` commit), but it is not load-bearing — `qa_notes` already contains "backup log missing: ..." on the affected records, so a careful researcher can already disambiguate them by string-matching. The commentary edit is a courtesy, not a correctness requirement.

### Q3 — Should `run_infrastructure_checks` be expanded in v1?

**Ruling: keep it narrowly to backup freshness for v1.** The Architect's YAGNI recommendation stands. Three reasons:

1. **The architecture document does not yet declare an infrastructure-check tier.** §4.1.6 declares per-record checks (1–7) and an aggregate check (8). Adding a third tier ("infrastructure") with one member and a documented contract is fine; expanding it to disk space, B2 reachability, and other operator concerns inflates the surface area before the contract has been validated.

2. **Each new infrastructure check needs its own threshold ruling.** Disk-free-space and B2-reachability are operationally interesting but neither has a documented threshold in `ARCHITECTURE.md` today. Adding them now would invite ad-hoc thresholds that the SME has not reviewed. Defer until a second concrete failure mode surfaces.

3. **The function name `run_infrastructure_checks` is not committing to a particular scope.** v1 can ship with one check; v2 can add others as separate `check_N_*` functions invoked from the same dispatcher. The name accommodates expansion without forcing it.

**Caveat for the Coder (mandatory note 1 below):** the plan's docstring on `run_infrastructure_checks` should explicitly say "currently covers only backup freshness (Check 9); future infrastructure checks may be added here without changing the function signature." This makes the v2 expansion path obvious and discourages anyone from inlining check 9 back into `run_record_checks`.

### Q4 — Should the infrastructure alert route to a separate channel?

**Ruling: keep it on `#lsb-alerts` with a distinct header in v1.** Three reasons:

1. **`CLAUDE.md` §5 declares exactly three operational channels.** Adding a fourth (`#lsb-infra`) is a meaningful operational change that would need to ripple into `CLAUDE.md` §5, `HOSTING_AND_DEV_OPS.md` §6, `SECURITY_AND_HARDENING.md` §8 (webhook env var inventory), and 1Password. The split itself does not require that change; the alerts already go where they need to go.

2. **The audience is the same person.** Mark monitors `#lsb-alerts` for both per-record and (today) aggregate alerts. Adding a header prefix (Architect's recommendation: "QA Infrastructure Failure" vs "QA Failure") gives Mark the visual distinction without forcing him to subscribe to a new channel.

3. **If the channel becomes noisy enough to need a split, that's a future ops decision, not a v1 decision.** Two infrastructure alerts in 48 hours from one stale backup log is not yet a noise problem; if and when infrastructure alerts grow in volume or in kind, that is the right moment to introduce `#lsb-infra` — *with* the matching `CLAUDE.md` §5 update.

**Note for the Coder (mandatory note 2 below):** the alert header text must not contain any forbidden vocabulary. "QA Infrastructure Failure" is fine. Do not write copy like "the operator's environment is unhealthy" — keep it precise: name the check, name the threshold, name the actual value, name the path checked.

---

## Mandatory notes the Coder must apply (PASS-WITH-NOTES)

The plan PASSes with the following notes. Each note must be reflected in the Task 1 commit; the Reviewer will check.

1. **Docstring on `run_infrastructure_checks` must signal future expansion intent.** Per Q3 ruling. Suggested wording: *"Run infrastructure-tier QA checks. Currently covers only backup freshness (Check 9). Future infrastructure checks (e.g., disk free space, B2 reachability) may be added here without changing the function signature. **Never mutates `InformantRecord.qa_passed`.**"* The last sentence is binding — it is the load-bearing comment that prevents a future maintainer from re-fusing the two batteries.

2. **Alert header copy must be precise and forbidden-vocabulary-clean.** Per Q4 ruling. The header should name the check, the threshold, the actual measured value, and the path checked. Do not use language that anthropomorphizes the host or the script. The existing per-record alert in `post_to_slack` is the right tonal template.

3. **Update to `qa_check.py` lines 58–62 (Check 9 threshold comment block) must explicitly call out the tier change.** The existing comment block describes Check 9's threshold but says nothing about which battery it belongs to. The new comment must say, in plain text: *"Check 9 is an infrastructure-tier check. It runs once per QA sweep (not once per record) and never sets `qa_passed=False` on any `InformantRecord`. Its alert path is `post_infrastructure_alert`, not `post_to_slack`. Adding this back into `run_record_checks` is a methodology violation — see `docs/status/2026-05-01-check9-infra-split-cda-sme-verdict.md`."*

4. **Documentation cross-reference required in `ARCHITECTURE.md` §4.1.6.** §4.1.6's table currently lists Checks 1–7 as per-record and Check 8 as aggregate. Check 9 is not formally documented in §4.1.6 today. The Architect should add a third sub-table or paragraph for Check 9 as an "infrastructure-tier" check with the same shape of contract as the aggregate paragraph (specifically: "does NOT mutate `qa_passed` on any individual record"). This is a doc edit, not a code edit, but it should land in the same Task 1 commit so the architecture document and the code do not drift. **Architect to write the §4.1.6 paragraph; Coder to land it alongside the code split.** No `DATA_DICTIONARY.md` change is required because `qa_passed` and `qa_notes` field semantics do not change.

5. **Compat shim retention is fine but must be documented as deprecated.** The Architect's plan keeps `run_qa_checks` as a compat shim that calls both batteries. That is acceptable for one cycle. The shim's docstring must say *"Deprecated for live collection. Prefer `run_record_checks` for per-record contexts and `run_infrastructure_checks` for sweep contexts. Removal target: F3 cleanup pass."* This sets a tombstone so the shim does not live forever.

6. **Test coverage note.** The plan adds two new tests (acceptance criteria 8 and 9). One additional test is recommended: a test that asserts `_assemble_record` in `runner.py` produces a record with empty `qa_notes` (or only the `campaign_id_tag`) when `logs/backup.log` is absent in the test working directory. This is the regression test that prevents the bug from coming back via a different path (e.g., a future contributor re-importing `run_qa_checks` from the runner). Suggested location: `tests/unit/test_runner.py::test_run_informant_no_backup_log_does_not_fail_qa`. Optional but strongly recommended.

7. **Commit message must reference this verdict file.** Per `CLAUDE.md` §8. Suggested body: *"Split Check 9 (backup freshness) out of the per-record QA battery. Check 9 is an infrastructure-tier check; it does not describe a property of any `InformantRecord` and must not mutate `qa_passed`. Resolves CI red on master since `45206cb` and the open-data ambiguity flagged by the SME. See `docs/status/2026-05-01-check9-infra-split-cda-sme-verdict.md` for the methodology ruling and `docs/status/2026-05-01-check9-infra-split-plan.md` for the Architect's plan. Task 2 (disposition of already-on-disk records) ruled out of scope — affected records remain `qa_passed=False` per `CLAUDE.md` §9 pitfall 10."*

---

## Rationale (summary)

The plan correctly identifies that wiring `check_9_backup_freshness` into the per-record QA battery violates the per-record-verdict contract on `qa_passed`. The architecture document's own treatment of the aggregate Check 8 (Smith's S / Sutrop CSI) establishes the binding pattern: alerts fire, but `qa_passed` does not move on any individual record when the failure does not describe a property of that record. Check 9 is an even cleaner case for that pattern than Check 8 — it has zero record dependency at all. The split as described is methodologically correct and should land.

The plan's defensive instincts are also correct: keep the alert path intact (commitment 8 of §1 preserved), keep the JSONL append-only (pitfall 10 of §9 preserved), do not introduce a new Slack channel without updating `CLAUDE.md` §5 in the same change.

PASS-WITH-NOTES rather than straight PASS because the seven mandatory notes above need to be in the Task 1 commit, not deferred. None of them block the Coder from starting; all of them must be satisfied before the Reviewer signs off.

---

## Disposition

- **Verdict:** PASS-WITH-NOTES.
- **Coder unblocked to start Task 1:** YES.
- **Task 2 in scope:** NO (Q2 ruled option (a) — out of scope).
- **Architect action required:** add the §4.1.6 paragraph for Check 9 (infrastructure tier) per mandatory note 4. Can land in the same commit as the code split or in a paired doc commit at the Architect's discretion.
- **Next gate:** Reviewer agent on the Task 1 commit. The Reviewer must verify all seven mandatory notes are present.
