# T5 — Reconcile dashboard TS types with published JSON shape — Architect plan (2026-06-08)

**Task:** T5 from `docs/status/2026-06-05-fresh-model-audit-pilot-findings.md` (F2+F3 = one task).
**Gate path:** Architect → Coder → Reviewer → Tester. **No CDA SME, no UI/UX** (see §4).

## 1. Bug + source-of-truth ruling
`DomainResultPublished` in `apps/dashboard/src/data/types.ts` declares shapes that
contradict the published JSON the dashboard loads. Consumers in `ContentArea.tsx` hide
the mismatch with 12 `as unknown as` casts. **The casts reflect reality; the types lie.**
FOUR independent sources agree on the correct (flat) shapes — only the TS type disagrees:
- `packages/cdb_core/cdb_core/schemas.py:404–407` (Pydantic write path — upstream SoT)
- `docs/DATA_DICTIONARY.md:237–240,250,256` (already CDA-SME-approved)
- `apps/dashboard/public/data/family.json` (runtime contract, verified — 15 models)
- → `types.ts` is the lone wrong node. Fix = conform TS to the published JSON, never the reverse.

## 2. Field corrections (`types.ts` `DomainResultPublished`)
| Field | Wrong (current) | Correct (published) |
|---|---|---|
| `mds_coordinates` | `Record<string,[[number,number]]>` | `Record<string,[number,number]>` (flat) |
| `similarity_matrix` | `Record<string,Record<string,number>>` | `number[][]` — JSDoc verbatim from DATA_DICTIONARY:239 "Model × model similarity, ordered by `models`." |
| `similarity_ci` | `Record<string,Record<string,[number,number]\|null>>` | `([number,number]\|null)[][]` — JSDoc from DATA_DICTIONARY:240 |
| `sutrop_csi` | `Record<string,Record<string,number>>` | `Record<string, SutropCsiEntry[]>` (SutropCsiEntry exists at types.ts:141) |
| `cultural_centrality_scores` | ABSENT from interface | ADD as required `Record<string,number>` |
| `similarity_matrix_array?` | phantom (ContentArea.tsx:39) | DELETE — absent from all published JSON |

Add exported `DomainExtended extends DomainResultPublished` to `types.ts` carrying the
genuinely-extra optional `term_*` + `centroid_piles` fields; DELETE the two inline local
`DomainExtended` copies (`App.tsx:19–41`, `ContentArea.tsx:25–47`) and import the shared one.
`centrality_ci?` already lives on `DomainResultPublished` (do not duplicate onto Extended).

## 3. Cast-removal inventory (`ContentArea.tsx`, 12 casts)
Lines 178, 181, 193, 196, 199, 207, 295, 296, 299, 300, 331, 341 — each becomes a plain
property access after the type fix (e.g. `domain.similarity_matrix`, `domain.sutrop_csi`,
`domain.cultural_centrality_scores`, `domain.display.top_terms`). After edits, `grep
"as unknown as" apps/dashboard/src/` must return NO matches for these field names.

**LATENT SUB-QUESTION the audit didn't enumerate — the `center` cast at line 296.** The
cast references an ellipse `center` field not on canonical `EllipseParams` (types.ts:72–78).
The Coder MUST grep the published JSON for `"center"` inside `mds_uncertainty` and either
(a) add `center: [number,number]` to `EllipseParams` if present, or (b) correct
`MDSPlot.tsx`'s prop type if absent. If this points to a separate latent bug, STOP and surface.

## 4. Gates — NO SME, NO UI/UX (both ruled no-op)
**UI/UX inapplicable:** pure type refactor, zero runtime value change (casts are
compile-time only), zero rendered-output change, zero copy/design-system surface — the four
UI/UX axes have nothing to assess. Guard: if `npm run build && npm run test` produces ANY
visual diff in `dist/`, STOP → route to UI/UX. **CDA SME inapplicable:** no measure added/
removed/re-semanticized, no threshold/ConsensusType, no `schemas.py` change (R7 not
triggered); the TS types are brought into line with shapes the SME already approved in
DATA_DICTIONARY. The one SME-adjacent point — `similarity_matrix` row/col indexing —
is handled by copying the dictionary's exact "ordered by `models`" phrasing into the JSDoc
(Reviewer gates the wording match). No novel methodological prose.

## 5. Critical risk + the "no fresh casts" contract
Removing a cast can surface a REAL downstream type error if a consumer relied on the wrong
(cast-asserted) shape. `npm run build` (tsc) is the gate. **If tsc errors after a cast
removal, the Coder must NOT re-add a cast to silence it** — either the corrected type is
right and a consumer is wrong (surface), or the published JSON has an unaccounted field
(surface with field name + JSON line). Paper-overs just relocate the lie.

## 6. Test plan
NEW `apps/dashboard/src/__tests__/DomainResultPublished.shape.test.ts`:
- Compile-time re-drift guard: `const _typeCheck: DomainExtended = familyData as DomainExtended;`
  (imports the real published JSON; tsc fails here if types ever re-drift).
- Runtime invariants tsc can't express: `mds_coordinates` flat [x,y]; `similarity_matrix`
  square 2-D matching `models.length`; `similarity_ci` dims match; `sutrop_csi` =
  model→entry[]; `cultural_centrality_scores` present. Iterate over family/holidays/food,
  skipping any that don't ship.
- Existing 31 tests must stay green (no edits expected; failure = stop-and-surface).
- `npm run build` + `npm run test` + `npm run lint` all green.

## 7. Acceptance criteria (abridged — see §10 of full plan)
Types match published JSON field-for-field; `cultural_centrality_scores` declared required;
`DomainExtended` exported once (grep-verified single definition); all 12 casts gone, no fresh
casts; phantom `similarity_matrix_array` gone everywhere; new shape test exercises all 3
domains; build+test+lint green; ZERO edits to `packages/` or `DATA_DICTIONARY.md`; zero
visual diff; one commit referencing this plan + Reviewer + Tester verdicts.

## 8. Affected files
- `apps/dashboard/src/data/types.ts` (corrected interface + exported DomainExtended)
- `apps/dashboard/src/components/ContentArea.tsx` (delete local interface, remove 12 casts)
- `apps/dashboard/src/App.tsx` (delete local interface, import shared)
- `apps/dashboard/src/__tests__/DomainResultPublished.shape.test.ts` (NEW)
- Reference only (DO NOT EDIT): `cdb_core/schemas.py:404–407`, `DATA_DICTIONARY.md:237–256`,
  `public/data/family.json`.

## 9. Follow-up candidate (P2, out of scope)
A CI grep against `interface DomainExtended` defined outside `data/types.ts` would prevent
inline-dup re-drift (analogous to T3-guard for pitfall #15). Flagged, not scheduled.

---

## OUTCOME — T5 DONE (`94bb189`)
Architect (this plan) → Coder → Reviewer **PASS** → Tester **PASS**. 12 casts removed,
duplicate `DomainExtended` unified to one exported type, `EllipseParams` corrected
(`center` added, phantom `ci_level` removed), +21 shape-conformance tests (31→52). build +
test + lint green; zero edits to `packages/` or `DATA_DICTIONARY.md`.

### Reviewer verdict — PASS
All 9 binding checks pass; 8 plan acceptance criteria pass. `tsc -b` passing IS the proof
every cast removal type-checks against the corrected types — no paper-over (`as unknown as`
appears ONLY in the test file's intentional compile-time guard; zero in production source).
JSDoc on `similarity_matrix`/`similarity_ci` matches DATA_DICTIONARY:239–240 verbatim.
`DomainExtended` defined exactly once (data/types.ts:289). **EllipseParams change verified
safe:** `center` is real (in all 3 published JSONs AND Pydantic `BootstrapEllipse`
schemas.py:23–32); `ci_level` was phantom (0 occurrences in data, schema, or any consumer).
R7 not triggered (no schemas.py / dictionary edit).

### Tester verdict — PASS
build ✓ / 52 tests / lint clean. **Revert-and-confirm-fail cycle on TWO fields:** reverting
`mds_coordinates`→nested and `similarity_matrix`→nested each made `npm run build` (tsc) FAIL
at the ContentArea consumer sites; `git checkout` restore → green. **Runtime-identical
structural verdict:** every ContentArea/App hunk is type-annotation / import / cast-token
removal with IDENTICAL property access + fallback — no conditional, ordering, arithmetic, or
prop-binding change; provably behavior-preserving. Coverage complete (7 invariants × 3
domains). Tree clean.

### CI nuance to carry forward (Tester finding)
The shape test's compile-time re-drift guard (`const _typeCheck: DomainExtended =
familyData`) only fires under `npm run build` (tsc -b), NOT `npm run test` (vitest transforms
via esbuild, which skips type-checking). The runtime `it()` assertions are an independent
second layer that catches actual data-shape deviation. **Implication:** CI must run
`npm run build` for the type↔data re-drift guard to be effective — confirm the dashboard CI
job does (it builds for deploy, so this is expected, but worth an explicit check if the
re-drift guard is to be relied on).

### Follow-up candidates surfaced (P2, out of scope, for the audit backlog)
- **T5-guard:** CI grep against `interface DomainExtended` defined outside `data/types.ts`
  (prevents inline-dup re-drift; analogous to T3-guard). Plan §9.
- **MDSPlot inline-type unification:** `MDSPlot.tsx` keeps its own inline uncertainty prop
  type (pre-existing coupling, not introduced by T5). Could fold into the shared
  `EllipseParams` now that it carries `center`. Reviewer-flagged.
