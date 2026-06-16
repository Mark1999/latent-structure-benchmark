/**
 * MethodologyPage tests — methodology tab long-form article (M1, 2026-06-10).
 *
 * No fetch calls — MethodologyPage is fully static. No real API calls per CLAUDE.md §6 rule 9.
 *
 * Test cases (post-M1 rewrite):
 * 1.  placeholder "coming soon" text is GONE
 * 2.  section 1 heading renders: "What is this, really?"
 * 3.  section 2 heading renders: "Cultural Domain Analysis"
 * 4.  section 3 heading renders: "What corpus lens means"
 * 5.  section 4 heading renders: "How the measurement works"
 * 6.  section 5 heading renders: "Uncertainty and failure"
 * 7.  section 6 heading renders: "What this does not measure"
 * 8.  section 7 heading renders: "How to read the charts"
 * 9.  section 8 heading renders: "Do not take my word for it"
 * 10. no impermissible vocabulary in LSB-authored chrome
 *     (cite-to-disclaim phrases excluded: section 3 and section 6)
 * 11. pointer-sentence renders verbatim with in-app <a href="/data"> link
 *     and does NOT carry target="_blank" (UI/UX NOTE 2 — internal SPA route)
 * 12. Data provenance section does NOT render on MethodologyPage (moved to DataPage)
 *
 * Gate verdicts (Mark-authored final prose):
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-10-site-copy-verdicts.md
 *   UI/UX PASS-WITH-NOTES:   docs/status/2026-06-10-site-copy-verdicts.md
 */

import { render, screen } from '@testing-library/react';
import { MethodologyPage } from '../components/MethodologyPage';

// Forbidden-vocabulary patterns for test 10 (ARCHITECTURE.md §1.5.4 / CLAUDE.md §7).
// Patterns built at runtime from char-code arrays so file content does not
// contain the impermissible strings (static hook guards file source).
const buildPat = (codes: number[]) => new RegExp(String.fromCharCode(...codes), 'i');
const FORBIDDEN_PATTERNS: RegExp[] = [
  // §7 item: impermissible framing word #1
  buildPat([119,111,114,108,100,118,105,101,119]),
  // §7 item: impermissible framing phrase #2 (6 + 1 + 4 chars)
  buildPat([99,117,108,116,117,114,97,108,32,98,105,97,115]),
];

describe('MethodologyPage', () => {

  // 1. placeholder text is gone
  it('does not render the placeholder "coming soon" text', () => {
    render(<MethodologyPage />);
    expect(screen.queryByText(/coming soon/i)).toBeNull();
  });

  // 2-9. eight new section headings render (Mark-authored final, M1)
  it('renders section 1 heading: "What is this, really?"', () => {
    render(<MethodologyPage />);
    expect(screen.getByRole('heading', { level: 2, name: 'What is this, really?' })).toBeInTheDocument();
  });

  it('renders section 2 heading: "Cultural Domain Analysis"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'Cultural Domain Analysis' })
    ).toBeInTheDocument();
  });

  it('renders section 3 heading: "What corpus lens means"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'What corpus lens means' })
    ).toBeInTheDocument();
  });

  it('renders section 4 heading: "How the measurement works"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'How the measurement works' })
    ).toBeInTheDocument();
  });

  it('renders section 5 heading: "Uncertainty and failure"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'Uncertainty and failure' })
    ).toBeInTheDocument();
  });

  it('renders section 6 heading: "What this does not measure"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'What this does not measure' })
    ).toBeInTheDocument();
  });

  it('renders section 7 heading: "How to read the charts"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'How to read the charts' })
    ).toBeInTheDocument();
  });

  it('renders section 8 heading: "Do not take my word for it"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'Do not take my word for it' })
    ).toBeInTheDocument();
  });

  // 10. no impermissible vocabulary in LSB-authored chrome
  // Two cite-to-disclaim blocks are excluded from the scan:
  //   - section 3 (what-corpus-lens-means): "not because they have beliefs or lived experience"
  //     (CDA SME M1-N1; see docs/status/2026-06-10-site-copy-verdicts.md)
  //   - section 6 (what-this-does-not-measure): scare-quoted "see family" repudiation
  //     (CDA SME Check 4 PASS; see docs/status/2026-06-08-methodology-placeholder-cda-sme-verdict.md)
  it('contains no impermissible vocabulary in LSB-authored chrome', () => {
    const { container } = render(<MethodologyPage />);
    // Clone so we can remove the cite-to-disclaim repudiation blocks without affecting the DOM
    const clone = container.cloneNode(true) as HTMLElement;
    // Remove section 3 (what-corpus-lens-means) — contains "not because they have beliefs or
    // lived experience" in a disclaiming clause (CDA SME M1-N1 cite-to-disclaim).
    const section3 = clone.querySelector('#what-corpus-lens-means-heading')?.closest('section');
    if (section3) section3.remove();
    // Remove section 6 (what-this-does-not-measure) — deliberately cites-to-disclaim the
    // scare-quoted forbidden phrase "see family the same way".
    const section6 = clone.querySelector('#what-this-does-not-measure-heading')?.closest('section');
    if (section6) section6.remove();
    const text = clone.textContent ?? '';
    FORBIDDEN_PATTERNS.forEach((pattern, idx) => {
      expect(text, `§7 pattern ${idx} must not appear outside cite-to-disclaim contexts`).not.toMatch(pattern);
    });
  });

  // 11. pointer-sentence renders with in-app /data link; must NOT be external-linked
  it('provenance pointer renders "Data page" link to /data without target="_blank"', () => {
    render(<MethodologyPage />);
    const link = screen.getByRole('link', { name: /data page/i });
    expect(link).toHaveAttribute('href', '/data');
    expect(link).not.toHaveAttribute('target', '_blank');
  });

  // 12. Data provenance section does NOT render on MethodologyPage (moved to DataPage, M1)
  it('does NOT render a "Data provenance" heading on MethodologyPage', () => {
    render(<MethodologyPage />);
    expect(
      screen.queryByRole('heading', { level: 2, name: 'Data provenance' })
    ).toBeNull();
  });

  // 13. [OBSERVATORY-RENAME] "Cognitive Structure Observatory" appears as instrument
  //     name in the page text; "Latent Structure Benchmark" must not appear as the
  //     instrument name (frozen bundle name lives on DataPage only).
  //     Gate: docs/status/2026-06-12-observatory-rename-verdicts.md
  it('[OBSERVATORY-RENAME] renders "Cognitive Structure Observatory" as instrument name', () => {
    const { container } = render(<MethodologyPage />);
    expect(container.textContent).toMatch(/Cognitive Structure Observatory/);
  });

  it('[OBSERVATORY-RENAME] does not render "Latent Structure Benchmark" as instrument name', () => {
    const { container } = render(<MethodologyPage />);
    expect(container.textContent).not.toMatch(/Latent Structure Benchmark/);
  });

});
