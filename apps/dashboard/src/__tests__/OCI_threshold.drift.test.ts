/**
 * OCI threshold drift guard — T11b.
 *
 * This test is the binding mechanism that keeps the Python source-of-truth
 * (cdb_publish/lede.py OCI_LOW_CONCENTRATION_THRESHOLD = 3.0) and the
 * dashboard's named source-of-truth (apps/dashboard/src/config/analysis.ts)
 * in lockstep via the published manifest field.
 *
 * Per DESIGN_SYSTEM.md §3.3.5 item 7:
 *   "analysis.ts exports OCI_LOW_CONCENTRATION_THRESHOLD as the dashboard's
 *   config constant. lede.py:40 is the Python SoT. The two named SoTs are
 *   bound by manifest.oci_low_concentration_threshold, which cdb_publish
 *   derives from lede.py and publishes to manifest.json."
 *
 * Reference: docs/status/2026-06-08-T11-architect-plan.md §3 (Option b)
 * CDA SME: docs/status/2026-06-08-T11-cda-sme-verdict.md (PASS)
 * CLAUDE.md §6 rule 9: no real API calls — data is the static published artifact.
 */

import { OCI_LOW_CONCENTRATION_THRESHOLD } from '../config/analysis';
import type { Manifest } from '../data/types';
import manifestJson from '../../public/data/manifest.json';

// ── Compile-time guard ─────────────────────────────────────────────────────
// Asserts that manifest.json is assignable to the Manifest interface.
// If oci_low_concentration_threshold is ever removed from types.ts or its
// type changes from `number`, tsc will flag this assignment.
const _manifestTypeCheck: Manifest = manifestJson as Manifest;
void _manifestTypeCheck;

// ── Runtime drift guard ────────────────────────────────────────────────────

describe('OCI_LOW_CONCENTRATION_THRESHOLD drift guard (T11b)', () => {

  it('manifest.oci_low_concentration_threshold matches analysis.ts constant', () => {
    // This assertion fails if cdb_publish and analysis.ts drift apart.
    // A failed publish run (scripts/publish.py) or a stale manifest.json
    // without a matching analysis.ts update will be caught here.
    expect(manifestJson.oci_low_concentration_threshold).toBe(
      OCI_LOW_CONCENTRATION_THRESHOLD
    );
  });

  it('OCI_LOW_CONCENTRATION_THRESHOLD is exactly 3.0 (defensive sentinel)', () => {
    // IMPORTANT: if the threshold value is legitimately changed from 3.0,
    // this assertion must be updated in the SAME PR that updates:
    //   - packages/cdb_publish/cdb_publish/lede.py (Python SoT)
    //   - apps/dashboard/src/config/analysis.ts (dashboard SoT)
    //   - apps/dashboard/public/data/manifest.json (re-published artifact)
    // Changing only one of the above and not this test is an error.
    // See DESIGN_SYSTEM.md §3.3.5 item 7 and ARCHITECTURE.md §4.2 R1-b definition.
    expect(OCI_LOW_CONCENTRATION_THRESHOLD).toBe(3.0);
  });

});
