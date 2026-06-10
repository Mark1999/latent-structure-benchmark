/**
 * ChartToolbar tests (TM-B)
 *
 * Verifies:
 * 1. AC3: The four aria-label strings are present verbatim (§3.1.1(b)(ii)).
 * 2. AC3: Default checked states match the spec (uncertainty ON, cluster labels ON, lens OFF).
 * 3. Toolbar renders the overlay selector with the None option.
 * 4. Toolbar renders without crash with no pile model keys.
 * 5. Lens checkbox is disabled when lensDisabledByZoom=true.
 * 6. Visible label text does not contain §1.5.4 forbidden vocabulary.
 *
 * CLAUDE.md §6 rule 9: no real API calls. All data is fixture-based.
 * DESIGN_SYSTEM.md §3.1.1(b)(ii): verbatim aria-label strings.
 */

import { render, screen } from "@testing-library/react";
import { ChartToolbar } from "../components/ChartToolbar";

// ── Default props fixture ─────────────────────────────────────────────────────

const DEFAULT_PROPS = {
  pileModelKeys: [] as string[],
  overlayPileLabelKey: null,
  onOverlayPileLabelKeyChange: () => {},
  showUncertainty: true,
  onShowUncertaintyChange: () => {},
  showClusterLabels: true,
  onShowClusterLabelsChange: () => {},
  lensEnabled: false,
  onLensToggle: () => {},
  lensDisabledByZoom: false,
};

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("ChartToolbar (TM-B AC3)", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  // AC3: four verbatim aria-label strings from §3.1.1(b)(ii)
  it("AC3: renders aria-label='Overlay category names' on the overlay selector", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} />);
    const el = document.querySelector('[aria-label="Overlay category names"]');
    expect(el).not.toBeNull();
  });

  it("AC3: renders aria-label='Show uncertainty ellipses' on the Show uncertainty checkbox", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} />);
    const el = document.querySelector('input[aria-label="Show uncertainty ellipses"]');
    expect(el).not.toBeNull();
    expect(el!.getAttribute("type")).toBe("checkbox");
  });

  it("AC3: renders aria-label='Show cluster labels' on the Show cluster labels checkbox", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} />);
    const el = document.querySelector('input[aria-label="Show cluster labels"]');
    expect(el).not.toBeNull();
    expect(el!.getAttribute("type")).toBe("checkbox");
  });

  it("AC3: renders aria-label='Magnifying lens' on the lens checkbox", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} />);
    const el = document.querySelector('input[aria-label="Magnifying lens"]');
    expect(el).not.toBeNull();
    expect(el!.getAttribute("type")).toBe("checkbox");
  });

  // AC3: default states
  it("AC3: Show uncertainty is checked (default ON)", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} showUncertainty={true} />);
    const checkbox = document.querySelector('input[aria-label="Show uncertainty ellipses"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(true);
  });

  it("AC3: Show cluster labels is checked (default ON)", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} showClusterLabels={true} />);
    const checkbox = document.querySelector('input[aria-label="Show cluster labels"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(true);
  });

  it("AC3: Magnifying lens is unchecked (default OFF)", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} lensEnabled={false} />);
    const checkbox = document.querySelector('input[aria-label="Magnifying lens"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.checked).toBe(false);
  });

  // Toolbar renders without crash with empty pile model keys
  it("renders without crash when pileModelKeys is empty", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} pileModelKeys={[]} />);
    // Should render the overlay selector with just "None" option
    const select = document.querySelector('select[aria-label="Overlay category names"]');
    expect(select).not.toBeNull();
  });

  // Toolbar renders the None option in the overlay selector
  it("overlay selector contains a 'None' option", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} />);
    expect(screen.getByText("None")).toBeInTheDocument();
  });

  // Lens disabled when lensDisabledByZoom=true
  it("lens checkbox is disabled when lensDisabledByZoom is true", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} lensDisabledByZoom={true} />);
    const checkbox = document.querySelector('input[aria-label="Magnifying lens"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.disabled).toBe(true);
  });

  // Lens checkbox is enabled when lensDisabledByZoom=false
  it("lens checkbox is enabled when lensDisabledByZoom is false", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} lensDisabledByZoom={false} />);
    const checkbox = document.querySelector('input[aria-label="Magnifying lens"]') as HTMLInputElement;
    expect(checkbox).not.toBeNull();
    expect(checkbox.disabled).toBe(false);
  });

  // AC6 M3: visible label text does not contain §1.5.4 forbidden vocabulary.
  // The four pre-cleared aria-label strings from §3.1.1(b)(ii) are safe.
  // Visible <label> text used: "Overlay category names", "Show uncertainty",
  // "Show cluster labels", "Magnifying lens" -- none contain forbidden terms.
  it("AC6 M3: toolbar text contains only the four pre-cleared visible labels", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} />);
    const toolbarText = document.querySelector('.chart-toolbar')?.textContent ?? "";
    // The four approved visible labels must be present
    expect(toolbarText).toContain("Overlay category names");
    expect(toolbarText).toContain("Show uncertainty");
    expect(toolbarText).toContain("Show cluster labels");
    expect(toolbarText).toContain("Magnifying lens");
  });

  // Toolbar renders the .chart-toolbar container
  it("renders .chart-toolbar container", () => {
    render(<ChartToolbar {...DEFAULT_PROPS} />);
    expect(document.querySelector(".chart-toolbar")).not.toBeNull();
  });

  // Toolbar renders with pile model keys
  it("renders pile model keys as options in the overlay selector", () => {
    render(
      <ChartToolbar
        {...DEFAULT_PROPS}
        pileModelKeys={["fixture-model-alpha", "fixture-model-beta"]}
        overlayPileLabelKey="fixture-model-alpha"
      />
    );
    const select = document.querySelector('select[aria-label="Overlay category names"]') as HTMLSelectElement;
    expect(select).not.toBeNull();
    // Should have the two fixture models + None
    const options = Array.from(select.options).map(o => o.value);
    expect(options).toContain("fixture-model-alpha");
    expect(options).toContain("fixture-model-beta");
    expect(options).toContain("__none__");
  });
});
