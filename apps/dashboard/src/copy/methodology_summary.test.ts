/**
 * Single-source-of-truth invariant test for taglineQuote.
 *
 * CDA SME carry-forward note 3 (binding):
 *   `taglineQuote === TAGLINE` must hold across all code changes.
 *   This test fails if someone hand-edits either string independently.
 *
 * Source: docs/status/2026-05-11-phase5-T13-cda-sme-verdict.md §5 note 3
 *         DESIGN_SYSTEM.md §12.7 (v0.4.4)
 */

import { it, expect } from "vitest";
import { TAGLINE } from "./framing";
import { taglineQuote } from "./methodology_summary";

it("taglineQuote is the same reference as the framing TAGLINE constant", () => {
  expect(taglineQuote).toBe(TAGLINE);
});
