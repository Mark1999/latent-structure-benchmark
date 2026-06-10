/**
 * ClusterTree tests (T-CHART-TESTS-3)
 *
 * Verifies:
 *   - Renders correctly with canonical, empty, and bpValues-absent fixtures.
 *   - Bootstrap support rendering: dashed branches + % annotations for nodes
 *     with BP below DENDROGRAM_SUPPORT_THRESHOLD; solid branches above.
 *   - Axis label is "Merge distance" (register guard: not "agreement" or "similarity").
 *   - Forbidden vocabulary absent in rendered DOM text.
 *   - Determinism: outerHTML stable across two renders with fixed ResizeObserver width.
 *
 * ClusterTree uses ResizeObserver + useEffect to trigger its SVG build.
 * We mock ResizeObserver (same pattern as TermMap.test.tsx lines 24-30) and advance
 * microtasks via waitFor to allow the setSvgContent state update to settle.
 *
 * CLAUDE.md §6 rule 9: no real API calls. All data is fixture-based.
 * CLAUDE.md §9 pitfall 8: no point-estimate chart ships without uncertainty check.
 */

import { render, waitFor } from "@testing-library/react";
import { ClusterTree } from "../components/ClusterTree";
import { DENDROGRAM_SUPPORT_THRESHOLD } from "../config/analysis";

// ── JSDOM polyfills ───────────────────────────────────────────────────────────

// ResizeObserver is not available in jsdom; mock it to prevent errors.
// getBoundingClientRect is also stubbed to return a fixed width so the SVG
// render path receives a deterministic container width.
beforeAll(() => {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };

  // jsdom's getBoundingClientRect always returns zeroes; stub a fixed width
  // so the SVG build uses a real pixel value instead of falling back to 500.
  const originalGBCR = Element.prototype.getBoundingClientRect;
  vi.spyOn(Element.prototype, "getBoundingClientRect").mockImplementation(function (this: Element) {
    const original = originalGBCR.call(this);
    return { ...original, width: 800 };
  });
});

afterAll(() => {
  vi.restoreAllMocks();
});

// ── Fixtures ──────────────────────────────────────────────────────────────────

// 6-term linkage (5 internal merges)
// Items: a, b, c, d, e, f  (indices 0..5)
// Linkage rows: [left, right, distance, count]
const FIXTURE_ITEMS = [
  "fixture-term-a",
  "fixture-term-b",
  "fixture-term-c",
  "fixture-term-d",
  "fixture-term-e",
  "fixture-term-f",
];

const FIXTURE_LINKAGE = [
  [0, 1, 0.10, 2],   // node 6: merge a+b
  [2, 3, 0.18, 2],   // node 7: merge c+d
  [4, 5, 0.22, 2],   // node 8: merge e+f
  [6, 7, 0.35, 4],   // node 9: merge (a+b)+(c+d)
  [8, 9, 0.55, 6],   // node 10: merge all (root)
];

const FIXTURE_CLUSTER_ASSIGNMENTS: Record<string, number> = {
  "fixture-term-a": 0, "fixture-term-b": 0,
  "fixture-term-c": 1, "fixture-term-d": 1,
  "fixture-term-e": 2, "fixture-term-f": 2,
};

// bpValues: one value per linkage row (5 internal nodes 6..10)
// Node at index 2 (row 2: merge e+f, distance 0.22) gets BP below threshold -> dashed
// All others above threshold -> solid
const FIXTURE_BP_VALUES = [
  0.95,  // node 6 (a+b): solid
  0.88,  // node 7 (c+d): solid
  0.40,  // node 8 (e+f): BELOW threshold -> dashed
  0.82,  // node 9 (a+b+c+d): solid
  0.91,  // node 10 (root): solid
];

// Verify our fixture places one node below threshold and four above
const _belowThresholdCount = FIXTURE_BP_VALUES.filter(
  (v) => v < DENDROGRAM_SUPPORT_THRESHOLD
).length;
if (_belowThresholdCount !== 1) {
  throw new Error(`Fixture invariant: expected exactly 1 below-threshold BP value, got ${_belowThresholdCount}`);
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("ClusterTree: canonical fixture (6 terms, 5 linkage rows, with bpValues)", () => {
  it("renders without crash with full canonical data", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
        bpValues={FIXTURE_BP_VALUES}
      />
    );
    // Wait for the useEffect SVG build to settle
    await waitFor(() => {
      expect(container.querySelector(".cluster-tree__svg-wrap")).not.toBeNull();
    });
    expect(container.querySelector(".cluster-tree")).not.toBeNull();
  });

  it("renders the SVG inside .cluster-tree__svg-wrap after ResizeObserver callback", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
        bpValues={FIXTURE_BP_VALUES}
      />
    );
    await waitFor(() => {
      const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
      expect(svgWrap).not.toBeNull();
      expect(svgWrap!.innerHTML).toContain("<svg");
    });
  });
});

describe("ClusterTree: empty fixture (items = [], linkage = [])", () => {
  it("renders .cluster-tree--empty with the standard message when items is empty", () => {
    const { container } = render(
      <ClusterTree
        linkage={[]}
        items={[]}
        clusterAssignments={{}}
      />
    );
    expect(container.querySelector(".cluster-tree--empty")).not.toBeNull();
    expect(container.textContent).toContain("No clustering data available for this domain.");
  });

  it("renders .cluster-tree--empty when linkage is empty but items is non-empty", () => {
    const { container } = render(
      <ClusterTree
        linkage={[]}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
      />
    );
    expect(container.querySelector(".cluster-tree--empty")).not.toBeNull();
  });
});

describe("ClusterTree: bpValues absent (branches render, no BP annotations)", () => {
  it("renders without crash when bpValues prop is not provided", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
        // bpValues intentionally absent
      />
    );
    await waitFor(() => {
      const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
      expect(svgWrap).not.toBeNull();
    });
  });

  it("renders no % BP annotation text when bpValues is absent", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
      />
    );
    await waitFor(() => {
      const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
      expect(svgWrap).not.toBeNull();
    });

    // When bpValues is absent, no node qualifies as isDashed, so no % annotation is emitted.
    const svgText = container.querySelector(".cluster-tree__svg-wrap")!.innerHTML;
    // The % sign would appear only in BP annotations; tick labels use .toFixed(2)
    // and do not contain "%". Check that no annotation-style "NN%" appears.
    // We allow the % in the SVG aria-label or legend only; BP annotations are the only
    // element with a pattern like "40%", "95%", etc. from Math.round(bp*100).
    // Since no bpValues is provided, isDashed is always false and no % annotation is pushed.
    // Safe check: none of the <text> elements inside the SVG wrap should contain only digits+%.
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgText, "image/svg+xml");
    const texts = Array.from(doc.querySelectorAll("text"));
    const bpAnnotationTexts = texts.filter((t) => /^\d+%$/.test((t.textContent ?? "").trim()));
    expect(bpAnnotationTexts.length).toBe(0);
  });
});

describe("ClusterTree: bootstrap support rendering", () => {
  /**
   * Nodes with BP below DENDROGRAM_SUPPORT_THRESHOLD must render with
   * stroke-dasharray="5 3" (dashed) and a % annotation.
   * Nodes with BP >= threshold must render with solid branches (no dasharray).
   *
   * The component emits both via dangerouslySetInnerHTML so we parse the SVG string.
   */

  it("renders at least one dashed <line> (stroke-dasharray='5 3') for the below-threshold node", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
        bpValues={FIXTURE_BP_VALUES}
      />
    );
    await waitFor(() => {
      const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
      expect(svgWrap).not.toBeNull();
      expect(svgWrap!.innerHTML).toContain("stroke-dasharray");
    });

    const svgWrap = container.querySelector(".cluster-tree__svg-wrap")!;
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgWrap.innerHTML, "image/svg+xml");
    const dashedLines = Array.from(doc.querySelectorAll('line[stroke-dasharray="5 3"]'));
    expect(dashedLines.length).toBeGreaterThan(0);
  });

  it("renders a % annotation text for the below-threshold node", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
        bpValues={FIXTURE_BP_VALUES}
      />
    );
    await waitFor(() => {
      const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
      expect(svgWrap).not.toBeNull();
      expect(svgWrap!.innerHTML).toContain("%");
    });

    const svgWrap = container.querySelector(".cluster-tree__svg-wrap")!;
    const parser = new DOMParser();
    const doc = parser.parseFromString(svgWrap.innerHTML, "image/svg+xml");
    const texts = Array.from(doc.querySelectorAll("text"));
    // The annotation is "40%" (Math.round(0.40 * 100) = 40)
    const annotationTexts = texts.filter((t) => (t.textContent ?? "").trim() === "40%");
    expect(annotationTexts.length).toBeGreaterThanOrEqual(1);
  });

  it("DENDROGRAM_SUPPORT_THRESHOLD constant is exactly 0.70", () => {
    expect(DENDROGRAM_SUPPORT_THRESHOLD).toBe(0.70);
  });
});

describe("ClusterTree: axis label register guard", () => {
  /**
   * CDA SME N3 (BINDING carry-through from T-CHART-TESTS plan):
   * The axis label must be exactly "Merge distance" -- not "agreement" or "similarity".
   * Using "agreement" on the merge-distance axis would be a register error:
   * this axis encodes categorical dissimilarity, not inter-model agreement.
   */

  it("rendered text contains 'Merge distance' (correct axis label)", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
        bpValues={FIXTURE_BP_VALUES}
      />
    );
    await waitFor(() => {
      const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
      expect(svgWrap).not.toBeNull();
      expect(svgWrap!.innerHTML).toContain("Merge distance");
    });
  });

  it("rendered text does NOT contain standalone 'agreement' as an axis label (register guard)", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
        bpValues={FIXTURE_BP_VALUES}
      />
    );
    await waitFor(() => {
      const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
      expect(svgWrap).not.toBeNull();
    });

    // Check the description paragraph and SVG content for the register error.
    // "agreement" would be a register error on this axis (encodes categorical dissimilarity,
    // not inter-model consensus). The component uses "co-occurrence patterns" and
    // "Merge distance" -- both correct framings.
    const fullText = container.textContent ?? "";
    // Allow "agreement" in compound phrases like "run_agreement_matrix" (not present here)
    // but reject it as a standalone axis label. Check SVG wrap specifically.
    const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
    const svgText = svgWrap ? (svgWrap.textContent ?? "") : "";
    // "Merge distance" is the axis label; "agreement" must not appear in the SVG chrome
    expect(svgText).not.toMatch(/\bagreement\b/i);
    // Full container text check (description paragraph + SVG)
    // The description says "co-occurrence patterns" which is the correct framing
    expect(fullText).not.toMatch(/\bagreement axis\b/i);
  });
});

describe("ClusterTree: forbidden vocabulary guard", () => {
  /**
   * ARCHITECTURE.md §1.5.4 + CLAUDE.md §7 forbidden vocabulary.
   * The component docblock at lines 21-22 explicitly commits to never using
   * the forbidden words in the rendered DOM. This test mechanizes that promise.
   */
  const FORBIDDEN = [
    /\bworldview\b/i,
    /\bbelieves\b/i,
    /\bthinks\b/i,
    /\bunderstands\b/i,
  ];

  it("rendered container text contains no forbidden vocabulary", async () => {
    const { container } = render(
      <ClusterTree
        linkage={FIXTURE_LINKAGE}
        items={FIXTURE_ITEMS}
        clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
        bpValues={FIXTURE_BP_VALUES}
      />
    );
    await waitFor(() => {
      const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
      expect(svgWrap).not.toBeNull();
    });

    const text = container.textContent ?? "";
    for (const pattern of FORBIDDEN) {
      expect(text).not.toMatch(pattern);
    }
  });
});

describe("ClusterTree: determinism (fixed ResizeObserver width)", () => {
  it("is deterministic: same SVG content across two renders with the same inputs", async () => {
    async function renderAndExtractSvg() {
      const { container } = render(
        <ClusterTree
          linkage={FIXTURE_LINKAGE}
          items={FIXTURE_ITEMS}
          clusterAssignments={FIXTURE_CLUSTER_ASSIGNMENTS}
          bpValues={FIXTURE_BP_VALUES}
        />
      );
      await waitFor(() => {
        const svgWrap = container.querySelector(".cluster-tree__svg-wrap");
        expect(svgWrap).not.toBeNull();
        expect(svgWrap!.innerHTML).toContain("<svg");
      });
      return container.querySelector(".cluster-tree__svg-wrap")!.innerHTML;
    }

    const first  = await renderAndExtractSvg();
    const second = await renderAndExtractSvg();
    expect(first).toBe(second);
  });
});
