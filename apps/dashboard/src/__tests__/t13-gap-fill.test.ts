/**
 * T13 gap-fill tests — Phase 5 T13 Tester audit (2026-05-11)
 *
 * Covers six checklist items not present in the three T13 test files written by
 * the Coder (methodology-summary.test.tsx, methodology_summary.test.ts,
 * app-state.test.ts T13 block):
 *
 *   1. CSS — nth-child(6) animation-delay: 320ms present in app.css
 *   2. CSS — min-height: 44px on DownloadBar button classes at mobile
 *   3. CSS — CiteModal / EmbedModal mobile sizing rules present
 *   4. CSS — ArticleHeader title scale-down at mobile (font-size-2xl)
 *   5. CSS — Site header nav display: none at mobile
 *   6. MDSPlot — viewBox attribute set on the rendered SVG (source + render)
 *
 * All tests are file-content assertions (read CSS/TSX source, regex match) or
 * lightweight DOM assertions on already-rendered fixtures. No real API calls.
 * No new dependencies.
 *
 * Sources:
 *   docs/status/2026-05-09-phase5-architect-plan.md §4 T13 AC 1-7
 *   DESIGN_SYSTEM.md §12.7 (v0.4.4, T13)
 *   apps/dashboard/src/styles/app.css — mobile block at line 978+
 *   apps/dashboard/src/components/MDSPlot.tsx — viewBox at line 403
 *
 * CLAUDE.md §6 R9: no real API calls. Fixtures only.
 */

// @vitest-environment jsdom

import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ── Paths ─────────────────────────────────────────────────────────────────────

const APP_CSS = readFileSync(resolve(__dirname, "../styles/app.css"), "utf-8");
const MDS_SRC = readFileSync(resolve(__dirname, "../components/MDSPlot.tsx"), "utf-8");

// ── 1. Cascade 6th slot: nth-child(6) animation-delay 320ms ──────────────────
//
// F-T13-1 (BLOCKING per UI/UX verdict): a 6th reveal-cascade-item slot is
// required for MethodologySummary / Footer. The animation-delay must be 320ms
// (same as slot 5) so the total cascade stays within the 600ms binding cap.
// DESIGN_SYSTEM.md §12.1.

describe("app.css — cascade 6th slot (F-T13-1 binding)", () => {
  it("nth-child(6) rule is present in app.css", () => {
    expect(APP_CSS).toContain("nth-child(6)");
  });

  it("nth-child(6) rule has animation-delay: 320ms", () => {
    // Extract the block containing nth-child(6) and assert on animation-delay.
    // Pattern: `.reveal-cascade-item:nth-child(6) { animation-delay: 320ms; }`
    expect(APP_CSS).toMatch(/nth-child\(6\)\s*\{[^}]*animation-delay:\s*320ms/);
  });

  it("nth-child(6) comment references MethodologySummary or Footer", () => {
    // The comment in app.css (F-T13-1) explains the rationale; verify it's there.
    expect(APP_CSS).toContain("F-T13-1");
  });
});

// ── 2. Mobile — DownloadBar touch targets ≥ 44px ─────────────────────────────
//
// T13 mobile gap 1: DESIGN_SYSTEM.md §12.7.
// The six button classes must have min-height: 44px inside @media (max-width: 768px).

describe("app.css — DownloadBar mobile touch targets (T13 mobile gap 1)", () => {
  it("min-height: 44px is present in the mobile media query", () => {
    // Find the mobile @media block and confirm min-height rule exists.
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    expect(mobileBlock).toContain("min-height: 44px");
  });

  it("download-bar__csv-btn is in the min-height: 44px selector group", () => {
    expect(APP_CSS).toContain(".download-bar__csv-btn");
    // The selector list must include the class and appear before min-height: 44px.
    const csvBtnIdx = APP_CSS.lastIndexOf(".download-bar__csv-btn");
    const minHeightIdx = APP_CSS.indexOf("min-height: 44px");
    // The selector must appear before the min-height declaration.
    expect(csvBtnIdx).toBeLessThan(minHeightIdx);
  });

  it("download-bar__cite-btn is in the min-height: 44px selector group", () => {
    expect(APP_CSS).toContain(".download-bar__cite-btn");
  });

  it("download-bar__embed-btn is in the min-height: 44px selector group", () => {
    expect(APP_CSS).toContain(".download-bar__embed-btn");
  });

  it("download-bar__png-btn is in the min-height: 44px selector group", () => {
    expect(APP_CSS).toContain(".download-bar__png-btn");
  });

  it("download-bar__permalink-btn is in the min-height: 44px selector group", () => {
    expect(APP_CSS).toContain(".download-bar__permalink-btn");
  });
});

// ── 3. Mobile — CiteModal / EmbedModal sizing ─────────────────────────────────
//
// T13 mobile gap 2: DESIGN_SYSTEM.md §12.7.
// Both modal dialogs must get width: calc(100% - 32px) + max-height: 90vh
// inside @media (max-width: 768px).

describe("app.css — CiteModal / EmbedModal mobile sizing (T13 mobile gap 2)", () => {
  it("cite-modal__dialog is present in mobile media query", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    expect(mobileBlock).toContain(".cite-modal__dialog");
  });

  it("embed-modal__dialog is present in mobile media query", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    expect(mobileBlock).toContain(".embed-modal__dialog");
  });

  it("modal mobile block contains width: calc(100% - 32px)", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    expect(mobileBlock).toContain("width: calc(100% - 32px)");
  });

  it("modal mobile block contains max-height: 90vh", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    expect(mobileBlock).toContain("max-height: 90vh");
  });

  it("modal mobile block contains overflow-y: auto", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    expect(mobileBlock).toContain("overflow-y: auto");
  });
});

// ── 4. Mobile — ArticleHeader title scale-down ────────────────────────────────
//
// T13 mobile gap 3: DESIGN_SYSTEM.md §12.7.
// .article-header__title must drop from --font-size-3xl to --font-size-2xl
// inside @media (max-width: 768px) so long titles do not overflow on phones.

describe("app.css — ArticleHeader title mobile scale-down (T13 mobile gap 3)", () => {
  it("article-header__title is overridden in the mobile media query", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    expect(mobileBlock).toContain(".article-header__title");
  });

  it("mobile article-header__title uses --font-size-2xl", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    // Extract the article-header__title override and check the font-size value.
    expect(mobileBlock).toContain("font-size: var(--font-size-2xl)");
  });
});

// ── 5. Mobile — Site header nav hidden ───────────────────────────────────────
//
// T13 mobile gap 4: DESIGN_SYSTEM.md §12.7.
// .site-header__nav must be display: none at mobile.
// (Phase 6 adds the hamburger; Phase 5 simply hides nav links on small screens.)

describe("app.css — site-header__nav hidden at mobile (T13 mobile gap 4)", () => {
  it("site-header__nav is overridden in the mobile media query", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    expect(mobileBlock).toContain(".site-header__nav");
  });

  it("mobile site-header__nav has display: none", () => {
    const mobileBlock = APP_CSS.slice(APP_CSS.indexOf("@media (max-width: 768px)"));
    // The rule should appear after the .site-header__nav selector.
    const navIdx = mobileBlock.lastIndexOf(".site-header__nav");
    const blockAfterNav = mobileBlock.slice(navIdx);
    // The closing brace of the selector block comes before the next rule.
    const blockContent = blockAfterNav.slice(0, blockAfterNav.indexOf("}") + 1);
    expect(blockContent).toContain("display: none");
  });
});

// ── 6. MDSPlot viewBox — source + DOM assertion ──────────────────────────────
//
// The MDSPlot SVG must declare a viewBox attribute so that `width: 100%; height: auto`
// in .mds-plot__svg scales the plot correctly on all screen widths.
// No existing test in mds-plot.test.tsx checks the viewBox attribute.

describe("MDSPlot — viewBox attribute (§3.3, DESIGN_SYSTEM.md)", () => {
  it("MDSPlot.tsx source contains a viewBox JSX attribute on the svg element", () => {
    // Structural assertion: the source sets viewBox on the svg element.
    expect(MDS_SRC).toContain("viewBox={");
  });

  it("MDSPlot.tsx source constructs viewBox from SVG_WIDTH and SVG_HEIGHT constants", () => {
    // The viewBox must use the named constants, not hardcoded pixel strings.
    // Pattern: viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
    expect(MDS_SRC).toMatch(/viewBox=\{`0 0 \$\{SVG_WIDTH\} \$\{SVG_HEIGHT\}`\}/);
  });

  it("MDSPlot.tsx defines SVG_WIDTH and SVG_HEIGHT as numeric constants", () => {
    expect(MDS_SRC).toContain("SVG_WIDTH");
    expect(MDS_SRC).toContain("SVG_HEIGHT");
    // Both must be declared as const (not inline literals).
    expect(MDS_SRC).toMatch(/const SVG_WIDTH\s*=/);
    expect(MDS_SRC).toMatch(/const SVG_HEIGHT\s*=/);
  });
});
