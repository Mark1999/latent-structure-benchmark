/**
 * DomainResultPublished shape test — T5 re-drift guard.
 *
 * Two-layer check:
 *   1. Compile-time: `const _typeCheck: DomainExtended = data as DomainExtended`
 *      fails if the TypeScript interface ever re-drifts from the published JSON.
 *   2. Runtime invariants: assertions that tsc cannot express (e.g. square matrix,
 *      flat [x,y] coordinates, sutrop_csi list-of-objects, etc.).
 *
 * Reference: docs/status/2026-06-08-T5-architect-plan.md §6.
 * CLAUDE.md §6 rule 9: no real API calls — all data is the static published artifact.
 */

import type { DomainExtended } from '../data/types';
import familyData from '../../public/data/family.json';
import holidaysData from '../../public/data/holidays.json';
import foodData from '../../public/data/food.json';

// ── Compile-time re-drift guard ────────────────────────────────────────────
// If DomainExtended ever re-drifts from the published JSON shape, tsc will
// flag one of these assignments during `npm run test` (typecheck phase).
const _familyCheck: DomainExtended = familyData as unknown as DomainExtended;
const _holidaysCheck: DomainExtended = holidaysData as unknown as DomainExtended;
const _foodCheck: DomainExtended = foodData as unknown as DomainExtended;

// Suppress "declared but never read" for the compile-time checks.
void _familyCheck; void _holidaysCheck; void _foodCheck;

// ── Helpers ────────────────────────────────────────────────────────────────

type RawDomain = typeof familyData;

/** Domains present on disk — all three must ship for the full guard to fire. */
const DOMAINS: Array<{ slug: string; data: RawDomain }> = [
  { slug: 'family',   data: familyData },
  { slug: 'holidays', data: holidaysData },
  { slug: 'food',     data: foodData },
];

// ── Runtime invariant tests ────────────────────────────────────────────────

describe('DomainResultPublished published-JSON shape invariants', () => {
  for (const { slug, data } of DOMAINS) {
    describe(`domain: ${slug}`, () => {

      it('models is a non-empty array', () => {
        expect(Array.isArray(data.models)).toBe(true);
        expect(data.models.length).toBeGreaterThan(0);
      });

      it('mds_coordinates: flat [x, y] pairs (not wrapped in outer array)', () => {
        const coords = data.mds_coordinates as Record<string, unknown>;
        expect(typeof coords).toBe('object');
        const entries = Object.entries(coords);
        expect(entries.length).toBeGreaterThan(0);
        for (const [modelId, coord] of entries) {
          expect(Array.isArray(coord), `${modelId}: coord is array`).toBe(true);
          const pair = coord as unknown[];
          // Flat [x, y]: exactly 2 numeric elements, neither of which is itself an array
          expect(pair.length).toBe(2);
          expect(typeof pair[0], `${modelId}: coord[0] is number`).toBe('number');
          expect(typeof pair[1], `${modelId}: coord[1] is number`).toBe('number');
          // Guard against the OLD shape [[x, y]] — outer length would still be 1
          expect(Array.isArray(pair[0]), `${modelId}: coord[0] must not be a nested array`).toBe(false);
        }
      });

      it('mds_uncertainty: entries have center field (EllipseParams)', () => {
        const uncertainty = data.mds_uncertainty as Record<string, Record<string, unknown> | null>;
        for (const [modelId, entry] of Object.entries(uncertainty)) {
          if (entry === null) continue; // R1-b / R1-c: null is valid
          expect(Array.isArray(entry.center), `${modelId}: center is array`).toBe(true);
          const c = entry.center as unknown[];
          expect(c.length).toBe(2);
          expect(typeof c[0]).toBe('number');
          expect(typeof c[1]).toBe('number');
          expect(typeof entry.semi_major).toBe('number');
          expect(typeof entry.semi_minor).toBe('number');
          expect(typeof entry.rotation_rad).toBe('number');
          expect(typeof entry.n_bootstrap).toBe('number');
          // ci_level was a phantom field — must NOT be present
          expect('ci_level' in entry).toBe(false);
        }
      });

      it('similarity_matrix: square 2-D array, dims keyed by similarity_model_ids or models', () => {
        const sm = data.similarity_matrix as unknown[][];
        expect(Array.isArray(sm)).toBe(true);
        // New invariant: when similarity_model_ids is present and non-empty,
        // dims must equal similarity_model_ids.length (not models.length).
        // Legacy invariant: when absent/empty, dims must equal models.length.
        const simModelIds = (data as Record<string, unknown>).similarity_model_ids as string[] | undefined;
        if (simModelIds && simModelIds.length > 0) {
          const nb = simModelIds.length;
          expect(sm.length, `similarity_matrix.length == similarity_model_ids.length`).toBe(nb);
          for (let i = 0; i < nb; i++) {
            expect(Array.isArray(sm[i]), `row ${i} is array`).toBe(true);
            expect((sm[i] as unknown[]).length, `row ${i} length == ${nb}`).toBe(nb);
            expect(typeof (sm[i] as unknown[])[0], `row ${i} col 0 is number`).toBe('number');
          }
          // similarity_model_ids must be a subset of models[].model_id
          const modelIdSet = new Set(data.models.map((m: { model_id: string }) => m.model_id));
          for (const mid of simModelIds) {
            expect(modelIdSet.has(mid), `${mid} in similarity_model_ids is in models`).toBe(true);
          }
          // no duplicate model ids
          expect(new Set(simModelIds).size, 'similarity_model_ids has no duplicates').toBe(simModelIds.length);
        } else {
          // Legacy branch: family and holidays (pre-FOOD-V02-FIX-SIMIDS)
          const n = data.models.length;
          expect(sm.length).toBe(n);
          for (let i = 0; i < n; i++) {
            expect(Array.isArray(sm[i]), `row ${i} is array`).toBe(true);
            expect((sm[i] as unknown[]).length, `row ${i} length == ${n}`).toBe(n);
            expect(typeof (sm[i] as unknown[])[0], `row ${i} col 0 is number`).toBe('number');
          }
        }
      });

      it('similarity_ci: 2-D array with same dims as similarity_matrix', () => {
        const sm = data.similarity_matrix as unknown[][];
        const sc = data.similarity_ci as unknown[][];
        expect(Array.isArray(sc)).toBe(true);
        const nb = sm.length;
        expect(sc.length, `similarity_ci.length == similarity_matrix.length`).toBe(nb);
        for (let i = 0; i < nb; i++) {
          expect(Array.isArray(sc[i]), `row ${i} is array`).toBe(true);
          const row = sc[i] as unknown[];
          expect(row.length, `row ${i} length == ${nb}`).toBe(nb);
          // Each cell is either null or a [lo, hi] pair
          for (let j = 0; j < nb; j++) {
            const cell = row[j];
            if (cell === null) continue;
            expect(Array.isArray(cell), `[${i}][${j}] is array or null`).toBe(true);
            const pair = cell as unknown[];
            expect(pair.length).toBe(2);
            expect(typeof pair[0]).toBe('number');
            expect(typeof pair[1]).toBe('number');
          }
        }
      });

      it('similarity_model_ids: no duplicates when present', () => {
        const simModelIds = (data as Record<string, unknown>).similarity_model_ids as string[] | undefined;
        if (simModelIds && simModelIds.length > 0) {
          expect(new Set(simModelIds).size, 'no duplicate model ids in similarity_model_ids').toBe(simModelIds.length);
        }
      });

      it('sutrop_csi: model_id → SutropCsiEntry[] (list of objects, not nested dict)', () => {
        const csi = data.sutrop_csi as Record<string, unknown>;
        expect(typeof csi).toBe('object');
        const entries = Object.entries(csi);
        expect(entries.length).toBeGreaterThan(0);
        for (const [modelId, value] of entries) {
          expect(Array.isArray(value), `${modelId}: sutrop_csi value is array`).toBe(true);
          const list = value as Array<Record<string, unknown>>;
          if (list.length > 0) {
            const first = list[0];
            expect(typeof first.item, `${modelId}[0].item is string`).toBe('string');
            expect(typeof first.csi, `${modelId}[0].csi is number`).toBe('number');
          }
        }
      });

      it('cultural_centrality_scores: present and is model_id → number dict', () => {
        const ccs = data.cultural_centrality_scores as Record<string, unknown> | undefined;
        expect(ccs).toBeDefined();
        expect(typeof ccs).toBe('object');
        const entries = Object.entries(ccs!);
        expect(entries.length).toBeGreaterThan(0);
        for (const [modelId, score] of entries) {
          expect(typeof score, `${modelId}: score is number`).toBe('number');
        }
      });

    });
  }
});
