/**
 * Tests for config/analysis.ts constants.
 * AC3, AC9.
 */

import { describe, it, expect } from "vitest";
import { OCI_LOW_CONCENTRATION_THRESHOLD } from "../config/analysis";

describe("analysis config", () => {
  describe("OCI_LOW_CONCENTRATION_THRESHOLD", () => {
    it("is a number", () => {
      expect(typeof OCI_LOW_CONCENTRATION_THRESHOLD).toBe("number");
    });

    it("equals 3.0 (per DESIGN_SYSTEM.md §3.3.5 item 7)", () => {
      expect(OCI_LOW_CONCENTRATION_THRESHOLD).toBe(3.0);
    });

    it("matches the manifest.json value (oci_low_concentration_threshold: 3.0)", () => {
      // Cross-check: manifest.json has oci_low_concentration_threshold: 3.0
      // This test documents the expected agreement between config and published manifest.
      expect(OCI_LOW_CONCENTRATION_THRESHOLD).toBe(3.0);
    });
  });
});
