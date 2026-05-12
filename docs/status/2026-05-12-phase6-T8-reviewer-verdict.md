---
filed: 2026-05-12
reviewer: LSB Reviewer agent (Sonnet)
task: Phase 6 T8 — Read-as-table toggle + ScreenReaderSummary
commit: 2894647
verdict: FAIL
---

# Phase 6 T8 — Reviewer verdict

**REVIEWER VERDICT: FAIL**

```
Check 1 — No LLM imports:            PASS
Check 2 — Append-only JSONL:         PASS
Check 3 — No secrets:                PASS
Check 4 — Forbidden vocabulary:      PASS
Check 5 — Schema + DATA_DICTIONARY:  N/A
Check 6 — New deps sign-off:         N/A
Check 7 — Prompt versioning:         N/A
Check 8 — Uncertainty in viz:        PASS
Check 9 — Prerequisite verdicts:     PASS
```

**Targeted check results:**

| Sub-check | Result |
|---|---|
| S11: no `generated_lede` in `screen_reader_summaries.ts` | PASS — grep returns 0 functional matches (only comments referencing the rule) |
| CDA SME binding template wording (MDS/FreeList/Similarity) | PASS |
| Table captions verbatim (S6, S5, S7) | PASS — all three captions byte-identical to CDA SME §4.1/§4.2/§4.3 |
| S1 enum mapping — 5 consensus types | PASS |
| S8 empty-state strings | PASS |
| S9 column headers | PASS |
| S10 sentence ceiling | PASS |
| Button labels (S4) | PASS |
| U1 Option A — always-present table container | PASS — all three viz components |
| U2 pressed-state border | PASS — `border: 2px solid var(--color-info)` with transparent rest-state |
| `--color-info` used for U2 (not hardcoded) | PASS |
| DESIGN_SYSTEM.md v0.4.6 update | PASS — version header, changelog, §7, §12.6 closure, §12.9, footer |
| S7 T14 advisory in commit body | PASS |
| `data/types.ts` not touched | PASS |
| No new package.json / pyproject.toml deps | PASS |
| MethodologySummary / ModelSelector / Legend / FailuresFindingsSection not touched | PASS |
| T5 test modification justification | PASS — the `visibleTextContent()` helper correctly narrows the "no bootstrap prose" check to non-`aria-hidden` content; justified because `SIMILARITY_TABLE_CAPTION` and `MDS_TABLE_CAPTION` both contain "bootstrap" and are always in the DOM (U1 Option A) |
| Tests: 1138/1138 | PASS |
| Lint: 0 errors | PASS |
| Build: clean | PASS — 88.57 KB gzip JS (+3.35 KB vs ~85.22 KB pre-T8), under 8 KB ceiling |
| R10 in tabular form — point estimates adjacent to CI/uncertainty | PASS (MdsTable, FreeListTable, SimilarityTable all verified) |
| No forbidden vocabulary in any new file | PASS |
| `agree` in Similarity surfaces | PASS — only appears in MDS mapConsensusType (WEAK_CONSENSUS phrase) and `agreement matrix` in MDS SR template; not in Similarity SR template, Similarity caption, or Similarity column headers |

---

## Failure

### F1 — `--color-text-secondary` used at `--font-size-xs` (12px) regular weight in `read-as-table.css`

**Check 13 — Design-system tokens**

The Reviewer instruction is explicit: "Verify `--color-text-caption` for 12px regular weight; never `--color-text-secondary` at body sizes."

DESIGN_SYSTEM.md v0.4.3 (binding, §1.2 changelog) documents why: `--color-text-secondary` (#7f8c8d) is approximately 3.40:1 on white, which fails WCAG AA for 12px regular-weight text (4.5:1 required). The correct token for 12px regular-weight text is `--color-text-caption` (#6c757d, ~4.60:1, WCAG AA compliant).

**Affected lines in `/opt/lsb-agent/apps/dashboard/src/styles/read-as-table.css`:**

- **Line 144:** `.read-as-table__td--mono { color: var(--color-text-secondary); }` at `font-size: var(--font-size-xs)` (12px regular). This class styles the `model_id` column cells in `MdsTable`. The text is readable content (not decorative), displayed at 12px regular weight. WCAG AA requires 4.5:1 at this size and weight; `--color-text-secondary` provides only ~3.40:1. **Fix: change to `var(--color-text-caption)`.**

- **Line 193:** `.read-as-table__shared-star { color: var(--color-text-secondary); }` at `font-size: var(--font-size-xs)` (12px regular). This styles the `★` shared-term glyph which has `aria-hidden="true"` in the DOM (decorative). WCAG 1.4.3 has an exception for decorative text, so this specific instance may be exempt from the contrast rule. However, the DESIGN_SYSTEM.md token guidance is a blanket rule ("use `--color-text-caption` for 12px regular") that applies beyond WCAG compliance. The shared-star token should be corrected for consistency. **Fix: change to `var(--color-text-caption)`.** (This is binding per DESIGN_SYSTEM.md even if the WCAG exception applies.)

The UI/UX plan-level verdict listed `--color-text-caption` and `--color-text-primary` as the T8 text tokens. The Coder introduced `--color-text-secondary` at 12px in the implementation, which was not in the plan's token audit. The Reviewer enforces token discipline independent of whether the UI/UX plan-review caught the deviation.

---

## Required before merge

1. In `/opt/lsb-agent/apps/dashboard/src/styles/read-as-table.css`:
   - Line 144: `.read-as-table__td--mono` — change `color: var(--color-text-secondary)` to `color: var(--color-text-caption)`
   - Line 193: `.read-as-table__shared-star` — change `color: var(--color-text-secondary)` to `color: var(--color-text-caption)`
2. Re-run `npm run test && npm run lint && npm run build` to confirm no regressions.
3. Submit for re-review.

No CDA SME re-review is required (the failure is CSS token selection only). No UI/UX re-review is required (both tokens exist in the plan's approved set; this is a selection error within the already-approved token palette, not a new visual decision).

---

## Notes on S11 (most critical check)

**PASS.** `grep "generated_lede" /opt/lsb-agent/apps/dashboard/src/copy/screen_reader_summaries.ts` returns only comment lines documenting the rule (lines 14-15, 123, 172, 241) — zero functional uses. `mdsScreenReaderSummary`, `freeListScreenReaderSummary`, and `similarityScreenReaderSummary` do not access `domainResult.generated_lede`. The CDA SME S11 lede-boundary is preserved.

---

*LSB Reviewer agent (Sonnet), 2026-05-12. Only Mark can override a FAIL.*

---

## Re-review: PASS (post-fix) — 2026-05-12

**Fix commit:** e801a76

**Verification:**

- Line 144 `.read-as-table__td--mono`: now `color: var(--color-text-caption)` — confirmed.
- Line 193 `.read-as-table__shared-star`: now `color: var(--color-text-caption)` — confirmed.
- Broader scan of T8 style and component files for `--color-text-secondary` + `font-size-xs` co-occurrence: two grep hits found, both non-issues — `tokens.css:110` is the token definition line (comment explicitly warns against 12px regular use), `DownloadBar.tsx:91` is a code comment documenting why the token is NOT used there. No live style rule violation.
- `npm run test`: 1138/1138 passed (34 test files).
- `npm run lint`: 0 errors.
- `npm run build`: clean — 88.57 KB JS gzip, 5.25 KB CSS gzip. No regression from pre-fix build numbers.
- All nine binding checks remain PASS or N/A as recorded in the original verdict above.

**REVIEWER VERDICT: PASS**

F1 resolved. No regressions. T8 may merge.

*LSB Reviewer agent (Sonnet), 2026-05-12 re-review.*
