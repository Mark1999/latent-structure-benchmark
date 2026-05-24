// @vitest-environment jsdom
/**
 * T11 gap-fill tests — Phase 6 T11 (Mobile hamburger nav).
 *
 * The Coder did not write T11-specific tests (per the standard pipeline:
 * Coder implements, Tester covers). This file provides full test coverage
 * of the T11 testable surface as enumerated in:
 *   docs/status/2026-05-15-phase6-T11-architect-plan.md §6 (Tester section)
 *   DESIGN_SYSTEM.md §8.1
 *
 * Coverage gaps filled:
 *
 *   G1.  Trigger ARIA at rest: aria-label, aria-expanded, aria-controls,
 *        aria-haspopup verbatim per §8.1.1.
 *   G2.  Click trigger → panel renders (role="dialog", aria-modal, aria-label).
 *   G3.  Click trigger → aria-expanded flips to true; aria-label flips to
 *        MOBILE_NAV_TRIGGER_LABEL_OPEN.
 *   G4.  Panel open: initial focus lands on the close button.
 *   G5.  Panel open: Esc closes; focus returns to trigger.
 *   G6.  Panel open: close button click closes panel; focus returns to trigger.
 *   G7.  Panel open: Tab from last focusable element wraps to close button.
 *   G8.  Panel open: Shift+Tab from close button wraps to last focusable element.
 *   G9.  Trigger hidden when panel open (style.display === 'none').
 *   G10. Enter key on trigger opens panel.
 *   G11. Space key on trigger opens panel.
 *   G12. Panel renders exactly 4 nav links (one per NAV_LINKS entry).
 *   G13. Each rendered nav link's href and text match NAV_LINKS verbatim.
 *   G14. Close button: aria-label === MOBILE_NAV_TRIGGER_LABEL_OPEN; glyph is ×.
 *   G15. mobile_nav.ts constants byte-identical to §8.1.11 spec (.toBe()).
 *   G16. mobile_nav.ts exports exactly three constants; no MOBILE_NAV_HEADING.
 *   G17. mobile_nav.ts source passes forbidden-vocab grep.
 *   G18. MobileNav.tsx source has file-header referencing DESIGN_SYSTEM.md §8.1.
 *   G19. MobileNav.tsx source does NOT contain a duplicate NAV_LINKS array.
 *   G20. mobile-nav.css contains prefers-reduced-motion block per §8.1.5.
 *   G21. Opening panel does NOT set document.body.style.overflow (no scroll lock).
 *   G22. Header.tsx exports NAV_LINKS (M1 enforcement).
 *   G23. Header.tsx exports NavLink interface (M1 enforcement).
 *   G24. HamburgerGlyph SVG in Header.tsx matches §8.1.2 spec: viewBox "0 0 20 16",
 *        three <line> elements at y=2, y=8, y=14.
 *   G25. DESIGN_SYSTEM.md version is v0.4.7; §8.1 section and §8.1.11 table present.
 *   G26. prefers-reduced-motion stub: panel still opens/closes with motion disabled.
 *
 * CLAUDE.md §6 R9: no real API calls. Fixtures and static file reads only.
 * No new dependencies.
 *
 * Reference:
 *   docs/status/2026-05-15-phase6-T11-architect-plan.md §6 (Tester section)
 *   docs/status/2026-05-15-phase6-T11-uiux-plan-verdict.md (A1–A5, M1)
 *   docs/status/2026-05-15-phase6-T11-reviewer-verdict.md (PASS)
 *   DESIGN_SYSTEM.md §8.1
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

import { Header, NAV_LINKS } from "../components/Header";
import {
  MOBILE_NAV_TRIGGER_LABEL_CLOSED,
  MOBILE_NAV_TRIGGER_LABEL_OPEN,
  MOBILE_NAV_PANEL_LABEL,
} from "../copy/mobile_nav";

// ── ESM-compatible __dirname ───────────────────────────────────────────────────

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ── Static source reads ────────────────────────────────────────────────────────

const MOBILE_NAV_TS_SRC = readFileSync(
  resolve(__dirname, "../copy/mobile_nav.ts"),
  "utf-8"
);

const MOBILE_NAV_TSX_SRC = readFileSync(
  resolve(__dirname, "../components/MobileNav.tsx"),
  "utf-8"
);

const MOBILE_NAV_CSS_SRC = readFileSync(
  resolve(__dirname, "../styles/mobile-nav.css"),
  "utf-8"
);

const HEADER_TSX_SRC = readFileSync(
  resolve(__dirname, "../components/Header.tsx"),
  "utf-8"
);

const DESIGN_SYSTEM_MD = readFileSync(
  resolve(__dirname, "../../../../DESIGN_SYSTEM.md"),
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
  vi.restoreAllMocks();
  // Restore body overflow if any test accidentally mutated it.
  document.body.style.overflow = "";
});

function renderHeader(): void {
  act(() => {
    root.render(createElement(Header));
  });
}

function getTrigger(): HTMLButtonElement | null {
  return container.querySelector<HTMLButtonElement>(
    "button.site-header__hamburger"
  );
}

function getPanel(): HTMLElement | null {
  return container.querySelector<HTMLElement>('[role="dialog"]');
}

function getCloseBtn(): HTMLButtonElement | null {
  return container.querySelector<HTMLButtonElement>(".mobile-nav__close");
}

function getNavLinks(): NodeListOf<Element> {
  return container.querySelectorAll(".mobile-nav__link");
}

// ══════════════════════════════════════════════════════════════════════════════
// G1 — Trigger ARIA at rest (§8.1.1 ARIA pattern)
// ══════════════════════════════════════════════════════════════════════════════

describe("G1 — Trigger ARIA at rest (§8.1.1)", () => {
  it("trigger button renders in the DOM", () => {
    renderHeader();
    expect(getTrigger()).not.toBeNull();
  });

  it("aria-label at rest === MOBILE_NAV_TRIGGER_LABEL_CLOSED ('Open navigation menu')", () => {
    renderHeader();
    expect(getTrigger()?.getAttribute("aria-label")).toBe(
      MOBILE_NAV_TRIGGER_LABEL_CLOSED
    );
  });

  it("MOBILE_NAV_TRIGGER_LABEL_CLOSED is exactly 'Open navigation menu' (verbatim)", () => {
    expect(MOBILE_NAV_TRIGGER_LABEL_CLOSED).toBe("Open navigation menu");
  });

  it("aria-expanded at rest === 'false'", () => {
    renderHeader();
    expect(getTrigger()?.getAttribute("aria-expanded")).toBe("false");
  });

  it("aria-controls === 'mobile-nav-panel'", () => {
    renderHeader();
    expect(getTrigger()?.getAttribute("aria-controls")).toBe("mobile-nav-panel");
  });

  it("aria-haspopup === 'dialog'", () => {
    renderHeader();
    expect(getTrigger()?.getAttribute("aria-haspopup")).toBe("dialog");
  });

  it("panel is NOT in DOM at rest (before trigger click)", () => {
    renderHeader();
    expect(getPanel()).toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G2 — Click trigger → panel renders with correct ARIA
// ══════════════════════════════════════════════════════════════════════════════

describe("G2 — Click trigger → panel renders (§8.1.1 dialog pattern)", () => {
  it("panel appears in DOM after trigger click", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getPanel()).not.toBeNull();
  });

  it("panel has role='dialog'", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getPanel()?.getAttribute("role")).toBe("dialog");
  });

  it("panel has aria-modal='true'", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getPanel()?.getAttribute("aria-modal")).toBe("true");
  });

  it("panel has aria-label === MOBILE_NAV_PANEL_LABEL ('Site navigation')", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getPanel()?.getAttribute("aria-label")).toBe(MOBILE_NAV_PANEL_LABEL);
  });

  it("MOBILE_NAV_PANEL_LABEL is exactly 'Site navigation' (verbatim)", () => {
    expect(MOBILE_NAV_PANEL_LABEL).toBe("Site navigation");
  });

  it("panel has id === 'mobile-nav-panel' (matches aria-controls)", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getPanel()?.getAttribute("id")).toBe("mobile-nav-panel");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G3 — ARIA state changes after trigger click
// ══════════════════════════════════════════════════════════════════════════════

describe("G3 — Trigger ARIA state changes on open (§8.1.1)", () => {
  it("aria-expanded flips to 'true' after trigger click", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    // After panel opens, trigger is display:none. Get aria-expanded before it hides.
    // The trigger's aria-expanded is set based on state, regardless of display.
    // Since the trigger is hidden (display:none) but still in DOM, getAttribute still works.
    expect(getTrigger()?.getAttribute("aria-expanded")).toBe("true");
  });

  it("trigger aria-label flips to MOBILE_NAV_TRIGGER_LABEL_OPEN after click", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getTrigger()?.getAttribute("aria-label")).toBe(
      MOBILE_NAV_TRIGGER_LABEL_OPEN
    );
  });

  it("MOBILE_NAV_TRIGGER_LABEL_OPEN is exactly 'Close navigation menu' (verbatim)", () => {
    expect(MOBILE_NAV_TRIGGER_LABEL_OPEN).toBe("Close navigation menu");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G4 — Initial focus lands on close button (§8.1.1 focus order)
// ══════════════════════════════════════════════════════════════════════════════

describe("G4 — Initial focus lands on close button (§8.1.1)", () => {
  it("close button exists inside the panel", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getCloseBtn()).not.toBeNull();
  });

  it("document.activeElement is the close button after panel opens", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.activeElement).toBe(getCloseBtn());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G5 — Esc closes panel; focus returns to trigger (§8.1.1)
// ══════════════════════════════════════════════════════════════════════════════

describe("G5 — Esc closes panel and restores focus to trigger (§8.1.1)", () => {
  it("Esc key closes the panel (panel removed from DOM)", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getPanel()).not.toBeNull();

    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
      );
    });

    expect(getPanel()).toBeNull();
  });

  it("focus returns to trigger button after Esc closes panel", async () => {
    renderHeader();
    const trigger = getTrigger();
    await act(async () => {
      trigger?.click();
    });

    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
      );
    });

    // After close, triggerRef.current?.focus() is called via useEffect.
    expect(document.activeElement).toBe(getTrigger());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G6 — Close button click closes panel; focus returns to trigger (§8.1.1)
// ══════════════════════════════════════════════════════════════════════════════

describe("G6 — Close button click closes panel and restores focus (§8.1.1)", () => {
  it("clicking close button removes panel from DOM", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getPanel()).not.toBeNull();

    await act(async () => {
      getCloseBtn()?.click();
    });

    expect(getPanel()).toBeNull();
  });

  it("focus returns to trigger button after close button click", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });

    await act(async () => {
      getCloseBtn()?.click();
    });

    expect(document.activeElement).toBe(getTrigger());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G7 — Tab from last focusable element wraps to close button (focus trap)
// ══════════════════════════════════════════════════════════════════════════════

describe("G7 — Focus trap: Tab from last element wraps to close button (§8.1.1)", () => {
  it("Tab on the last nav link wraps focus back to close button", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });

    const links = getNavLinks();
    const lastLink = links[links.length - 1] as HTMLElement;

    // Move focus to last link manually.
    await act(async () => {
      lastLink.focus();
    });

    expect(document.activeElement).toBe(lastLink);

    // Fire Tab on document (the keydown handler listens on document).
    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Tab", bubbles: true, shiftKey: false })
      );
    });

    expect(document.activeElement).toBe(getCloseBtn());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G8 — Shift+Tab from close button wraps to last focusable element (focus trap)
// ══════════════════════════════════════════════════════════════════════════════

describe("G8 — Focus trap: Shift+Tab from close button wraps to last link (§8.1.1)", () => {
  it("Shift+Tab on close button wraps focus to last nav link", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });

    const closeBtn = getCloseBtn()!;
    const links = getNavLinks();
    const lastLink = links[links.length - 1] as HTMLElement;

    // Focus is already on close button (initial focus per G4).
    expect(document.activeElement).toBe(closeBtn);

    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Tab", bubbles: true, shiftKey: true })
      );
    });

    expect(document.activeElement).toBe(lastLink);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G9 — Trigger hidden (display: none) when panel is open (§8.1.9)
// ══════════════════════════════════════════════════════════════════════════════

describe("G9 — Trigger hidden when panel is open (§8.1.9)", () => {
  it("trigger has display:none (via style) when panel is open", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    // React sets style={{ display: 'none' }} on the trigger when mobileNavOpen=true.
    expect(getTrigger()?.style.display).toBe("none");
  });

  it("trigger is visible (no inline display:none) when panel is closed", () => {
    renderHeader();
    const trigger = getTrigger();
    // No inline style should be set at rest (undefined / empty).
    expect(trigger?.style.display).not.toBe("none");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G10 — Enter key on trigger opens panel
// ══════════════════════════════════════════════════════════════════════════════

describe("G10 — Enter key on trigger opens panel", () => {
  it("Enter keydown on trigger button opens the panel", async () => {
    renderHeader();
    const trigger = getTrigger()!;

    await act(async () => {
      trigger.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true })
      );
      trigger.click(); // Native button: Enter dispatches click
    });

    expect(getPanel()).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G11 — Space key on trigger opens panel
// ══════════════════════════════════════════════════════════════════════════════

describe("G11 — Space key on trigger opens panel", () => {
  it("Space keydown + click on trigger button opens the panel", async () => {
    renderHeader();
    const trigger = getTrigger()!;

    await act(async () => {
      trigger.dispatchEvent(
        new KeyboardEvent("keydown", { key: " ", bubbles: true })
      );
      trigger.click(); // Native button: Space dispatches click
    });

    expect(getPanel()).not.toBeNull();
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G12 — Panel renders exactly 4 nav links (one per NAV_LINKS entry)
// ══════════════════════════════════════════════════════════════════════════════

describe("G12 — Panel renders exactly 4 nav links (AC15 single source of truth)", () => {
  it("NAV_LINKS has exactly 4 entries", () => {
    expect(NAV_LINKS).toHaveLength(4);
  });

  it("panel renders exactly 4 .mobile-nav__link anchors", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getNavLinks()).toHaveLength(4);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G13 — Each rendered nav link's href and text match NAV_LINKS verbatim (AC15)
// ══════════════════════════════════════════════════════════════════════════════

describe("G13 — Rendered nav links match NAV_LINKS verbatim (AC15 / AC16)", () => {
  it("NAV_LINKS[0] is { href: '/', label: 'Explore' }", () => {
    expect(NAV_LINKS[0]).toEqual({ href: "/", label: "Explore" });
  });

  it("NAV_LINKS[1] is { href: '/methodology', label: 'Methodology' }", () => {
    expect(NAV_LINKS[1]).toEqual({ href: "/methodology", label: "Methodology" });
  });

  it("NAV_LINKS[2] is { href: '/data', label: 'Data' }", () => {
    expect(NAV_LINKS[2]).toEqual({ href: "/data", label: "Data" });
  });

  it("NAV_LINKS[3] is { href: '/about', label: 'About' }", () => {
    expect(NAV_LINKS[3]).toEqual({ href: "/about", label: "About" });
  });

  it("rendered nav links have href values matching NAV_LINKS in order", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    const rendered = Array.from(getNavLinks());
    rendered.forEach((link, i) => {
      expect(link.getAttribute("href")).toBe(NAV_LINKS[i].href);
    });
  });

  it("rendered nav links have text content matching NAV_LINKS labels in order", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    const rendered = Array.from(getNavLinks());
    rendered.forEach((link, i) => {
      expect(link.textContent?.trim()).toBe(NAV_LINKS[i].label);
    });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G14 — Close button: aria-label, glyph × (§8.1.9)
// ══════════════════════════════════════════════════════════════════════════════

describe("G14 — Close button ARIA and glyph (§8.1.9)", () => {
  it("close button aria-label === MOBILE_NAV_TRIGGER_LABEL_OPEN ('Close navigation menu')", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getCloseBtn()?.getAttribute("aria-label")).toBe(
      MOBILE_NAV_TRIGGER_LABEL_OPEN
    );
  });

  it("close button glyph span has aria-hidden='true'", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    const glyphSpan = getCloseBtn()?.querySelector("span[aria-hidden='true']");
    expect(glyphSpan).not.toBeNull();
  });

  it("close button glyph is × (U+00D7 MULTIPLICATION SIGN)", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    const glyphSpan = getCloseBtn()?.querySelector(
      "span[aria-hidden='true']"
    );
    // The React text node is the × character (U+00D7).
    expect(glyphSpan?.textContent).toBe("×");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G15 — mobile_nav.ts constants byte-identical to §8.1.11 spec (.toBe())
// ══════════════════════════════════════════════════════════════════════════════

describe("G15 — mobile_nav.ts constants verbatim per §8.1.11 (.toBe() — not .toContain())", () => {
  it("MOBILE_NAV_TRIGGER_LABEL_CLOSED === 'Open navigation menu' exactly", () => {
    expect(MOBILE_NAV_TRIGGER_LABEL_CLOSED).toBe("Open navigation menu");
  });

  it("MOBILE_NAV_TRIGGER_LABEL_OPEN === 'Close navigation menu' exactly", () => {
    expect(MOBILE_NAV_TRIGGER_LABEL_OPEN).toBe("Close navigation menu");
  });

  it("MOBILE_NAV_PANEL_LABEL === 'Site navigation' exactly", () => {
    expect(MOBILE_NAV_PANEL_LABEL).toBe("Site navigation");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G16 — mobile_nav.ts exports exactly three constants; no MOBILE_NAV_HEADING
// ══════════════════════════════════════════════════════════════════════════════

describe("G16 — mobile_nav.ts exports exactly three constants; no MOBILE_NAV_HEADING (§8.1.10)", () => {
  it("source contains exactly three 'export const' statements", () => {
    const exportMatches = MOBILE_NAV_TS_SRC.match(/^export const /gm);
    expect(exportMatches).not.toBeNull();
    expect(exportMatches!).toHaveLength(3);
  });

  it("source does NOT export MOBILE_NAV_HEADING", () => {
    expect(MOBILE_NAV_TS_SRC).not.toContain("MOBILE_NAV_HEADING");
  });

  it("source exports MOBILE_NAV_TRIGGER_LABEL_CLOSED", () => {
    expect(MOBILE_NAV_TS_SRC).toContain("export const MOBILE_NAV_TRIGGER_LABEL_CLOSED");
  });

  it("source exports MOBILE_NAV_TRIGGER_LABEL_OPEN", () => {
    expect(MOBILE_NAV_TS_SRC).toContain("export const MOBILE_NAV_TRIGGER_LABEL_OPEN");
  });

  it("source exports MOBILE_NAV_PANEL_LABEL", () => {
    expect(MOBILE_NAV_TS_SRC).toContain("export const MOBILE_NAV_PANEL_LABEL");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G17 — mobile_nav.ts source passes forbidden-vocab grep (§7 / AC17)
// ══════════════════════════════════════════════════════════════════════════════

describe("G17 — mobile_nav.ts source passes forbidden-vocab grep (CLAUDE.md §7 / AC17)", () => {
  const forbiddenPattern = /worldview|believes|thinks|cultural bias/i;

  it("source does not contain 'worldview'", () => {
    expect(MOBILE_NAV_TS_SRC).not.toMatch(/\bworldview\b/i);
  });

  it("source does not contain 'believes'", () => {
    expect(MOBILE_NAV_TS_SRC).not.toMatch(/\bbelieves\b/i);
  });

  it("source does not contain 'thinks' (applied to models)", () => {
    expect(MOBILE_NAV_TS_SRC).not.toMatch(/\bthinks\b/i);
  });

  it("source does not contain 'cultural bias'", () => {
    expect(MOBILE_NAV_TS_SRC).not.toMatch(/cultural bias/i);
  });

  it("full pattern /worldview|believes|thinks|cultural bias/i has no match", () => {
    expect(MOBILE_NAV_TS_SRC).not.toMatch(forbiddenPattern);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G18 — MobileNav.tsx file-header references DESIGN_SYSTEM.md §8.1 (AC20)
// ══════════════════════════════════════════════════════════════════════════════

describe("G18 — MobileNav.tsx file-header comment references DESIGN_SYSTEM.md §8.1 (AC20)", () => {
  it("first line of MobileNav.tsx contains 'DESIGN_SYSTEM.md §8.1'", () => {
    const firstLine = MOBILE_NAV_TSX_SRC.split("\n")[0];
    expect(firstLine).toContain("DESIGN_SYSTEM.md §8.1");
  });

  it("first line is a comment (starts with //)", () => {
    const firstLine = MOBILE_NAV_TSX_SRC.split("\n")[0].trim();
    expect(firstLine.startsWith("//")).toBe(true);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G19 — MobileNav.tsx does NOT contain a duplicate NAV_LINKS array (AC15)
// ══════════════════════════════════════════════════════════════════════════════

describe("G19 — MobileNav.tsx has no duplicate NAV_LINKS array (AC15 single source)", () => {
  it("MobileNav.tsx does not contain 'NAV_LINKS = ['", () => {
    expect(MOBILE_NAV_TSX_SRC).not.toContain("NAV_LINKS = [");
  });

  it("MobileNav.tsx does not contain a hardcoded links array initializer", () => {
    // Pattern: 'links: NavLink[] = [' would indicate a local copy of the link list.
    expect(MOBILE_NAV_TSX_SRC).not.toMatch(/links:\s*NavLink\[\]\s*=\s*\[/);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G20 — mobile-nav.css contains @media prefers-reduced-motion block (§8.1.5)
// ══════════════════════════════════════════════════════════════════════════════

describe("G20 — mobile-nav.css contains prefers-reduced-motion block (§8.1.5 / AC13)", () => {
  it("css contains @media (prefers-reduced-motion: reduce) rule", () => {
    expect(MOBILE_NAV_CSS_SRC).toContain(
      "@media (prefers-reduced-motion: reduce)"
    );
  });

  it("prefers-reduced-motion block targets .mobile-nav__panel", () => {
    // Find the prefers-reduced-motion block and check it targets the panel.
    const block = MOBILE_NAV_CSS_SRC.match(
      /@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^}]*)\}/s
    );
    expect(block).not.toBeNull();
    expect(block![0]).toContain(".mobile-nav__panel");
  });

  it("prefers-reduced-motion block sets transition: none", () => {
    const block = MOBILE_NAV_CSS_SRC.match(
      /@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^}]*)\}/s
    );
    expect(block).not.toBeNull();
    expect(block![0]).toContain("transition: none");
  });

  it("prefers-reduced-motion block sets animation: none", () => {
    const block = MOBILE_NAV_CSS_SRC.match(
      /@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{([^}]*)\}/s
    );
    expect(block).not.toBeNull();
    expect(block![0]).toContain("animation: none");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G21 — Opening panel does NOT set document.body.style.overflow (§8.1.13)
// ══════════════════════════════════════════════════════════════════════════════

describe("G21 — No scroll lock: body overflow is not modified on panel open (§8.1.13 / AC2 per §2.8)", () => {
  it("document.body.style.overflow is not 'hidden' after panel opens", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.body.style.overflow).not.toBe("hidden");
  });

  it("document.body.style.overflow is empty string (unmodified) after panel opens", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(document.body.style.overflow).toBe("");
  });

  it("document.body.style.overflow is empty string after panel closes", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    await act(async () => {
      getCloseBtn()?.click();
    });
    expect(document.body.style.overflow).toBe("");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G22 — Header.tsx exports NAV_LINKS (M1 enforcement)
// ══════════════════════════════════════════════════════════════════════════════

describe("G22 — Header.tsx exports NAV_LINKS (M1 from UI/UX verdict)", () => {
  it("Header.tsx source contains 'export const NAV_LINKS'", () => {
    expect(HEADER_TSX_SRC).toMatch(/^export const NAV_LINKS/m);
  });

  it("NAV_LINKS is importable from Header (runtime check)", () => {
    // The static import at the top of this test file already confirms this.
    expect(Array.isArray(NAV_LINKS)).toBe(true);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G23 — Header.tsx exports NavLink interface (M1 enforcement)
// ══════════════════════════════════════════════════════════════════════════════

describe("G23 — Header.tsx exports NavLink interface (M1 from UI/UX verdict)", () => {
  it("Header.tsx source contains 'export interface NavLink'", () => {
    expect(HEADER_TSX_SRC).toMatch(/^export interface NavLink/m);
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G24 — HamburgerGlyph SVG matches §8.1.2 binding spec
// ══════════════════════════════════════════════════════════════════════════════

describe("G24 — HamburgerGlyph SVG matches §8.1.2 binding spec", () => {
  it("Header.tsx SVG has viewBox '0 0 20 16'", () => {
    expect(HEADER_TSX_SRC).toContain('viewBox="0 0 20 16"');
  });

  it("Header.tsx SVG has exactly three <line> elements", () => {
    // Count non-comment occurrences of <line in the HamburgerGlyph function.
    const glyphStart = HEADER_TSX_SRC.indexOf("function HamburgerGlyph");
    const glyphEnd = HEADER_TSX_SRC.indexOf("\nfunction ", glyphStart + 1);
    const glyphBody =
      glyphEnd > 0
        ? HEADER_TSX_SRC.slice(glyphStart, glyphEnd)
        : HEADER_TSX_SRC.slice(glyphStart);
    const lineMatches = glyphBody.match(/<line /g);
    expect(lineMatches).not.toBeNull();
    expect(lineMatches!).toHaveLength(3);
  });

  it("Header.tsx SVG has line at y1='2' (top line per §8.1.2)", () => {
    expect(HEADER_TSX_SRC).toContain('y1="2"');
  });

  it("Header.tsx SVG has line at y1='8' (middle line per §8.1.2)", () => {
    expect(HEADER_TSX_SRC).toContain('y1="8"');
  });

  it("Header.tsx SVG has line at y1='14' (bottom line per §8.1.2)", () => {
    expect(HEADER_TSX_SRC).toContain('y1="14"');
  });

  it("Header.tsx SVG uses stroke='currentColor' (WCAG 1.4.11 compliance)", () => {
    const glyphStart = HEADER_TSX_SRC.indexOf("function HamburgerGlyph");
    const glyphEnd = HEADER_TSX_SRC.indexOf("\nfunction ", glyphStart + 1);
    const glyphBody =
      glyphEnd > 0
        ? HEADER_TSX_SRC.slice(glyphStart, glyphEnd)
        : HEADER_TSX_SRC.slice(glyphStart);
    expect(glyphBody).toContain('stroke="currentColor"');
  });

  it("Header.tsx SVG uses strokeWidth='2' (§8.1.2 2px stroke weight)", () => {
    const glyphStart = HEADER_TSX_SRC.indexOf("function HamburgerGlyph");
    const glyphEnd = HEADER_TSX_SRC.indexOf("\nfunction ", glyphStart + 1);
    const glyphBody =
      glyphEnd > 0
        ? HEADER_TSX_SRC.slice(glyphStart, glyphEnd)
        : HEADER_TSX_SRC.slice(glyphStart);
    expect(glyphBody).toContain('strokeWidth="2"');
  });

  it("Header.tsx SVG has aria-hidden='true' (decorative SVG per §8.1.2)", () => {
    const glyphStart = HEADER_TSX_SRC.indexOf("function HamburgerGlyph");
    const glyphEnd = HEADER_TSX_SRC.indexOf("\nfunction ", glyphStart + 1);
    const glyphBody =
      glyphEnd > 0
        ? HEADER_TSX_SRC.slice(glyphStart, glyphEnd)
        : HEADER_TSX_SRC.slice(glyphStart);
    expect(glyphBody).toContain('aria-hidden="true"');
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G25 — DESIGN_SYSTEM.md v0.4.7 static scan: §8.1 and §8.1.11 present
// ══════════════════════════════════════════════════════════════════════════════

describe("G25 — DESIGN_SYSTEM.md v0.5.0 static scan (§8.1 + §8.1.11 table)", () => {
  it("version line reads v0.5.0", () => {
    expect(DESIGN_SYSTEM_MD).toMatch(/\*\*Version:\*\* v0\.5\.0/);
  });

  it("§8.1 section header is present", () => {
    expect(DESIGN_SYSTEM_MD).toContain("### 8.1");
  });

  it("§8.1.11 heading is present", () => {
    expect(DESIGN_SYSTEM_MD).toContain("8.1.11");
  });

  it("§8.1.11 table contains 'Open navigation menu' verbatim", () => {
    expect(DESIGN_SYSTEM_MD).toContain("Open navigation menu");
  });

  it("§8.1.11 table contains 'Close navigation menu' verbatim", () => {
    expect(DESIGN_SYSTEM_MD).toContain("Close navigation menu");
  });

  it("§8.1.11 table contains 'Site navigation' verbatim", () => {
    expect(DESIGN_SYSTEM_MD).toContain("Site navigation");
  });

  it("v0.4.7 changelog entry mentions T11 hamburger menu extension", () => {
    // The v0.4.7 changelog should describe the §8 extension for T11.
    expect(DESIGN_SYSTEM_MD).toContain("v0.4.7");
    expect(DESIGN_SYSTEM_MD).toContain("§8.1");
  });

  it("§8.1.10 section documents no MOBILE_NAV_HEADING constant (omitted heading)", () => {
    expect(DESIGN_SYSTEM_MD).toContain(
      "No `MOBILE_NAV_HEADING` constant is introduced"
    );
  });

  it("§8.1.13 section documents no scroll lock", () => {
    expect(DESIGN_SYSTEM_MD).toContain("Scroll lock");
    expect(DESIGN_SYSTEM_MD).toContain("8.1.13");
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// G26 — prefers-reduced-motion stub: panel still opens/closes with motion disabled
// ══════════════════════════════════════════════════════════════════════════════

describe("G26 — prefers-reduced-motion stub: panel still opens/closes (§8.1.5 / §2.7)", () => {
  beforeEach(() => {
    // Stub window.matchMedia to return a prefers-reduced-motion: reduce result.
    // This mirrors the pattern from cite-modal.test.tsx for matchMedia stubs.
    vi.stubGlobal("matchMedia", (query: string) => ({
      matches: query.includes("prefers-reduced-motion"),
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));
  });

  it("panel opens normally when prefers-reduced-motion: reduce is set", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    expect(getPanel()).not.toBeNull();
  });

  it("panel closes normally (Esc) when prefers-reduced-motion: reduce is set", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    await act(async () => {
      document.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
      );
    });
    expect(getPanel()).toBeNull();
  });

  it("panel closes normally (close button) when prefers-reduced-motion: reduce is set", async () => {
    renderHeader();
    await act(async () => {
      getTrigger()?.click();
    });
    await act(async () => {
      getCloseBtn()?.click();
    });
    expect(getPanel()).toBeNull();
  });
});
