/**
 * Permalink codec tests.
 *
 * T10 acceptance criteria:
 *   - Round-trip: decodePermalink(encodePermalink(state)) equals the original state.
 *   - Invalid URL hash returns null.
 *   - Empty string returns null.
 *   - Permalink with domain=family&models=a,b,c#mds decodes correctly.
 *
 * No DOM needed — pure function tests.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T10
 */

import { describe, it, expect } from "vitest";
import { encodePermalink, decodePermalink } from "../lib/permalink";
import type { PermalinkState } from "../lib/permalink";

// ── Round-trip tests ──────────────────────────────────────────────────────────

describe("encodePermalink / decodePermalink round-trip", () => {
  it("round-trips a simple family + 3 models state", () => {
    const state: PermalinkState = {
      domain: "family",
      models: ["claude-opus-4-6", "openai/gpt-5.4", "deepseek/deepseek-v3.2"],
      vizTab: "mds",
    };
    const encoded = encodePermalink(state);
    const decoded = decodePermalink(encoded);
    expect(decoded).not.toBeNull();
    expect(decoded!.domain).toBe(state.domain);
    expect(decoded!.models).toEqual(state.models);
    expect(decoded!.vizTab).toBe(state.vizTab);
  });

  it("round-trips a holidays domain state", () => {
    const state: PermalinkState = {
      domain: "holidays",
      models: ["openai/gpt-5.4", "claude-sonnet-4-6"],
      vizTab: "mds",
    };
    const encoded = encodePermalink(state);
    const decoded = decodePermalink(encoded);
    expect(decoded).not.toBeNull();
    expect(decoded!.domain).toBe("holidays");
    expect(decoded!.models).toEqual(["openai/gpt-5.4", "claude-sonnet-4-6"]);
    expect(decoded!.vizTab).toBe("mds");
  });

  it("round-trips a single-model selection", () => {
    const state: PermalinkState = {
      domain: "family",
      models: ["x-ai/grok-4"],
      vizTab: "mds",
    };
    const encoded = encodePermalink(state);
    const decoded = decodePermalink(encoded);
    expect(decoded).not.toBeNull();
    expect(decoded!.models).toEqual(["x-ai/grok-4"]);
  });

  it("round-trips a full 11-model selection", () => {
    const models = [
      "claude-opus-4-6",
      "claude-sonnet-4-6",
      "deepseek/deepseek-v3.2",
      "google/gemini-2.5-pro",
      "meta-llama/llama-4-maverick",
      "microsoft/phi-4",
      "mistralai/mistral-large-2512",
      "mistralai/mistral-small-2603",
      "openai/gpt-5.4",
      "openai/gpt-5.4-mini",
      "x-ai/grok-4",
    ];
    const state: PermalinkState = {
      domain: "family",
      models,
      vizTab: "mds",
    };
    const encoded = encodePermalink(state);
    const decoded = decodePermalink(encoded);
    expect(decoded).not.toBeNull();
    expect(decoded!.models).toEqual(models);
  });
});

// ── Encode format tests ───────────────────────────────────────────────────────

describe("encodePermalink format", () => {
  it("includes ?domain= search param", () => {
    const encoded = encodePermalink({
      domain: "family",
      models: ["claude-opus-4-6"],
      vizTab: "mds",
    });
    expect(encoded).toContain("domain=family");
  });

  it("includes #mds hash", () => {
    const encoded = encodePermalink({
      domain: "family",
      models: ["claude-opus-4-6"],
      vizTab: "mds",
    });
    expect(encoded).toMatch(/#mds$/);
  });

  it("starts with ?", () => {
    const encoded = encodePermalink({
      domain: "family",
      models: ["a"],
      vizTab: "mds",
    });
    expect(encoded.startsWith("?")).toBe(true);
  });
});

// ── Decode invalid input tests ────────────────────────────────────────────────

describe("decodePermalink invalid inputs", () => {
  it("returns null for empty string", () => {
    expect(decodePermalink("")).toBeNull();
  });

  it("returns null for missing domain param", () => {
    expect(decodePermalink("?models=a,b#mds")).toBeNull();
  });

  it("returns null for missing models param", () => {
    expect(decodePermalink("?domain=family#mds")).toBeNull();
  });

  it("returns null for empty models value", () => {
    expect(decodePermalink("?domain=family&models=#mds")).toBeNull();
  });

  it("returns null for invalid viz tab (unrecognised fragment)", () => {
    // Non-mds, non-freelist, non-empty hash → invalid
    expect(decodePermalink("?domain=family&models=a#similarity")).toBeNull();
    expect(decodePermalink("?domain=family&models=a#drift")).toBeNull();
    expect(decodePermalink("?domain=family&models=a#unknown")).toBeNull();
  });

  it("accepts #freelist as a valid viz tab (Phase 6 T7)", () => {
    // #freelist is now an active tab per T7.
    const result = decodePermalink("?domain=family&models=a#freelist");
    expect(result).not.toBeNull();
    expect(result?.vizTab).toBe("freelist");
  });

  it("returns null for a bare fragment with no search params", () => {
    // Just "#mds" with no domain/models
    expect(decodePermalink("#mds")).toBeNull();
  });

  it("returns null for random garbage", () => {
    expect(decodePermalink("not-a-url-at-all")).toBeNull();
  });
});

// ── Specific decode format ────────────────────────────────────────────────────

describe("decodePermalink specific format", () => {
  it("decodes ?domain=family&models=a,b,c#mds correctly", () => {
    const result = decodePermalink("?domain=family&models=a,b,c#mds");
    expect(result).not.toBeNull();
    expect(result!.domain).toBe("family");
    expect(result!.models).toEqual(["a", "b", "c"]);
    expect(result!.vizTab).toBe("mds");
  });

  it("handles empty hash (defaults to mds)", () => {
    const result = decodePermalink("?domain=holidays&models=x");
    expect(result).not.toBeNull();
    expect(result!.vizTab).toBe("mds");
  });

  it("is case-insensitive for the hash part", () => {
    // '#MDS' vs '#mds' — decodePermalink lowercases the hash
    const result = decodePermalink("?domain=family&models=a#MDS");
    expect(result).not.toBeNull();
    expect(result!.vizTab).toBe("mds");
  });
});

// ── Gap-fill: '/' chars in model_id are percent-encoded ──────────────────────
// Identified by the Tester agent at T10 review. encodePermalink uses
// URLSearchParams which percent-encodes '/' as '%2F' inside param values.
// This test makes the contract explicit and guards against any future
// change that would break URL-safe encoding for provider-prefixed model ids.

describe("encodePermalink — slash encoding in model_id (gap-fill)", () => {
  it("encodes '/' in a model_id as '%2F' in the URL string", () => {
    // deepseek/deepseek-v3.2 contains a '/'; the encoded URL must contain
    // '%2F' (or '%2f') so the permalink survives copy-paste and HTTP routing.
    const encoded = encodePermalink({
      domain: "family",
      models: ["deepseek/deepseek-v3.2"],
      vizTab: "mds",
    });
    // URLSearchParams encodes '/' in a param value as '%2F'.
    expect(encoded.toLowerCase()).toContain("%2f");
  });

  it("round-trips a model_id with multiple '/' chars without corruption", () => {
    // meta-llama/llama-4-maverick contains one '/'.
    // After encode → decode the model_id must be restored verbatim.
    const state: PermalinkState = {
      domain: "family",
      models: ["meta-llama/llama-4-maverick", "openai/gpt-5.4"],
      vizTab: "mds",
    };
    const decoded = decodePermalink(encodePermalink(state));
    expect(decoded).not.toBeNull();
    expect(decoded!.models).toEqual(["meta-llama/llama-4-maverick", "openai/gpt-5.4"]);
  });
});
