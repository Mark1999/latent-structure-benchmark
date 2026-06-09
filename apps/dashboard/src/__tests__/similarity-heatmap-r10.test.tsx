/**
 * SimilarityHeatmap R10 compliance tests (Phase 9a T3).
 *
 * Verifies the restored CI-crosses-null treatment:
 *   - Dashed border on crossing cells (DESIGN_SYSTEM.md §12.8 T3 restored).
 *   - Solid border on non-crossing / null-CI / diagonal cells.
 *   - Four aria-label variants (CDA SME T3 §2 binding strings).
 *   - No forbidden vocabulary in aria-label or caption strings.
 *   - Production fixture counts (food >= 30 dashed; family 0 dashed).
 *
 * CLAUDE.md §6 rule 9: no real API calls — all data is fixture-based.
 * CLAUDE.md §6 rule 10 (R10): no point estimate without uncertainty on any viz.
 * CLAUDE.md §9 pitfall #8: no viz without uncertainty check.
 */

import { render } from "@testing-library/react";
import { SimilarityHeatmap } from "../components/SimilarityHeatmap";
import { SIMILARITY_NULL_VALUE } from "../config/analysis";
import foodJson from "../../public/data/food.json";
import familyJson from "../../public/data/family.json";

// ── Fixture model helpers ─────────────────────────────────────────────────────

function makeModels(ids: string[]) {
  return ids.map((id) => ({ model_id: id, provider: "fixture-provider", family: "fixture" }));
}

// Short 3-model fixture for unit tests
const FIXTURE_MODEL_A = "fixture-alpha";
const FIXTURE_MODEL_B = "fixture-beta";
const FIXTURE_MODEL_C = "fixture-gamma";

const FIXTURE_MODELS = makeModels([FIXTURE_MODEL_A, FIXTURE_MODEL_B, FIXTURE_MODEL_C]);
const ALL_SELECTED = new Set([FIXTURE_MODEL_A, FIXTURE_MODEL_B, FIXTURE_MODEL_C]);

// similarity_matrix: a[i][j] is the sim for row i, col j
// Values: A-B = 0.45 (seq-2 stop, sim < 0.5 → dark stroke), A-C = 0.70 (seq-3, sim >= 0.6 → white stroke)
const FIXTURE_MATRIX: number[][] = [
  [1.0,  0.45, 0.70],
  [0.45, 1.0,  0.55],
  [0.70, 0.55, 1.0],
];

// CI matrix: A-B crosses null (0.35, 0.60) → dashed; A-C does not (0.60, 0.80);
//            B-C does not (0.48, 0.62); all diagonals are [1.0, 1.0].
const FIXTURE_CI: ([number, number] | null)[][] = [
  [[1.0, 1.0],  [0.35, 0.60], [0.60, 0.80]],
  [[0.35, 0.60], [1.0, 1.0],  [0.48, 0.62]],
  [[0.60, 0.80], [0.48, 0.62], [1.0, 1.0]],
];

// ── 1. Crossing cell → dashed + aria CI + "includes...0.50" suffix ────────────

describe("SimilarityHeatmap — crossing cell (test case 1)", () => {
  it("renders a dashed-border rect for a cell whose CI crosses SIMILARITY_NULL_VALUE", () => {
    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={FIXTURE_CI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    // A-B cell: CI [0.35, 0.60] crosses 0.5 → dashed.
    // displayModel strips provider prefix/claude- prefix; "fixture-alpha" → "fixture-alpha"
    const crossingRect = document.querySelector(
      '[aria-label*="fixture-alpha versus fixture-beta"]'
    ) as SVGRectElement | null;
    expect(crossingRect).not.toBeNull();

    // Must have dashed stroke
    const dashArray = crossingRect!.getAttribute("stroke-dasharray");
    expect(dashArray).toBe("3,2");

    // strokeWidth must be 1.5
    const sw = crossingRect!.getAttribute("stroke-width");
    expect(sw).toBe("1.5");
  });

  it("includes the CI values in the aria-label of a crossing cell (Variant B)", () => {
    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={FIXTURE_CI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const crossingRect = document.querySelector(
      '[aria-label*="fixture-alpha versus fixture-beta"]'
    ) as SVGRectElement | null;
    expect(crossingRect).not.toBeNull();

    const label = crossingRect!.getAttribute("aria-label") ?? "";
    // Must contain "95 percent confidence interval"
    expect(label).toMatch(/95 percent confidence interval/);
    // Must contain the "includes...0.50" suffix
    expect(label).toMatch(/confidence interval includes the no-shared-structure value of 0\.50/);
  });
});

// ── 2-3. Non-crossing cells → solid, CI in aria, no suffix ───────────────────

describe("SimilarityHeatmap — non-crossing cell (test cases 2-3)", () => {
  it("renders a solid border (no dasharray) for a non-crossing cell", () => {
    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={FIXTURE_CI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    // A-C cell: CI [0.60, 0.80] does NOT cross 0.5 → solid.
    const nonCrossingRect = document.querySelector(
      '[aria-label*="fixture-alpha versus fixture-gamma"]'
    ) as SVGRectElement | null;
    expect(nonCrossingRect).not.toBeNull();

    // Must NOT have dashed stroke
    const dashArray = nonCrossingRect!.getAttribute("stroke-dasharray");
    expect(dashArray).toBeNull();
  });

  it("includes CI values in aria-label of a non-crossing cell but NOT the suffix (Variant A)", () => {
    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={FIXTURE_CI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    // A-C cell: Variant A — CI present but not crossing.
    const nonCrossingRect = document.querySelector(
      '[aria-label*="fixture-alpha versus fixture-gamma"]'
    ) as SVGRectElement | null;
    const label = nonCrossingRect!.getAttribute("aria-label") ?? "";

    // Must contain CI values
    expect(label).toMatch(/95 percent confidence interval/);
    // Must NOT have the "includes...0.50" suffix
    expect(label).not.toMatch(/confidence interval includes the no-shared-structure value/);
  });
});

// ── 4. Null CI → solid + "confidence interval not available" ─────────────────

describe("SimilarityHeatmap — null CI cell (test case 4)", () => {
  it("renders solid border and 'confidence interval not available' for null-CI cell (Variant C)", () => {
    // B-C CI set to null
    const ciWithNull: ([number, number] | null)[][] = [
      [[1.0, 1.0],  [0.35, 0.60], [0.60, 0.80]],
      [[0.35, 0.60], [1.0, 1.0],  null],
      [[0.60, 0.80], null,         [1.0, 1.0]],
    ];

    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={ciWithNull}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    // B-C cell: null CI → Variant C.
    const nullCiRect = document.querySelector(
      '[aria-label*="fixture-beta versus fixture-gamma"]'
    ) as SVGRectElement | null;
    expect(nullCiRect).not.toBeNull();

    const label = nullCiRect!.getAttribute("aria-label") ?? "";
    expect(label).toMatch(/confidence interval not available/);

    // Solid border (no dasharray)
    expect(nullCiRect!.getAttribute("stroke-dasharray")).toBeNull();
  });
});

// ── 5. Diagonal → solid + "self-similarity: 1.00 by construction" ────────────

describe("SimilarityHeatmap — diagonal cell (test case 5)", () => {
  it("renders solid border and 'self-similarity: 1.00 by construction' for diagonal (Variant D)", () => {
    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={FIXTURE_CI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    // A-A diagonal: Variant D.
    const diagRect = document.querySelector(
      '[aria-label*="fixture-alpha self-similarity: 1.00 by construction"]'
    ) as SVGRectElement | null;
    expect(diagRect).not.toBeNull();

    // Must NOT have dashed stroke even though diagonal CI is [1.0, 1.0] (not crossing, irrelevant)
    expect(diagRect!.getAttribute("stroke-dasharray")).toBeNull();
  });

  it("never renders a dashed border for any diagonal cell even if the CI were to cross null", () => {
    // Pathological fixture: diagonal CI crosses null (code bug scenario).
    // The diagonal short-circuit must prevent dashing regardless.
    const pathologicalCi: ([number, number] | null)[][] = [
      [[0.30, 0.70], [0.35, 0.60], [0.60, 0.80]],  // diag[0][0] crosses null — must STILL be solid
      [[0.35, 0.60], [0.30, 0.70], [0.48, 0.62]],
      [[0.60, 0.80], [0.48, 0.62], [0.30, 0.70]],
    ];

    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={pathologicalCi}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const diagRect = document.querySelector(
      '[aria-label*="fixture-alpha self-similarity: 1.00 by construction"]'
    ) as SVGRectElement | null;
    expect(diagRect).not.toBeNull();
    expect(diagRect!.getAttribute("stroke-dasharray")).toBeNull();
  });
});

// ── 6. Boundary arithmetic — strict < on both sides ──────────────────────────

describe("SimilarityHeatmap — boundary arithmetic (test case 6, SIMILARITY_NULL_VALUE strict < )", () => {
  it("SIMILARITY_NULL_VALUE constant is exactly 0.5", () => {
    expect(SIMILARITY_NULL_VALUE).toBe(0.5);
  });

  // We verify boundary behavior through the rendered aria-labels.
  // [0.499, 0.501] → crosses null → dashed + Variant B suffix.
  it("[0.499, 0.501] crosses null → dashed (strict < satisfied on both sides)", () => {
    const ci: ([number, number] | null)[][] = [
      [[1.0, 1.0],    [0.499, 0.501], [0.60, 0.80]],
      [[0.499, 0.501], [1.0, 1.0],    [0.48, 0.62]],
      [[0.60, 0.80],   [0.48, 0.62],  [1.0, 1.0]],
    ];

    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={ci}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const rect = document.querySelector(
      '[aria-label*="fixture-alpha versus fixture-beta"]'
    ) as SVGRectElement | null;
    expect(rect).not.toBeNull();
    expect(rect!.getAttribute("stroke-dasharray")).toBe("3,2");
    expect(rect!.getAttribute("aria-label")).toMatch(
      /confidence interval includes the no-shared-structure value of 0\.50/
    );
  });

  // [0.5, 0.501] → ci[0] == 0.5 → strict < fails on lower bound → solid (NOT crossing).
  it("[0.5, 0.501] does NOT cross null (ci[0] == 0.5, strict < fails)", () => {
    const ci: ([number, number] | null)[][] = [
      [[1.0, 1.0],   [0.5, 0.501], [0.60, 0.80]],
      [[0.5, 0.501], [1.0, 1.0],   [0.48, 0.62]],
      [[0.60, 0.80], [0.48, 0.62], [1.0, 1.0]],
    ];

    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={ci}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const rect = document.querySelector(
      '[aria-label*="fixture-alpha versus fixture-beta"]'
    ) as SVGRectElement | null;
    expect(rect).not.toBeNull();
    expect(rect!.getAttribute("stroke-dasharray")).toBeNull();
    expect(rect!.getAttribute("aria-label")).not.toMatch(
      /confidence interval includes the no-shared-structure value/
    );
  });

  // [0.499, 0.5] → ci[1] == 0.5 → strict < fails on upper bound → solid (NOT crossing).
  it("[0.499, 0.5] does NOT cross null (ci[1] == 0.5, strict < fails)", () => {
    const ci: ([number, number] | null)[][] = [
      [[1.0, 1.0],   [0.499, 0.5], [0.60, 0.80]],
      [[0.499, 0.5], [1.0, 1.0],   [0.48, 0.62]],
      [[0.60, 0.80], [0.48, 0.62], [1.0, 1.0]],
    ];

    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={ci}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const rect = document.querySelector(
      '[aria-label*="fixture-alpha versus fixture-beta"]'
    ) as SVGRectElement | null;
    expect(rect).not.toBeNull();
    expect(rect!.getAttribute("stroke-dasharray")).toBeNull();
  });

  // [0.499, 0.499] → ci[1] < 0.5 → does not cross null → solid.
  it("[0.499, 0.499] does NOT cross null (ci[1] < 0.5, upper bound below null)", () => {
    const ci: ([number, number] | null)[][] = [
      [[1.0, 1.0],   [0.499, 0.499], [0.60, 0.80]],
      [[0.499, 0.499], [1.0, 1.0],   [0.48, 0.62]],
      [[0.60, 0.80],   [0.48, 0.62], [1.0, 1.0]],
    ];

    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={ci}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const rect = document.querySelector(
      '[aria-label*="fixture-alpha versus fixture-beta"]'
    ) as SVGRectElement | null;
    expect(rect).not.toBeNull();
    expect(rect!.getAttribute("stroke-dasharray")).toBeNull();
  });
});

// ── 7. Dual-index alignment — filtered cell reads correct original-index CI ───

describe("SimilarityHeatmap — dual-index alignment (test case 7)", () => {
  it("a filtered selection reads the correct original-model-order CI, not display-position CI", () => {
    // 4-model fixture; select only models at original positions 1 and 3.
    // The CI at [1][3] crosses null, but [0][2] does not.
    // If the component incorrectly used display indices (0,1) instead of
    // original indices (1,3), it would look up [0][2] and show a solid border.
    const models4 = makeModels([
      "fixture-model-0",  // not selected
      "fixture-model-1",  // selected → display row 0
      "fixture-model-2",  // not selected
      "fixture-model-3",  // selected → display row 1
    ]);

    const matrix4: number[][] = [
      [1.0, 0.8, 0.7, 0.45],
      [0.8, 1.0, 0.6, 0.45],
      [0.7, 0.6, 1.0, 0.45],
      [0.45, 0.45, 0.45, 1.0],
    ];

    // [1][3] crosses null; [0][2] does NOT cross null.
    const ci4: ([number, number] | null)[][] = [
      [[1.0, 1.0], [0.7, 0.9], [0.65, 0.75], [0.65, 0.75]],  // [0][2] = [0.65,0.75] no-cross
      [[0.7, 0.9], [1.0, 1.0], [0.55, 0.65], [0.35, 0.60]],  // [1][3] = [0.35,0.60] CROSSES
      [[0.65, 0.75], [0.55, 0.65], [1.0, 1.0], [0.55, 0.65]],
      [[0.65, 0.75], [0.35, 0.60], [0.55, 0.65], [1.0, 1.0]],
    ];

    const selectedOnly1And3 = new Set(["fixture-model-1", "fixture-model-3"]);

    render(
      <SimilarityHeatmap
        similarityMatrix={matrix4}
        similarityCi={ci4}
        models={models4}
        selectedModelIds={selectedOnly1And3}
      />
    );

    // The displayed (0,1) cell is original (1,3) which crosses null → must be dashed.
    const rect = document.querySelector(
      '[aria-label*="fixture-model-1 versus fixture-model-3"]'
    ) as SVGRectElement | null;
    expect(rect).not.toBeNull();
    expect(rect!.getAttribute("stroke-dasharray")).toBe("3,2");
    expect(rect!.getAttribute("aria-label")).toMatch(
      /confidence interval includes the no-shared-structure value of 0\.50/
    );
  });
});

// ── 8. R10 BINDING GUARD: every off-diagonal aria-label has one of the 3 CI phrases ─

describe("SimilarityHeatmap — R10 binding guard (test case 8)", () => {
  /**
   * R10 BINDING GUARD.
   * Every off-diagonal <rect> aria-label MUST contain exactly one of the three
   * CI disclosure phrases — no bare point estimate is acceptable.
   * The three valid phrases (CDA SME T3 §2):
   *   1. "95 percent confidence interval" (Variants A and B)
   *   2. "confidence interval not available" (Variant C)
   *   3. "confidence interval includes the no-shared-structure value of 0.50" (Variant B suffix)
   * The test fails if any off-diagonal cell aria-label lacks all three.
   */
  const CI_PHRASES = [
    "95 percent confidence interval",
    "confidence interval not available",
    "confidence interval includes the no-shared-structure value of 0.50",
  ];

  it("all off-diagonal rects have an aria-label containing at least one of the 3 CI phrases", () => {
    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={FIXTURE_CI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const allRects = Array.from(
      document.querySelectorAll(".similarity-heatmap__cell")
    ) as SVGRectElement[];

    const offDiagonalRects = allRects.filter((rect) => {
      const label = rect.getAttribute("aria-label") ?? "";
      // Diagonal cells contain "self-similarity" — exclude them.
      return !label.includes("self-similarity");
    });

    expect(offDiagonalRects.length).toBeGreaterThan(0);

    for (const rect of offDiagonalRects) {
      const label = rect.getAttribute("aria-label") ?? "";
      const hasCI = CI_PHRASES.some((phrase) => label.includes(phrase));
      expect(hasCI).toBe(true);
    }
  });

  it("no off-diagonal rect has a bare-point-estimate aria-label (only similarity and no CI phrase)", () => {
    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={FIXTURE_CI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const allRects = Array.from(
      document.querySelectorAll(".similarity-heatmap__cell")
    ) as SVGRectElement[];

    for (const rect of allRects) {
      const label = rect.getAttribute("aria-label") ?? "";
      // A bare-point-estimate aria-label would match "versus.*similarity [0-9]" with no CI phrase.
      if (label.includes("versus")) {
        const hasCI = CI_PHRASES.some((phrase) => label.includes(phrase));
        expect(hasCI).toBe(true);
      }
    }
  });
});

// ── 9. Forbidden-vocab guard on aria-label and caption ───────────────────────

describe("SimilarityHeatmap — forbidden vocabulary guard (test case 9)", () => {
  /**
   * ARCHITECTURE.md §1.5.4 + CLAUDE.md §7 forbidden vocabulary.
   * None of the following may appear in any aria-label or in the caption:
   *   "worldview", "believes", "thinks", "agrees", "perceives", "understands",
   *   "missing", "placeholder", "pending", " vs " (approved connective is "versus").
   */
  const FORBIDDEN_PATTERNS = [
    /\bworldview\b/i,
    /\bbelieves\b/i,
    / vs /i,        // "vs" without "versus" (the non-cognitive connective is "versus")
    /\bthinks\b/i,
    /\bagrees\b/i,
    /\bperceives\b/i,
    /\bunderstands\b/i,
    /\bmissing\b/i,
    /\bplaceholder\b/i,
    /\bpending\b/i,
  ];

  it("no aria-label on any cell contains forbidden vocabulary", () => {
    render(
      <SimilarityHeatmap
        similarityMatrix={FIXTURE_MATRIX}
        similarityCi={FIXTURE_CI}
        models={FIXTURE_MODELS}
        selectedModelIds={ALL_SELECTED}
      />
    );

    const allRects = Array.from(
      document.querySelectorAll("[aria-label]")
    ) as Element[];

    for (const el of allRects) {
      const label = el.getAttribute("aria-label") ?? "";
      for (const pattern of FORBIDDEN_PATTERNS) {
        expect(label).not.toMatch(pattern);
      }
    }
  });

  it("the binding caption text does not contain forbidden vocabulary", () => {
    // Caption lives in ContentArea; here we check the strings that would appear
    // in the caption as defined by CDA SME T3 §3.
    const CAPTION =
      "Each cell shows how similarly two models organize this domain " +
      "(1.00 = identical organization; 0.50 = no shared structure). " +
      "Dashed cells: 95% confidence interval includes the no-shared-structure value of 0.50.";

    for (const pattern of FORBIDDEN_PATTERNS) {
      expect(CAPTION).not.toMatch(pattern);
    }
  });
});

// ── 10. Production fixture: food >= 30 dashed cells, family 0 dashed cells ────

describe("SimilarityHeatmap — production fixture dashed-cell counts (test case 10)", () => {
  /**
   * food.json: 8 models, 34 of 56 off-diagonal cells have CIs crossing 0.5
   * (Architect plan §1 regression report). Test asserts >= 30 to provide slack
   * for minor corpus updates while still guarding against a full regression.
   * family.json: 0 dashed cells (all CIs above the null) — false-positive guard.
   */

  function countDashedCells(
    matrix: number[][],
    ci: ([number, number] | null)[][],
    n: number,
  ): number {
    let count = 0;
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i === j) continue;
        const cellCi = ci[i]?.[j] ?? null;
        if (cellCi !== null && cellCi[0] < 0.5 && 0.5 < cellCi[1]) {
          count++;
        }
      }
    }
    return count;
  }

  it("food.json: at least 30 off-diagonal cells have CIs crossing SIMILARITY_NULL_VALUE", () => {
    const foodData = foodJson as {
      models: Array<{ model_id: string; provider: string; family: string }>;
      similarity_matrix: number[][];
      similarity_ci: ([number, number] | null)[][];
    };
    const n = foodData.models.length;
    const dashed = countDashedCells(
      foodData.similarity_matrix,
      foodData.similarity_ci,
      n,
    );
    expect(dashed).toBeGreaterThanOrEqual(30);
  });

  it("food.json: dashed cells render correctly (smoke render, no crash)", () => {
    const foodData = foodJson as {
      models: Array<{ model_id: string; provider: string; family: string }>;
      similarity_matrix: number[][];
      similarity_ci: ([number, number] | null)[][];
    };
    const allIds = new Set(foodData.models.map((m) => m.model_id));

    render(
      <SimilarityHeatmap
        similarityMatrix={foodData.similarity_matrix}
        similarityCi={foodData.similarity_ci}
        models={foodData.models}
        selectedModelIds={allIds}
      />
    );

    const dashedRects = Array.from(
      document.querySelectorAll('[stroke-dasharray="3,2"]')
    );
    expect(dashedRects.length).toBeGreaterThanOrEqual(30);
  });

  it("family.json: 0 off-diagonal cells have CIs crossing SIMILARITY_NULL_VALUE (false-positive guard)", () => {
    const familyData = familyJson as {
      models: Array<{ model_id: string; provider: string; family: string }>;
      similarity_matrix: number[][];
      similarity_ci: ([number, number] | null)[][];
    };
    const n = familyData.models.length;
    const dashed = countDashedCells(
      familyData.similarity_matrix,
      familyData.similarity_ci,
      n,
    );
    expect(dashed).toBe(0);
  });

  it("family.json: no dashed cells render (false-positive guard, smoke render)", () => {
    const familyData = familyJson as {
      models: Array<{ model_id: string; provider: string; family: string }>;
      similarity_matrix: number[][];
      similarity_ci: ([number, number] | null)[][];
    };
    const allIds = new Set(familyData.models.map((m) => m.model_id));

    render(
      <SimilarityHeatmap
        similarityMatrix={familyData.similarity_matrix}
        similarityCi={familyData.similarity_ci}
        models={familyData.models}
        selectedModelIds={allIds}
      />
    );

    const dashedRects = Array.from(
      document.querySelectorAll('[stroke-dasharray="3,2"]')
    );
    expect(dashedRects.length).toBe(0);
  });
});
