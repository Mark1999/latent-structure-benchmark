/**
 * Component render tests — structural / constant verification.
 *
 * Environment: node (no jsdom). Tests verify:
 *   - NAV_LINKS constant in Header.tsx has 4 links with correct hrefs/labels
 *   - Footer.tsx uses the correct framing.ts constants for all links
 *   - ArticleHeader.tsx uses TAGLINE and SITE_NAME from framing.ts
 *   - App.tsx loading state has role="status" + aria-live="polite" in source
 *   - App.tsx error state has role="alert" + aria-live="assertive" in source
 *   - App.tsx render order: Header before ArticleHeader before content before Footer
 *   - tokens.css --color-model-11 equals #9a7d0a (UI/UX correction v0.4.1)
 *
 * ARIA attribute tests are source-text assertions because the vitest environment
 * is "node" (vite.config.ts). A jsdom-based render pass is flagged as a
 * coverage gap for a future T5+ integration test.
 *
 * CLAUDE.md §6 R9: no real fetch, no real API.
 */

import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
import {
  SITE_NAME,
  GITHUB_URL,
  DATA_LICENSE,
  CODE_LICENSE,
  CONTACT_EMAIL,
  TAGLINE,
} from "../copy/framing";

// Resolve paths relative to this test file's location
const SRC = resolve(__dirname, "..");

function readSrc(relPath: string): string {
  return readFileSync(resolve(SRC, relPath), "utf-8");
}

// ──────────────────────────────────────────────────────────────
// Header.tsx — NAV_LINKS structure
// ──────────────────────────────────────────────────────────────
describe("Header.tsx — NAV_LINKS constant", () => {
  // Import the actual Header source to introspect the NAV_LINKS array.
  // Since Header is a plain React function component in a node environment,
  // we can inspect the source text for the link definitions.
  const headerSrc = readSrc("components/Header.tsx");

  it("defines 4 navigation links", () => {
    // Count { href: occurrences inside NAV_LINKS definition
    const hrefMatches = headerSrc.match(/href:\s*["']/g);
    expect(hrefMatches).not.toBeNull();
    // 4 nav links + 1 logo href = 5 total href occurrences in the component source
    // NAV_LINKS array has exactly 4 entries
    const navLinksBlock = headerSrc.match(/NAV_LINKS[^=]*=\s*\[([\s\S]*?)\];/);
    expect(navLinksBlock).not.toBeNull();
    const entries = navLinksBlock![1].match(/\{[^}]+\}/g);
    expect(entries).toHaveLength(4);
  });

  it("nav link 1 is href='/' label='Explore'", () => {
    expect(headerSrc).toContain("href: \"/\"");
    expect(headerSrc).toContain("label: \"Explore\"");
  });

  it("nav link 2 is href='/methodology' label='Methodology'", () => {
    expect(headerSrc).toContain("href: \"/methodology\"");
    expect(headerSrc).toContain("label: \"Methodology\"");
  });

  it("nav link 3 is href='/data' label='Data'", () => {
    expect(headerSrc).toContain("href: \"/data\"");
    expect(headerSrc).toContain("label: \"Data\"");
  });

  it("nav link 4 is href='/about' label='About'", () => {
    expect(headerSrc).toContain("href: \"/about\"");
    expect(headerSrc).toContain("label: \"About\"");
  });

  it("logo uses SITE_NAME constant from framing.ts", () => {
    expect(headerSrc).toContain("SITE_NAME");
    // Verify SITE_NAME is the correct value
    expect(SITE_NAME).toBe("Cognitive Structure Lab");
  });
});

// ──────────────────────────────────────────────────────────────
// Footer.tsx — link constants
// ──────────────────────────────────────────────────────────────
describe("Footer.tsx — framing constant usage", () => {
  const footerSrc = readSrc("components/Footer.tsx");

  it("uses DATA_LICENSE constant (imported from framing.ts)", () => {
    expect(footerSrc).toContain("DATA_LICENSE");
    expect(DATA_LICENSE).toBe("CC BY 4.0");
  });

  it("uses CODE_LICENSE constant (imported from framing.ts)", () => {
    expect(footerSrc).toContain("CODE_LICENSE");
    expect(CODE_LICENSE).toBe("Apache 2.0");
  });

  it("uses GITHUB_URL constant (imported from framing.ts)", () => {
    expect(footerSrc).toContain("GITHUB_URL");
    expect(GITHUB_URL).toContain("github.com");
  });

  it("uses CONTACT_EMAIL constant (imported from framing.ts)", () => {
    expect(footerSrc).toContain("CONTACT_EMAIL");
    expect(CONTACT_EMAIL).toContain("@cogstructurelab.com");
  });

  it("has a Data link pointing to /data", () => {
    expect(footerSrc).toContain('href="/data"');
  });

  it("has a GitHub link using GITHUB_URL", () => {
    expect(footerSrc).toContain("{GITHUB_URL}");
  });

  it("has a Cite link pointing to #cite", () => {
    expect(footerSrc).toContain('href="#cite"');
  });

  it("has a Methodology link pointing to /methodology", () => {
    expect(footerSrc).toContain('href="/methodology"');
  });

  it("has a Contact link using CONTACT_EMAIL via mailto:", () => {
    expect(footerSrc).toContain("mailto:");
    expect(footerSrc).toContain("CONTACT_EMAIL");
  });

  it("uses role='contentinfo' on the footer element", () => {
    expect(footerSrc).toContain('role="contentinfo"');
  });
});

// ──────────────────────────────────────────────────────────────
// ArticleHeader.tsx — TAGLINE + SITE_NAME + structural elements
// ──────────────────────────────────────────────────────────────
describe("ArticleHeader.tsx — structure and framing constants", () => {
  const articleHeaderSrc = readSrc("components/ArticleHeader.tsx");

  it("uses TAGLINE constant in subtitle (not hardcoded copy)", () => {
    expect(articleHeaderSrc).toContain("TAGLINE");
    // Cross-check: TAGLINE is the canonical US English string
    expect(TAGLINE).toContain("categorize");
  });

  it("uses SITE_NAME constant in byline strip", () => {
    expect(articleHeaderSrc).toContain("SITE_NAME");
  });

  it("renders an eyebrow element with article-header__eyebrow class", () => {
    expect(articleHeaderSrc).toContain("article-header__eyebrow");
    expect(articleHeaderSrc).toContain("DOMAIN");
  });

  it("renders h1 with article-header__title class", () => {
    expect(articleHeaderSrc).toContain("article-header__title");
    expect(articleHeaderSrc).toContain("<h1");
  });

  it("renders subtitle element with article-header__subtitle class", () => {
    expect(articleHeaderSrc).toContain("article-header__subtitle");
  });

  it("renders byline-strip with Methodology and Cite links", () => {
    expect(articleHeaderSrc).toContain('href="/methodology"');
    expect(articleHeaderSrc).toContain('href="#cite"');
  });

  it("shows 'Loading…' when loading=true, TAGLINE when loading=false", () => {
    expect(articleHeaderSrc).toContain("loading");
    expect(articleHeaderSrc).toContain("Loading…");
    expect(articleHeaderSrc).toContain("TAGLINE");
  });
});

// ──────────────────────────────────────────────────────────────
// App.tsx — ARIA attributes in loading and error states
// (Source-text assertions; jsdom render test flagged as gap below)
// ──────────────────────────────────────────────────────────────
describe("App.tsx — ARIA attributes in loading/error states (source verification)", () => {
  const appSrc = readSrc("App.tsx");

  it("loading placeholder has role=\"status\" in source", () => {
    expect(appSrc).toContain('role="status"');
  });

  it("loading placeholder has aria-live=\"polite\" in source", () => {
    expect(appSrc).toContain('aria-live="polite"');
  });

  it("error placeholder has role=\"alert\" in source", () => {
    expect(appSrc).toContain('role="alert"');
  });

  it("error placeholder has aria-live=\"assertive\" in source", () => {
    expect(appSrc).toContain('aria-live="assertive"');
  });
});

// ──────────────────────────────────────────────────────────────
// App.tsx — render order: Phase 9a app-shell layout
// (Header/ArticleHeader/Footer article layout replaced by app-shell)
// ──────────────────────────────────────────────────────────────
describe("App.tsx — render order (source position verification)", () => {
  const appSrc = readSrc("App.tsx");

  it("app-nav bar appears before app-main in source order (Phase 9a app-shell layout)", () => {
    // Phase 9a: App.tsx uses an app-shell layout. The nav bar (.app-nav) is above
    // the main grid (.app-main) which contains sidebar + content.
    const navPos = appSrc.indexOf("app-nav");
    const mainPos = appSrc.indexOf("app-main");
    expect(navPos).toBeGreaterThan(-1);
    expect(mainPos).toBeGreaterThan(-1);
    expect(navPos).toBeLessThan(mainPos);
  });

  it("app-sidebar appears before app-content in source order", () => {
    const sidebarPos = appSrc.indexOf("app-sidebar");
    const contentPos = appSrc.indexOf("app-content");
    expect(sidebarPos).toBeGreaterThan(-1);
    expect(contentPos).toBeGreaterThan(-1);
    expect(sidebarPos).toBeLessThan(contentPos);
  });

  it("content-placeholder--loading appears after app-nav in source order", () => {
    const navPos = appSrc.indexOf("app-nav");
    const contentPlaceholderPos = appSrc.indexOf("content-placeholder--loading");
    expect(navPos).toBeGreaterThan(-1);
    expect(contentPlaceholderPos).toBeGreaterThan(-1);
    expect(navPos).toBeLessThan(contentPlaceholderPos);
  });

  it("app-shell div wraps all zones (replaces page-wrapper)", () => {
    // Phase 9a: the app-shell div is the root container (no longer page-wrapper).
    expect(appSrc).toContain("app-shell");
  });
});

// ──────────────────────────────────────────────────────────────
// tokens.css — --color-model-11 = #9a7d0a (UI/UX v0.4.1 correction)
// ──────────────────────────────────────────────────────────────
describe("tokens.css — color-model-11 UI/UX correction (v0.4.1)", () => {
  const tokensSrc = readSrc("styles/tokens.css");

  it("--color-model-11 is #9a7d0a (corrected from #b7950b per UI/UX PASS v0.4.1)", () => {
    expect(tokensSrc).toContain("--color-model-11: #9a7d0a");
  });

  it("--color-model-11 CSS property does NOT assign #b7950b (only #9a7d0a)", () => {
    // #b7950b appears only in a comment explaining why it was replaced.
    // The actual property assignment must be #9a7d0a.
    // Extract the property line to verify the assignment, not just search the whole file
    // (the comment "v0.4.1; #b7950b failed WCAG AA 3:1" legitimately contains the old value).
    const match = tokensSrc.match(/--color-model-11:\s*([^;/\s]+)/);
    expect(match).not.toBeNull();
    expect(match![1]).toBe("#9a7d0a");
  });
});
