---
filed: 2026-05-15
reviewer: Tester agent (Sonnet)
task: Phase 6 T13 — add `food` as third domain (sub-option B)
coder_commit: bfa62a2
reviewer_verdict: docs/status/2026-05-15-phase6-T13-reviewer-verdict.md (PASS)
test_file_written: apps/dashboard/src/__tests__/phase6-t13-food-domain.test.ts
verdict: PASS
---

# Phase 6 T13 — Tester verdict

**TESTER VERDICT: PASS**

---

## Test suite results

| Suite | Command | Before | After | Delta |
|---|---|---|---|---|
| Dashboard tests | `npm run test` | 1497 passed | 1557 passed | +60 |
| Dashboard lint | `npm run lint` | 1 warning (Header.tsx pre-existing) | 1 warning (same) | 0 |
| Dashboard build | `npm run build` | 301.33 kB JS / 89.70 kB gzipped | 301.33 kB JS / 89.70 kB gzipped | 0 |

The pre-existing `Header.tsx` ESLint warning (`react-refresh/only-export-components`)
is unchanged from pre-T13. Zero new warnings, zero errors.

---

## Audit of Coder's AC21/AC22 tests

### AC21 — app-state.test.ts (1 test added at line 252)

Test: "manifest with food, family, and holidays produces 3 available pills and at
least 2 unavailable pills (AC21)"

Audit findings:
- The test correctly replicates `buildDomainList()` logic from App.tsx.
- `availableDomains.toHaveLength(3)` and `unavailableDomains` checks: correct.
- Food dedup from `FUTURE_DOMAINS`: asserted correctly.
- Emotion and justice remain unavailable: asserted correctly.
- No off-by-one error, no hardcoded N=2 remnant.
- **PASS — no issues found.**

### AC22 — domain-picker.test.tsx (5 tests added in describe block at line 329)

Tests:
1. "renders exactly 3 pills when all three domains are available" — correct
2. "food pill is available (aria-disabled is not 'true') when all three are active" — correct
3. "clicking the food pill calls onSelect('food') when food is available" — correct
4. "ArrowRight from pill 2 (index 2) wraps to pill 0 — 3-pill cycle (AC22)" — VERIFIED:
   The math comment in the test says `(2 + 1 + 3) % 3 = 0`. This is correct.
   The UI/UX verdict confirms `(currentIndex + direction + total) % total` with total=3
   produces the right wrap-around. No off-by-one.
5. "ArrowRight cycles through all 3 pills: 0→1→2→0 wrap-around (AC22 full cycle)" — correct.
   Sequential steps 0→1→2→0 each asserted individually.

No hardcoded N=2 found anywhere in the 5 new tests.
**PASS — no issues found.**

---

## Gap-fill test file written

`apps/dashboard/src/__tests__/phase6-t13-food-domain.test.ts`

Note: the filename `t13-gap-fill.test.ts` was already occupied by a Phase 5 T13
gap-fill file (unrelated CSS/MDSPlot checks from 2026-05-11). This file uses the
unambiguous phase-scoped name `phase6-t13-food-domain.test.ts`.

### Coverage items (G1–G29, 60 tests)

**A. food.yaml content (AC1) — G1, G2 — 8 tests**
- G1: food.yaml has exactly 5 keys, no `description` field
- G2: byte-exact values for all 5 fields (slug, version, display_name,
  prompt_seed="type of food or dish", truncation_k=50)

**B. food.json shape (AC5, AC10, AC11) — G3–G9 — 18 tests**
- G3: top-level required fields present (9 assertions: domain_slug, consensus_type,
  consensus_score, consensus_ci, models, romney_small_n_warning=true, generated_lede)
- G4: generated_lede byte-exact matches AC10 binding text
- G5: generated_lede does NOT contain "signalling" (British) — M1 regression guard
- G6: models array length is 8
- G7: model_ids set is the expected 8-model set; grok-4.20 explicitly absent
- G8: generated_lede says "8 frontier models" (not 9)
- G9: generated_lede free of §7 forbidden vocabulary (regex scan)

**C. holidays.json regression (AC12 — M1 cascade) — G10–G12 — 3 tests**
- G10: holidays.json generated_lede uses "signaling" not "signalling"
- G11: holidays.json models array length unchanged at 9
- G12: holidays.json consensus_type unchanged (STRONG_CONSENSUS)

**D. family.json non-regression (AC12) — G13–G14 — 2 tests**
- G13: family.json generated_lede does NOT contain "signaling" OR "signalling"
  (uses strong_consensus_homogeneous pattern — unaffected by M1)
- G14: family.json models array length unchanged at 11

**E. manifest.json shape (AC5) — G15–G17 — 4 tests**
- G15: domains array length is 3
- G16: domain slugs set equals {family, holidays, food}
- G17: failures map has entries for all three domains

**F. failures/food.json (AC5) — G18–G19 — 5 tests**
- G18: domain_slug=food, n_records=0, records=[]
- G19: framing_note matches holidays domain; contains §1.5-compliant language
  (pipeline attribution phrasing)

**G. lede_v1.py M1 fix (regression guard) — G20 — 3 tests**
- G20: lede_v1.py exists; contains "signaling" (US); does NOT contain "signalling"

**H. data/raw/informants.jsonl invariants (AC2, AC3, AC19) — G21–G24 — 5 tests**
- G21: exactly 45 records with domain_slug="food"
- G22: 5 grok-4.20 food records all have qa_passed=False
- G23: all 45 food records reference T13 campaign_id in qa_notes
- G24: all 45 food records have non-empty model_version_returned (pitfall #1)

**I. data/results/food/0.2.json shape (AC4) — G25 — 4 tests**
- G25: top-level keys match family/0.2.json exactly; domain_slug=food; analysis_version=0.2

**J. scripts/run_phase6_t13_food.py (AC18) — G26–G27 — 7 tests**
- G26: driver scopes to "food"; FOOD_DOMAINS does not include family or holidays
- G27: no CDB_MAX_SPEND_USD, MAX_SPEND_USD, cost_cap, or cost_limit (CLAUDE.md R14)

**K. CDA SME / AC10 documentation invariants — G28–G29 — 4 tests**
- G28: AC10 verdict file exists and contains "PASS-WITH-NOTES"
- G29: AC10 verdict file contains the binding verbatim post-fix lede text

---

## Skip-with-message posture for gitignored artifacts

Tests for `apps/dashboard/public/data/*.json` files (G3–G19) follow the
`readIfExists()` pattern: if the file is absent (CI without a prior publish run),
the test body returns early after logging a SKIP warning rather than failing.
On this VPS where `cdb_publish/build.py` has run, all gitignored artifacts exist
and all 60 tests run and pass without any skips.

---

## Coverage gaps

None. All 29 canonical gap-fill items from the task specification are covered.
The Coder's AC21/AC22 tests are correct and were not duplicated.

---

## Concerns for Mark

None. The food domain shipped cleanly at n=8 (grok-4.20 excluded by qa_check,
5 records preserved in informants.jsonl per pitfall #10). The methodology-page
carry-forwards (F1, F2, F3 from the AC10 verdict) are routed to T14 per the
CDA SME verdict and do not gate T13.

The one test that required a fix during gap-fill was G19's framing_note check:
the standard framing says "not a claim about the model's intent or state-of-mind"
(a negation, which is §1.5-compliant). The initial assertion used `.not.toContain("model's intent")`
which correctly failed because the phrase appears in its proper negated form.
Corrected to assert the full negated phrase is present.

---

*End of Tester verdict for Phase 6 T13. Filed: 2026-05-15.*
