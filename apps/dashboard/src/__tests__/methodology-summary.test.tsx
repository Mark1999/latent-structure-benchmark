// @vitest-environment jsdom
/**
 * Tests for MethodologySummary component — T13
 *
 * Uses jsdom environment (per-file override via @vitest-environment directive).
 * Renders components with React 19 createRoot + act().
 *
 * Verifies:
 *   1. SME-approved body text renders in the body paragraph.
 *   2. Tagline text renders in the tagline paragraph.
 *   3. <h2> with id "methodology-summary-heading" and text "About this measurement".
 *   4. <section> has aria-labelledby="methodology-summary-heading".
 *   5. methodologyPageUrl=null → footnote is plain text, no <a> element.
 *   6. methodologyPageUrl="/methodology" → footnote contains <a href="/methodology">.
 *   7. Tagline paragraph has class methodology-summary__tagline; body has methodology-summary__body.
 *
 * Source: docs/status/2026-05-11-phase5-T13-uiux-plan-verdict.md
 *         DESIGN_SYSTEM.md §12.7 (v0.4.4)
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { MethodologySummary } from "../components/MethodologySummary";
import type { MethodologySummaryProps } from "../components/MethodologySummary";
import { methodologySummary, methodologyFootnote, taglineQuote } from "../copy/methodology_summary";

// ── Render helper ─────────────────────────────────────────────────────────────

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

function renderComponent(props: MethodologySummaryProps = {}): void {
  act(() => {
    root.render(createElement(MethodologySummary, props));
  });
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("MethodologySummary — body text", () => {
  it("renders the SME-approved methodology summary text in the body paragraph", () => {
    renderComponent();
    const bodyEl = container.querySelector(".methodology-summary__body");
    expect(bodyEl).not.toBeNull();
    // Confirm the opening of the six-sentence prose is present.
    expect(bodyEl?.textContent).toContain("Cultural Domain Analysis (CDA)");
  });

  it("body paragraph textContent matches the verbatim methodologySummary constant", () => {
    renderComponent();
    const bodyEl = container.querySelector(".methodology-summary__body");
    expect(bodyEl?.textContent).toBe(methodologySummary);
  });
});

describe("MethodologySummary — tagline text", () => {
  it("renders the tagline text in the tagline paragraph", () => {
    renderComponent();
    const taglineEl = container.querySelector(".methodology-summary__tagline");
    expect(taglineEl).not.toBeNull();
    expect(taglineEl?.textContent).toBe(taglineQuote);
  });

  it("tagline paragraph has class methodology-summary__tagline", () => {
    renderComponent();
    const taglineEl = container.querySelector(".methodology-summary__tagline");
    expect(taglineEl?.tagName).toBe("P");
    expect(taglineEl?.className).toBe("methodology-summary__tagline");
  });
});

describe("MethodologySummary — heading", () => {
  it("renders <h2> with id 'methodology-summary-heading' and text 'About this measurement'", () => {
    renderComponent();
    const heading = container.querySelector("h2#methodology-summary-heading");
    expect(heading).not.toBeNull();
    expect(heading?.textContent).toBe("About this measurement");
    expect(heading?.className).toBe("methodology-summary__heading");
  });

  it("heading is an h2 element (not h1, h3 or other)", () => {
    renderComponent();
    const h2 = container.querySelector("h2");
    expect(h2).not.toBeNull();
    expect(h2?.id).toBe("methodology-summary-heading");
    // Ensure no h1 or h3 exists inside the component.
    expect(container.querySelector("h1")).toBeNull();
    expect(container.querySelector("h3")).toBeNull();
  });
});

describe("MethodologySummary — ARIA", () => {
  it("<section> has aria-labelledby='methodology-summary-heading'", () => {
    renderComponent();
    const section = container.querySelector("section.methodology-summary");
    expect(section).not.toBeNull();
    expect(section?.getAttribute("aria-labelledby")).toBe("methodology-summary-heading");
  });
});

describe("MethodologySummary — footnote conditional rendering", () => {
  it("with methodologyPageUrl=null → footnote is plain text, no <a> element (F-T13-5)", () => {
    renderComponent({ methodologyPageUrl: null });
    const footnoteEl = container.querySelector(".methodology-summary__footnote");
    expect(footnoteEl).not.toBeNull();
    expect(footnoteEl?.textContent).toBe(methodologyFootnote);
    // No anchor element inside the footnote.
    expect(footnoteEl?.querySelector("a")).toBeNull();
  });

  it("with default (no prop) → footnote is plain text, no <a> element", () => {
    renderComponent();
    const footnoteEl = container.querySelector(".methodology-summary__footnote");
    expect(footnoteEl).not.toBeNull();
    expect(footnoteEl?.querySelector("a")).toBeNull();
  });

  it("with methodologyPageUrl='/methodology' → footnote contains <a href='/methodology'>", () => {
    renderComponent({ methodologyPageUrl: "/methodology" });
    const footnoteEl = container.querySelector(".methodology-summary__footnote");
    expect(footnoteEl).not.toBeNull();
    const link = footnoteEl?.querySelector("a");
    expect(link).not.toBeNull();
    expect(link?.getAttribute("href")).toBe("/methodology");
    expect(link?.textContent).toContain("Read the full methodology page");
  });

  it("footnote with URL includes both footnote prose and the link text", () => {
    renderComponent({ methodologyPageUrl: "/methodology" });
    const footnoteEl = container.querySelector(".methodology-summary__footnote");
    expect(footnoteEl?.textContent).toContain("A full methodology page");
    expect(footnoteEl?.textContent).toContain("Read the full methodology page");
  });
});

describe("MethodologySummary — CSS classes", () => {
  it("body paragraph has class methodology-summary__body", () => {
    renderComponent();
    const bodyEl = container.querySelector(".methodology-summary__body");
    expect(bodyEl?.tagName).toBe("P");
    expect(bodyEl?.className).toBe("methodology-summary__body");
  });

  it("outer element is a <section> with class methodology-summary", () => {
    renderComponent();
    const section = container.querySelector("section.methodology-summary");
    expect(section).not.toBeNull();
  });
});
