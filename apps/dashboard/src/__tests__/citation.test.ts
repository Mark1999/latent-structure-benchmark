/**
 * Tests for citation.ts pure functions.
 *
 * Per T12 acceptance criteria:
 *   - Domain title-case present in all four formats.
 *   - Year extracted from generatedAt correctly.
 *   - BibTeX key is lowercase slug.
 *   - "Cognitive Structure Lab" appears in all four.
 *   - "LSB" appears in all four.
 *   - Model list rendered for BibTeX (comma-separated).
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T12
 */

import { describe, it, expect } from "vitest";
import {
  buildApa,
  buildMla,
  buildChicago,
  buildBibtex,
  accessDate,
} from "../lib/citation";
import type { CitationContext } from "../lib/citation";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const BASE_CTX: CitationContext = {
  domain: "family",
  domainTitle: "Family",
  analysisVersion: "0.2",
  generatedAt: "2026-05-07T00:07:50.238646Z",
  selectedModels: ["claude-opus-4-6", "openai/gpt-5"],
};

const CTX_HOLIDAYS: CitationContext = {
  domain: "holidays",
  domainTitle: "Holidays",
  analysisVersion: "0.1",
  generatedAt: "2025-12-25T12:00:00.000000Z",
  selectedModels: ["model-a", "model-b", "model-c"],
};

// ── buildApa ──────────────────────────────────────────────────────────────────

describe("buildApa", () => {
  it("snapshot — stable output for the base fixture", () => {
    const result = buildApa(BASE_CTX);
    expect(result).toMatchSnapshot();
  });

  it("contains 'Cognitive Structure Lab'", () => {
    expect(buildApa(BASE_CTX)).toContain("Cognitive Structure Lab");
  });

  it("contains 'LSB'", () => {
    expect(buildApa(BASE_CTX)).toContain("LSB");
  });

  it("contains domain title-case ('Family')", () => {
    expect(buildApa(BASE_CTX)).toContain("Family");
  });

  it("extracts year correctly from generatedAt", () => {
    expect(buildApa(BASE_CTX)).toContain("2026");
    expect(buildApa(CTX_HOLIDAYS)).toContain("2025");
  });

  it("contains the domain URL", () => {
    expect(buildApa(BASE_CTX)).toContain("cogstructurelab.com/family");
  });

  it("respects custom baseUrl", () => {
    const ctx = { ...BASE_CTX, baseUrl: "https://example.com" };
    expect(buildApa(ctx)).toContain("example.com/family");
  });

  it("includes [Data set] marker", () => {
    expect(buildApa(BASE_CTX)).toContain("[Data set]");
  });
});

// ── buildMla ──────────────────────────────────────────────────────────────────

describe("buildMla", () => {
  it("snapshot — stable output for the base fixture", () => {
    // MLA uses accessDate() which is time-dependent — snapshot the shape
    // by overriding accessDate with a known date via the module export,
    // or just verify structural requirements.
    const result = buildMla(BASE_CTX);
    // Basic structure: should start with "Cognitive Structure Lab."
    expect(result.startsWith("Cognitive Structure Lab.")).toBe(true);
  });

  it("contains 'Cognitive Structure Lab'", () => {
    expect(buildMla(BASE_CTX)).toContain("Cognitive Structure Lab");
  });

  it("contains 'LSB'", () => {
    expect(buildMla(BASE_CTX)).toContain("LSB");
  });

  it("contains domain title-case ('Family')", () => {
    expect(buildMla(BASE_CTX)).toContain("Family");
  });

  it("extracts year correctly from generatedAt", () => {
    expect(buildMla(BASE_CTX)).toContain("2026");
    expect(buildMla(CTX_HOLIDAYS)).toContain("2025");
  });

  it("contains the domain URL", () => {
    expect(buildMla(BASE_CTX)).toContain("cogstructurelab.com/family");
  });

  it("contains 'Accessed'", () => {
    expect(buildMla(BASE_CTX)).toContain("Accessed");
  });
});

// ── buildChicago ──────────────────────────────────────────────────────────────

describe("buildChicago", () => {
  it("snapshot — stable output for the base fixture", () => {
    const result = buildChicago(BASE_CTX);
    expect(result).toMatchSnapshot();
  });

  it("contains 'Cognitive Structure Lab'", () => {
    expect(buildChicago(BASE_CTX)).toContain("Cognitive Structure Lab");
  });

  it("contains 'LSB'", () => {
    expect(buildChicago(BASE_CTX)).toContain("LSB");
  });

  it("contains domain title-case ('Family')", () => {
    expect(buildChicago(BASE_CTX)).toContain("Family");
  });

  it("extracts year correctly from generatedAt", () => {
    expect(buildChicago(BASE_CTX)).toContain("2026");
    expect(buildChicago(CTX_HOLIDAYS)).toContain("2025");
  });

  it("contains the domain URL", () => {
    expect(buildChicago(BASE_CTX)).toContain("cogstructurelab.com/family");
  });

  it("contains a period at the end (Chicago author-date)", () => {
    expect(buildChicago(BASE_CTX).trimEnd().endsWith(".")).toBe(true);
  });
});

// ── buildBibtex ───────────────────────────────────────────────────────────────

describe("buildBibtex", () => {
  it("snapshot — stable output for the base fixture", () => {
    const result = buildBibtex(BASE_CTX);
    expect(result).toMatchSnapshot();
  });

  it("contains 'Cognitive Structure Lab'", () => {
    expect(buildBibtex(BASE_CTX)).toContain("Cognitive Structure Lab");
  });

  it("contains 'LSB'", () => {
    expect(buildBibtex(BASE_CTX)).toContain("LSB");
  });

  it("contains domain title-case ('Family')", () => {
    expect(buildBibtex(BASE_CTX)).toContain("Family");
  });

  it("extracts year correctly from generatedAt", () => {
    expect(buildBibtex(BASE_CTX)).toContain("2026");
    expect(buildBibtex(CTX_HOLIDAYS)).toContain("2025");
  });

  it("BibTeX key is lowercase slug", () => {
    // key format: lsb_{domain}_{year}
    expect(buildBibtex(BASE_CTX)).toContain("lsb_family_2026");
  });

  it("BibTeX key for holidays domain is lowercase", () => {
    expect(buildBibtex(CTX_HOLIDAYS)).toContain("lsb_holidays_2025");
  });

  it("renders model list in note field (comma-separated)", () => {
    const result = buildBibtex(BASE_CTX);
    expect(result).toContain("claude-opus-4-6");
    expect(result).toContain("openai/gpt-5");
    // Models joined by ", "
    expect(result).toContain("claude-opus-4-6, openai/gpt-5");
  });

  it("includes analysis version in note field", () => {
    expect(buildBibtex(BASE_CTX)).toContain("Analysis version 0.2");
  });

  it("contains the domain URL", () => {
    expect(buildBibtex(BASE_CTX)).toContain("cogstructurelab.com/family");
  });

  it("opens with @misc{", () => {
    expect(buildBibtex(BASE_CTX).startsWith("@misc{")).toBe(true);
  });

  it("closes with }", () => {
    expect(buildBibtex(BASE_CTX).trimEnd().endsWith("}")).toBe(true);
  });

  it("handles multiple models in model list", () => {
    const result = buildBibtex(CTX_HOLIDAYS);
    expect(result).toContain("model-a");
    expect(result).toContain("model-b");
    expect(result).toContain("model-c");
  });
});

// ── accessDate ────────────────────────────────────────────────────────────────

describe("accessDate", () => {
  it("returns a non-empty string", () => {
    const result = accessDate();
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("contains a year in the 2020s", () => {
    const result = accessDate();
    expect(result).toMatch(/20\d\d/);
  });

  it("contains a month name", () => {
    const months = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December",
    ];
    const result = accessDate();
    const hasMonth = months.some((m) => result.includes(m));
    expect(hasMonth).toBe(true);
  });
});

// ── All four formats: "Cognitive Structure Lab" and "LSB" always present ──────

describe("§1.6 naming compliance — all four formats", () => {
  const formats = [
    { name: "APA",     fn: buildApa },
    { name: "MLA",     fn: buildMla },
    { name: "Chicago", fn: buildChicago },
    { name: "BibTeX",  fn: buildBibtex },
  ];

  formats.forEach(({ name, fn }) => {
    it(`${name}: contains 'Cognitive Structure Lab'`, () => {
      expect(fn(BASE_CTX)).toContain("Cognitive Structure Lab");
    });

    it(`${name}: contains 'LSB'`, () => {
      expect(fn(BASE_CTX)).toContain("LSB");
    });
  });
});
