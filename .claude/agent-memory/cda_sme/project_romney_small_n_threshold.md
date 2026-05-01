---
name: Romney small-n warning threshold is n < 15
description: Binding threshold for DomainResult.romney_small_n_warning is n_models < 15, reconciled 2026-04-23
type: project
---

The binding threshold for `romney_small_n_warning` in `DomainResult` is **n_models < 15**, not n < 8.

**Why:** F2-T02 verdict (2026-04-20) stated n < 8; Phase 4a slate verdict (2026-04-22) Note A stated n < 15. The 2026-04-23 amendment reconciled to n < 15 because `SME_REVIEW.md` §1.1 grounds the Romney 5.0 operational threshold in the n=12 small-n regime (Anders & Batchelder 2015). n < 8 would silently bless n=8–14 as "not small-n," contradicting §1.1's own premise. RWB 1986 was calibrated at n=20–40; the CCT small-n cutoff is ~n<15.

**How to apply:** When reviewing any code or copy touching `romney_small_n_warning`, enforce n < 15. Citation in code/docs should attribute to "SME_REVIEW.md §1.1 small-n rationale + Anders & Batchelder 2015" — NOT a literal SME_REVIEW.md quote, since §1.1 doesn't contain the numeric n<15 explicitly (flagged as doc-hygiene follow-up). Phase 4a's n=10 (family) and n=8 (holidays) both trigger the flag.
