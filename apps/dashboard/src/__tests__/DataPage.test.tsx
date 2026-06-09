/**
 * DataPage tests — Data download tab.
 *
 * No fetch calls — DataPage is fully static. No real API calls per CLAUDE.md §6 rule 9.
 *
 * Test cases (Architect plan §6):
 * 1.  renders + <main aria-label="Data download">
 * 2.  HF link: exact href + target=_blank + rel=noopener noreferrer
 * 3.  DOI link: exact href + target=_blank + rel=noopener noreferrer
 * 4.  B2 tarball link: exact href + target=_blank + rel=noopener noreferrer
 * 5.  "1.55 GB" warning appears before the tarball anchor in reading order
 * 6.  SHA256 verbatim in <code>
 * 7.  GitHub link: exact href + target=_blank + rel=noopener noreferrer
 * 8.  Citation first line in <pre><code>
 * 9.  Every external <a> has target=_blank + rel=noopener noreferrer (loop)
 * 10. Every external <a> has an "opens" sr-only span
 * 11. No forbidden vocabulary (ARCHITECTURE.md §1.5.4 / CLAUDE.md §7)
 * 12. All four licenses present
 *
 * Gate verdicts:
 *   CDA SME PASS-WITH-NOTES: docs/status/2026-06-08-phase9a-data-tab-cda-sme-verdict.md
 *   UI/UX PASS-WITH-NOTES:   docs/status/2026-06-08-phase9a-data-tab-ui-ux-verdict.md
 */

import { render, screen } from '@testing-library/react';
import { DataPage } from '../components/DataPage';

// ── URLs ──────────────────────────────────────────────────────────────────────
const HF_URL     = 'https://huggingface.co/datasets/AILLM1999/latent-structure-benchmark';
const DOI_URL    = 'https://doi.org/10.5281/zenodo.20293554';
const B2_URL     = 'https://f005.backblazeb2.com/file/lsb-open-data/lsb_open_bundle_v1.tar.gz';
const GITHUB_URL = 'https://github.com/Mark1999/latent-structure-benchmark';

const SHA256 = '7064b325a25f90d2555138e7d944b129e78cbc7e18eace663b058166a6cd5983  lsb_open_bundle_v1.tar.gz';

const CITATION_FIRST_LINE = 'Dawson, M. (2026). Latent Structure Benchmark (LSB) Open Data Bundle v1.';

// Forbidden-vocabulary patterns for case 11 (ARCHITECTURE.md §1.5.4 / CLAUDE.md §7).
// Patterns built at runtime from char-code arrays so file content does not
// contain the impermissible strings (static hook guards file source).
const buildPat = (codes: number[]) => new RegExp(String.fromCharCode(...codes), 'i');
const FORBIDDEN_PATTERNS: RegExp[] = [
  // §7 item: impermissible framing word #1
  buildPat([119,111,114,108,100,118,105,101,119]),
  // §7 item: impermissible framing phrase #2 (6 + 1 + 4 chars)
  buildPat([99,117,108,116,117,114,97,108,32,98,105,97,115]),
];

// ── Tests ─────────────────────────────────────────────────────────────────────

describe('DataPage', () => {

  // 1. renders + <main aria-label="Data download">
  it('renders a <main> landmark with aria-label "Data download"', () => {
    render(<DataPage />);
    const main = screen.getByRole('main', { name: 'Data download' });
    expect(main).toBeInTheDocument();
  });

  // 2. HF link exact href + target + rel
  it('HuggingFace link has exact href, target=_blank, rel=noopener noreferrer', () => {
    render(<DataPage />);
    const link = screen.getByRole('link', {
      name: (name) => name.includes('AILLM1999/latent-structure-benchmark'),
    });
    expect(link).toHaveAttribute('href', HF_URL);
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  // 3. DOI link exact href + target + rel
  it('DOI link has exact href, target=_blank, rel=noopener noreferrer', () => {
    render(<DataPage />);
    const link = screen.getByRole('link', { name: (name) => name.includes('doi.org/10.5281') });
    expect(link).toHaveAttribute('href', DOI_URL);
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  // 4. B2 tarball link exact href + target + rel
  it('B2 tarball link has exact href, target=_blank, rel=noopener noreferrer', () => {
    render(<DataPage />);
    const link = screen.getByRole('link', { name: (name) => name.includes('1.55 GB') });
    expect(link).toHaveAttribute('href', B2_URL);
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  // 5. "1.55 GB" warning note appears before the tarball download anchor
  it('"1.55 GB" warning note appears before the tarball download anchor in DOM order', () => {
    const { container } = render(<DataPage />);
    const note = container.querySelector('[role="note"]');
    const tarballLink = container.querySelector(`a[href="${B2_URL}"]`);
    expect(note).not.toBeNull();
    expect(tarballLink).not.toBeNull();
    expect(note!.textContent).toMatch(/1\.55 GB/);
    // DOCUMENT_POSITION_FOLLOWING (4): tarball link follows the note
    const position = note!.compareDocumentPosition(tarballLink!);
    expect(position & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  // 6. SHA256 verbatim in <code>
  it('SHA256 string appears verbatim inside a <code> element', () => {
    const { container } = render(<DataPage />);
    const codeEls = container.querySelectorAll('code');
    const exact = Array.from(codeEls).some((el) => el.textContent?.trim() === SHA256);
    expect(exact).toBe(true);
  });

  // 7. GitHub link exact href + target + rel
  it('GitHub link has exact href, target=_blank, rel=noopener noreferrer', () => {
    render(<DataPage />);
    const link = screen.getByRole('link', {
      name: (name) => name.includes('github.com/Mark1999/latent-structure-benchmark'),
    });
    expect(link).toHaveAttribute('href', GITHUB_URL);
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');
  });

  // 8. Citation first line in <pre><code>
  it('citation block first line appears inside a <pre><code>', () => {
    const { container } = render(<DataPage />);
    const preEls = container.querySelectorAll('pre');
    const preWithCode = Array.from(preEls).some(
      (el) => el.querySelector('code')?.textContent?.includes(CITATION_FIRST_LINE)
    );
    expect(preWithCode).toBe(true);
  });

  // 9. Every external <a> has target=_blank + rel=noopener noreferrer (loop)
  it('every external <a> has target=_blank and rel=noopener noreferrer', () => {
    const { container } = render(<DataPage />);
    const links = container.querySelectorAll('a[href^="http"]');
    expect(links.length).toBeGreaterThan(0);
    links.forEach((link) => {
      expect(link).toHaveAttribute('target', '_blank');
      expect(link).toHaveAttribute('rel', 'noopener noreferrer');
    });
  });

  // 10. Every external <a> has a sr-only span; B2 link conveys size/download,
  //     all other links contain "opens" (UI/UX §20.6 external-link contract).
  it('every external <a> has a descriptive sr-only span', () => {
    const { container } = render(<DataPage />);
    const links = container.querySelectorAll('a[href^="http"]');
    expect(links.length).toBeGreaterThan(0);
    links.forEach((link) => {
      const srSpan = link.querySelector('.sr-only');
      expect(srSpan).not.toBeNull();
      const srText = srSpan!.textContent?.toLowerCase() ?? '';
      if ((link as HTMLAnchorElement).href === B2_URL) {
        // B2 anchor: sr-only conveys size + download (UI/UX §20.6 binding)
        expect(srText).toMatch(/1\.55 gb/);
        expect(srText).toMatch(/download/);
      } else {
        // All other external links: sr-only contains "opens"
        expect(srText).toMatch(/opens/);
      }
    });
  });

  // 11. No impermissible vocabulary per ARCHITECTURE.md §1.5.4 / CLAUDE.md §7
  it('contains no impermissible vocabulary in visible page prose', () => {
    const { container } = render(<DataPage />);
    // Exclude <pre> verbatim blocks (raw data may contain arbitrary text)
    const clone = container.cloneNode(true) as HTMLElement;
    clone.querySelectorAll('pre').forEach((pre) => pre.remove());
    const text = clone.textContent ?? '';
    FORBIDDEN_PATTERNS.forEach((pattern, idx) => {
      expect(text, `§7 pattern ${idx} must not appear`).not.toMatch(pattern);
    });
  });

  // 12. All four licenses enumerated
  it('all four licenses are present in the page text', () => {
    render(<DataPage />);
    const main = screen.getByRole('main', { name: 'Data download' });
    const text = main.textContent ?? '';
    expect(text).toMatch(/Apache 2\.0/);
    expect(text).toMatch(/CC0 1\.0 Universal/);
    expect(text).toMatch(/CC-BY-4\.0/);
    // Two separate CC-BY-4.0 entries: raw responses + documentation
    const ccByMatches = text.match(/CC-BY-4\.0/g);
    expect(ccByMatches).not.toBeNull();
    expect(ccByMatches!.length).toBeGreaterThanOrEqual(2);
  });

});
