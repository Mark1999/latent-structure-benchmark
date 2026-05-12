// @vitest-environment jsdom
/**
 * T7 gap-fill tests — Phase 6 T7 (FreeListCompare).
 *
 * Gaps filled against:
 *   - CDA SME §5.1 verbatim caption text: exact string (not just fragment)
 *   - CDA SME §5.5 "no methodology narration": assert no <details>, no info-icon,
 *     no "we chose" / "we use" / "methodology" / "bootstrap" / "smoothing" text
 *   - UI/UX F-T7-A1: h2 is the first child element of the root div (not just present)
 *   - No h1→h3 skip regression: h2 element precedes h3 in DOM order
 *   - Static-file forbidden vocab scan (T0 gap-fill pattern):
 *     FreeListCompare.tsx, FreeListColumn.tsx, freelist-compare.css source text
 *   - F-T7-C1 CSS opacity: assert .freelist-column__freq-fill opacity is 0.8
 *   - Schema drift safety net: extra property in sutrop_csi entry does not crash
 *   - Cross-column highlight via focus (not just hover): focusin propagates
 *
 * CLAUDE.md §6 R9: no real API calls. Static-file reads + inline fixtures only.
 *
 * Reference: docs/status/2026-05-12-phase6-T7-architect-plan.md §3
 *            docs/status/2026-05-12-phase6-T7-cda-sme-verdict.md §5.1, §5.2, §5.5
 *            docs/status/2026-05-12-phase6-T7-uiux-plan-verdict.md F-T7-A1, F-T7-C1
 *            docs/status/2026-05-12-phase6-T7-reviewer-verdict.md
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { FreeListCompare } from "../components/FreeListCompare";
import type { FreeListCompareProps } from "../components/FreeListCompare";
import type {
  DomainResultPublished,
  WithinModelResult,
  EllipseParams,
} from "../data/types";

// ── Static source files (T0 gap-fill pattern) ─────────────────────────────────

const FREE_LIST_COMPARE_SRC = readFileSync(
  resolve(__dirname, "../components/FreeListCompare.tsx"),
  "utf-8"
);
const FREE_LIST_COLUMN_SRC = readFileSync(
  resolve(__dirname, "../components/FreeListColumn.tsx"),
  "utf-8"
);
const FREE_LIST_COMPARE_CSS = readFileSync(
  resolve(__dirname, "../styles/freelist-compare.css"),
  "utf-8"
);

// ── Render helpers ─────────────────────────────────────────────────────────────

let container: HTMLDivElement;
let root: ReturnType<typeof createRoot>;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(() => {
  act(() => {
    root.unmount();
  });
  container.remove();
});

function renderCompare(props: FreeListCompareProps): void {
  act(() => {
    root.render(createElement(FreeListCompare, props));
  });
}

// ── Fixture builder (mirrors freelist-compare.test.tsx) ───────────────────────

function makeFixture(
  modelIds: string[],
  sutropCsiOverride?: Record<
    string,
    | Array<{
        item: string;
        csi: number;
        f_mentions: number;
        n_runs: number;
        mean_position: number;
      }>
    | undefined
  >
): DomainResultPublished {
  const mds_coordinates: Record<string, [number, number]> = {};
  const mds_uncertainty: Record<string, EllipseParams | null> = {};
  const within_model_results: WithinModelResult[] = [];

  modelIds.forEach((id, i) => {
    mds_coordinates[id] = [i * 0.1, i * 0.1];
    mds_uncertainty[id] = null;
    within_model_results.push({
      model_id: id,
      n_runs: 4,
      oci: 10.0,
      oci_ci: null,
      underestimates_uncertainty: false,
      deterministic_output: false,
      salience_stability_rho: null,
      elbow_stability: null,
      mds_procrustes_rmse: null,
      centrality_scores_by_run: {},
      centroid_run_id: "run-1",
      mds_within_model: [],
    });
  });

  const defaultSutropCsi: Record<
    string,
    Array<{
      item: string;
      csi: number;
      f_mentions: number;
      n_runs: number;
      mean_position: number;
    }>
  > = {};
  for (const id of modelIds) {
    defaultSutropCsi[id] = [
      { item: "alpha", csi: 0.75, f_mentions: 3, n_runs: 4, mean_position: 1.0 },
      { item: "beta", csi: 0.50, f_mentions: 2, n_runs: 4, mean_position: 2.0 },
    ];
  }

  const sutropCsi =
    sutropCsiOverride !== undefined
      ? { ...defaultSutropCsi, ...sutropCsiOverride }
      : defaultSutropCsi;

  return {
    domain_slug: "test-domain",
    analysis_version: "0.2",
    models: modelIds.map((id) => ({
      provider: "test",
      model_id: id,
      family: id,
      origin: "us" as const,
      open_weights: false,
      collection_method: "api",
      quantization: null,
      release_date: "2026-01-01",
      version_label: id,
      source_notes: "",
    })),
    free_lists: {} as unknown as Record<string, string[]>,
    mds_coordinates: mds_coordinates as unknown as Record<
      string,
      [[number, number]]
    >,
    mds_uncertainty,
    similarity_matrix: {},
    similarity_ci: {},
    consensus_score: 0.71,
    consensus_ci: [0.65, 0.77],
    consensus_type: "STRONG_CONSENSUS",
    sutrop_csi: sutropCsi as unknown as Record<string, Record<string, number>>,
    within_model_results,
    groundings: [],
    generated_lede: "Test lede.",
    generated_at: "2026-05-12T00:00:00Z",
    display: {
      r1_states: Object.fromEntries(
        modelIds.map((id) => [id, "typical_concentration" as const])
      ),
      top_terms: Object.fromEntries(modelIds.map((id) => [id, ["alpha", "beta"]])),
      top_terms_metric: "sutrop_csi",
    },
  };
}

const TWO_MODEL_COLORS: Record<string, string> = {
  "model-a": "#3360a9",
  "model-b": "#c0392b",
};

// ══════════════════════════════════════════════════════════════════════════════
// GAP 1: CDA SME §5.1 exact verbatim caption string (regression guard)
//
// The Coder's test uses .toContain() in two halves, which would not catch
// a minor reword (e.g., "that model's" instead of "this model's").
// This test asserts the full exact string from CDA SME §5.1.
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — CDA SME §5.1 R10 caption verbatim exact match (gap-fill)", () => {
  it("R10 caption text is exactly the CDA SME §5.1 binding string", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const captions = container.querySelectorAll(".freelist-column__r10-caption");
    expect(captions.length).toBeGreaterThan(0);
    // The apostrophe in "model’s" is rendered from &apos; (U+0027) in the source.
    // The DOM textContent normalises it to U+0027 (straight apostrophe).
    // Construct expected string with String.fromCharCode(39) to avoid the editor
    // substituting a typographic apostrophe (U+2019) in the source file literal,
    // which would break Object.is equality (the component renders U+0027).
    const APOSTROPHE = String.fromCharCode(39); // U+0027 APOSTROPHE
    const EXPECTED =
      "Bar shows the fraction of this model" +
      APOSTROPHE +
      "s collection runs that produced this term.";
    expect(captions[0].textContent).toBe(EXPECTED);
  });

  it("R10 caption matches verbatim regardless of entity encoding (straight or curly apostrophe)", () => {
    // Guard against both &apos; (U+0027) and the typographic apostrophe (U+2019).
    // The DOM textContent normalises both to the character the browser renders.
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const caption = container.querySelector(".freelist-column__r10-caption");
    const text = caption?.textContent ?? "";
    // Must contain ALL required sub-phrases in one contiguous string:
    //   "Bar shows the fraction of this model" + apostrophe-variant + "s collection runs that produced this term."
    expect(text).toMatch(
      /^Bar shows the fraction of this model['’]s collection runs that produced this term\.$/
    );
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 2: CDA SME §5.5 "no methodology narration" guard
//
// No <details>, no info-icon button, no "we chose" / "we use" / "methodology"
// / "bootstrap" / "smoothing" prose anywhere in the rendered output.
// This is a "future agent doesn't add a tooltip" regression test.
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — CDA SME §5.5 no methodology narration (gap-fill)", () => {
  it("renders no <details> element (no expandable methodology section)", () => {
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const details = container.querySelectorAll("details");
    expect(details.length).toBe(0);
  });

  it("renders no <summary> element (no expandable methodology section)", () => {
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const summaries = container.querySelectorAll("summary");
    expect(summaries.length).toBe(0);
  });

  it("renders no info-icon button (title='info' or aria-label containing 'info')", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    // Any button with title="info" or aria-label="info" or similar info-icon pattern
    const buttons = container.querySelectorAll("button");
    buttons.forEach((btn) => {
      const title = (btn.getAttribute("title") ?? "").toLowerCase();
      const label = (btn.getAttribute("aria-label") ?? "").toLowerCase();
      expect(title).not.toContain("info");
      expect(label).not.toContain("info");
    });
  });

  it("rendered text contains no 'we chose' methodology prose", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const allText = (container.textContent ?? "").toLowerCase();
    expect(allText).not.toContain("we chose");
  });

  it("rendered text contains no 'we use' methodology prose", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const allText = (container.textContent ?? "").toLowerCase();
    expect(allText).not.toContain("we use");
  });

  it("rendered text contains no 'bootstrap' methodology prose", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const allText = (container.textContent ?? "").toLowerCase();
    expect(allText).not.toContain("bootstrap");
  });

  it("rendered text contains no 'smoothing' methodology prose", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const allText = (container.textContent ?? "").toLowerCase();
    expect(allText).not.toContain("smoothing");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 3: UI/UX F-T7-A1 — h2 is first child element of root (not just present)
//
// The Coder's test confirms the h2 exists and has text "Free list comparison"
// but does not verify it is the first child element. F-T7-A1 requires it to
// be first child before the description <p> and columns row.
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — F-T7-A1: h2 is first child of root element (gap-fill)", () => {
  it("sr-only h2 is the first child of the .freelist-compare root div", () => {
    const domainResult = makeFixture(["model-a"]);
    renderCompare({
      domainResult,
      modelColors: { "model-a": "#3360a9" },
      selectedModels: ["model-a"],
    });

    const rootDiv = container.querySelector(".freelist-compare");
    expect(rootDiv).not.toBeNull();

    const firstChild = rootDiv!.firstElementChild;
    expect(firstChild).not.toBeNull();
    expect(firstChild!.tagName.toLowerCase()).toBe("h2");
    expect(firstChild!.textContent).toBe("Free list comparison");
  });

  it("h2 precedes h3 in DOM order (no h1→h3 skip regression)", () => {
    // With columns rendered, verify the sr-only h2 appears before any h3
    // in document order — the heading hierarchy is h2 then h3.
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const allHeadings = container.querySelectorAll("h2, h3");
    expect(allHeadings.length).toBeGreaterThan(0);

    // The first heading in the container must be the h2 (not an h3)
    expect(allHeadings[0].tagName.toLowerCase()).toBe("h2");

    // Every h3 must come after the h2 in the NodeList
    let seenH2 = false;
    allHeadings.forEach((heading) => {
      if (heading.tagName.toLowerCase() === "h2") {
        seenH2 = true;
      }
      if (heading.tagName.toLowerCase() === "h3") {
        // By the time we encounter an h3, we must already have passed the h2
        expect(seenH2).toBe(true);
      }
    });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 4: Static-file forbidden vocabulary scan (T0 gap-fill pattern)
//
// Reads source text of FreeListCompare.tsx, FreeListColumn.tsx, and
// freelist-compare.css directly and asserts none contain the CLAUDE.md §7
// forbidden phrases in user-facing or source prose.
//
// Field names from the data (e.g., "sutrop_csi", "f_mentions") are exempt
// per §7. We test the forbidden PHRASES, not isolated words.
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare static-source forbidden vocabulary scan (gap-fill)", () => {
  // Forbidden phrases per CLAUDE.md §7 and ARCHITECTURE.md §1.5.4.
  //
  // IMPORTANT: Only multi-word model-applied constructions are tested here.
  // Single-word entries ("worldview", "missing", "placeholder", "pending")
  // are EXCLUDED from the source-file scan because both FreeListCompare.tsx
  // and FreeListColumn.tsx contain self-documenting compliance headers that
  // explicitly list those words in a quoted/documented context (e.g.,
  // "Forbidden vocabulary: no 'worldview'..."). Testing those individual
  // words in source text would false-positive on those compliance docstrings.
  //
  // The empty-state framing words ("missing", "no data yet", "pending",
  // "placeholder") are covered by the rendered-DOM tests in the Coder's
  // freelist-compare.test.tsx (Case A/B/C vocabulary checks). This source
  // scan adds a complementary layer targeting model-cognition constructions
  // that should never appear even in quoted documentation contexts, because
  // a documentation comment that says 'the model believes X' would be a
  // live violation even if "quoted" — the phrasing applies to LSB subjects.
  //
  // The T0 gap-fill pattern (t0-gap-fill.test.ts) uses the same approach:
  // the scanned files (InspectRoot.tsx etc.) don't have compliance-doc headers
  // that self-reference forbidden vocabulary, so individual words work there.
  const FORBIDDEN_PHRASES = [
    "model believes",
    "model thinks",
    "model understands",
    "How models see the world",
    "How models see",
    "What the model understands",
    "Cultural bias",
  ];

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`FreeListCompare.tsx does not contain forbidden phrase: "${phrase}"`, () => {
      expect(FREE_LIST_COMPARE_SRC.toLowerCase()).not.toContain(
        phrase.toLowerCase()
      );
    });
  }

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`FreeListColumn.tsx does not contain forbidden phrase: "${phrase}"`, () => {
      expect(FREE_LIST_COLUMN_SRC.toLowerCase()).not.toContain(
        phrase.toLowerCase()
      );
    });
  }

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`freelist-compare.css does not contain forbidden phrase: "${phrase}"`, () => {
      expect(FREE_LIST_COMPARE_CSS.toLowerCase()).not.toContain(
        phrase.toLowerCase()
      );
    });
  }
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 5: F-T7-C1 CSS opacity — source-level regression check
//
// The Reviewer confirmed opacity is 0.8 in the CSS. This test reads the
// CSS source and verifies the value, guarding against a future edit that
// reverts to 0.6 (the original plan §2.3 value that failed contrast).
// ══════════════════════════════════════════════════════════════════════════════

describe("freelist-compare.css — F-T7-C1 bar fill opacity (gap-fill)", () => {
  it("freelist-compare.css contains 'opacity: 0.8' (not 0.6) for freq-fill", () => {
    // The CSS source must declare opacity: 0.8 for .freelist-column__freq-fill.
    // It must NOT declare opacity: 0.6 (which failed 3:1 contrast for model-3/4).
    expect(FREE_LIST_COMPARE_CSS).toContain("opacity: 0.8");
  });

  it("freelist-compare.css does NOT contain 'opacity: 0.6' for freq-fill (contrast guard)", () => {
    // Guard against regression to the original plan §2.3 opacity that failed
    // WCAG SC 1.4.11 3:1 graphical contrast for model-3 (#e67e22) and model-4 (#27ae60).
    // The CSS file may mention 0.6 in comments (the contrast arithmetic uses it);
    // we check that 0.6 does not appear as a live CSS property value.
    // The only occurrence of "0.6" in the file is in a comment block.
    const cssLines = FREE_LIST_COMPARE_CSS.split("\n");
    const liveOpacityLines = cssLines.filter((line) => {
      const trimmed = line.trim();
      // Skip comment lines
      if (trimmed.startsWith("*") || trimmed.startsWith("/*")) return false;
      return trimmed.includes("opacity") && trimmed.includes("0.6");
    });
    expect(liveOpacityLines.length).toBe(0);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 6: Schema drift safety net
//
// If a sutrop_csi entry has an unexpected extra property (e.g., from a
// future schema extension), the component must render gracefully without
// throwing. This mirrors the "Other top-level fields" T0 pattern.
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — schema drift safety net (gap-fill)", () => {
  it("renders without crashing when sutrop_csi entries have unexpected extra properties", () => {
    // Inject an entry with an extra field the component doesn't know about
    const sutropWithExtras = [
      {
        item: "alpha",
        csi: 0.75,
        f_mentions: 3,
        n_runs: 4,
        mean_position: 1.0,
        unexpected_field: 42,          // future schema extension
        another_unknown: "extra-data", // another unknown field
      },
    ];

    const domainResult = makeFixture(["model-a"], {
      "model-a": sutropWithExtras as unknown as Array<{
        item: string;
        csi: number;
        f_mentions: number;
        n_runs: number;
        mean_position: number;
      }>,
    });

    // Must not throw
    expect(() => {
      renderCompare({
        domainResult,
        modelColors: { "model-a": "#3360a9" },
        selectedModels: ["model-a"],
      });
    }).not.toThrow();

    // Must still render the term
    const items = container.querySelectorAll("li.freelist-column__item");
    expect(items.length).toBe(1);
    const termSpan = container.querySelector(".freelist-column__term");
    expect(termSpan?.textContent).toBe("alpha");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// GAP 7: Cross-column highlight via focus (not just hover)
//
// The Coder's cross-column test uses mouseover (simulating hover).
// AC #6 requires focus parity. This test verifies that focusin on a term
// in one column propagates the highlight to the SAME term in another column.
// ══════════════════════════════════════════════════════════════════════════════

describe("FreeListCompare — cross-column focus highlight parity (AC #6 gap-fill)", () => {
  it("focusin on a term in column A highlights the same term in column B", () => {
    // Both model-a and model-b have "alpha" — focusin on model-a's alpha
    // should apply --hovered to model-b's alpha too.
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    // Find all "alpha" items across both columns
    const allItems = container.querySelectorAll("li.freelist-column__item");
    const alphaItems = Array.from(allItems).filter((li) =>
      li.getAttribute("aria-label")?.startsWith("alpha")
    );
    // Should have 2 alpha items (one per column)
    expect(alphaItems.length).toBe(2);

    // Focus the first alpha item (column A)
    act(() => {
      alphaItems[0].dispatchEvent(new FocusEvent("focusin", { bubbles: true }));
    });

    // Both alpha items should have the --hovered class (cross-column propagation)
    expect(
      alphaItems[0].classList.contains("freelist-column__item--hovered")
    ).toBe(true);
    expect(
      alphaItems[1].classList.contains("freelist-column__item--hovered")
    ).toBe(true);
  });

  it("focusout on a term in column A clears the highlight in both columns", () => {
    const domainResult = makeFixture(["model-a", "model-b"]);
    renderCompare({
      domainResult,
      modelColors: TWO_MODEL_COLORS,
      selectedModels: ["model-a", "model-b"],
    });

    const allItems = container.querySelectorAll("li.freelist-column__item");
    const alphaItems = Array.from(allItems).filter((li) =>
      li.getAttribute("aria-label")?.startsWith("alpha")
    );
    expect(alphaItems.length).toBe(2);

    // Focus then blur
    act(() => {
      alphaItems[0].dispatchEvent(new FocusEvent("focusin", { bubbles: true }));
    });
    act(() => {
      alphaItems[0].dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
    });

    // Both alpha items should no longer have the --hovered class
    expect(
      alphaItems[0].classList.contains("freelist-column__item--hovered")
    ).toBe(false);
    expect(
      alphaItems[1].classList.contains("freelist-column__item--hovered")
    ).toBe(false);
  });
});
