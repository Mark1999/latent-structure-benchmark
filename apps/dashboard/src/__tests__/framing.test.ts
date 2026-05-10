/**
 * Tests for copy/framing.ts canonical constants.
 *
 * AC3, AC9: No real fetch. No forbidden vocabulary.
 * Source: DESIGN_SYSTEM.md §0, ARCHITECTURE.md §1.5, CLAUDE.md §7
 */

import { describe, it, expect } from "vitest";
import {
  TAGLINE,
  TAGLINE_LONG,
  CORPUS_LENS_TERM,
  SITE_NAME,
  SITE_URL,
  GITHUB_URL,
} from "../copy/framing";

describe("framing constants", () => {
  describe("TAGLINE", () => {
    it("is a non-empty string", () => {
      expect(typeof TAGLINE).toBe("string");
      expect(TAGLINE.length).toBeGreaterThan(0);
    });

    it("contains the canonical 'categorize' verb (US English, per CDA SME Q8 binding)", () => {
      // CDA SME plan-level binding: US English "categorize", not "categorise"
      expect(TAGLINE).toContain("categorize");
      expect(TAGLINE).not.toContain("categorise");
    });

    it("contains 'reproducible' — a key commitment of LSB", () => {
      expect(TAGLINE).toContain("reproducible");
    });

    it("contains 'comparable across models'", () => {
      expect(TAGLINE).toContain("comparable across models");
    });

    it("contains 'trackable across time'", () => {
      expect(TAGLINE).toContain("trackable across time");
    });

    it("begins with 'LSB measures'", () => {
      expect(TAGLINE.startsWith("LSB measures")).toBe(true);
    });
  });

  describe("TAGLINE — forbidden vocabulary (CLAUDE.md §7 / ARCHITECTURE.md §1.5.4)", () => {
    const forbiddenPatterns = [
      /\bbelieves\b/i,
      /\bthinks?\b/i,
      /\bworldview\b/i,
      /\bcultural bias\b/i,
      /\bwhat the model understands?\b/i,
      /\bhow models see the world\b/i,
      /\bmodel.{0,20}worldview\b/i,
    ];

    for (const pattern of forbiddenPatterns) {
      it(`does not contain forbidden pattern: ${pattern}`, () => {
        expect(TAGLINE).not.toMatch(pattern);
      });
    }
  });

  describe("TAGLINE_LONG", () => {
    it("is a non-empty string", () => {
      expect(typeof TAGLINE_LONG).toBe("string");
      expect(TAGLINE_LONG.length).toBeGreaterThan(0);
    });

    it("does not contain forbidden vocabulary", () => {
      const forbiddenPatterns = [
        /\bbelieves\b/i,
        /\bworldview\b/i,
        /\bcultural bias\b/i,
      ];
      for (const pattern of forbiddenPatterns) {
        expect(TAGLINE_LONG).not.toMatch(pattern);
      }
    });

    it("contains 'corpus lens' — the plain-language term (ARCHITECTURE.md §1.5.1)", () => {
      expect(TAGLINE_LONG.toLowerCase()).toContain("corpus lens");
    });
  });

  describe("CORPUS_LENS_TERM", () => {
    it("equals 'corpus lens'", () => {
      expect(CORPUS_LENS_TERM).toBe("corpus lens");
    });
  });

  describe("SITE_NAME", () => {
    it("is 'Cognitive Structure Lab'", () => {
      expect(SITE_NAME).toBe("Cognitive Structure Lab");
    });
  });

  describe("SITE_URL", () => {
    it("points to cogstructurelab.com", () => {
      expect(SITE_URL).toContain("cogstructurelab.com");
    });
  });

  describe("GITHUB_URL", () => {
    it("points to a GitHub URL", () => {
      expect(GITHUB_URL).toContain("github.com");
    });
  });
});
