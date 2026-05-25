// @vitest-environment jsdom
/**
 * T0 gap-fill tests — Phase 6 T0 (Operator Inspection Mode).
 *
 * Gaps filled against:
 *   - F-T0-A1 uniqueness: assert that ALL §2.4 section titles produce distinct HTML ids.
 *   - AC5 (reader mode): App.tsx full-page branch still contains ArticleHeader,
 *     DataExplorer, and MethodologySummary when no ?inspect= param is present.
 *   - AC6 (embed mode ordering): ?embed=true with no ?inspect= still reaches the
 *     embed-root block — the inspectSlug check does NOT intercept embed requests.
 *   - AC11 (forbidden vocabulary): comprehensive §7 scan of all three inspect
 *     component source files plus InspectSection descriptions in InspectRoot.tsx.
 *
 * CLAUDE.md §6 R9: no real API calls. All assertions are on static source text
 * or on the DOM via the same vi.mock pattern used in inspect.test.tsx.
 *
 * Reference: docs/status/2026-05-12-phase6-T0-architect-plan.md §3
 *            docs/status/2026-05-12-phase6-T0-uiux-plan-verdict.md F-T0-A1
 *            CLAUDE.md §7 (full forbidden vocabulary table)
 */

import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";

const APP_SRC = readFileSync(resolve(__dirname, "../App.tsx"), "utf-8");
const INSPECT_ROOT_SRC = readFileSync(
  resolve(__dirname, "../components/InspectRoot.tsx"),
  "utf-8"
);
const INSPECT_SECTION_SRC = readFileSync(
  resolve(__dirname, "../components/InspectSection.tsx"),
  "utf-8"
);
const INSPECT_TABLE_SRC = readFileSync(
  resolve(__dirname, "../components/InspectTable.tsx"),
  "utf-8"
);

// ── id-from-title helper (mirrors InspectSection.tsx titleToId) ───────────────

function titleToId(title: string): string {
  return title
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "");
}

// ── F-T0-A1: section title uniqueness ────────────────────────────────────────

describe("F-T0-A1 — section title uniqueness (all §2.4 titles produce distinct ids)", () => {
  /**
   * The plan §2.4 and the UI/UX F-T0-A1 binding note both state that
   * all section titles within a single page view must be unique so no
   * duplicate id attributes are created in the DOM.
   *
   * This test is the set-level uniqueness guarantee that the Coder's
   * individual-slug tests do not cover.
   */

  // All domain-mode section headings from §2.4 (plan table rows, verbatim)
  const DOMAIN_MODE_TITLES = [
    "Domain header",
    "Models in this domain",
    "Free lists (per model)",
    "MDS coordinates",
    "MDS uncertainty (bootstrap ellipses)",
    "Similarity matrix",
    "Similarity confidence intervals",
    "Consensus",
    "Cultural centrality",
    "Cross-model agreement",
    "Sutrop CSI (salience)",
    "Salience index agreement",
    "Within-model results",
    "G1 stability fields",
    "Groundings",
    "Display block (precomputed UI helpers)",
    "Other top-level fields",
  ];

  // Manifest-mode section headings from §2.4
  const MANIFEST_MODE_TITLES = [
    "Manifest top-level",
    "Domains in this manifest",
  ];

  it("all domain-mode section titles produce distinct slugified ids", () => {
    const ids = DOMAIN_MODE_TITLES.map(titleToId);
    const idSet = new Set(ids);
    // If there are any duplicate ids, the Set will be smaller than the array.
    expect(idSet.size).toBe(DOMAIN_MODE_TITLES.length);
  });

  it("all manifest-mode section titles produce distinct slugified ids", () => {
    const ids = MANIFEST_MODE_TITLES.map(titleToId);
    const idSet = new Set(ids);
    expect(idSet.size).toBe(MANIFEST_MODE_TITLES.length);
  });

  it("domain-mode ids are valid HTML ids (no spaces, only a-z, 0-9, hyphen)", () => {
    const ids = DOMAIN_MODE_TITLES.map(titleToId);
    for (const id of ids) {
      // HTML id must be non-empty and contain only alphanumeric/hyphen chars
      expect(id.length).toBeGreaterThan(0);
      expect(id).toMatch(/^[a-z0-9-]+$/);
    }
  });

  it("manifest-mode ids are valid HTML ids (no spaces, only a-z, 0-9, hyphen)", () => {
    const ids = MANIFEST_MODE_TITLES.map(titleToId);
    for (const id of ids) {
      expect(id.length).toBeGreaterThan(0);
      expect(id).toMatch(/^[a-z0-9-]+$/);
    }
  });

  it("InspectRoot.tsx uses exactly the §2.4 domain section headings (source sync check)", () => {
    // Confirm each §2.4 heading string appears in InspectRoot.tsx source.
    // This catches drift where a heading is renamed in the plan but not updated
    // in the component (or vice versa), which would break the uniqueness guarantee.
    for (const title of DOMAIN_MODE_TITLES) {
      expect(INSPECT_ROOT_SRC).toContain(`title="${title}"`);
    }
  });

  it("InspectRoot.tsx uses exactly the §2.4 manifest section headings (source sync check)", () => {
    for (const title of MANIFEST_MODE_TITLES) {
      expect(INSPECT_ROOT_SRC).toContain(`title="${title}"`);
    }
  });

  it("InspectSection.tsx titleToId strips parentheses (MDS uncertainty title test)", () => {
    // Specific regression for the parenthesised title that the UI/UX verdict mentioned
    const id = titleToId("MDS uncertainty (bootstrap ellipses)");
    expect(id).toBe("mds-uncertainty-bootstrap-ellipses");
    // No parentheses or spaces in the output
    expect(id).not.toContain("(");
    expect(id).not.toContain(")");
    expect(id).not.toContain(" ");
  });
});

// ── AC5: reader mode unchanged ────────────────────────────────────────────────

describe("AC5 — reader mode unchanged: App.tsx full-page branch still has pre-T0 lineup", () => {
  /**
   * The plan §3 AC5 requires that loading the dashboard without ?inspect=
   * renders the existing reader view, byte-identical to pre-T0 behavior.
   *
   * The new inspectSlug check is an early-return that must NOT interfere
   * with the full-page branch. We verify at source level that the full-page
   * branch (the non-embed, non-inspect path) still contains all three
   * components that form the reader view.
   */

  it("App.tsx app-shell branch renders DataExplorer (Phase 9a: ArticleHeader removed from explore page)", () => {
    // Phase 9a: the explore page is an app-shell. ArticleHeader is no longer rendered.
    // DataExplorer remains the core content component.
    expect(APP_SRC).toContain("<DataExplorer");
  });

  it("App.tsx does NOT render ArticleHeader (Phase 9a: article sections removed from explore page)", () => {
    // Phase 9a app-shell: ArticleHeader, MethodologySummary, and FailuresFindingsSection
    // are no longer rendered from App.tsx on the explore page. The layout is now
    // a full-viewport sidebar + content grid.
    expect(APP_SRC).not.toContain("<ArticleHeader");
  });

  it("App.tsx does NOT render MethodologySummary (Phase 9a: article sections removed)", () => {
    expect(APP_SRC).not.toContain("<MethodologySummary");
  });

  it("App.tsx inspectSlug check appears BEFORE the app-shell return", () => {
    // The inspectSlug guard must be an early-return so the app-shell branch
    // is reached whenever inspect mode is inactive.
    // Verify that 'inspectSlug !== null' appears before the app-shell JSX root div
    // ('className="app-shell"') in source.
    const inspectCheckIdx = APP_SRC.indexOf("inspectSlug !== null");
    const appShellIdx = APP_SRC.indexOf('className="app-shell"');
    expect(inspectCheckIdx).toBeGreaterThan(-1);
    expect(appShellIdx).toBeGreaterThan(-1);
    expect(inspectCheckIdx).toBeLessThan(appShellIdx);
  });

  it("App.tsx inspectSlug check appears BEFORE embedMode early-return", () => {
    // The ordering in App.tsx: inspectSlug check → embedMode check → full page.
    // Both are present; inspect check is first.
    const inspectCheckIdx = APP_SRC.indexOf("inspectSlug !== null");
    const embedRootIdx = APP_SRC.indexOf("embed-root");
    expect(inspectCheckIdx).toBeGreaterThan(-1);
    expect(embedRootIdx).toBeGreaterThan(-1);
    // inspect guard fires before embed-root block
    expect(inspectCheckIdx).toBeLessThan(embedRootIdx);
  });
});

// ── AC6: embed mode ordering ──────────────────────────────────────────────────

describe("AC6 — embed mode unchanged: inspectSlug null check does not intercept ?embed=true", () => {
  /**
   * App.tsx evaluates inspectSlug before embedMode.
   * When ?inspect= is absent (inspectSlug === null), the embed-root branch
   * must still be reachable.
   *
   * This is a source-level ordering test: the embed-root JSX must appear
   * AFTER the inspectSlug null check in the source, confirming the early-
   * return semantics are correct (inspect takes over only when slug is present;
   * otherwise embed mode is checked next).
   */

  it("App.tsx embed-root block is still present after T0 changes", () => {
    expect(APP_SRC).toContain("embed-root");
  });

  it("App.tsx embedMode is still checked (isEmbedMode call is present)", () => {
    expect(APP_SRC).toContain("isEmbedMode");
    expect(APP_SRC).toContain("embedMode");
  });

  it("App.tsx embed-root branch does NOT contain InspectRoot rendering", () => {
    // The embed-root branch is the code block between 'embed-root' and the
    // full-page return. Confirm InspectRoot is NOT nested inside it.
    const embedRootStart = APP_SRC.indexOf("embed-root");
    const pageWrapperStart = APP_SRC.indexOf("page-wrapper");
    const embedBlock = APP_SRC.slice(embedRootStart, pageWrapperStart);
    expect(embedBlock).not.toContain("<InspectRoot");
  });

  it("App.tsx inspectSlug null guard prevents inspect mode when slug is null", () => {
    // When inspectSlug is null, the early-return does not fire, so embed and
    // full-page branches remain reachable. Confirm the guard is a null check.
    expect(APP_SRC).toContain("inspectSlug !== null");
    // The null case must fall through to the next check (embedMode)
    expect(APP_SRC).toContain("if (embedMode)");
  });
});

// ── AC11: comprehensive forbidden vocabulary scan ────────────────────────────

describe("AC11 — no forbidden vocabulary in any inspect component source", () => {
  /**
   * CLAUDE.md §7 full forbidden table. Tests both the prose-generating
   * components and the css file.
   *
   * Note: these patterns are tested as substrings in source text. Field names
   * from the JSON data (e.g., 'cultural_centrality_scores') are exempt per §7
   * ("field names from the data — which are not LSB-authored prose — are exempt").
   * We test the forbidden PHRASES, not individual standalone words.
   */

  const FORBIDDEN_PHRASES = [
    "believes",
    "Model X believes",
    "How models see the world",
    "How models see",
    "What the model understands",
    "Cultural bias",
    "worldview",
    // Note: "thinks" is only forbidden when applied to models; the
    // word itself may appear in innocuous contexts (e.g., code comments
    // about logic). We check the specific forbidden construction.
    "model thinks",
    "model believes",
    "model understands",
  ];

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`InspectRoot.tsx does not contain forbidden phrase: "${phrase}"`, () => {
      // Case-insensitive check to catch capitalization variants
      expect(INSPECT_ROOT_SRC.toLowerCase()).not.toContain(phrase.toLowerCase());
    });
  }

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`InspectSection.tsx does not contain forbidden phrase: "${phrase}"`, () => {
      expect(INSPECT_SECTION_SRC.toLowerCase()).not.toContain(phrase.toLowerCase());
    });
  }

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`InspectTable.tsx does not contain forbidden phrase: "${phrase}"`, () => {
      expect(INSPECT_TABLE_SRC.toLowerCase()).not.toContain(phrase.toLowerCase());
    });
  }

  it("inspect.css does not contain forbidden vocabulary", () => {
    const cssSrc = readFileSync(
      resolve(__dirname, "../styles/inspect.css"),
      "utf-8"
    ).toLowerCase();
    for (const phrase of FORBIDDEN_PHRASES) {
      expect(cssSrc).not.toContain(phrase.toLowerCase());
    }
  });
});
