/**
 * Tests for api/client.ts fetch functions.
 *
 * AC3, AC8: No real fetch calls. All network is mocked with vi.fn().
 * Source: CLAUDE.md §6 R9 (no real API calls in tests).
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { fetchManifest, fetchDomain } from "../api/client";
import type { Manifest, DomainResultPublished } from "../data/types";

// Mock the global fetch
const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
  mockFetch.mockReset();
});

const MOCK_MANIFEST: Manifest = {
  built_at: "2026-05-10T00:00:00Z",
  domains: [
    {
      slug: "family",
      analysis_version: "0.2",
      n_models: 11,
      model_ids: ["claude-opus-4-6", "openai/gpt-5.4"],
      generated_at: "2026-05-07T00:07:50Z",
    },
    {
      slug: "holidays",
      analysis_version: "0.2",
      n_models: 9,
      model_ids: ["claude-opus-4-6", "openai/gpt-5.4"],
      generated_at: "2026-05-07T00:15:00Z",
    },
  ],
  oci_low_concentration_threshold: 3.0,
};

const MOCK_DOMAIN_RESULT: Partial<DomainResultPublished> = {
  domain_slug: "family",
  analysis_version: "0.2",
  models: [],
  generated_lede: "Frontier language models organize family vocabulary with strong categorical agreement.",
  consensus_type: "STRONG_CONSENSUS",
  consensus_score: 0.85,
  consensus_ci: [0.78, 0.91],
  groundings: [],
  generated_at: "2026-05-07T00:07:50Z",
  display: {
    r1_states: {},
    top_terms: {},
    top_terms_metric: "sutrop_csi",
  },
};

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

describe("fetchManifest", () => {
  it("fetches /data/manifest.json and returns typed Manifest", async () => {
    mockFetch.mockResolvedValueOnce(makeOkResponse(MOCK_MANIFEST));

    const result = await fetchManifest();

    expect(mockFetch).toHaveBeenCalledOnce();
    const [url, options] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/data/manifest.json");
    expect(options?.credentials).toBe("omit");

    expect(result.domains).toHaveLength(2);
    expect(result.domains[0].slug).toBe("family");
    expect(result.oci_low_concentration_threshold).toBe(3.0);
  });

  it("throws when fetch response is not ok (HTTP 404)", async () => {
    mockFetch.mockResolvedValueOnce(makeErrorResponse(404, "Not Found"));

    await expect(fetchManifest()).rejects.toThrow("HTTP 404");
  });

  it("throws when fetch itself fails (network error)", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network error"));

    await expect(fetchManifest()).rejects.toThrow("Network error");
  });

  it("uses credentials: 'omit' (same-origin, no auth)", async () => {
    mockFetch.mockResolvedValueOnce(makeOkResponse(MOCK_MANIFEST));

    await fetchManifest();

    const [, options] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(options?.credentials).toBe("omit");
  });
});

describe("fetchDomain", () => {
  it("fetches /data/{slug}.json when no version specified", async () => {
    mockFetch.mockResolvedValueOnce(makeOkResponse(MOCK_DOMAIN_RESULT));

    await fetchDomain("family");

    const [url] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/data/family.json");
  });

  it("fetches /data/{slug}.v{version}.json when version specified", async () => {
    mockFetch.mockResolvedValueOnce(makeOkResponse(MOCK_DOMAIN_RESULT));

    await fetchDomain("family", "0.2");

    const [url] = mockFetch.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/data/family.v0.2.json");
  });

  it("returns typed DomainResultPublished", async () => {
    mockFetch.mockResolvedValueOnce(makeOkResponse(MOCK_DOMAIN_RESULT));

    const result = await fetchDomain("family");

    expect(result.domain_slug).toBe("family");
    expect(result.generated_lede.toLowerCase()).toContain("frontier language models");
    expect(result.display.top_terms_metric).toBe("sutrop_csi");
  });

  it("throws when fetch response is not ok (HTTP 500)", async () => {
    mockFetch.mockResolvedValueOnce(makeErrorResponse(500, "Server Error"));

    await expect(fetchDomain("family")).rejects.toThrow("HTTP 500");
  });

  it("includes slug name in error message", async () => {
    mockFetch.mockResolvedValueOnce(makeErrorResponse(404, "Not Found"));

    await expect(fetchDomain("holidays")).rejects.toThrow('"holidays"');
  });

  it("includes version in error message when version is given", async () => {
    mockFetch.mockResolvedValueOnce(makeErrorResponse(404, "Not Found"));

    await expect(fetchDomain("family", "0.2")).rejects.toThrow("v0.2");
  });
});
