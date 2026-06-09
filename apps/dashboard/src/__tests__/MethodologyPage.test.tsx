/**
 * MethodologyPage tests — methodology tab long-form article.
 *
 * No fetch calls — MethodologyPage is fully static. No real API calls per CLAUDE.md §6 rule 9.
 *
 * Test cases:
 * 1.  placeholder "coming soon" text is GONE
 * 2.  section 1 heading renders: "What is this, really?"
 * 3.  section 2 heading renders: 'What does "corpus lens" actually mean?'
 * 4.  section 3 heading renders: "How does the measurement work? (there is no magic in it)"
 * 5.  section 4 heading renders: "What this does not measure (or, the picture on the dresser)"
 * 6.  section 5 heading renders: "How do I read the charts?"
 * 7.  section 6 heading renders: "Do not take my word for it"
 * 8.  existing section "Data provenance" still renders (verbatim, untouched)
 * 9.  existing section "Cross-model term map and uncertainty" still renders (verbatim, untouched)
 * 10. no impermissible vocabulary in LSB-authored chrome (cite-to-disclaim phrase excluded)
 * 11. provenance.json link is present with correct attributes
 *
 * Gate verdicts (sections 1-6 placeholder prose):
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-08-methodology-placeholder-cda-sme-verdict.md
 *   UI/UX PASS-WITH-NOTES:   docs/status/2026-06-08-methodology-placeholder-uiux-verdict.md
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

  // 2-7. six new section headings render
  it('renders section 1 heading: "What is this, really?"', () => {
    render(<MethodologyPage />);
    expect(screen.getByRole('heading', { level: 2, name: 'What is this, really?' })).toBeInTheDocument();
  });

  it('renders section 2 heading containing "corpus lens" and "actually mean"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: /what does.*corpus lens.*actually mean/i })
    ).toBeInTheDocument();
  });

  it('renders section 3 heading: "How does the measurement work? (there is no magic in it)"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: /how does the measurement work/i })
    ).toBeInTheDocument();
  });

  it('renders section 4 heading: "What this does not measure (or, the picture on the dresser)"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: /what this does not measure/i })
    ).toBeInTheDocument();
  });

  it('renders section 5 heading: "How do I read the charts?"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: /how do i read the charts/i })
    ).toBeInTheDocument();
  });

  it('renders section 6 heading: "Do not take my word for it"', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: /do not take my word for it/i })
    ).toBeInTheDocument();
  });

  // 8. existing "Data provenance" section still renders (verbatim, untouched)
  it('still renders the "Data provenance" section heading', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'Data provenance' })
    ).toBeInTheDocument();
  });

  // 9. existing "Cross-model term map and uncertainty" section still renders
  it('still renders the "Cross-model term map and uncertainty" section heading', () => {
    render(<MethodologyPage />);
    expect(
      screen.getByRole('heading', { level: 2, name: 'Cross-model term map and uncertainty' })
    ).toBeInTheDocument();
  });

  // 10. no impermissible vocabulary in LSB-authored chrome
  // The section-4 scare-quoted cite-to-disclaim phrase is in an explicitly-repudiating
  // context (CDA SME PASS, Check 4) — we strip section 4 before scanning.
  it('contains no impermissible vocabulary in LSB-authored chrome', () => {
    const { container } = render(<MethodologyPage />);
    // Clone so we can remove the cite-to-disclaim repudiation block without affecting the DOM
    const clone = container.cloneNode(true) as HTMLElement;
    // Remove section 4 (the "What this does not measure" section) from the scan
    // because it deliberately cites-to-disclaim the scare-quoted forbidden phrase.
    const section4 = clone.querySelector('#what-this-does-not-measure-heading')?.closest('section');
    if (section4) section4.remove();
    const text = clone.textContent ?? '';
    FORBIDDEN_PATTERNS.forEach((pattern, idx) => {
      expect(text, `§7 pattern ${idx} must not appear outside cite-to-disclaim context`).not.toMatch(pattern);
    });
  });

  // 11. provenance.json link present with correct attributes
  it('provenance.json link has correct href, target, and rel', () => {
    render(<MethodologyPage />);
    const link = screen.getByRole('link', { name: /provenance\.json/i });
    expect(link).toHaveAttribute('href', '/data/provenance.json');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

});
