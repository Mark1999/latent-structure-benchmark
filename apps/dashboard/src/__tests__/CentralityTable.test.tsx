/**
 * CentralityTable tests (T7 — vitest harness activation)
 *
 * Verifies: read-as-table role+state; columns match published bare-tuple shape
 * (no "Bootstrap N" column); CI columns only present when CI data is provided.
 * CLAUDE.md §6 rule 9: no real API calls. Fixture-based only.
 */

import { render, screen } from "@testing-library/react";
import { CentralityTable } from "../components/CentralityTable";

// ── Fixture data ──────────────────────────────────────────────────────────────

const FIXTURE_IDS = ["fixture-model-alpha", "fixture-model-beta", "fixture-model-gamma"];

const FIXTURE_SCORES: Record<string, number> = {
  "fixture-model-alpha": 0.812,
  "fixture-model-beta": 0.634,
  "fixture-model-gamma": 0.401,
};

// Published shape: bare [lo, hi] tuple — no per-model Bootstrap N
const FIXTURE_CI: Record<string, [number, number]> = {
  "fixture-model-alpha": [0.777, 0.845],
  "fixture-model-beta": [0.601, 0.667],
  "fixture-model-gamma": [0.372, 0.429],
};

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("CentralityTable", () => {
  it("renders a table with correct role and accessible caption", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        consensusType="STRONG_CONSENSUS"
        sortedIds={FIXTURE_IDS}
        centralityScores={FIXTURE_SCORES}
        centralityCi={FIXTURE_CI}
      />
    );

    const table = screen.getByRole("table");
    expect(table).toBeInTheDocument();

    // Caption should mention the domain slug
    const caption = table.querySelector("caption");
    expect(caption).not.toBeNull();
    expect(caption!.textContent).toMatch(/fixture-domain/);
  });

  it("renders Rank, Model, model_id, Centrality score columns always", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        consensusType="WEAK_CONSENSUS"
        sortedIds={FIXTURE_IDS}
        centralityScores={FIXTURE_SCORES}
      />
    );

    // The four always-present column headers
    expect(screen.getByText("Rank")).toBeInTheDocument();
    expect(screen.getByText("Model")).toBeInTheDocument();
    expect(screen.getByText("model_id")).toBeInTheDocument();
    expect(screen.getByText("Centrality score")).toBeInTheDocument();
  });

  it("renders 95% CI lower and upper columns when centralityCi is provided", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        sortedIds={FIXTURE_IDS}
        centralityScores={FIXTURE_SCORES}
        centralityCi={FIXTURE_CI}
      />
    );

    expect(screen.getByText("95% CI lower")).toBeInTheDocument();
    expect(screen.getByText("95% CI upper")).toBeInTheDocument();
  });

  it("does NOT render a Bootstrap N column (bare-tuple shape contract)", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        sortedIds={FIXTURE_IDS}
        centralityScores={FIXTURE_SCORES}
        centralityCi={FIXTURE_CI}
      />
    );

    // The published centrality_ci shape is model_id → [lo, hi] with no per-model N.
    // A "Bootstrap N" column would misrepresent the data shape.
    expect(screen.queryByText(/Bootstrap N/i)).toBeNull();
    expect(screen.queryByText(/bootstrap n/i)).toBeNull();
  });

  it("does NOT render CI columns when centralityCi is absent", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        sortedIds={FIXTURE_IDS}
        centralityScores={FIXTURE_SCORES}
        // no centralityCi
      />
    );

    expect(screen.queryByText("95% CI lower")).toBeNull();
    expect(screen.queryByText("95% CI upper")).toBeNull();
  });

  it("renders the correct number of data rows (one per sortedId)", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        sortedIds={FIXTURE_IDS}
        centralityScores={FIXTURE_SCORES}
        centralityCi={FIXTURE_CI}
      />
    );

    const tbody = document.querySelector("tbody");
    expect(tbody).not.toBeNull();
    const rows = tbody!.querySelectorAll("tr");
    expect(rows).toHaveLength(FIXTURE_IDS.length);
  });

  it("renders empty state message when sortedIds is empty", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        sortedIds={[]}
        centralityScores={{}}
      />
    );

    expect(
      screen.getByText(/Select one or more models/)
    ).toBeInTheDocument();
  });

  it("renders model short name (after last slash) in Model column", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        sortedIds={["openrouter/fixture-model-alpha"]}
        centralityScores={{ "openrouter/fixture-model-alpha": 0.5 }}
      />
    );

    // Short name strips the prefix
    expect(screen.getByText("fixture-model-alpha")).toBeInTheDocument();
  });

  it("renders 'negative centrality' note for scores below zero", () => {
    render(
      <CentralityTable
        domainSlug="fixture-domain"
        sortedIds={["fixture-model-neg"]}
        centralityScores={{ "fixture-model-neg": -0.123 }}
      />
    );

    expect(screen.getByText("negative centrality")).toBeInTheDocument();
  });
});
