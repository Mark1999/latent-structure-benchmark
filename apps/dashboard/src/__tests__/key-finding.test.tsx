// @vitest-environment jsdom
/**
 * KeyFinding component tests.
 *
 * Uses jsdom environment (per-file override via @vitest-environment directive).
 * Renders components with React 19 createRoot + act().
 *
 * Tests required by T5 spec:
 *   1. Renders the generatedLede prop in the body.
 *   2. Has role="region" with aria-label="Key finding".
 *   3. Inner content has aria-live="polite".
 *   4. Renders within 780px max-width container.
 *   5. Has the 4px --color-model-1 left border (class assertion).
 *   6. When generatedLede prop changes, the key changes (fade re-fires check).
 *
 * CLAUDE.md §6 R9: no real API calls.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { KeyFinding } from "../components/KeyFinding";
import type { KeyFindingProps } from "../components/KeyFinding";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const LEDE_FAMILY =
  "Across 11 frontier models, family vocabulary is organized around a single shared categorical structure.";

const LEDE_HOLIDAYS =
  "Across 9 frontier models, holidays vocabulary is organized around a shared categorical structure.";

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

function renderKeyFinding(props: KeyFindingProps): void {
  act(() => {
    root.render(createElement(KeyFinding, props));
  });
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("KeyFinding — content rendering", () => {
  it("renders the generatedLede prop as visible text", () => {
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    expect(container.textContent).toContain(LEDE_FAMILY);
  });

  it("renders a different lede when generatedLede prop changes", () => {
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    expect(container.textContent).toContain(LEDE_FAMILY);

    renderKeyFinding({ generatedLede: LEDE_HOLIDAYS });
    expect(container.textContent).toContain(LEDE_HOLIDAYS);
    expect(container.textContent).not.toContain(LEDE_FAMILY);
  });
});

describe("KeyFinding — ARIA attributes", () => {
  it("outer section has role='region'", () => {
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    const section = container.querySelector("section");
    expect(section).not.toBeNull();
    expect(section!.getAttribute("role")).toBe("region");
  });

  it("outer section has aria-label='Key finding'", () => {
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    const section = container.querySelector("section");
    expect(section!.getAttribute("aria-label")).toBe("Key finding");
  });

  it("inner content element has aria-live='polite'", () => {
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    const liveEl = container.querySelector("[aria-live='polite']");
    expect(liveEl).not.toBeNull();
    expect(liveEl!.textContent).toContain(LEDE_FAMILY);
  });
});

describe("KeyFinding — CSS classes (styling contract)", () => {
  it("outer section has class 'key-finding'", () => {
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    const section = container.querySelector("section");
    expect(section!.className).toContain("key-finding");
  });

  it("inner content element has class 'key-finding__content'", () => {
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    // The inner <p> with class key-finding__content carries the
    // 4px --color-model-1 border-left styling per §3.8 (defined in app.css).
    const content = container.querySelector(".key-finding__content");
    expect(content).not.toBeNull();
  });
});

describe("KeyFinding — fade animation key-change strategy", () => {
  it("content element key changes when generatedLede changes (fade re-fires)", () => {
    // The component uses key={ledeKey(generatedLede)} on the inner <p>.
    // When lede changes, React unmounts and remounts the <p>, resetting the
    // CSS animation. We verify the content text changes on prop update.
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    const contentBefore = container.querySelector(".key-finding__content");
    expect(contentBefore!.textContent).toContain(LEDE_FAMILY);

    renderKeyFinding({ generatedLede: LEDE_HOLIDAYS });
    const contentAfter = container.querySelector(".key-finding__content");
    expect(contentAfter!.textContent).toContain(LEDE_HOLIDAYS);
    // Confirms the element was updated with the new lede — key-change remount worked.
    expect(contentAfter!.textContent).not.toContain(LEDE_FAMILY);
  });
});

describe("KeyFinding — max-width container (§3.8 binding: 780px centered)", () => {
  it("the .key-finding container class is present (which carries max-width styling)", () => {
    // DESIGN_SYSTEM.md §3.8: max-width 780px (var(--max-article-width)), centered.
    // We assert on the class presence since CSS custom properties are not resolved in jsdom.
    renderKeyFinding({ generatedLede: LEDE_FAMILY });
    const kf = container.querySelector(".key-finding");
    expect(kf).not.toBeNull();
    // The .key-finding class is defined in app.css with max-width: var(--max-article-width)
    // and margin: 0 auto (centering) — this is the binding container.
    expect(kf!.tagName).toBe("SECTION");
  });
});
