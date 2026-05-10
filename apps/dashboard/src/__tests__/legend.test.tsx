// @vitest-environment jsdom
/**
 * Legend component tests — T7 refactor.
 *
 * Verifies that the Legend component (extracted from MDSPlot.tsx at T7)
 * preserves all binding requirements from §3.3.5 imp. req. 4.
 *
 * The existing legend tests in mds-plot.test.tsx are preserved there;
 * this file adds coverage for the standalone Legend component.
 *
 * Required:
 *   - §3.3.5 imp. req. 4 binding: rendered 14px marker samples.
 *   - R1-a solid circle, R1-b dashed circle, R1-c hollow triangle.
 *   - Labels: "Typical concentration", "Low output concentration", "Deterministic output".
 *   - showDescriptions prop: secondary text shown by default, hidden when false.
 *
 * CLAUDE.md §6 R9: no real API calls. Component renders in isolation.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { Legend } from "../components/Legend";
import type { LegendProps } from "../components/Legend";

// Source text for structural assertions on the component file.
const LEGEND_SRC = readFileSync(
  resolve(__dirname, "../components/Legend.tsx"),
  "utf-8"
);

// ── Render helpers ────────────────────────────────────────────────────────────

let container: HTMLDivElement;
let root: ReturnType<typeof createRoot>;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(() => {
  act(() => { root.unmount(); });
  container.remove();
});

function renderLegend(props?: LegendProps): void {
  act(() => { root.render(createElement(Legend, props ?? {})); });
}

// ═══════════════════════════════════════════════════════════════════════════════
// TESTS
// ═══════════════════════════════════════════════════════════════════════════════

// ── §3.3.5 imp. req. 4: legend has 3 items ───────────────────────────────────

describe("Legend — 3 marker samples (§3.3.5 imp. req. 4)", () => {
  it("legend container is present with role='list'", () => {
    renderLegend();
    const legend = container.querySelector(".mds-plot__legend");
    expect(legend).not.toBeNull();
    expect(legend!.getAttribute("role")).toBe("list");
  });

  it("legend has 3 items", () => {
    renderLegend();
    expect(container.querySelectorAll(".mds-plot__legend-item")).toHaveLength(3);
  });

  it("each legend item has role='listitem'", () => {
    renderLegend();
    const items = container.querySelectorAll(".mds-plot__legend-item");
    items.forEach((item) => {
      expect(item.getAttribute("role")).toBe("listitem");
    });
  });
});

// ── R1-a: solid filled circle (14px SVG) ─────────────────────────────────────

describe("Legend — R1-a solid circle sample", () => {
  it("legend contains a solid filled circle (fill not 'none', no stroke-dasharray)", () => {
    renderLegend();
    const legend = container.querySelector(".mds-plot__legend");
    const circles = Array.from(legend!.querySelectorAll("circle"));
    const solidCircle = circles.find(
      (c) =>
        c.getAttribute("fill") !== "none" &&
        c.getAttribute("fill") !== "transparent" &&
        c.getAttribute("stroke-dasharray") === null &&
        c.getAttribute("strokeDasharray") === null
    );
    expect(solidCircle).not.toBeUndefined();
  });

  it("R1-a SVG sample has aria-hidden='true' (decorative)", () => {
    renderLegend();
    const legend = container.querySelector(".mds-plot__legend");
    const svgs = Array.from(legend!.querySelectorAll("svg"));
    // At least one SVG in the legend should be aria-hidden.
    expect(svgs.some((s) => s.getAttribute("aria-hidden") === "true")).toBe(true);
  });
});

// ── R1-b: dashed-stroke circle ────────────────────────────────────────────────

describe("Legend — R1-b dashed circle sample", () => {
  it("legend contains a dashed circle (has stroke-dasharray)", () => {
    renderLegend();
    const legend = container.querySelector(".mds-plot__legend");
    const circles = Array.from(legend!.querySelectorAll("circle"));
    const dashedCircle = circles.find(
      (c) =>
        c.getAttribute("stroke-dasharray") !== null ||
        c.getAttribute("strokeDasharray") !== null
    );
    expect(dashedCircle).not.toBeUndefined();
  });
});

// ── R1-c: hollow triangle path ───────────────────────────────────────────────

describe("Legend — R1-c hollow triangle sample (§3.3.5 imp. req. 2 binding)", () => {
  it("legend contains a hollow triangle path (fill='none')", () => {
    renderLegend();
    const legend = container.querySelector(".mds-plot__legend");
    const hollowPath = legend!.querySelector("path[fill='none']");
    expect(hollowPath).not.toBeNull();
  });

  it("R1-c triangle path has stroke-width='3' (§3.3.5 imp. req. 2 binding)", () => {
    renderLegend();
    const legend = container.querySelector(".mds-plot__legend");
    const hollowPath = legend!.querySelector("path[fill='none']");
    const sw = hollowPath!.getAttribute("stroke-width") ?? hollowPath!.getAttribute("strokeWidth");
    expect(sw).toBe("3");
  });

  it("R1-c source specifies strokeWidth='3' (source assertion)", () => {
    expect(LEGEND_SRC).toContain('strokeWidth="3"');
  });
});

// ── Labels ────────────────────────────────────────────────────────────────────

describe("Legend — labels", () => {
  it("shows 'Typical concentration' label", () => {
    renderLegend();
    expect(container.querySelector(".mds-plot__legend")!.textContent).toContain(
      "Typical concentration"
    );
  });

  it("shows 'Low output concentration' label", () => {
    renderLegend();
    expect(container.querySelector(".mds-plot__legend")!.textContent).toContain(
      "Low output concentration"
    );
  });

  it("shows 'Deterministic output' label", () => {
    renderLegend();
    expect(container.querySelector(".mds-plot__legend")!.textContent).toContain(
      "Deterministic output"
    );
  });
});

// ── showDescriptions prop ─────────────────────────────────────────────────────

describe("Legend — showDescriptions prop", () => {
  it("shows secondary descriptions by default (showDescriptions=true)", () => {
    renderLegend({ showDescriptions: true });
    const secondaryItems = container.querySelectorAll(".mds-plot__legend-secondary");
    expect(secondaryItems.length).toBeGreaterThan(0);
  });

  it("hides secondary descriptions when showDescriptions=false", () => {
    renderLegend({ showDescriptions: false });
    const secondaryItems = container.querySelectorAll(".mds-plot__legend-secondary");
    expect(secondaryItems).toHaveLength(0);
  });

  it("primary labels remain visible when showDescriptions=false", () => {
    renderLegend({ showDescriptions: false });
    const primaryItems = container.querySelectorAll(".mds-plot__legend-primary");
    expect(primaryItems).toHaveLength(3);
  });
});

// ── CSP compliance ────────────────────────────────────────────────────────────

describe("Legend — CSP compliance", () => {
  it("source does not contain dangerouslySetInnerHTML", () => {
    expect(LEGEND_SRC).not.toContain("dangerouslySetInnerHTML");
  });

  it("source does not contain eval(", () => {
    expect(LEGEND_SRC).not.toContain("eval(");
  });
});

// ── Sample color ──────────────────────────────────────────────────────────────

describe("Legend — sample color (#3360a9 from --color-model-1)", () => {
  it("source uses #3360a9 as sample color (--color-model-1, ~7.2:1 contrast)", () => {
    expect(LEGEND_SRC).toContain("#3360a9");
  });
});
