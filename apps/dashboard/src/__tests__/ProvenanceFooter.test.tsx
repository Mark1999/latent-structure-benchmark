/**
 * ProvenanceFooter tests (T7 — vitest harness activation)
 *
 * All network calls are mocked — no real fetch. Fixtures inline below.
 * CLAUDE.md §6 rule 9: no real API calls in tests.
 */

import { render, screen, waitFor } from "@testing-library/react";
import { ProvenanceFooter } from "../components/ProvenanceFooter";

// ── Fixture data ──────────────────────────────────────────────────────────────

const PROVENANCE_FULL = {
  numpy_version: "1.26.4",
  scipy_version: "1.13.0",
  generated_at_utc: "2026-05-31T14:22:00Z",
  domains: {
    family: {
      version: "0.7",
      model_count: 24,
      sha256: "fixture-sha256-family",
      guard: "fixture-guard",
    },
    food: {
      version: "0.7",
      model_count: 18,
      sha256: "fixture-sha256-food",
      guard: "fixture-guard",
    },
  },
};

const PROVENANCE_NO_DATE = {
  numpy_version: "1.26.4",
  scipy_version: "1.13.0",
  // no generated_at_utc
  domains: {
    family: {
      version: "0.7",
      model_count: 24,
      sha256: "fixture-sha256-family",
      guard: "fixture-guard",
    },
  },
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function mockFetch(data: object | null, ok = true) {
  vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
    ok,
    json: async () => data,
  } as Response);
}

afterEach(() => {
  vi.restoreAllMocks();
});

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("ProvenanceFooter", () => {
  it("renders NumPy/SciPy versions and baseline date when provenance data is present", async () => {
    mockFetch(PROVENANCE_FULL);
    render(<ProvenanceFooter activeDomain={null} />);

    await waitFor(() => {
      expect(
        screen.getByText(/Calculated with NumPy 1\.26\.4 and SciPy 1\.13\.0/)
      ).toBeInTheDocument();
    });

    // Baseline date sourced from generated_at_utc.slice(0,10)
    expect(screen.getByText(/baseline 2026-05-31/)).toBeInTheDocument();
  });

  it("renders when activeDomain is present in provenance domains block (B5b pass)", async () => {
    mockFetch(PROVENANCE_FULL);
    render(<ProvenanceFooter activeDomain="family" />);

    await waitFor(() => {
      expect(
        screen.getByText(/Calculated with NumPy 1\.26\.4/)
      ).toBeInTheDocument();
    });
  });

  it("renders nothing when activeDomain is absent from provenance domains block (B5b render-nothing)", async () => {
    // 'holidays' is NOT in PROVENANCE_FULL.domains
    mockFetch(PROVENANCE_FULL);
    const { container } = render(<ProvenanceFooter activeDomain="holidays" />);

    // Wait long enough for the fetch to resolve
    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it("renders nothing when versions are absent from provenance JSON", async () => {
    mockFetch({ generated_at_utc: "2026-05-31T14:22:00Z", domains: {} });
    const { container } = render(<ProvenanceFooter activeDomain={null} />);

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it("renders nothing when fetch fails (render-nothing fallback)", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new Error("network"));
    const { container } = render(<ProvenanceFooter activeDomain={null} />);

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it("does not render date span when generated_at_utc is absent", async () => {
    mockFetch(PROVENANCE_NO_DATE);
    render(<ProvenanceFooter activeDomain="family" />);

    await waitFor(() => {
      expect(
        screen.getByText(/Calculated with NumPy 1\.26\.4/)
      ).toBeInTheDocument();
    });

    // Date span must not appear
    expect(screen.queryByText(/baseline/)).toBeNull();
  });

  it("date shown is exactly generated_at_utc.slice(0,10), not hardcoded", async () => {
    const custom = {
      ...PROVENANCE_FULL,
      generated_at_utc: "2025-12-01T00:00:00Z",
    };
    mockFetch(custom);
    render(<ProvenanceFooter activeDomain={null} />);

    await waitFor(() => {
      expect(screen.getByText(/baseline 2025-12-01/)).toBeInTheDocument();
    });
    // Ensure it is NOT the fixture date 2026-05-31
    expect(screen.queryByText(/baseline 2026-05-31/)).toBeNull();
  });

  it("renders normally on a non-domain route (activeDomain undefined)", async () => {
    mockFetch(PROVENANCE_FULL);
    render(<ProvenanceFooter />);

    await waitFor(() => {
      expect(
        screen.getByText(/Calculated with NumPy 1\.26\.4/)
      ).toBeInTheDocument();
    });
  });
});
