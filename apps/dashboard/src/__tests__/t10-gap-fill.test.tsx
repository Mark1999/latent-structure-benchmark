// @vitest-environment jsdom
/**
 * T10 gap-fill tests — Phase 6 T10 (FailuresFindingsSection).
 *
 * The Coder's failures-findings.test.tsx (42 tests, 983/983 suite pass) covers
 * the primary acceptance criteria. This file fills the following checklist gaps
 * identified by the Tester audit (2026-05-12):
 *
 *   G1.  No <a> tag with href matching "/methodology" in FailuresFindingsSection
 *        (CDA SME S7 / plan §5 "no methodology-page hyperlink at T10").
 *   G2.  No methodology narration prose ("we chose" / "why we") in source;
 *        no extra <details> elements beyond per-record accordions in component.
 *   G3.  Forbidden vocabulary static scan of FailuresFindingsSection.tsx,
 *        FailuresInspectView.tsx, and failures-findings.css (the Coder tests
 *        only scan the copy module's exported runtime values; this fills the
 *        T0/T7 gap-fill pattern of scanning source text of TSX + CSS files).
 *   G4.  F-T10-C1 nuanced: the two xs-size classes that are the "suspect" sites
 *        (.failure-record__field-shape, .failure-record__block-value--provenance)
 *        use --color-text-caption, not --color-text-secondary. The existing test
 *        only asserts caption is present somewhere; this asserts it is present
 *        on the specific selectors and that secondary is absent from those selectors.
 *   G5.  Empty-state render: framing_note paragraph IS present when records:[]
 *        (Coder tests assert EMPTY_CAPTION and no <ol> but not that the
 *        framing_note paragraph also renders in the empty-state).
 *   G6.  Fetch-failed defensive case DOM render: ERROR_FETCH_FAILED string
 *        appears in the DOM when fetchFailures rejects (plan AC21; Coder tests
 *        only verify the source string, not the DOM render).
 *   G7.  Both record types discriminator-based UI (DOM level): "Follow-up
 *        interview" badge text appears on the decline_interview record and NOT
 *        on the failure record; "Collection failure" appears on the failure record.
 *
 * CLAUDE.md §6 R9: no real API calls. All network is mocked.
 * No new dependencies.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ── Source files ──────────────────────────────────────────────────────────────

const FAILURES_SECTION_SRC = readFileSync(
  resolve(__dirname, "../components/FailuresFindingsSection.tsx"),
  "utf-8"
);
const FAILURES_INSPECT_VIEW_SRC = readFileSync(
  resolve(__dirname, "../components/FailuresInspectView.tsx"),
  "utf-8"
);
const FAILURES_CSS = readFileSync(
  resolve(__dirname, "../styles/failures-findings.css"),
  "utf-8"
);

// ── Mock the API client ───────────────────────────────────────────────────────

vi.mock("../api/client", () => ({
  fetchManifest: vi.fn(),
  fetchDomain: vi.fn(),
  fetchFailures: vi.fn(),
}));

import { fetchFailures } from "../api/client";
const mockFetchFailures = vi.mocked(fetchFailures);

// ── Fixture helpers ───────────────────────────────────────────────────────────

const FRAMING_NOTE =
  "These records preserve verbatim outputs from collection sessions that did not produce a parseable primary-step response. Each record is a property of the LSB collection pipeline's output distribution, not a claim about the model's intent or state-of-mind. The `originating_outcome_class` field names the LSB-side detection rule (e.g., `refusal_string_match` describes a string-pattern match by the LSB pipeline, not a model decision to refuse). See the methodology page for the failures-as-findings framing.";

function makeEmptyFixture(): unknown {
  return {
    domain_slug: "family",
    generated_at: "2026-05-12T16:53:22Z",
    n_records: 0,
    n_failure_records: 0,
    n_decline_interview_records: 0,
    framing_note: FRAMING_NOTE,
    records: [],
  };
}

function makeMixedFixture(): unknown {
  return {
    domain_slug: "family",
    generated_at: "2026-05-12T16:53:22Z",
    n_records: 2,
    n_failure_records: 1,
    n_decline_interview_records: 1,
    framing_note: FRAMING_NOTE,
    records: [
      {
        record_type: "failure",
        collection_date: "2026-04-22T18:19:57.413728",
        model_id: "fixture-model-a",
        domain_slug: "family",
        error_type: "HTTPStatusError",
        error_message: "Client error '400 Bad Request' fixture text",
        run_index: 0,
        originating_outcome_class: null,
        retry_attempts: [],
      },
      {
        record_type: "decline_interview",
        collection_date: "2026-04-23T22:58:15.852179+00:00",
        model_id: "fixture-model-b",
        domain_slug: "family",
        decline_interview_id: "fixture-di-id-001",
        originating_informant_id: "fixture-inf-id",
        originating_failure_id: null,
        originating_step: "pile_sort",
        originating_outcome_class: "empty_output",
        detection_rule_version: "v1",
        model_version_returned: "fixture-model-b-v20260401",
        provider: "fixture-provider",
        prompt_version: "decline_v1",
        sha256_manifest: "aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899",
        prompt_verbatim: "Fixture follow-up prompt text.",
        response_verbatim: "Fixture model output text.",
        thinking_verbatim: "",
        input_tokens: 100,
        output_tokens: 200,
        latency_ms: 1000,
        stop_reason: "stop",
        qa_notes: "",
        version_drift_flag: false,
      },
    ],
  };
}

// ── G1. No methodology-page link (<a href="...methodology...") ────────────────
//
// CDA SME S7 (binding): T10 does NOT wire the methodology-page link.
// Plan §5: "Hyperlinking the methodology page from the section" is explicitly
// out of scope. The framing_note text mentions "See the methodology page" as
// plain prose; no <a> element wraps it.

describe("G1 — no methodology-page hyperlink in FailuresFindingsSection (CDA SME S7)", () => {
  it("FailuresFindingsSection.tsx contains no href matching 'methodology'", () => {
    // Pattern: any href= attribute containing "methodology"
    expect(FAILURES_SECTION_SRC.toLowerCase()).not.toMatch(/href=["'][^"']*methodology/);
  });

  it("FailuresFindingsSection.tsx contains no <a> element at all", () => {
    // The component should not render any anchor elements (all methodology
    // page links are deferred to T14 doc-sweep).
    // We check the JSX source for anchor element usage.
    expect(FAILURES_SECTION_SRC).not.toMatch(/<a\s/);
  });
});

// ── G2. No methodology narration prose; no extra <details> ───────────────────
//
// Plan §5 explicitly excludes methodology narration. CDA SME §5.5 note:
// "No methodology-page link rendered at T10." Reviewer confirmed no
// <details> other than per-record accordions.

describe("G2 — no methodology narration; no extra <details> in section (plan §5 / CDA SME §5.5)", () => {
  it("FailuresFindingsSection.tsx does not contain 'we chose' narration prose", () => {
    expect(FAILURES_SECTION_SRC.toLowerCase()).not.toContain("we chose");
  });

  it("FailuresFindingsSection.tsx does not contain 'why we' narration prose", () => {
    expect(FAILURES_SECTION_SRC.toLowerCase()).not.toContain("why we");
  });

  it("FailuresFindingsSection.tsx uses <details> only for per-record accordions (no methodology accordion)", () => {
    // The only <details> elements should be inside FailureRecordRow.
    // We verify there is no separate standalone <details> in the section
    // container (FailuresFindingsSection function body) beyond the record list.
    //
    // Strategy: confirm the component source contains <details> (the accordions
    // exist) and that there is no second standalone <details> wrapping a
    // methodology explanation block (which would introduce prose outside
    // FailureRecordRow's <li><details> structure).
    //
    // The section's own JSX body (outside FailureRecordRow) must not contain
    // a <details> element directly.
    //
    // Approach: extract the FailuresFindingsSection JSX body (after the
    // FailureRecordRow component definition) and assert it has no <details>.
    const sectionStart = FAILURES_SECTION_SRC.indexOf("export function FailuresFindingsSection(");
    expect(sectionStart).toBeGreaterThan(-1);
    const sectionBody = FAILURES_SECTION_SRC.slice(sectionStart);
    // The section body should NOT contain a <details> element directly —
    // those live inside FailureRecordRow (which is a separate function).
    expect(sectionBody).not.toContain("<details");
  });
});

// ── G3. Forbidden vocabulary static scan of TSX + CSS source files ────────────
//
// The Coder's test 18 scans the copy module's exported runtime values only.
// This test fills the T0/T7 gap-fill pattern: scan the static source text of
// the TSX and CSS files for CLAUDE.md §7 forbidden phrases.
//
// Field names from the published JSON data (e.g., "originating_outcome_class",
// "response_verbatim") are data identifiers and are exempt per §7.
// Verbatim model output in <pre> blocks is rendered via React text nodes from
// the fixture data, not authored in the source — exempt.
// The "See the methodology page" phrase in FRAMING_NOTE is T9-emitted content,
// not T10-authored prose — exempt.
// Comments and documentation strings are checked as they may contain prohibited
// phrasing that leaked into LSB-facing text.

describe("G3 — forbidden vocabulary scan of T10 source files (CLAUDE.md §7)", () => {
  // These phrases are forbidden in any LSB-authored text, including source
  // comments that narrate the component's purpose. The T0 gap-fill test
  // includes the same list.
  const FORBIDDEN_PHRASES = [
    "model believes",
    "model thinks",
    "model understands",
    "model's worldview",
    "worldview",
    "how models see the world",
    "how models see",
    "what the model understands",
    "cultural bias",
    // Specific refusal-state attribution not in LSB-authored captions
    // (field names like "refusal_string_match" and comments quoting them are exempt)
    "model refused",
    "model declined",
  ] as const;

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`FailuresFindingsSection.tsx does not contain forbidden phrase: "${phrase}"`, () => {
      expect(FAILURES_SECTION_SRC.toLowerCase()).not.toContain(phrase.toLowerCase());
    });
  }

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`FailuresInspectView.tsx does not contain forbidden phrase: "${phrase}"`, () => {
      expect(FAILURES_INSPECT_VIEW_SRC.toLowerCase()).not.toContain(phrase.toLowerCase());
    });
  }

  for (const phrase of FORBIDDEN_PHRASES) {
    it(`failures-findings.css does not contain forbidden phrase: "${phrase}"`, () => {
      expect(FAILURES_CSS.toLowerCase()).not.toContain(phrase.toLowerCase());
    });
  }
});

// ── G4. F-T10-C1 nuanced: xs-size classes use --color-text-caption ───────────
//
// The Reviewer noted: two --color-text-secondary uses in failures-findings.css
// are acceptable (.failure-record__date at 14px and .failure-record__block-label
// at bold+uppercase 12px). The "suspect" xs-size regular-weight classes must use
// --color-text-caption (not --color-text-secondary) per DESIGN_SYSTEM.md §1.2.
//
// This test asserts the specific CSS rule blocks for the xs-size regular classes
// use --color-text-caption.

describe("G4 — F-T10-C1 nuanced: xs-size regular-weight classes use --color-text-caption (not --color-text-secondary)", () => {
  it(".failure-record__field-shape uses --color-text-caption (not --color-text-secondary)", () => {
    // Find the .failure-record__field-shape rule block in the CSS.
    const idx = FAILURES_CSS.indexOf(".failure-record__field-shape");
    expect(idx).toBeGreaterThan(-1);
    // Extract the rule block up to the next closing brace.
    const blockEnd = FAILURES_CSS.indexOf("}", idx);
    const ruleBlock = FAILURES_CSS.slice(idx, blockEnd + 1);
    expect(ruleBlock).toContain("--color-text-caption");
    expect(ruleBlock).not.toContain("--color-text-secondary");
  });

  it(".failure-record__block-value--provenance uses --color-text-caption (not --color-text-secondary)", () => {
    const idx = FAILURES_CSS.indexOf(".failure-record__block-value--provenance");
    expect(idx).toBeGreaterThan(-1);
    const blockEnd = FAILURES_CSS.indexOf("}", idx);
    const ruleBlock = FAILURES_CSS.slice(idx, blockEnd + 1);
    expect(ruleBlock).toContain("--color-text-caption");
    expect(ruleBlock).not.toContain("--color-text-secondary");
  });

  it(".failure-record__date uses --color-text-secondary (acceptable: 14px --font-size-sm)", () => {
    // Positive assertion: .failure-record__date is at 14px (--font-size-sm),
    // which is within the DESIGN_SYSTEM.md §1.2 "secondary labels at 14px+"
    // allowance. This test documents and guards the acceptable use.
    const idx = FAILURES_CSS.indexOf(".failure-record__date");
    expect(idx).toBeGreaterThan(-1);
    const blockEnd = FAILURES_CSS.indexOf("}", idx);
    const ruleBlock = FAILURES_CSS.slice(idx, blockEnd + 1);
    expect(ruleBlock).toContain("--color-text-secondary");
    expect(ruleBlock).toContain("--font-size-sm");
  });
});

// ── G5. Empty-state render: framing_note IS present when records:[] ───────────
//
// The Coder's tests 10a-10b assert EMPTY_CAPTION and no <ol>.
// Missing: assertion that framing_note paragraph also appears in the empty-state.
// Plan §2.4: "empty-state: section heading + framing_note + counts caption +
// EMPTY_CAPTION; no <ol>." framing_note must be present.

describe("G5 — empty-state render: framing_note appears when records is empty (T10 plan §2.4)", () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
    vi.restoreAllMocks();
    mockFetchFailures.mockReset();
  });

  it("renders framing_note paragraph even when records array is empty", async () => {
    const fixture = makeEmptyFixture();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    const framingPara = container.querySelector(".failures-findings__framing");
    expect(framingPara).not.toBeNull();
    expect(framingPara!.textContent).toBe(FRAMING_NOTE);
  });

  it("renders section heading even when records array is empty", async () => {
    const fixture = makeEmptyFixture();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    const heading = container.querySelector("h2");
    expect(heading).not.toBeNull();
    expect(heading!.textContent).toBe("Collection records and follow-up interviews");
  });

  it("does not render any <details> element when records array is empty", async () => {
    const fixture = makeEmptyFixture();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    expect(container.querySelectorAll("details").length).toBe(0);
  });
});

// ── G6. Fetch-failed defensive case DOM render ────────────────────────────────
//
// Plan AC21: the defensive fetch-failed case renders the section heading
// + ERROR_FETCH_FAILED caption without crashing the page.
// The Coder's test 2 only verifies the source-level error path; this test
// asserts the DOM renders the correct text via a mocked rejection.

describe("G6 — fetch-failed defensive case: ERROR_FETCH_FAILED renders in DOM (T10 plan AC21)", () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
    vi.restoreAllMocks();
    mockFetchFailures.mockReset();
  });

  it("renders ERROR_FETCH_FAILED caption in .failures-findings__error when fetch rejects", async () => {
    mockFetchFailures.mockRejectedValueOnce(new Error("Network error (fixture)"));

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    const errorEl = container.querySelector(".failures-findings__error");
    expect(errorEl).not.toBeNull();
    expect(errorEl!.textContent).toBe(
      "Collection records could not be loaded for this domain."
    );
  });

  it("renders section heading even when fetch rejects (page does not crash)", async () => {
    mockFetchFailures.mockRejectedValueOnce(new Error("Network error (fixture)"));

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    const heading = container.querySelector("h2");
    expect(heading).not.toBeNull();
    expect(heading!.textContent).toBe("Collection records and follow-up interviews");
  });

  it("does not render the framing_note paragraph when fetch rejects", async () => {
    mockFetchFailures.mockRejectedValueOnce(new Error("Network error (fixture)"));

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    const framingPara = container.querySelector(".failures-findings__framing");
    expect(framingPara).toBeNull();
  });
});

// ── G7. Both record types discriminator-based UI (DOM level) ─────────────────
//
// The Coder's test 7 asserts the copy module contains the correct strings.
// Tests 6a-6c assert aria-label prefixes in the DOM.
// Missing: DOM-level assertion that the badge text visible to a sighted reader
// renders "Follow-up interview" on decline_interview and "Collection failure"
// on failure records — and NOT vice versa.

describe("G7 — both record types: discriminator-based badge UI in DOM (T10 plan §2.4, CDA SME S4a)", () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    container = document.createElement("div");
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
    vi.restoreAllMocks();
    mockFetchFailures.mockReset();
  });

  it("failure record renders 'Collection failure' badge in DOM", async () => {
    const fixture = makeMixedFixture();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    const badges = container.querySelectorAll(".failure-record__badge");
    expect(badges.length).toBe(2);
    // First record is the failure
    expect(badges[0].textContent).toBe("Collection failure");
  });

  it("decline_interview record renders 'Follow-up interview' badge in DOM", async () => {
    const fixture = makeMixedFixture();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    const badges = container.querySelectorAll(".failure-record__badge");
    // Second record is the decline_interview
    expect(badges[1].textContent).toBe("Follow-up interview");
  });

  it("failure record badge does NOT render 'Follow-up interview' text", async () => {
    const fixture = makeMixedFixture();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    const badges = container.querySelectorAll(".failure-record__badge");
    expect(badges[0].textContent).not.toBe("Follow-up interview");
    expect(badges[0].textContent).not.toContain("Follow-up");
  });

  it("renders exactly two <details> elements for two records", async () => {
    const fixture = makeMixedFixture();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    expect(container.querySelectorAll("details").length).toBe(2);
  });

  it("decline_interview record renders originating_outcome_class in summary row", async () => {
    const fixture = makeMixedFixture();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    await act(async () => {
      await Promise.resolve();
    });

    // The decline_interview summary should show originating_outcome_class
    const summaries = container.querySelectorAll("summary");
    expect(summaries[1].textContent).toContain("empty_output");
  });
});
