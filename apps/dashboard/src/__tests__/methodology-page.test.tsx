// @vitest-environment jsdom
/**
 * Tests for MethodologyPagePlaceholder component and /methodology route — Phase 8 T10.
 *
 * Uses jsdom environment (per-file override via @vitest-environment directive).
 * Renders components with React 19 createRoot + act().
 *
 * Assertions required by UI/UX verdict 2026-05-19-phase8-T10-ui-ux-verdict.md
 * (required-before-merge item 3):
 *
 *   P1. <h1> present with text "Methodology".
 *   P2. Body contains "in preparation".
 *   P3. Link href equals the file-root GitHub URL with no "#" suffix.
 *   P4. Rendered HTML does NOT contain forbidden vocabulary:
 *       "worldview", "believes", "thinks" (model-attribution), "coming in Phase 6".
 *
 * Additional structural assertions:
 *   P5. Copy constants from methodology_page.ts match rendered output verbatim.
 *   P6. archLinkHref has no "#" anchor character.
 *   P7. isMethodologyPage() helper returns true when pathname is "/methodology".
 *   P8. isMethodologyPage() helper returns false for other pathnames.
 *
 * Source:
 *   docs/status/2026-05-19-phase8-T10-ui-ux-verdict.md (required-before-merge item 3)
 *   CLAUDE.md §7 (forbidden vocabulary)
 *   DESIGN_SYSTEM.md §2.1
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

import { MethodologyPagePlaceholder } from "../components/MethodologyPagePlaceholder";
import {
  pageTitle,
  pageBody,
  archLinkText,
  archLinkHref,
} from "../copy/methodology_page";

// ── ESM-compatible __dirname ───────────────────────────────────────────────────

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ── Static source reads ────────────────────────────────────────────────────────

const APP_TSX_SRC = readFileSync(
  resolve(__dirname, "../App.tsx"),
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

function renderPlaceholder(): void {
  act(() => {
    root.render(createElement(MethodologyPagePlaceholder));
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// P1 — <h1> present with text "Methodology"
// ══════════════════════════════════════════════════════════════════════════════

describe("P1 — <h1> present with text 'Methodology' (UI/UX RBM 3)", () => {
  it("<h1> element is present in the rendered output", () => {
    renderPlaceholder();
    const h1 = container.querySelector("h1");
    expect(h1).not.toBeNull();
  });

  it("<h1> text content is 'Methodology' exactly", () => {
    renderPlaceholder();
    const h1 = container.querySelector("h1");
    expect(h1?.textContent).toBe("Methodology");
  });

  it("<h1> text matches the pageTitle constant from methodology_page.ts", () => {
    renderPlaceholder();
    const h1 = container.querySelector("h1");
    expect(h1?.textContent).toBe(pageTitle);
  });

  it("pageTitle constant is exactly 'Methodology'", () => {
    expect(pageTitle).toBe("Methodology");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// P2 — Body contains "in preparation"
// ══════════════════════════════════════════════════════════════════════════════

describe("P2 — Body contains 'in preparation' (UI/UX RBM 3)", () => {
  it("rendered HTML contains 'in preparation'", () => {
    renderPlaceholder();
    expect(container.textContent).toContain("in preparation");
  });

  it("pageBody constant contains 'in preparation'", () => {
    expect(pageBody).toContain("in preparation");
  });

  it("pageBody constant is rendered verbatim in the component", () => {
    renderPlaceholder();
    expect(container.textContent).toContain(pageBody);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// P3 — Link href equals the file-root GitHub URL with no "#" suffix
// ══════════════════════════════════════════════════════════════════════════════

describe("P3 — Link href is the file-root GitHub URL with no '#' anchor (UI/UX RBM 3)", () => {
  it("an <a> element with the GitHub ARCHITECTURE.md href is present", () => {
    renderPlaceholder();
    const link = container.querySelector<HTMLAnchorElement>(
      `a[href="${archLinkHref}"]`
    );
    expect(link).not.toBeNull();
  });

  it("link href equals the canonical archLinkHref constant exactly", () => {
    renderPlaceholder();
    const links = container.querySelectorAll<HTMLAnchorElement>("a");
    const archLink = Array.from(links).find(
      (a) => a.getAttribute("href") === archLinkHref
    );
    expect(archLink).not.toBeNull();
    expect(archLink?.getAttribute("href")).toBe(
      "https://github.com/Mark1999/latent-structure-benchmark/blob/master/ARCHITECTURE.md"
    );
  });

  it("archLinkHref does not contain a '#' anchor character (UI/UX RBM 1 — no heading anchor)", () => {
    expect(archLinkHref).not.toContain("#");
  });

  it("archLinkHref ends with 'ARCHITECTURE.md' (file root, no suffix)", () => {
    expect(archLinkHref.endsWith("ARCHITECTURE.md")).toBe(true);
  });

  it("archLinkHref contains 'Mark1999/latent-structure-benchmark' (actual repo path)", () => {
    expect(archLinkHref).toContain("Mark1999/latent-structure-benchmark");
  });

  it("link text content matches archLinkText", () => {
    renderPlaceholder();
    const links = container.querySelectorAll<HTMLAnchorElement>("a");
    const archLink = Array.from(links).find(
      (a) => a.getAttribute("href") === archLinkHref
    );
    expect(archLink?.textContent?.trim()).toBe(archLinkText);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// P4 — Forbidden vocabulary absent from rendered HTML (UI/UX RBM 3 / CLAUDE.md §7)
// ══════════════════════════════════════════════════════════════════════════════

describe("P4 — Forbidden vocabulary absent from rendered output (CLAUDE.md §7 / UI/UX RBM 3)", () => {
  it("rendered text does not contain 'worldview'", () => {
    renderPlaceholder();
    expect(container.textContent?.toLowerCase()).not.toMatch(/\bworldview\b/);
  });

  it("rendered text does not contain 'believes'", () => {
    renderPlaceholder();
    expect(container.textContent?.toLowerCase()).not.toMatch(/\bbelieves\b/);
  });

  it("rendered text does not contain 'thinks' (model-attribution form)", () => {
    renderPlaceholder();
    // Check only textContent (not source), since "thinks" is not expected in copy.
    expect(container.textContent?.toLowerCase()).not.toMatch(/\bthinks\b/);
  });

  it("rendered text does not contain 'coming in Phase 6'", () => {
    renderPlaceholder();
    expect(container.textContent).not.toContain("coming in Phase 6");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// P5 — Copy constants match rendered output verbatim
// ══════════════════════════════════════════════════════════════════════════════

describe("P5 — Copy constants from methodology_page.ts match rendered output", () => {
  it("archLinkText constant is rendered as the link's text content", () => {
    renderPlaceholder();
    const links = container.querySelectorAll<HTMLAnchorElement>("a");
    const archLink = Array.from(links).find(
      (a) => a.getAttribute("href") === archLinkHref
    );
    expect(archLink?.textContent?.trim()).toBe(archLinkText);
  });

  it("archLinkText contains '§1.5' (ARCHITECTURE.md section reference)", () => {
    expect(archLinkText).toContain("§1.5");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// P6 — archLinkHref structural integrity
// ══════════════════════════════════════════════════════════════════════════════

describe("P6 — archLinkHref structural integrity", () => {
  it("archLinkHref starts with 'https://'", () => {
    expect(archLinkHref.startsWith("https://")).toBe(true);
  });

  it("archLinkHref points to github.com", () => {
    expect(archLinkHref).toContain("github.com");
  });

  it("archLinkHref contains '/blob/master/'", () => {
    expect(archLinkHref).toContain("/blob/master/");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// P7/P8 — isMethodologyPage() helper in App.tsx source (static text checks)
// ══════════════════════════════════════════════════════════════════════════════
// jsdom pathname is always '/'; we cannot navigate routes in unit tests.
// Static source-text checks confirm the helper is present and correct.

describe("P7/P8 — isMethodologyPage() helper in App.tsx source", () => {
  it("App.tsx contains 'function isMethodologyPage'", () => {
    expect(APP_TSX_SRC).toContain("function isMethodologyPage");
  });

  it("isMethodologyPage checks pathname === '/methodology'", () => {
    expect(APP_TSX_SRC).toContain("pathname === \"/methodology\"");
  });

  it("isMethodologyPage is wrapped in try/catch (mirrors isEmbedMode / isInspectMode pattern)", () => {
    const fnStart = APP_TSX_SRC.indexOf("function isMethodologyPage");
    const fnEnd = APP_TSX_SRC.indexOf("\nfunction ", fnStart + 1);
    const fnBody =
      fnEnd > 0
        ? APP_TSX_SRC.slice(fnStart, fnEnd)
        : APP_TSX_SRC.slice(fnStart, fnStart + 300);
    expect(fnBody).toContain("try {");
    expect(fnBody).toContain("} catch {");
  });

  it("App.tsx renders <MethodologyPagePlaceholder /> when methodologyPage is true", () => {
    expect(APP_TSX_SRC).toContain("return <MethodologyPagePlaceholder />");
  });

  it("App.tsx does NOT pass methodologyPageUrl to MethodologySummary (Phase 9a: MethodologySummary not in App.tsx)", () => {
    // Phase 9a app-shell: MethodologySummary is no longer rendered from App.tsx.
    // The /methodology route is served via MethodologyPagePlaceholder instead.
    // methodologyPageUrl prop usage is now in MethodologySummary.tsx itself if needed.
    expect(APP_TSX_SRC).not.toContain('methodologyPageUrl="/methodology"');
  });
});
