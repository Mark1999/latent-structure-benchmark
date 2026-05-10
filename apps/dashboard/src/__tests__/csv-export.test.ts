/**
 * CSV export tests.
 *
 * T10 acceptance criteria:
 *   - CSV has the exact 12 binding columns from §5 in the correct order.
 *   - CSV has one row per selected model.
 *   - Ellipse params are empty string for R1-b and R1-c rows.
 *   - Ellipse params are present (numeric) for R1-a rows.
 *   - Special chars in model_id, family, etc. are correctly CSV-quoted.
 *   - Header row matches §5 binding.
 *   - Comment row documents null semantics.
 *
 * No DOM needed — pure function tests.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T10
 *         DESIGN_SYSTEM.md §5 CSV export spec
 */

import { describe, it, expect } from "vitest";
import { domainResultToCsv } from "../lib/csv-export";
import type { DomainResultPublished, EllipseParams, R1State, WithinModelResult } from "../data/types";

// ── Fixture builder ───────────────────────────────────────────────────────────

function makeEllipse(): EllipseParams {
  return {
    semi_major: 0.12,
    semi_minor: 0.07,
    rotation_rad: 2.85,
    n_bootstrap: 500,
    ci_level: 0.95,
  };
}

function makeWmr(modelId: string, oci: number, deterministic: boolean): WithinModelResult {
  return {
    model_id: modelId,
    n_runs: 5,
    oci,
    oci_ci: null,
    underestimates_uncertainty: false,
    deterministic_output: deterministic,
    salience_stability_rho: null,
    elbow_stability: null,
    mds_procrustes_rmse: null,
    centrality_scores_by_run: {},
    centroid_run_id: "run-1",
    mds_within_model: [],
  };
}

function makeFixture(
  modelSetup: Array<{
    id: string;
    family: string;
    origin: string;
    r1: R1State;
    oci: number;
    deterministic: boolean;
  }>
): DomainResultPublished {
  const mds_coordinates: Record<string, [number, number]> = {};
  const mds_uncertainty: Record<string, EllipseParams | null> = {};
  const r1_states: Record<string, R1State> = {};
  const top_terms: Record<string, string[]> = {};
  const within_model_results: WithinModelResult[] = [];

  modelSetup.forEach(({ id, r1, oci, deterministic }, i) => {
    mds_coordinates[id] = [(i - modelSetup.length / 2) * 0.1, (i % 3 - 1) * 0.1];
    r1_states[id] = r1;
    top_terms[id] = ["a", "b"];
    mds_uncertainty[id] = r1 === "typical_concentration" ? makeEllipse() : null;
    within_model_results.push(makeWmr(id, oci, deterministic));
  });

  return {
    domain_slug: "family",
    analysis_version: "0.2",
    models: modelSetup.map(({ id, family, origin }) => ({
      provider: "test",
      model_id: id,
      family,
      origin,
      open_weights: false,
      collection_method: "api",
      quantization: null,
      release_date: "2026-01-01",
      version_label: id,
      source_notes: "",
    })),
    free_lists: {},
    mds_coordinates: mds_coordinates as unknown as Record<string, [[number, number]]>,
    mds_uncertainty,
    similarity_matrix: {},
    similarity_ci: {},
    consensus_score: 0.8,
    consensus_ci: [0.7, 0.9],
    consensus_type: "STRONG_CONSENSUS",
    sutrop_csi: {},
    within_model_results,
    groundings: [],
    generated_lede: "Test lede.",
    generated_at: "2026-05-07T00:07:50.238646Z",
    romney_small_n_warning: true,
    display: { r1_states, top_terms, top_terms_metric: "sutrop_csi" },
  };
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("domainResultToCsv — column structure", () => {
  const fixture = makeFixture([
    { id: "model-a", family: "claude", origin: "us", r1: "typical_concentration", oci: 50.0, deterministic: false },
  ]);

  it("includes a comment row before the header", () => {
    const csv = domainResultToCsv(fixture, ["model-a"]);
    const lines = csv.split("\n");
    expect(lines[0].startsWith("#")).toBe(true);
  });

  it("has the 12 binding columns in order on the header row", () => {
    const csv = domainResultToCsv(fixture, ["model-a"]);
    const lines = csv.split("\n");
    // Header is the second line (after comment).
    const header = lines[1];
    expect(header).toBe(
      "model_id,family,origin,mds_x,mds_y,semi_major,semi_minor,rotation_rad,n_bootstrap,oci,deterministic_output,r1_state"
    );
  });
});

describe("domainResultToCsv — row count", () => {
  const fixture = makeFixture([
    { id: "model-a", family: "claude", origin: "us", r1: "typical_concentration", oci: 50.0, deterministic: false },
    { id: "model-b", family: "gpt", origin: "us", r1: "low_concentration", oci: 1.5, deterministic: false },
    { id: "model-c", family: "deepseek", origin: "cn", r1: "deterministic", oci: 0.0, deterministic: true },
  ]);

  it("has one data row per selected model when all 3 are selected", () => {
    const csv = domainResultToCsv(fixture, ["model-a", "model-b", "model-c"]);
    const dataRows = csv.split("\n").filter((l) => !l.startsWith("#") && l.trim().length > 0).slice(1);
    expect(dataRows).toHaveLength(3);
  });

  it("has one data row when only 1 model is selected", () => {
    const csv = domainResultToCsv(fixture, ["model-a"]);
    const dataRows = csv.split("\n").filter((l) => !l.startsWith("#") && l.trim().length > 0).slice(1);
    expect(dataRows).toHaveLength(1);
  });

  it("has zero data rows when no models are selected", () => {
    const csv = domainResultToCsv(fixture, []);
    const dataRows = csv.split("\n").filter((l) => !l.startsWith("#") && l.trim().length > 0).slice(1);
    expect(dataRows).toHaveLength(0);
  });
});

describe("domainResultToCsv — ellipse params by R1 state", () => {
  const fixture = makeFixture([
    { id: "r1a", family: "claude", origin: "us", r1: "typical_concentration", oci: 220.0, deterministic: false },
    { id: "r1b", family: "gpt", origin: "us", r1: "low_concentration", oci: 1.5, deterministic: false },
    { id: "r1c", family: "deepseek", origin: "cn", r1: "deterministic", oci: 0.0, deterministic: true },
  ]);

  function parseRows(csv: string): Record<string, string>[] {
    const lines = csv.split("\n").filter((l) => !l.startsWith("#") && l.trim().length > 0);
    const headers = lines[0].split(",");
    return lines.slice(1).map((line) => {
      const values = line.split(",");
      return Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ""]));
    });
  }

  it("R1-a row has numeric semi_major, semi_minor, rotation_rad, n_bootstrap", () => {
    const csv = domainResultToCsv(fixture, ["r1a"]);
    const [row] = parseRows(csv);
    expect(row["semi_major"]).toBe("0.12");
    expect(row["semi_minor"]).toBe("0.07");
    expect(row["rotation_rad"]).toBe("2.85");
    expect(row["n_bootstrap"]).toBe("500");
  });

  it("R1-b row has empty string for ellipse params", () => {
    const csv = domainResultToCsv(fixture, ["r1b"]);
    const [row] = parseRows(csv);
    expect(row["semi_major"]).toBe("");
    expect(row["semi_minor"]).toBe("");
    expect(row["rotation_rad"]).toBe("");
    expect(row["n_bootstrap"]).toBe("");
  });

  it("R1-c row has empty string for ellipse params", () => {
    const csv = domainResultToCsv(fixture, ["r1c"]);
    const [row] = parseRows(csv);
    expect(row["semi_major"]).toBe("");
    expect(row["semi_minor"]).toBe("");
    expect(row["rotation_rad"]).toBe("");
    expect(row["n_bootstrap"]).toBe("");
  });

  it("R1-a row has correct oci and deterministic_output", () => {
    const csv = domainResultToCsv(fixture, ["r1a"]);
    const [row] = parseRows(csv);
    expect(row["oci"]).toBe("220");
    expect(row["deterministic_output"]).toBe("false");
  });

  it("R1-c row has oci=0 and deterministic_output=true", () => {
    const csv = domainResultToCsv(fixture, ["r1c"]);
    const [row] = parseRows(csv);
    expect(row["oci"]).toBe("0");
    expect(row["deterministic_output"]).toBe("true");
  });

  it("R1-a row has r1_state=typical_concentration", () => {
    const csv = domainResultToCsv(fixture, ["r1a"]);
    const [row] = parseRows(csv);
    expect(row["r1_state"]).toBe("typical_concentration");
  });

  it("R1-b row has r1_state=low_concentration", () => {
    const csv = domainResultToCsv(fixture, ["r1b"]);
    const [row] = parseRows(csv);
    expect(row["r1_state"]).toBe("low_concentration");
  });
});

describe("domainResultToCsv — CSV quoting", () => {
  it("quotes model_id containing a comma", () => {
    const fixture = makeFixture([
      { id: "model,with,commas", family: "test", origin: "us", r1: "typical_concentration", oci: 10.0, deterministic: false },
    ]);
    const csv = domainResultToCsv(fixture, ["model,with,commas"]);
    // The model_id should be quoted in the CSV.
    expect(csv).toContain('"model,with,commas"');
  });

  it("quotes family containing double quotes", () => {
    const fixture = makeFixture([
      { id: "model-x", family: 'family"name', origin: "us", r1: "typical_concentration", oci: 10.0, deterministic: false },
    ]);
    const csv = domainResultToCsv(fixture, ["model-x"]);
    // Double quotes inside a quoted field are escaped as "".
    expect(csv).toContain('"family""name"');
  });

  it("plain model_id with no special chars is not quoted", () => {
    const fixture = makeFixture([
      { id: "simple-id", family: "test", origin: "us", r1: "typical_concentration", oci: 10.0, deterministic: false },
    ]);
    const csv = domainResultToCsv(fixture, ["simple-id"]);
    const dataLine = csv.split("\n").filter((l) => !l.startsWith("#") && l.trim().length > 0)[1];
    expect(dataLine.startsWith("simple-id,")).toBe(true);
  });
});

describe("domainResultToCsv — family and origin columns", () => {
  const fixture = makeFixture([
    { id: "claude-opus-4-6", family: "claude", origin: "us", r1: "typical_concentration", oci: 50.0, deterministic: false },
    { id: "deepseek/deepseek-v3.2", family: "deepseek", origin: "cn", r1: "typical_concentration", oci: 80.0, deterministic: false },
  ]);

  it("includes correct family for each model", () => {
    const csv = domainResultToCsv(fixture, ["claude-opus-4-6", "deepseek/deepseek-v3.2"]);
    const lines = csv.split("\n").filter((l) => !l.startsWith("#") && l.trim().length > 0);
    // data rows start at index 1
    const row1 = lines[1];
    const row2 = lines[2];
    expect(row1).toContain(",claude,");
    expect(row2).toContain(",deepseek,");
  });

  it("includes correct origin for each model", () => {
    const csv = domainResultToCsv(fixture, ["claude-opus-4-6", "deepseek/deepseek-v3.2"]);
    const lines = csv.split("\n").filter((l) => !l.startsWith("#") && l.trim().length > 0);
    const row1 = lines[1];
    const row2 = lines[2];
    expect(row1).toContain(",us,");
    expect(row2).toContain(",cn,");
  });
});
