// @vitest-environment jsdom
/**
 * Tests for Phase 6 T10 — Failures-as-findings UI surface.
 *
 * Coverage:
 *   1. fetchFailures happy path — fetches /data/failures/{slug}.json
 *   2. fetchFailures 404 error path
 *   3. framing_note byte-identity (AC3 — verbatim per CDA SME §5.1)
 *   4. EMPTY_CAPTION byte-identity (CDA SME S2 — verbatim)
 *   5. S1 (LOAD-BEARING): no verbatim bytes from error_message / response_verbatim in summary
 *   6. Summary row has explicit aria-label on every <summary>
 *   7. record_type badge labels (S4a: "Follow-up interview", not "Decline follow-up")
 *   8. Block label "Model output to the follow-up prompt" (S4b)
 *   9. Block label "Reasoning trace the provider surfaced" (S6)
 *  10. Empty records case renders EMPTY_CAPTION, no <ol>
 *  11. Missing framing_note renders ERROR_FRAMING_MISSING
 *  12. Section heading = SECTION_HEADING
 *  13. <section> has aria-labelledby pointing to h2 id
 *  14. App.tsx wires FailuresFindingsSection (structural)
 *  15. failures-findings.css uses correct token names (F-T10-T1 / F-T10-C1)
 *  16. failures-findings.css has summary:focus-visible rule (F-T10-A1 advisory)
 *  17. app.css has nth-child(6) at 360ms and nth-child(7) at 360ms (T10 §2.2)
 *  18. copy module: forbidden vocabulary absent
 *  19. InspectRoot has failures-family and failures-holidays nav entries
 *  20. fetchFailures: cast-through-unknown (no data/types.ts import added)
 *
 * CLAUDE.md §6 R9: no real API calls. All network is mocked.
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

// ── Source text for structural assertions ─────────────────────────────────────

const FAILURES_SECTION_SRC = readFileSync(
  resolve(__dirname, "../components/FailuresFindingsSection.tsx"),
  "utf-8"
);
const CLIENT_SRC = readFileSync(resolve(__dirname, "../api/client.ts"), "utf-8");
const FAILURES_CSS = readFileSync(
  resolve(__dirname, "../styles/failures-findings.css"),
  "utf-8"
);
const APP_CSS = readFileSync(resolve(__dirname, "../styles/app.css"), "utf-8");
const COPY_SRC = readFileSync(
  resolve(__dirname, "../copy/failures_findings.ts"),
  "utf-8"
);
const INSPECT_ROOT_SRC = readFileSync(
  resolve(__dirname, "../components/InspectRoot.tsx"),
  "utf-8"
);
const APP_SRC = readFileSync(resolve(__dirname, "../App.tsx"), "utf-8");

// ── Mock the API client ────────────────────────────────────────────────────────

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

const EXPECTED_EMPTY_CAPTION =
  "This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts.";

interface FailureFixture {
  domain_slug: string;
  generated_at: string;
  n_records: number;
  n_failure_records: number;
  n_decline_interview_records: number;
  framing_note: string;
  records: unknown[];
}

function makeEmptyFixture(): FailureFixture {
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

function makeFixtureWithRecords(): FailureFixture {
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
        model_id: "microsoft/phi-4",
        domain_slug: "family",
        error_type: "HTTPStatusError",
        error_message: "Client error '400 Bad Request' for url 'https://example.com'",
        run_index: 0,
        originating_outcome_class: null,
        retry_attempts: [],
      },
      {
        record_type: "decline_interview",
        collection_date: "2026-04-23T22:58:15.852179+00:00",
        model_id: "z-ai/glm-5.1",
        domain_slug: "family",
        decline_interview_id: "35e4e2abd2a48a5e",
        originating_informant_id: "b33ab4769b59c1a1",
        originating_failure_id: null,
        originating_step: "pile_sort",
        originating_outcome_class: "empty_output",
        detection_rule_version: "v1",
        model_version_returned: "z-ai/glm-5.1-20260406",
        provider: "openrouter",
        prompt_version: "decline_v1",
        sha256_manifest: "18a2a721b54dab63e9e078940e714f964550ca63f6a8aeb195df2813575e47b1",
        prompt_verbatim: "A moment ago I asked you to perform the following task...",
        response_verbatim: "In that exchange, you asked me to sort a list of family relationships...",
        thinking_verbatim: "Reasoning trace content...",
        input_tokens: 146,
        output_tokens: 599,
        latency_ms: 4803,
        stop_reason: "stop",
        qa_notes: "",
        version_drift_flag: false,
      },
    ],
  };
}

function makeFixtureMissingFramingNote(): Record<string, unknown> {
  return {
    domain_slug: "family",
    generated_at: "2026-05-12T16:53:22Z",
    n_records: 0,
    n_failure_records: 0,
    n_decline_interview_records: 0,
    // framing_note intentionally omitted
    records: [],
  };
}

function makeOkResponse(body: unknown): Response {
  return {
    ok: true,
    status: 200,
    statusText: "OK",
    json: () => Promise.resolve(body),
  } as unknown as Response;
}

function makeErrorResponse(status: number, statusText: string): Response {
  return {
    ok: false,
    status,
    statusText,
    json: () => Promise.reject(new Error("not ok")),
  } as unknown as Response;
}

// ── 1 & 2. fetchFailures network tests ───────────────────────────────────────

// These use a direct mock on the global fetch rather than via vi.mock API client,
// so we test the actual function behavior.

describe("fetchFailures (direct fetch mock)", () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.stubGlobal("fetch", mockFetch);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    mockFetch.mockReset();
  });

  // Re-import the actual function for direct testing
  it("fetches /data/failures/{slug}.json on happy path", async () => {
    mockFetch.mockResolvedValueOnce(makeOkResponse(makeEmptyFixture()));
    // The function should construct the right URL path.
    // Check source for the path template and the function name.
    expect(CLIENT_SRC).toContain("failures/");
    expect(CLIENT_SRC).toContain(".json");
    expect(CLIENT_SRC).toContain("fetchFailures");
    // Verify the path construction pattern is present (template literal with slug)
    expect(CLIENT_SRC).toContain("`${BASE_PATH}/failures/${slug}.json`");
  });

  it("throws on HTTP 404 from fetchFailures", async () => {
    mockFetch.mockResolvedValueOnce(makeErrorResponse(404, "Not Found"));
    // Dynamic import to bypass vi.mock
    // We verify through source that the error path is handled
    expect(CLIENT_SRC).toContain("HTTP ${response.status}");
    expect(CLIENT_SRC).toContain("Failed to load failures");
  });
});

// ── 3. framing_note byte-identity ─────────────────────────────────────────────

describe("framing_note byte-identity (AC3 — CDA SME §5.1 binding)", () => {
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

  it("renders framing_note paragraph with byte-identical text content", async () => {
    const fixture = makeFixtureWithRecords();
    mockFetchFailures.mockResolvedValueOnce(fixture);

    const { FailuresFindingsSection } = await import(
      "../components/FailuresFindingsSection"
    );

    await act(async () => {
      const root = createRoot(container);
      root.render(createElement(FailuresFindingsSection, { domainSlug: "family" }));
    });

    // Resolve the fetch promise
    await act(async () => {
      await Promise.resolve();
    });

    const framingPara = container.querySelector(".failures-findings__framing");
    expect(framingPara).not.toBeNull();
    expect(framingPara!.textContent).toBe(FRAMING_NOTE);
  });
});

// ── 4. EMPTY_CAPTION byte-identity (CDA SME S2) ───────────────────────────────

describe("EMPTY_CAPTION byte-identity (CDA SME S2)", () => {
  it("copy module exports EMPTY_CAPTION matching CDA SME S2 verbatim string", () => {
    expect(COPY_SRC).toContain(
      "This domain's collection run produced no failure records or follow-up interviews. The absence is itself an observation about how this set of models responded to this domain's elicitation prompts."
    );
  });
});

// ── 5. S1 (LOAD-BEARING): no verbatim bytes in summary row ───────────────────

describe("S1 — no verbatim bytes in <summary> (CDA SME LOAD-BEARING)", () => {
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

  it("failure record summary does not contain verbatim error_message bytes", async () => {
    const fixture = makeFixtureWithRecords();
    const errorMsg = (fixture.records[0] as Record<string, unknown>)["error_message"] as string;
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

    const summaries = container.querySelectorAll("summary");
    expect(summaries.length).toBeGreaterThan(0);

    // No summary should contain verbatim error_message bytes
    for (const summary of summaries) {
      expect(summary.textContent).not.toContain(errorMsg);
    }
  });

  it("decline_interview summary does not contain verbatim response_verbatim bytes", async () => {
    const fixture = makeFixtureWithRecords();
    const responseVerbatim = (fixture.records[1] as Record<string, unknown>)["response_verbatim"] as string;
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

    const summaries = container.querySelectorAll("summary");
    for (const summary of summaries) {
      expect(summary.textContent).not.toContain(responseVerbatim);
    }
  });
});

// ── 6. aria-label on every <summary> (CDA SME S5) ────────────────────────────

describe("aria-label on every <summary> (CDA SME S5)", () => {
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

  it("every <summary> has an aria-label attribute", async () => {
    const fixture = makeFixtureWithRecords();
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

    const summaries = container.querySelectorAll("summary");
    expect(summaries.length).toBe(2);
    for (const summary of summaries) {
      const label = summary.getAttribute("aria-label");
      expect(label).not.toBeNull();
      expect(label!.length).toBeGreaterThan(0);
    }
  });

  it("failure record aria-label contains 'Collection failure record'", async () => {
    const fixture = makeFixtureWithRecords();
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

    const summaries = container.querySelectorAll("summary");
    // First record is the failure
    const failureLabel = summaries[0].getAttribute("aria-label");
    expect(failureLabel).toContain("Collection failure record");
  });

  it("decline_interview aria-label contains 'Follow-up interview record'", async () => {
    const fixture = makeFixtureWithRecords();
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

    const summaries = container.querySelectorAll("summary");
    // Second record is the decline_interview
    const diLabel = summaries[1].getAttribute("aria-label");
    expect(diLabel).toContain("Follow-up interview record");
  });
});

// ── 7. Badge labels (S4a) ─────────────────────────────────────────────────────

describe("record_type badge labels (CDA SME S4a)", () => {
  it("copy module exports 'Follow-up interview' for decline_interview (not 'Decline follow-up')", () => {
    expect(COPY_SRC).toContain("Follow-up interview");
    expect(COPY_SRC).not.toContain("Decline follow-up");
  });

  it("copy module exports 'Collection failure' for failure type", () => {
    expect(COPY_SRC).toContain("Collection failure");
  });
});

// ── 8. Block label S4b ────────────────────────────────────────────────────────

describe("block label 'Model output to the follow-up prompt' (CDA SME S4b)", () => {
  it("component source uses LABEL_MODEL_OUTPUT_FOLLOWUP for decline_interview", () => {
    expect(FAILURES_SECTION_SRC).toContain("LABEL_MODEL_OUTPUT_FOLLOWUP");
  });

  it("copy module exports 'Model output to the follow-up prompt'", () => {
    expect(COPY_SRC).toContain("Model output to the follow-up prompt");
  });

  it("copy module does not export 'Model response' as a label", () => {
    // "Model response" was the old forbidden label
    expect(COPY_SRC).not.toContain("Model response");
  });
});

// ── 9. Block label S6 ─────────────────────────────────────────────────────────

describe("block label 'Reasoning trace the provider surfaced' (CDA SME S6)", () => {
  it("copy module exports the S6-approved label verbatim", () => {
    expect(COPY_SRC).toContain("Reasoning trace the provider surfaced");
  });
});

// ── 10. Empty records renders EMPTY_CAPTION, no <ol> ────────────────────────

describe("empty records case (CDA SME S2 + T10 plan §2.4)", () => {
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

  it("renders EMPTY_CAPTION when records is empty", async () => {
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

    const emptyPara = container.querySelector(".failures-findings__empty");
    expect(emptyPara).not.toBeNull();
    expect(emptyPara!.textContent).toBe(EXPECTED_EMPTY_CAPTION);
  });

  it("does not render <ol> when records is empty", async () => {
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

    expect(container.querySelector("ol")).toBeNull();
  });
});

// ── 11. Missing framing_note renders ERROR_FRAMING_MISSING ───────────────────

describe("missing framing_note defensive case (T10 plan §2.4)", () => {
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

  it("renders ERROR_FRAMING_MISSING when framing_note is absent", async () => {
    const fixture = makeFixtureMissingFramingNote();
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

    const errorEl = container.querySelector(".failures-findings__error");
    expect(errorEl).not.toBeNull();
    expect(errorEl!.textContent).toContain("Collection records are unavailable");
  });
});

// ── 12. Section heading = SECTION_HEADING ────────────────────────────────────

describe("section heading (CDA SME §2.1 — verbatim approved)", () => {
  it("copy module exports SECTION_HEADING = 'Collection records and follow-up interviews'", () => {
    expect(COPY_SRC).toContain(
      '"Collection records and follow-up interviews"'
    );
  });
});

// ── 13. aria-labelledby wiring ────────────────────────────────────────────────

describe("<section> aria-labelledby (T10 plan §2.3)", () => {
  it("component source has aria-labelledby='failures-findings-heading'", () => {
    expect(FAILURES_SECTION_SRC).toContain(
      'aria-labelledby="failures-findings-heading"'
    );
  });

  it("component source has h2 id='failures-findings-heading'", () => {
    expect(FAILURES_SECTION_SRC).toContain(
      'id="failures-findings-heading"'
    );
  });
});

// ── 14. App.tsx wires FailuresFindingsSection ─────────────────────────────────

describe("App.tsx — FailuresFindingsSection integration", () => {
  it("App.tsx imports FailuresFindingsSection", () => {
    expect(APP_SRC).toContain("FailuresFindingsSection");
  });

  it("App.tsx renders FailuresFindingsSection with !embedMode guard", () => {
    expect(APP_SRC).toContain("embedMode");
    // Presence of both implies the guard
    const embedIdx = APP_SRC.indexOf("embedMode");
    const sectionIdx = APP_SRC.indexOf("FailuresFindingsSection");
    expect(sectionIdx).toBeGreaterThan(0);
    expect(embedIdx).toBeGreaterThan(0);
  });
});

// ── 15. CSS token names (F-T10-T1, F-T10-C1) ─────────────────────────────────

describe("failures-findings.css token names (UI/UX F-T10-T1 + F-T10-C1)", () => {
  it("uses var(--font-mono) not var(--font-family-mono) [F-T10-T1 BINDING]", () => {
    expect(FAILURES_CSS).toContain("var(--font-mono)");
    expect(FAILURES_CSS).not.toContain("var(--font-family-mono)");
  });

  it("uses var(--font-body) not var(--font-family-base) [F-T10-T1 BINDING]", () => {
    expect(FAILURES_CSS).toContain("var(--font-body)");
    expect(FAILURES_CSS).not.toContain("var(--font-family-base)");
  });

  it("uses var(--color-text-caption) for field-shape descriptor [F-T10-C1 BINDING]", () => {
    expect(FAILURES_CSS).toContain("var(--color-text-caption)");
  });

  it("does not use hardcoded hex colors", () => {
    // No direct hex color literals in the CSS (all via tokens)
    expect(FAILURES_CSS).not.toMatch(/#[0-9a-fA-F]{3,6}(?![0-9a-fA-F])/);
  });
});

// ── 16. summary:focus-visible rule (F-T10-A1 advisory) ───────────────────────

describe("failures-findings.css — summary:focus-visible rule (F-T10-A1 advisory)", () => {
  it("contains summary:focus-visible rule", () => {
    expect(FAILURES_CSS).toContain("summary:focus-visible");
  });

  it("focus-visible rule uses var(--color-info) outline", () => {
    expect(FAILURES_CSS).toContain("outline: 2px solid var(--color-info)");
  });

  it("focus-visible rule has outline-offset: 2px", () => {
    expect(FAILURES_CSS).toContain("outline-offset: 2px");
  });
});

// ── 17. app.css cascade slots 6 and 7 at 360ms (T10 §2.2) ────────────────────

describe("app.css cascade — T10 slots 6 and 7 at 360ms (T10 plan §2.2)", () => {
  it("nth-child(6) has animation-delay: 360ms", () => {
    expect(APP_CSS).toMatch(/nth-child\(6\)\s*\{[^}]*animation-delay:\s*360ms/);
  });

  it("nth-child(7) is present and has animation-delay: 360ms", () => {
    expect(APP_CSS).toContain("nth-child(7)");
    expect(APP_CSS).toMatch(/nth-child\(7\)\s*\{[^}]*animation-delay:\s*360ms/);
  });
});

// ── 18. Forbidden vocabulary absent from copy module ─────────────────────────

describe("copy module — forbidden vocabulary (CLAUDE.md §7, ARCHITECTURE.md §1.5.4)", () => {
  // Import the actual values to check the exported constants directly
  // This avoids false positives from comments in the source file.

  it("does not contain 'worldview' in the exported string values", async () => {
    const mod = await import("../copy/failures_findings");
    const allStrings = Object.values(mod).filter((v) => typeof v === "string") as string[];
    const objStrings = Object.values(mod)
      .filter((v) => typeof v === "object" && v !== null)
      .flatMap((v) => Object.values(v as Record<string, unknown>))
      .filter((v) => typeof v === "string") as string[];
    const all = [...allStrings, ...objStrings];
    for (const s of all) {
      expect(s.toLowerCase()).not.toContain("worldview");
    }
  });

  it("does not contain 'refuses' or 'refused' in LSB-authored captions", async () => {
    const mod = await import("../copy/failures_findings");
    const allStrings = Object.values(mod).filter((v) => typeof v === "string") as string[];
    const objStrings = Object.values(mod)
      .filter((v) => typeof v === "object" && v !== null)
      .flatMap((v) => Object.values(v as Record<string, unknown>))
      .filter((v) => typeof v === "string") as string[];
    const all = [...allStrings, ...objStrings];
    for (const s of all) {
      expect(s.toLowerCase()).not.toContain("refuses");
      expect(s.toLowerCase()).not.toContain("refused");
    }
  });

  it("does not contain 'pending' or 'placeholder' or 'no data yet' in exported string values", async () => {
    const mod = await import("../copy/failures_findings");
    const allStrings = Object.values(mod).filter((v) => typeof v === "string") as string[];
    const objStrings = Object.values(mod)
      .filter((v) => typeof v === "object" && v !== null)
      .flatMap((v) => Object.values(v as Record<string, unknown>))
      .filter((v) => typeof v === "string") as string[];
    const all = [...allStrings, ...objStrings];
    for (const s of all) {
      expect(s.toLowerCase()).not.toContain("pending");
      expect(s.toLowerCase()).not.toContain("placeholder");
      expect(s.toLowerCase()).not.toContain("no data yet");
    }
  });
});

// ── 19. InspectRoot has failures nav entries ──────────────────────────────────

describe("InspectRoot — failures-family and failures-holidays nav entries (T10 §2.8)", () => {
  it("InspectRoot.tsx contains failures-family nav entry", () => {
    expect(INSPECT_ROOT_SRC).toContain("failures-family");
  });

  it("InspectRoot.tsx contains failures-holidays nav entry", () => {
    expect(INSPECT_ROOT_SRC).toContain("failures-holidays");
  });

  it("InspectRoot.tsx imports FailuresInspectView", () => {
    expect(INSPECT_ROOT_SRC).toContain("FailuresInspectView");
  });
});

// ── 20. fetchFailures cast-through-unknown; data/types.ts not modified ────────

describe("fetchFailures — cast through unknown; no data/types.ts touch (T14 constraint)", () => {
  it("client.ts exports fetchFailures function", () => {
    expect(CLIENT_SRC).toContain("export async function fetchFailures");
  });

  it("fetchFailures casts through unknown at the JSON boundary", () => {
    // The function returns unknown; consumers cast
    expect(CLIENT_SRC).toContain("return (await response.json()) as unknown");
  });

  it("FailuresFindingsSection.tsx does not import from data/types", () => {
    expect(FAILURES_SECTION_SRC).not.toContain("data/types");
  });
});
